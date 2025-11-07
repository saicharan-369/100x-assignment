"""SQLAlchemy table metadata mirroring the MySQL DDL."""
from __future__ import annotations

from sqlalchemy import (
    BOOLEAN,
    CHAR,
    Column,
    DECIMAL,
    INTEGER,
    MetaData,
    SMALLINT,
    String,
    Table,
    DateTime,
)

metadata = MetaData()

property_table = Table(
    "property",
    metadata,
    Column("property_key", String(32), primary_key=True),
    Column("property_title", String(255)),
    Column("address", String(255)),
    Column("market", String(100)),
    Column("flood", String(50)),
    Column("street_address", String(255)),
    Column("city", String(100)),
    Column("state", CHAR(2)),
    Column("zip_code", CHAR(5)),
    Column("property_type", String(100)),
    Column("highway", String(50)),
    Column("train", String(50)),
    Column("tax_rate", DECIMAL(7, 4)),
    Column("sqft_basement", INTEGER),
    Column("htw", String(50)),
    Column("pool", BOOLEAN),
    Column("commercial", BOOLEAN),
    Column("water", String(50)),
    Column("sewage", String(50)),
    Column("year_built", SMALLINT),
    Column("sqft_mixed_use", INTEGER),
    Column("sqft_total", INTEGER),
    Column("parking", String(50)),
    Column("bed", SMALLINT),
    Column("bath", DECIMAL(3, 1)),
    Column("basement", BOOLEAN),
    Column("layout", String(50)),
    Column("rent_restricted", BOOLEAN),
    Column("neighborhood_rating", SMALLINT),
    Column("latitude", DECIMAL(10, 6)),
    Column("longitude", DECIMAL(10, 6)),
    Column("subdivision", String(255)),
    Column("school_average", DECIMAL(4, 2)),
    Column("created_at", DateTime),
)

leads_table = Table(
    "leads",
    metadata,
    Column("property_key", String(32), primary_key=True),
    Column("reviewed_status", String(100)),
    Column("most_recent_status", String(100)),
    Column("source", String(100)),
    Column("occupancy", String(100)),
    Column("net_yield", DECIMAL(6, 3)),
    Column("irr", DECIMAL(6, 3)),
    Column("selling_reason", String(255)),
    Column("seller_retained_broker", BOOLEAN),
    Column("final_reviewer", String(100)),
)

valuation_table = Table(
    "valuation",
    metadata,
    Column("property_key", String(32), primary_key=True),
    Column("scenario_rank", SMALLINT, primary_key=True),
    Column("list_price", DECIMAL(14, 2)),
    Column("previous_rent", DECIMAL(14, 2)),
    Column("arv", DECIMAL(14, 2)),
    Column("expected_rent", DECIMAL(14, 2)),
    Column("rent_zestimate", DECIMAL(14, 2)),
    Column("low_fmr", DECIMAL(14, 2)),
    Column("high_fmr", DECIMAL(14, 2)),
    Column("redfin_value", DECIMAL(14, 2)),
    Column("zestimate", DECIMAL(14, 2)),
)

rehab_table = Table(
    "rehab",
    metadata,
    Column("property_key", String(32), primary_key=True),
    Column("scenario_rank", SMALLINT, primary_key=True),
    Column("underwriting_rehab", DECIMAL(14, 2)),
    Column("rehab_calculation", DECIMAL(14, 2)),
    Column("paint", BOOLEAN),
    Column("flooring_flag", BOOLEAN),
    Column("foundation_flag", BOOLEAN),
    Column("roof_flag", BOOLEAN),
    Column("hvac_flag", BOOLEAN),
    Column("kitchen_flag", BOOLEAN),
    Column("bathroom_flag", BOOLEAN),
    Column("appliances_flag", BOOLEAN),
    Column("windows_flag", BOOLEAN),
    Column("landscaping_flag", BOOLEAN),
    Column("trashout_flag", BOOLEAN),
)

hoa_table = Table(
    "hoa",
    metadata,
    Column("property_key", String(32), primary_key=True),
    Column("scenario_rank", SMALLINT, primary_key=True),
    Column("hoa_amount", DECIMAL(12, 2)),
    Column("hoa_flag", BOOLEAN),
)

taxes_table = Table(
    "taxes",
    metadata,
    Column("property_key", String(32), primary_key=True),
    Column("amount", DECIMAL(14, 2)),
)
