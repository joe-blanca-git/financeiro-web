from sqlalchemy import Column, String, Date
from app.core.database import Base

class Feriado(Base):
    __tablename__ = "feriados"

    data = Column(Date, primary_key=True)          # Dia sem expediente bancário (não conta como dia útil)
    descricao = Column(String(100), nullable=True)  # Ex.: "Nossa Senhora Aparecida"
