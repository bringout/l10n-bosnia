"""fiscal_log uuid

Revision ID: 3c03afe323b2
Revises: 2cb9fbbd9f47
Create Date: 2025-01-08 16:01:05.191381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision: str = '3c03afe323b2'
down_revision: Union[str, None] = '2cb9fbbd9f47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    #https://www.rossgray.co.uk/posts/alembic-migrations-involving-postgresql-column-default-values/
    op.alter_column("fiscal_log", "id", default=uuid.uuid4)



def downgrade() -> None:
    pass
