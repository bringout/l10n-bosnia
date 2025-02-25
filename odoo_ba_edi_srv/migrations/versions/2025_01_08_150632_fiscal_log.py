"""fiscal_log

Revision ID: 2cb9fbbd9f47
Revises: 9aa37cdd0ee8
Create Date: 2025-01-08 15:06:32.210258

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import datetime
import uuid

# https://docs.sqlalchemy.org/en/20/dialects/postgresql.html#postgresql-data-types
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '2cb9fbbd9f47'
down_revision: Union[str, None] = '9aa37cdd0ee8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    # https://stackoverflow.com/questions/15668115/alembic-how-to-migrate-custom-type-in-a-model
    # https://stackoverflow.com/questions/47206201/how-to-use-enum-with-sqlalchemy-and-alembic

    op.create_table(
        "fiscal_log",
        sa.Column("id", UUID(), nullable=False, default=uuid.uuid4),
        sa.Column("created", sa.DateTime(), default=datetime.datetime.now()),
        sa.Column("resolved", sa.DateTime() ),
        sa.Column("input", sa.String(), nullable=False),
        sa.Column("input_file", sa.String(), nullable=False),
        sa.Column("output", sa.String()),
        #https://makimo.com/blog/upgrading-postgresqls-enum-type-with-sqlalchemy-using-alembic-migration/
        sa.Column("status", sa.Enum('STARTED', 'FAILED', 'OK', name='status'), default='STARTED' ),
        sa.Column("type", sa.Enum('FISCAL', 'NONFISCAL', 'REPORT', name='type') ),
        sa.Column("input_number", sa.String() ),
        sa.Column("fiscal_number", sa.String() ),
        sa.Column("fiscal_number_2", sa.String() ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint('id')
    )


def downgrade() -> None:
    op.drop_table("fiscal_log")
