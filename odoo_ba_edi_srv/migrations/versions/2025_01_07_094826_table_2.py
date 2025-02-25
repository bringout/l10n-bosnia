"""table 2

Revision ID: 9aa37cdd0ee8
Revises: c6b516e182b2
Create Date: 2025-01-07 09:48:26.447695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9aa37cdd0ee8'
down_revision: Union[str, None] = 'c6b516e182b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "table_2",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("naz", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )



def downgrade() -> None:
    op.drop_table("table_2")
