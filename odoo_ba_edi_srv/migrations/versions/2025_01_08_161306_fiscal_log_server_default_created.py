"""fiscal_log server_default created

Revision ID: 652b184c388c
Revises: 3c03afe323b2
Create Date: 2025-01-08 16:13:06.453263

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '652b184c388c'
down_revision: Union[str, None] = '3c03afe323b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("fiscal_log", "created", server_default=sa.func.current_timestamp())
    pass

def downgrade() -> None:
    pass
