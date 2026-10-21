from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class Gerente(Base):
    __tablename__ = "gerente"

    idGerente = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(Integer, nullable=False, unique=True)
    nome = Column(String(100), nullable=False)
    idUser = Column(Integer, ForeignKey("users.iduser"), nullable=True, unique=True)  # login do gerente (nível Comercial - Vendas)
    obs = Column(String(500), nullable=True)
