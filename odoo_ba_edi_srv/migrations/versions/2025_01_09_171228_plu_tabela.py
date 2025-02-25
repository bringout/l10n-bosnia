"""plu tabela

Revision ID: 2eedb6445f60
Revises: 652b184c388c
Create Date: 2025-01-09 17:12:28.089299

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision: str = '2eedb6445f60'
down_revision: Union[str, None] = '652b184c388c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fiscal_plu",
        sa.Column("id", sa.Integer() ),
        sa.Column("created", sa.DateTime(), server_default=sa.func.current_timestamp()),
        sa.Column("naziv", sa.String() ),
        sa.Column("cijena", sa.Numeric(10,2) ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint('id')
    )


def downgrade() -> None:
    op.drop_table("fiscal_plu")
