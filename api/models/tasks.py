from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, CHAR, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id = Column(Integer, primary_key=True, autoincrement=True, comment='자동생성')
    nickname = Column(String(20), nullable=True)
    pwd = Column(String(60), nullable=False, comment='암호화')
    email = Column(String(320), nullable=True)
    gender = Column(Boolean, nullable=False, comment='True 이면 남자, False 이면 여자')
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='자동')
    updated_at = Column(DateTime, nullable=True)

    settings = relationship("Settings", back_populates="user_info", cascade="all, delete, delete-orphan")
    notes = relationship("Notes", back_populates="user_info", cascade="all, delete, delete-orphan")
    calendars = relationship("Calendars", back_populates="user_info", cascade="all, delete, delete-orphan")


class Settings(Base):
    __tablename__ = 'settings'

    user_id = Column(Integer, ForeignKey('user_info.user_id'), primary_key=True)
    user_id2 = Column(Integer, ForeignKey('user_info.user_id'), primary_key=True)
    theme = Column(String(7), nullable=False, comment="Hex color")
    font_size = Column(Integer, nullable=False, default=17)
    updated_at = Column(DateTime, nullable=True)

    user_info = relationship("UserInfo", back_populates="settings")


class Notes(Base):
    __tablename__ = 'notes'

    note_id = Column(Integer, primary_key=True, autoincrement=True, comment='자동생성')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='자동')
    updated_at = Column(DateTime, nullable=True)

    user_info = relationship("UserInfo", back_populates="notes")
    erd = relationship("ERD", back_populates="notes", cascade="all, delete, delete-orphan")


class ERD(Base):
    __tablename__ = 'erd'

    erd_id = Column(Integer, primary_key=True, autoincrement=True)
    note_id = Column(Integer, ForeignKey('notes.note_id'), nullable=False, comment='자동생성')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False)
    title = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now, comment='자동')
    updated_at = Column(DateTime, nullable=True)

    notes = relationship("Notes", back_populates="erd")


class AI(Base):
    __tablename__ = 'AI'

    goal_id = Column(Integer, primary_key=True)
    note_id = Column(Integer, ForeignKey('notes.note_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False)
    content = Column(Text, nullable=False, comment='분석 결과')

    notes = relationship("Notes", back_populates="ai")


class API(Base):
    __tablename__ = 'api'

    api_id = Column(Integer, primary_key=True, autoincrement=True, comment='자동 생성')
    note_id = Column(Integer, ForeignKey('notes.note_id'), nullable=False, comment='자동생성')
    user_id = Column(Integer, ForeignKey('user_info.user_id'), nullable=False)
    title = Column(String(100), nullable=True)
    content = Column(Text, nullable=True)
    update_at = Column(DateTime, nullable=True)

    notes = relationship("Notes", back_populates="api")


class AdminInfo(Base):
    __tablename__ = 'admin_info'

    admin_id = Column(Integer, primary_key=True)
    admin_name = Column(String(20), nullable=False)
    admin_email = Column(String(320), nullable=False)
    admin_pwd = Column(String(60), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)

    admin_logs = relationship("AdminLogs", back_populates="admin_info")


class AdminLogs(Base):
    __tablename__ = 'admin_logs'

    log_id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey('admin_info.admin_id'), nullable=False)
    target_table = Column(String, nullable=False)
    action = Column(String, nullable=False, default='50')
    created_at = Column(DateTime, nullable=False)
    target_id = Column(Integer, nullable=False)

    admin_info = relationship("AdminInfo", back_populates="admin_logs")

