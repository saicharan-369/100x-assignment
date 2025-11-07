"""Transformation logic converting raw payloads into normalized domain models."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Iterator

import pandas as pd

from src.models.property import (
    HOARecord,
    LeadRecord,
    PropertyRecord,
    RehabRecord,
    TaxRecord,
    ValuationRecord,
    iter_scenarios,
)
from src.utils.cleaning import normalize_string


@dataclass(slots=True)
class NormalizedBundle:
    """Container holding all derived entities for persistence."""

    properties: list[PropertyRecord]
    leads: list[LeadRecord]
    valuations: list[ValuationRecord]
    rehabs: list[RehabRecord]
    hoas: list[HOARecord]
    taxes: list[TaxRecord]


class DatasetTransformer:
    """Transform raw dictionaries into validated schema-aligned objects."""

    def __init__(self, field_config: pd.DataFrame | None = None) -> None:
        self.field_config = field_config

        self.property_fields = self._build_field_map(
            table_name="property",
            overrides={
                "Zip": "zip_code",
                "SQFT_MU": "sqft_mixed_use",
                "BasementYesNo": "basement",
            },
        )
        self.lead_fields = self._build_field_map("leads")
        self.valuation_fields = self._build_field_map("valuation")
        self.rehab_fields = self._build_field_map("rehab")
        self.hoa_fields = self._build_field_map("hoa")
        self.tax_fields = self._build_field_map("taxes", overrides={"Taxes": "amount"})

    def transform(self, records: Iterable[dict[str, object]]) -> NormalizedBundle:
        properties: list[PropertyRecord] = []
        leads: list[LeadRecord] = []
        valuations: list[ValuationRecord] = []
        rehabs: list[RehabRecord] = []
        hoas: list[HOARecord] = []
        taxes: list[TaxRecord] = []
        seen_properties: set[str] = set()

        for index, record in enumerate(records, start=1):
            property_key = self._build_property_key(record, index)

            if property_key in seen_properties:
                continue
            seen_properties.add(property_key)

            property_payload = {
                "property_key": property_key,
                **self._project_fields(record, self.property_fields),
            }
            property_model = PropertyRecord(**property_payload)
            properties.append(property_model)

            lead_payload = {
                "property_key": property_key,
                **self._project_fields(record, self.lead_fields),
            }
            if self._has_meaningful_payload(lead_payload, skip_keys={"property_key"}):
                leads.append(LeadRecord(**lead_payload))

            taxes_payload = {
                "property_key": property_key,
                **self._project_fields(record, self.tax_fields),
            }
            if self._has_meaningful_payload(taxes_payload, skip_keys={"property_key"}):
                taxes.append(TaxRecord(**taxes_payload))

            valuation_scenarios = iter_scenarios(record.get("Valuation"))
            for scenario_rank, scenario in valuation_scenarios:
                valuation_payload = {
                    "property_key": property_key,
                    "scenario_rank": scenario_rank,
                    **self._project_fields(scenario, self.valuation_fields),
                }
                if self._has_meaningful_payload(valuation_payload, skip_keys={"property_key", "scenario_rank"}):
                    valuations.append(ValuationRecord(**valuation_payload))

            rehab_scenarios = iter_scenarios(record.get("Rehab"))
            for scenario_rank, scenario in rehab_scenarios:
                rehab_payload = {
                    "property_key": property_key,
                    "scenario_rank": scenario_rank,
                    **self._project_fields(scenario, self.rehab_fields),
                }
                if self._has_meaningful_payload(rehab_payload, skip_keys={"property_key", "scenario_rank"}):
                    rehabs.append(RehabRecord(**rehab_payload))

            hoa_scenarios = iter_scenarios(record.get("HOA"))
            for scenario_rank, scenario in hoa_scenarios:
                hoa_payload = {
                    "property_key": property_key,
                    "scenario_rank": scenario_rank,
                    **self._project_fields(scenario, self.hoa_fields),
                }
                if self._has_meaningful_payload(hoa_payload, skip_keys={"property_key", "scenario_rank"}):
                    hoas.append(HOARecord(**hoa_payload))

        return NormalizedBundle(
            properties=properties,
            leads=leads,
            valuations=valuations,
            rehabs=rehabs,
            hoas=hoas,
            taxes=taxes,
        )

    def _build_field_map(
        self,
        table_name: str,
        overrides: dict[str, str] | None = None,
    ) -> dict[str, str]:
        if self.field_config is None:
            return {}

        filtered = self.field_config[
            self.field_config["Target Table"].astype(str).str.lower() == table_name.lower()
        ]["Column Name"]

        mapping: dict[str, str] = {}
        for column_name in filtered:
            if not isinstance(column_name, str):
                continue
            normalized = overrides.get(column_name) if overrides else None
            if not normalized:
                normalized = self._to_snake_case(column_name)
            mapping[column_name] = normalized
        return mapping

    def _project_fields(self, source: dict[str, object] | None, mapping: dict[str, str]) -> dict[str, object]:
        if not source:
            return {}
        projected: dict[str, object] = {}
        for raw_key, target_key in mapping.items():
            if raw_key in source:
                projected[target_key] = source.get(raw_key)
        return projected

    def _build_property_key(self, record: dict[str, object], index: int) -> str:
        components: list[str] = []
        for key in ("Street_Address", "City", "State", "Zip"):
            value = normalize_string(record.get(key))
            if value:
                components.append(value.lower())
        if not components:
            fallback = normalize_string(record.get("Property_Title")) or normalize_string(record.get("Address"))
            if fallback:
                components.append(fallback.lower())
        seed = "||".join(components) or f"record-{index}"
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
        state = normalize_string(record.get("State"))
        state_prefix = (state or "XX").upper()
        return f"{state_prefix}-{digest}"

    @staticmethod
    def _to_snake_case(value: str) -> str:
        sanitized = value.replace(" ", "_").replace("-", "_")
        result: list[str] = []
        prev_lower = False
        for char in sanitized:
            if char.isupper() and prev_lower:
                result.append("_")
            result.append(char.lower())
            prev_lower = char.islower()
        snake = "".join(result)
        snake = snake.replace("__", "_")
        return snake

    @staticmethod
    def _has_meaningful_payload(payload: dict[str, object], skip_keys: set[str]) -> bool:
        for key, value in payload.items():
            if key in skip_keys:
                continue
            if value is not None and value != "":
                return True
        return False

    def iter_property_records(self, data: Iterable[dict[str, object]]) -> Iterator[PropertyRecord]:
        """Yield property records for streaming use-cases."""

        bundle = self.transform(data)
        yield from bundle.properties
