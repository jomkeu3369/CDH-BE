"""empty message

Revision ID: be8cc8887939
Revises: c0e7eac98cc4
Create Date: 2024-11-28 13:22:44.404460

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be8cc8887939'
down_revision: Union[str, None] = 'c0e7eac98cc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('member',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='PK'),
    sa.Column('invite_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False, comment='사용자 고유 아이디'),
    sa.Column('nickname', sa.String(length=20), nullable=False),
    sa.Column('joined_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['invite_id'], ['group.invite_id'], ),
    sa.ForeignKeyConstraint(['nickname'], ['user_info.nickname'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('invite_id')
    )
    op.create_unique_constraint(None, 'group', ['invite_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'group', type_='unique')
    op.drop_table('member')
    # ### end Alembic commands ###
