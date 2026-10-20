from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Representante(Base):
    __tablename__ = "representantes"

    idRepresentante = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(Integer, nullable=False, unique=True)
    nome = Column(String(100), nullable=False)
    idGerente = Column(Integer, ForeignKey("gerente.idGerente"), nullable=True)
    obs = Column(String(500), nullable=True)

    gerente = relationship("Gerente")
