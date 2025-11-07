"""Configuration objects and constants for the ETL pipeline."""
from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ETLSettings(BaseSettings):
    """Centralized runtime configuration for the ETL pipeline."""

    data_path: Path = Field(default=Path("data/fake_property_data_new.json"), description="Path to the raw property dataset.")
    field_config_path: Path = Field(default=Path("data/Field Config.xlsx"), description="Path to the field configuration workbook.")

    mysql_host: str = Field(default="127.0.0.1", description="MySQL hostname.")
    mysql_port: int = Field(default=3306, description="MySQL port.")
    mysql_user: str = Field(default="db_user", description="MySQL username.")
    mysql_password: str = Field(default="6equj5_db_user", description="MySQL password.")
    mysql_database: str = Field(default="home_db", description="Target MySQL database name.")

    batch_size: int = Field(default=1000, ge=1, description="Number of records to insert per batch during loading.")
    echo_sql: bool = Field(default=False, description="Enable SQLAlchemy engine echo for debugging.")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", env_prefix="ETL_")

    @property
    def sqlalchemy_url(self) -> str:
        """Construct a SQLAlchemy MySQL connection URL."""

        return (
            f"mysql+mysqlconnector://{self.mysql_user}:{self.mysql_password}"  # noqa: S105
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )
