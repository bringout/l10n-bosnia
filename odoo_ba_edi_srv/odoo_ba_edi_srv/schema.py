from sqlalchemy import Column, Integer, MetaData, String, Table, Enum, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
import uuid

metadata = MetaData()

dbos_hello = Table(
    "dbos_hello",
    metadata,
    Column("greet_count", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
)

table_2 = Table(
    "table_2",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("naz", String, nullable=False),
)

fiscal_log = Table(
        "fiscal_log",
        metadata,
        Column("id", UUID, nullable=False, default=uuid.uuid4),
        Column("created", DateTime),
        Column("resolved", DateTime),
        Column("input", String, nullable=False),
        Column("input_file", String, nullable=False),
        Column("output", String),
        Column("status", Enum('STARTED', 'FAILED', 'OK', name='status'), default='STARTED' ),
        Column("type", Enum('FISCAL', 'NONFISCAL', 'REPORT', name='type') ),
        Column("input_number", String ),
        Column("fiscal_number", String ),
        Column("fiscal_number_2", String ),
)

fiscal_plu = Table(
        "fiscal_plu",
        metadata,
        Column("id", Integer, primary_key=True ),
        Column("created", DateTime),
        Column("naziv", String ),
        Column("cijena", Numeric(10,2) ),
        Column("tarifa", String ),
)