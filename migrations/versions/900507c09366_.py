"""empty message

Revision ID: 900507c09366
Revises: 3e04ffa8c4bb
Create Date: 2024-11-23 12:37:34.810740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '900507c09366'
down_revision: Union[str, None] = '3e04ffa8c4bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('api', sa.Column('content', sa.Text(), nullable=True))
    op.drop_column('api', 'description')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('api', sa.Column('description', mysql.TEXT(), nullable=True))
    op.drop_column('api', 'content')
    # ### end Alembic commands ###