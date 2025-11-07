"""Domain models representing the normalized relational schema."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.utils.cleaning import (
    ensure_sequence,
    normalize_bool,
    normalize_decimal,
    normalize_float,
    normalize_int,
    normalize_string,
)


class CleanBaseModel(BaseModel):
    """Base model applying shared pydantic configuration."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class PropertyRecord(CleanBaseModel):
    """Core property entity stored in the `property` table."""

    property_key: str = Field(description="Deterministic identifier built from address details.")
    property_title: Optional[str] = Field(default=None)
    address: Optional[str] = Field(default=None)
    market: Optional[str] = Field(default=None)
    flood: Optional[str] = Field(default=None)
    street_address: Optional[str] = Field(default=None)
    city: Optional[str] = Field(default=None)
    state: Optional[str] = Field(default=None)
    zip_code: Optional[str] = Field(default=None, alias="zip")
    property_type: Optional[str] = Field(default=None)
    highway: Optional[str] = Field(default=None)
    train: Optional[str] = Field(default=None)
    tax_rate: Optional[Decimal] = Field(default=None)
    sqft_basement: Optional[int] = Field(default=None)
    htw: Optional[str] = Field(default=None)
    pool: Optional[bool] = Field(default=None)
    commercial: Optional[bool] = Field(default=None)
    water: Optional[str] = Field(default=None)
    sewage: Optional[str] = Field(default=None)
    year_built: Optional[int] = Field(default=None)
    sqft_mixed_use: Optional[int] = Field(default=None, alias="sqft_mu")
    sqft_total: Optional[int] = Field(default=None)
    parking: Optional[str] = Field(default=None)
    bed: Optional[int] = Field(default=None)
    bath: Optional[float] = Field(default=None)
    basement: Optional[bool] = Field(default=None, alias="basementyesno")
    layout: Optional[str] = Field(default=None)
    rent_restricted: Optional[bool] = Field(default=None)
    neighborhood_rating: Optional[int] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    subdivision: Optional[str] = Field(default=None)
    school_average: Optional[float] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator(
        "property_title",
        "address",
        "market",
        "flood",
        "street_address",
        "city",
        "state",
        "property_type",
        "highway",
        "train",
        "htw",
        "water",
        "sewage",
        "parking",
        "layout",
        "subdivision",
        "zip_code",
    )
    @classmethod
    def _normalize_string(cls, value: Any) -> Optional[str]:
        return normalize_string(value)

    @field_validator("pool", "commercial", "rent_restricted", mode="before")
    @classmethod
    def _normalize_bool(cls, value: Any) -> Optional[bool]:
        return normalize_bool(value)

    @field_validator("tax_rate", mode="before")
    @classmethod
    def _normalize_tax(cls, value: Any) -> Optional[Decimal]:
        return normalize_decimal(value)

    @field_validator(
        "sqft_basement",
        "sqft_mixed_use",
        "sqft_total",
        "bed",
        "neighborhood_rating",
        mode="before",
    )
    @classmethod
    def _normalize_ints(cls, value: Any) -> Optional[int]:
        return normalize_int(value)

    @field_validator("bath", "latitude", "longitude", "school_average", mode="before")
    @classmethod
    def _normalize_float(cls, value: Any) -> Optional[float]:
        return normalize_float(value)

    @field_validator("year_built", mode="before")
    @classmethod
    def _normalize_year(cls, value: Any) -> Optional[int]:
        year = normalize_int(value)
        if year and year < 1700:
            return None
        if year and year > datetime.utcnow().year:
            return None
        return year

    @field_validator("basement", mode="before")
    @classmethod
    def _normalize_basement(cls, value: Any) -> Optional[bool]:
        return normalize_bool(value)

    @field_validator("zip_code", mode="wrap")
    @classmethod
    def _normalize_zip(cls, value: Optional[str], handler):
        zip_str = handler(value)
        if zip_str is None:
            return None
        sanitized = zip_str.replace(" ", "").replace("-", "")
        if sanitized.isdigit():
            return sanitized.zfill(5)
        return zip_str


class LeadRecord(CleanBaseModel):
    """Lead metadata associated with a property."""

    property_key: str
    reviewed_status: Optional[str] = Field(default=None)
    most_recent_status: Optional[str] = Field(default=None)
    source: Optional[str] = Field(default=None)
    occupancy: Optional[str] = Field(default=None)
    net_yield: Optional[float] = Field(default=None)
    irr: Optional[float] = Field(default=None)
    selling_reason: Optional[str] = Field(default=None)
    seller_retained_broker: Optional[bool] = Field(default=None)
    final_reviewer: Optional[str] = Field(default=None)

    @field_validator("reviewed_status", "most_recent_status", "source", "occupancy", "selling_reason", "final_reviewer")
    @classmethod
    def _normalize_text(cls, value: Any) -> Optional[str]:
        return normalize_string(value)

    @field_validator("net_yield", "irr", mode="before")
    @classmethod
    def _normalize_numeric(cls, value: Any) -> Optional[float]:
        return normalize_float(value)

    @field_validator("seller_retained_broker", mode="before")
    @classmethod
    def _normalize_bool(cls, value: Any) -> Optional[bool]:
        return normalize_bool(value)


class ValuationRecord(CleanBaseModel):
    """Individual valuation scenario for a property."""

    property_key: str
    scenario_rank: int
    list_price: Optional[Decimal] = Field(default=None)
    previous_rent: Optional[Decimal] = Field(default=None)
    arv: Optional[Decimal] = Field(default=None)
    expected_rent: Optional[Decimal] = Field(default=None)
    rent_zestimate: Optional[Decimal] = Field(default=None)
    low_fmr: Optional[Decimal] = Field(default=None)
    high_fmr: Optional[Decimal] = Field(default=None)
    redfin_value: Optional[Decimal] = Field(default=None)
    zestimate: Optional[Decimal] = Field(default=None)

    @field_validator(
        "list_price",
        "previous_rent",
        "arv",
        "expected_rent",
        "rent_zestimate",
        "low_fmr",
        "high_fmr",
        "redfin_value",
        "zestimate",
        mode="before",
    )
    @classmethod
    def _normalize_money(cls, value: Any) -> Optional[Decimal]:
        return normalize_decimal(value)


class RehabRecord(CleanBaseModel):
    """Rehab scenario information for a property."""

    property_key: str
    scenario_rank: int
    underwriting_rehab: Optional[Decimal] = Field(default=None)
    rehab_calculation: Optional[Decimal] = Field(default=None)
    paint: Optional[bool] = Field(default=None)
    flooring_flag: Optional[bool] = Field(default=None)
    foundation_flag: Optional[bool] = Field(default=None)
    roof_flag: Optional[bool] = Field(default=None)
    hvac_flag: Optional[bool] = Field(default=None)
    kitchen_flag: Optional[bool] = Field(default=None)
    bathroom_flag: Optional[bool] = Field(default=None)
    appliances_flag: Optional[bool] = Field(default=None)
    windows_flag: Optional[bool] = Field(default=None)
    landscaping_flag: Optional[bool] = Field(default=None)
    trashout_flag: Optional[bool] = Field(default=None)

    @field_validator("underwriting_rehab", "rehab_calculation", mode="before")
    @classmethod
    def _normalize_cost(cls, value: Any) -> Optional[Decimal]:
        return normalize_decimal(value)

    @field_validator(
        "paint",
        "flooring_flag",
        "foundation_flag",
        "roof_flag",
        "hvac_flag",
        "kitchen_flag",
        "bathroom_flag",
        "appliances_flag",
        "windows_flag",
        "landscaping_flag",
        "trashout_flag",
        mode="before",
    )
    @classmethod
    def _normalize_flag(cls, value: Any) -> Optional[bool]:
        return normalize_bool(value)


class HOARecord(CleanBaseModel):
    """HOA dues scenarios."""

    property_key: str
    scenario_rank: int
    hoa_amount: Optional[Decimal] = Field(default=None, alias="hoa")
    hoa_flag: Optional[bool] = Field(default=None)

    @field_validator("hoa_amount", mode="before")
    @classmethod
    def _normalize_amount(cls, value: Any) -> Optional[Decimal]:
        return normalize_decimal(value)

    @field_validator("hoa_flag", mode="before")
    @classmethod
    def _normalize_flag(cls, value: Any) -> Optional[bool]:
        return normalize_bool(value)


class TaxRecord(CleanBaseModel):
    """Property tax snapshot."""

    property_key: str
    amount: Optional[Decimal] = Field(default=None, alias="taxes")

    @field_validator("amount", mode="before")
    @classmethod
    def _normalize_amount(cls, value: Any) -> Optional[Decimal]:
        return normalize_decimal(value)


def iter_scenarios(raw_value: Any) -> list[tuple[int, dict[str, Any]]]:
    """Flatten nested scenario lists into enumerated dictionaries."""

    items = ensure_sequence(raw_value)
    return [(index + 1, dict(item)) for index, item in enumerate(items)]
