"""empty message

Revision ID: 6dd4f5f25df5
Revises: 2b57c9741d4e
Create Date: 2025-02-19 13:29:05.206502

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6dd4f5f25df5'
down_revision: Union[str, None] = '2b57c9741d4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("fiscal_plu", "tarifa", default="0")
    pass


def downgrade() -> None:
    pass
