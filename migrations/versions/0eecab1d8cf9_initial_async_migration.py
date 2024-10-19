"""initial async migration

Revision ID: 0eecab1d8cf9
Revises: 07a0ef49c7f5
Create Date: 2024-10-09 19:51:49.193625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0eecab1d8cf9'
down_revision: Union[str, None] = '07a0ef49c7f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('edit_date', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('question', 'edit_date')
    # ### end Alembic commands ###