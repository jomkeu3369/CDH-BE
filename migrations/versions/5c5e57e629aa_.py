"""empty message

Revision ID: 5c5e57e629aa
Revises: 0fad4b28b04a
Create Date: 2024-10-14 00:46:26.429583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '5c5e57e629aa'
down_revision: Union[str, None] = '0fad4b28b04a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agreement',
    sa.Column('id', sa.BigInteger(), nullable=False, comment='동의 고유번호'),
    sa.Column('user_id', sa.BigInteger(), nullable=False, comment='사용자 고유 아이디'),
    sa.Column('agree_term', sa.Boolean(), nullable=False, comment='이용약관 동의 여부'),
    sa.Column('agree_privacy', sa.Boolean(), nullable=False, comment='개인정보 이용 동의 여부'),
    sa.Column('agree_sensitive', sa.Boolean(), nullable=False, comment='민감정보 동의 여부 (AI사용동의)'),
    sa.Column('create_at', sa.DateTime(), nullable=False, comment='생성 시각'),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('calenders',
    sa.Column('calender_id', sa.Integer(), nullable=False, comment='자동생성'),
    sa.Column('user_id', sa.BigInteger(), nullable=False, comment='사용자 고유 아이디'),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=False),
    sa.Column('update_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], ),
    sa.PrimaryKeyConstraint('calender_id')
    )
    op.create_table('login_log',
    sa.Column('id', sa.BigInteger(), nullable=False, comment='PK'),
    sa.Column('user_id', sa.BigInteger(), nullable=False, comment='사용자 고유 아이디'),
    sa.Column('login_at', sa.DateTime(), nullable=False, comment='로그인 시각'),
    sa.Column('login_ip', sa.String(length=50), nullable=False, comment='로그인 IP'),
    sa.Column('login_useragent', sa.String(length=255), nullable=True, comment='로그인 시 useragent'),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sign_up_log',
    sa.Column('id', sa.BigInteger(), nullable=False, comment='PK'),
    sa.Column('user_id', sa.BigInteger(), nullable=False, comment='사용자 고유 아이디'),
    sa.Column('sign_up_ip', sa.String(length=50), nullable=False, comment='회원 가입 IP'),
    sa.Column('sign_up_datetime', sa.DateTime(), nullable=False, comment='회원 가입 일시'),
    sa.Column('sign_up_useragent', sa.String(length=255), nullable=False, comment='회원 가입 시 useragent'),
    sa.ForeignKeyConstraint(['user_id'], ['user_info.user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('AI', 'note_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='노트 고유 아이디',
               existing_nullable=False)
    op.drop_constraint('AI_ibfk_2', 'AI', type_='foreignkey')
    op.drop_column('AI', 'user_id')
    op.alter_column('admin_info', 'admin_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='관리자고유번호',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('admin_info', 'admin_name',
               existing_type=mysql.VARCHAR(length=20),
               comment='관리자 닉네임',
               existing_nullable=False)
    op.alter_column('admin_info', 'admin_email',
               existing_type=mysql.VARCHAR(length=320),
               comment='관리자 이메일',
               existing_nullable=False)
    op.alter_column('admin_info', 'admin_pwd',
               existing_type=mysql.VARCHAR(length=60),
               comment='관리자 비밀번호 (암호화)',
               existing_nullable=False)
    op.alter_column('admin_info', 'created_at',
               existing_type=mysql.DATETIME(),
               comment='계정 생성 시각',
               existing_nullable=False)
    op.alter_column('admin_info', 'updated_at',
               existing_type=mysql.DATETIME(),
               comment='계정 수정 시각',
               existing_nullable=True)
    op.alter_column('admin_logs', 'log_id',
               existing_type=mysql.INTEGER(),
               comment='로그 ID',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('admin_logs', 'admin_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               existing_nullable=False)
    op.alter_column('admin_logs', 'target_table',
               existing_type=mysql.VARCHAR(length=199),
               type_=sa.String(length=200),
               existing_nullable=False)
    op.alter_column('api', 'api_id',
               existing_type=mysql.INTEGER(),
               comment='API 명세서 고유 아이디',
               existing_comment='자동 생성',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('api', 'note_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='노트 고유 아이디',
               existing_comment='자동생성',
               existing_nullable=False)
    op.alter_column('api', 'title',
               existing_type=mysql.VARCHAR(length=100),
               comment='노트 제목',
               existing_nullable=True)
    op.alter_column('api', 'content',
               existing_type=mysql.TEXT(),
               type_=sa.Enum('내용1', '내용2'),
               comment='내용',
               existing_nullable=True)
    op.alter_column('api', 'update_at',
               existing_type=mysql.DATETIME(),
               nullable=False,
               comment='문서 생성 시각')
    op.drop_constraint('api_ibfk_2', 'api', type_='foreignkey')
    op.drop_column('api', 'user_id')
    op.alter_column('erd', 'note_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='노트 고유 아이디',
               existing_comment='자동생성',
               existing_nullable=False)
    op.drop_constraint('erd_ibfk_2', 'erd', type_='foreignkey')
    op.drop_column('erd', 'user_id')
    op.alter_column('notes', 'note_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='노트 고유 아이디',
               existing_comment='자동생성',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('notes', 'user_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='사용자 고유 아이디',
               existing_nullable=False)
    op.add_column('settings', sa.Column('pk', sa.BigInteger(), nullable=False))
    op.alter_column('settings', 'user_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='사용자 고유 아이디',
               existing_nullable=False)
    op.alter_column('settings', 'theme',
               existing_type=mysql.VARCHAR(length=7),
               comment='hax color',
               existing_comment='Hex color',
               existing_nullable=False)
    op.drop_constraint('settings_ibfk_2', 'settings', type_='foreignkey')
    op.drop_column('settings', 'user_id2')
    op.alter_column('user_info', 'user_id',
               existing_type=mysql.INTEGER(),
               type_=sa.BigInteger(),
               comment='사용자 고유 아이디',
               existing_comment='자동생성',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('user_info', 'gender',
               existing_type=mysql.TINYINT(display_width=1),
               comment='True : 남자, False : 여자',
               existing_comment='True 이면 남자, False 이면 여자',
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user_info', 'gender',
               existing_type=mysql.TINYINT(display_width=1),
               comment='True 이면 남자, False 이면 여자',
               existing_comment='True : 남자, False : 여자',
               existing_nullable=False)
    op.alter_column('user_info', 'user_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment='자동생성',
               existing_comment='사용자 고유 아이디',
               existing_nullable=False,
               autoincrement=True)
    op.add_column('settings', sa.Column('user_id2', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('settings_ibfk_2', 'settings', 'user_info', ['user_id2'], ['user_id'])
    op.alter_column('settings', 'theme',
               existing_type=mysql.VARCHAR(length=7),
               comment='Hex color',
               existing_comment='hax color',
               existing_nullable=False)
    op.alter_column('settings', 'user_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment=None,
               existing_comment='사용자 고유 아이디',
               existing_nullable=False)
    op.drop_column('settings', 'pk')
    op.alter_column('notes', 'user_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment=None,
               existing_comment='사용자 고유 아이디',
               existing_nullable=False)
    op.alter_column('notes', 'note_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment='자동생성',
               existing_comment='노트 고유 아이디',
               existing_nullable=False,
               autoincrement=True)
    op.add_column('erd', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('erd_ibfk_2', 'erd', 'user_info', ['user_id'], ['user_id'])
    op.alter_column('erd', 'note_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment='자동생성',
               existing_comment='노트 고유 아이디',
               existing_nullable=False)
    op.add_column('api', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('api_ibfk_2', 'api', 'user_info', ['user_id'], ['user_id'])
    op.alter_column('api', 'update_at',
               existing_type=mysql.DATETIME(),
               nullable=True,
               comment=None,
               existing_comment='문서 생성 시각')
    op.alter_column('api', 'content',
               existing_type=sa.Enum('내용1', '내용2'),
               type_=mysql.TEXT(),
               comment=None,
               existing_comment='내용',
               existing_nullable=True)
    op.alter_column('api', 'title',
               existing_type=mysql.VARCHAR(length=100),
               comment=None,
               existing_comment='노트 제목',
               existing_nullable=True)
    op.alter_column('api', 'note_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment='자동생성',
               existing_comment='노트 고유 아이디',
               existing_nullable=False)
    op.alter_column('api', 'api_id',
               existing_type=mysql.INTEGER(),
               comment='자동 생성',
               existing_comment='API 명세서 고유 아이디',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('admin_logs', 'target_table',
               existing_type=sa.String(length=200),
               type_=mysql.VARCHAR(length=199),
               existing_nullable=False)
    op.alter_column('admin_logs', 'admin_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               existing_nullable=False)
    op.alter_column('admin_logs', 'log_id',
               existing_type=mysql.INTEGER(),
               comment=None,
               existing_comment='로그 ID',
               existing_nullable=False,
               autoincrement=True)
    op.alter_column('admin_info', 'updated_at',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='계정 수정 시각',
               existing_nullable=True)
    op.alter_column('admin_info', 'created_at',
               existing_type=mysql.DATETIME(),
               comment=None,
               existing_comment='계정 생성 시각',
               existing_nullable=False)
    op.alter_column('admin_info', 'admin_pwd',
               existing_type=mysql.VARCHAR(length=60),
               comment=None,
               existing_comment='관리자 비밀번호 (암호화)',
               existing_nullable=False)
    op.alter_column('admin_info', 'admin_email',
               existing_type=mysql.VARCHAR(length=320),
               comment=None,
               existing_comment='관리자 이메일',
               existing_nullable=False)
    op.alter_column('admin_info', 'admin_name',
               existing_type=mysql.VARCHAR(length=20),
               comment=None,
               existing_comment='관리자 닉네임',
               existing_nullable=False)
    op.alter_column('admin_info', 'admin_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment=None,
               existing_comment='관리자고유번호',
               existing_nullable=False,
               autoincrement=True)
    op.add_column('AI', sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('AI_ibfk_2', 'AI', 'user_info', ['user_id'], ['user_id'])
    op.alter_column('AI', 'note_id',
               existing_type=sa.BigInteger(),
               type_=mysql.INTEGER(),
               comment=None,
               existing_comment='노트 고유 아이디',
               existing_nullable=False)
    op.drop_table('sign_up_log')
    op.drop_table('login_log')
    op.drop_table('calenders')
    op.drop_table('agreement')
    # ### end Alembic commands ###
