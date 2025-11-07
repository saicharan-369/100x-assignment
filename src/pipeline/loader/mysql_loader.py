"""SQLAlchemy-based loader for inserting normalized records into MySQL."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, Sequence

from sqlalchemy import Engine, Table, create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models.property import HOARecord, LeadRecord, PropertyRecord, RehabRecord, TaxRecord, ValuationRecord
from src.models.tables import hoa_table, leads_table, property_table, rehab_table, taxes_table, valuation_table


class LoaderError(RuntimeError):
    """Raised when persistence into MySQL fails."""


class SQLAlchemyLoader:
    """Persist domain objects into database tables using SQLAlchemy ORM mappings."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except SQLAlchemyError as exc:  # pragma: no cover - passthrough
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def from_url(cls, url: str, echo: bool = False) -> "SQLAlchemyLoader":
        engine = create_engine(url, echo=echo, future=True)
        return cls(engine)

    def insert_properties(self, session: Session, properties: Sequence[PropertyRecord]) -> None:
        self._bulk_insert(session, property_table, properties)

    def insert_leads(self, session: Session, leads: Sequence[LeadRecord]) -> None:
        self._bulk_insert(session, leads_table, leads)

    def insert_valuations(self, session: Session, valuations: Sequence[ValuationRecord]) -> None:
        self._bulk_insert(session, valuation_table, valuations)

    def insert_rehabs(self, session: Session, rehabs: Sequence[RehabRecord]) -> None:
        self._bulk_insert(session, rehab_table, rehabs)

    def insert_hoas(self, session: Session, hoas: Sequence[HOARecord]) -> None:
        self._bulk_insert(session, hoa_table, hoas)

    def insert_taxes(self, session: Session, taxes: Sequence[TaxRecord]) -> None:
        self._bulk_insert(session, taxes_table, taxes)

    def clear_existing_data(self, session: Session) -> None:
        """Remove existing rows to keep reruns idempotent."""

        # Delete in dependency order so child tables are cleared before parent table.
        for table in (valuation_table, rehab_table, hoa_table, taxes_table, leads_table, property_table):
            session.execute(table.delete())

    def _bulk_insert(self, session: Session, table: Table, models: Sequence) -> None:
        if not models:
            return
        column_names = {column.name for column in table.columns}
        payload: list[dict[str, object]] = []
        for model in models:
            if hasattr(model, "model_dump"):
                dump = model.model_dump(mode="python", by_alias=True, exclude_unset=False)
            else:  # pragma: no cover - defensive
                dump = dict(model)

            # Ensure all table columns are present; fallback to None when missing so SQLAlchemy
            # does not request an undefined bind parameter during bulk inserts.
            normalized_row = {name: dump.get(name) for name in column_names}
            payload.append(normalized_row)
        session.execute(table.insert(), payload)
