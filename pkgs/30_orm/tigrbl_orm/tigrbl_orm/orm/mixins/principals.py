from __future__ import annotations

import re
from secrets import randbits
from time import time_ns

from sqlalchemy import String, TypeDecorator

from tigrbl.specs import ColumnSpec, F, S, acol
from tigrbl._spec.storage_spec import ForeignKeySpec
from tigrbl.types import PgUUID, UUID, declarative_mixin, declared_attr, uuid4, Mapped
from tigrbl_core._spec.datatypes import DataTypeSpec

from .utils import _infer_schema, uuid_example, CRUD_IO, RO_IO


_ULID_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_ULID_PATTERN = rf"^[0-7][{_ULID_ALPHABET}]{{25}}$"


def _new_ulid() -> str:
    timestamp_ms = time_ns() // 1_000_000
    value = (timestamp_ms << 80) | randbits(80)
    return "".join(
        _ULID_ALPHABET[(value >> shift) & 31] for shift in range(125, -1, -5)
    )


class _ULIDString(TypeDecorator[str]):
    impl = String(26)
    cache_ok = True

    @property
    def python_type(self) -> type[str]:
        return str

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        if value is not None and (
            not isinstance(value, str) or re.fullmatch(_ULID_PATTERN, value) is None
        ):
            raise ValueError("Expected a canonical 26-character uppercase ULID")
        return value


@declarative_mixin
class GUIDPk:
    """Universal surrogate primary key."""

    id: Mapped[UUID] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                primary_key=True,
                default=uuid4,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=RO_IO,
        )
    )


@declarative_mixin
class ULIDPk:
    """Add a canonical ULID string primary key, generated on insert."""

    id: Mapped[str] = acol(
        spec=ColumnSpec(
            storage=S(
                type_=_ULIDString(),
                primary_key=True,
                nullable=False,
                default=_new_ulid,
            ),
            field=F(
                py_type=str,
                constraints={
                    "min_length": 26,
                    "max_length": 26,
                    "pattern": _ULID_PATTERN,
                },
            ),
            io=RO_IO,
            datatype=DataTypeSpec(logical_name="ulid"),
        )
    )


@declarative_mixin
class TenantColumn:
    """Adds ``tenant_id`` with a schema-qualified FK to ``<schema>.tenants.id``."""

    @declared_attr
    def tenant_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__tenant_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.tenants.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class UserColumn:
    """Adds ``user_id`` with a schema-qualified FK to ``<schema>.users.id``."""

    @declared_attr
    def user_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__user_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.users.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class OrgColumn:
    """Adds ``org_id`` with a schema-qualified FK to ``<schema>.orgs.id``."""

    @declared_attr
    def org_id(cls) -> Mapped[UUID]:
        schema = getattr(cls, "__org_table_schema__", None) or _infer_schema(cls)
        spec = ColumnSpec(
            storage=S(
                type_=PgUUID(as_uuid=True),
                fk=ForeignKeySpec(target=f"{schema}.orgs.id"),
                nullable=False,
                index=True,
            ),
            field=F(py_type=UUID, constraints={"examples": [uuid_example]}),
            io=CRUD_IO,
        )
        return acol(spec=spec)


@declarative_mixin
class Principal:
    __abstract__ = True


__all__ = [
    "GUIDPk",
    "ULIDPk",
    "TenantColumn",
    "UserColumn",
    "OrgColumn",
    "Principal",
]
