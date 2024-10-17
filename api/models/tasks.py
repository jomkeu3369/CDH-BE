from sqlalchemy import create_engine, Column, Integer, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship

from api.database import Base

from datetime import datetime

class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment='사용자 고유 아이디')
    nickname = Column(String(20), nullable=True)
    pwd = Column(String(60), nullable=False, comment='암호화')
    email = Column(String(320), nullable=True)
    gender = Column(Boolean, nullable=False, comment='True : 남자, False : 여자')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='자동')
    updated_at = Column(DateTime, nullable=True)

    settings = relationship("Settings", back_populates="user_info", cascade="all, delete, delete-orphan")
    notes = relationship("Notes", back_populates="user_info", cascade="all, delete, delete-orphan")
    calendars = relationship("Calendars", back_populates="user_info", cascade="all, delete, delete-orphan")
    agreements = relationship("Agreement", back_populates="user_info", cascade="all, delete, delete-orphan")
    loginLog = relationship("LoginLog", back_populates="user_info", cascade="all, delete, delete-orphan")
    signupLog = relationship("SignUpLog", back_populates="user_info", cascade="all, delete, delete-orphan")


class Settings(Base): # pk 오류
    __tablename__ = 'settings'

    pk = Column(Integer, primary_key=True, autoincrement=True, comment="설정 고유 아이디")
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False, comment='사용자 고유 아이디')
    theme = Column(String(7), nullable=False, comment='hax color')
    font_size = Column(Integer, nullable=False, default=17)
    updated_at = Column(DateTime, nullable=True)

    user_info = relationship("UserInfo", back_populates="settings")


class Notes(Base):
    __tablename__ = 'notes'

    note_id = Column(Integer, primary_key=True, autoincrement=True, comment='노트 고유 아이디')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False, comment='사용자 고유 아이디')
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='자동')
    updated_at = Column(DateTime, nullable=True)

    user_info = relationship("UserInfo", back_populates="notes")
    erd = relationship("ERD", back_populates="notes", cascade="all, delete, delete-orphan")
    api = relationship("API", back_populates="notes", cascade="all, delete, delete-orphan")
    ai = relationship("AI", back_populates="notes", cascade="all, delete, delete-orphan")


class Calendars(Base):
    __tablename__ = 'calenders'

    calender_id = Column(Integer, primary_key=True, autoincrement=True, comment='자동생성')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False, comment='사용자 고유 아이디')
    content = Column(Text, nullable=True)
    create_at = Column(DateTime, nullable=False, default=datetime.now)
    update_at = Column(DateTime, nullable=True)

    user_info = relationship("UserInfo", back_populates="calendars")


class ERD(Base):
    __tablename__ = 'erd'

    erd_id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey('notes.note_id'), nullable=False, comment='노트 고유 아이디')
    title = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='자동')
    updated_at = Column(DateTime, nullable=True)

    notes = relationship("Notes", back_populates="erd")


class AI(Base):
    __tablename__ = 'AI'

    goal_id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey('notes.note_id'), nullable=False, comment='노트 고유 아이디')
    content = Column(Text, nullable=False, comment='분석 결과')

    notes = relationship("Notes", back_populates="ai")


class API(Base):
    __tablename__ = 'api'

    api_id = Column(Integer, primary_key=True, autoincrement=True, comment='API 명세서 고유 아이디')
    note_id = Column(Integer, ForeignKey('notes.note_id'), nullable=False, comment='노트 고유 아이디')
    title = Column(String(100), nullable=True, comment='노트 제목')
    content = Column(Text, nullable=True, comment='내용')
    update_at = Column(DateTime, nullable=False, default=datetime.now, comment='문서 생성 시각')

    notes = relationship("Notes", back_populates="api")


class AdminInfo(Base):
    __tablename__ = 'admin_info'

    admin_id = Column(Integer, primary_key=True, autoincrement=True, comment='관리자고유번호')
    admin_name = Column(String(20), nullable=False, comment='관리자 닉네임')
    admin_email = Column(String(320), nullable=False, comment='관리자 이메일')
    admin_pwd = Column(String(60), nullable=False, comment='관리자 비밀번호 (암호화)')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='계정 생성 시각')
    updated_at = Column(DateTime, nullable=True, comment='계정 수정 시각')

    admin_logs = relationship("AdminLogs", back_populates="admin_info")


class AdminLogs(Base):
    __tablename__ = 'admin_logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True, comment='로그 ID')
    admin_id = Column(Integer, ForeignKey('admin_info.admin_id'), nullable=False)
    target_table = Column(String(200), nullable=False)
    action = Column(String(100), nullable=False, default='50')
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    target_id = Column(Integer, nullable=False)

    admin_info = relationship("AdminInfo", back_populates="admin_logs")


class Agreement(Base):
    __tablename__ = 'agreement'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='동의 고유번호')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False, comment='사용자 고유 아이디')
    agree_term = Column(Boolean, nullable=False, comment='이용약관 동의 여부')
    agree_privacy = Column(Boolean, nullable=False, comment='개인정보 이용 동의 여부')
    agree_sensitive = Column(Boolean, nullable=False, comment='민감정보 동의 여부 (AI사용동의)')
    create_at = Column(DateTime, nullable=False, default=datetime.now, comment='생성 시각')

    user_info = relationship("UserInfo", back_populates="agreements")

class LoginLog(Base):
    __tablename__ = 'login_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='PK')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False, comment='사용자 고유 아이디')
    login_at = Column(DateTime, nullable=False, default=datetime.now, comment='로그인 시각')
    login_ip = Column(String(50), nullable=False, comment='로그인 IP')
    login_useragent = Column(String(255), nullable=True, comment='로그인 시 useragent')

    user_info = relationship("UserInfo", back_populates="loginLog")

class SignUpLog(Base):
    __tablename__ = 'sign_up_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='PK')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False, comment='사용자 고유 아이디')
    sign_up_ip = Column(String(50), nullable=False, comment='회원 가입 IP')
    sign_up_datetime = Column(DateTime, nullable=False, default=datetime.now, comment='회원 가입 일시')
    sign_up_useragent = Column(String(255), nullable=False, comment='회원 가입 시 useragent')

    user_info = relationship("UserInfo", back_populates="signupLog")
