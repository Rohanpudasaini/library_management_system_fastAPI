"""changed librarian to mapped_column

Revision ID: 4c3d3320683f
Revises: 653de0aabf52
Create Date: 2024-03-22 10:20:21.880579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4c3d3320683f'
down_revision: Union[str, None] = '653de0aabf52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
