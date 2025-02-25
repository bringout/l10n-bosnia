"""empty message

Revision ID: 2b57c9741d4e
Revises: 12e6c311eaf5
Create Date: 2025-02-19 13:27:10.324988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b57c9741d4e'
down_revision: Union[str, None] = '12e6c311eaf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("fiscal_plu", "tarifa", default="0")
    pass


def downgrade() -> None:
    pass
