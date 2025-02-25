"""empty message

Revision ID: 12e6c311eaf5
Revises: 2eedb6445f60
Create Date: 2025-02-19 13:21:13.763002

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12e6c311eaf5'
down_revision: Union[str, None] = '2eedb6445f60'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("fiscal_plu", sa.Column("tarifa", sa.String()) )


def downgrade() -> None:
    pass
