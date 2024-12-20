"""empty message

Revision ID: cb3a848342a0
Revises: edbb16838862
Create Date: 2024-11-30 13:44:56.140630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'cb3a848342a0'
down_revision: Union[str, None] = 'edbb16838862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_group_invite_id', table_name='user_group')
    op.drop_table('user_group')
    op.drop_table('member')
    op.drop_index('ix_group_invite_id', table_name='group')
    op.drop_table('group')
    op.drop_constraint('notes_ibfk_2', 'notes', type_='foreignkey')
    op.drop_column('notes', 'teamspace_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('teamspace_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('notes_ibfk_2', 'notes', 'group', ['teamspace_id'], ['id'])
    op.create_table('group',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False, comment='PK'),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False, comment='사용자 고유 아이디'),
    sa.Column('members', mysql.JSON(), nullable=True),
    sa.Column('invite_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], name='group_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_group_invite_id', 'group', ['invite_id'], unique=True)
    op.create_table('member',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False, comment='PK'),
    sa.Column('invite_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False, comment='사용자 고유 아이디'),
    sa.Column('joined_at', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['invite_id'], ['group.invite_id'], name='member_ibfk_1', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], name='member_ibfk_3'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('user_group',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False, comment='PK'),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False, comment='사용자 고유 아이디'),
    sa.Column('members', mysql.JSON(), nullable=True),
    sa.Column('invite_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], name='user_group_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_index('ix_user_group_invite_id', 'user_group', ['invite_id'], unique=True)
    # ### end Alembic commands ###
