"""End-to-end ETL orchestration for the property dataset."""
from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from src.config import ETLSettings
from src.pipeline.io.reader import RawDatasetReader
from src.pipeline.loader.mysql_loader import SQLAlchemyLoader
from src.pipeline.transform import DatasetTransformer

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class PipelineSummary:
    properties: int
    leads: int
    valuations: int
    rehabs: int
    hoas: int
    taxes: int

    def as_dict(self) -> dict[str, int]:
        return {
            "properties": self.properties,
            "leads": self.leads,
            "valuations": self.valuations,
            "rehabs": self.rehabs,
            "hoas": self.hoas,
            "taxes": self.taxes,
        }


def run_pipeline(settings: ETLSettings | None = None, *, dry_run: bool = False) -> PipelineSummary:
    """Execute the ETL pipeline end-to-end."""

    settings = settings or ETLSettings()

    LOGGER.info("Reading raw dataset from %s", settings.data_path)
    reader = RawDatasetReader(settings.data_path)
    raw_records = reader.load()
    LOGGER.info("Loaded %d raw property records", len(raw_records))

    LOGGER.info("Loading field configuration from %s", settings.field_config_path)
    field_config = pd.read_excel(settings.field_config_path)

    transformer = DatasetTransformer(field_config=field_config)
    bundle = transformer.transform(raw_records)

    summary = PipelineSummary(
        properties=len(bundle.properties),
        leads=len(bundle.leads),
        valuations=len(bundle.valuations),
        rehabs=len(bundle.rehabs),
        hoas=len(bundle.hoas),
        taxes=len(bundle.taxes),
    )

    LOGGER.info("Transform complete: %s", summary.as_dict())

    if dry_run:
        LOGGER.info("Dry-run enabled: skipping MySQL load stage")
        return summary

    loader = SQLAlchemyLoader.from_url(settings.sqlalchemy_url, echo=settings.echo_sql)
    LOGGER.info("Persisting bundle into MySQL at %s", settings.sqlalchemy_url)
    with loader.session_scope() as session:
        loader.clear_existing_data(session)
        loader.insert_properties(session, bundle.properties)
        loader.insert_leads(session, bundle.leads)
        loader.insert_taxes(session, bundle.taxes)
        loader.insert_valuations(session, bundle.valuations)
        loader.insert_rehabs(session, bundle.rehabs)
        loader.insert_hoas(session, bundle.hoas)

    LOGGER.info("Load phase complete")
    return summary
