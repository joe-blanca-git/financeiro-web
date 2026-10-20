from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    iduser = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(50), nullable=False, unique=True, index=True)
    password = Column(String(1000), nullable=False)
    active = Column(String(1), nullable=True, default='S')
    createdAt = Column(DateTime, nullable=True, default=func.now())
    refresh_token_google = Column(String(1000), nullable=True)
    # Convite de primeiro acesso: só o hash do token do link e a validade (8 horas)
    convite_token_hash = Column(String(64), nullable=True, index=True)
    convite_expira_em = Column(DateTime, nullable=True)
