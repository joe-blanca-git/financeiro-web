from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PrevisaoTitulosLiquidados(Base):
    __tablename__ = "previsao_titulos_liquidados"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    estabelecimento = Column(String(20), nullable=True)
    especie_documento = Column(String(20), nullable=True)
    serie_documento = Column(String(20), nullable=True)
    titulo = Column(String(50), nullable=True, index=True)
    parcela = Column(String(20), nullable=True)
    cliente = Column(String(50), nullable=True, index=True)
    nome_cliente = Column(String(255), nullable=True)
    portador = Column(String(50), nullable=True)
    matriz = Column(String(100), nullable=True)
    representante = Column(String(50), nullable=True)
    nome_representante = Column(String(255), nullable=True)
    carteira = Column(String(50), nullable=True)
    data_vencimento = Column(Date, nullable=True, index=True)
    data_credito = Column(Date, nullable=True)
    data_emissao = Column(Date, nullable=True)
    trans_abrev = Column(String(50), nullable=True)
    unid_negocio = Column(String(50), nullable=True)
    ad = Column(String(50), nullable=True)
    acumula_atraso = Column(String(20), nullable=True)
    nome_abreviado = Column(String(100), nullable=True)
    descricao_especie = Column(String(100), nullable=True)
    referencia = Column(String(100), nullable=True)
    val_movimento = Column(Numeric(15, 2), nullable=True)
    val_antecipado = Column(Numeric(15, 2), nullable=True)
    descto_abatim = Column(Numeric(15, 2), nullable=True)
    juros = Column(Numeric(15, 2), nullable=True)
    valor_liquido = Column(Numeric(15, 2), nullable=True)
    valor_pendente = Column(Numeric(15, 2), nullable=True)
    retencoes = Column(Numeric(15, 2), nullable=True)
    liquidacao = Column(Date, nullable=True, index=True)
    vl_cheque = Column(Numeric(15, 2), nullable=True)
    grupo_cliente = Column(String(50), nullable=True)
    numero_plaqueta = Column(String(50), nullable=True)
    ult_aprop_desp_fin = Column(String(100), nullable=True)
    data_transacao = Column(Date, nullable=True)
    cliente_matriz = Column(String(50), nullable=True)
    valor_original = Column(Numeric(15, 2), nullable=True)
    processo_exportacao = Column(String(50), nullable=True)
    soma_valor_original = Column(String(20), nullable=True)
    pedido_venda = Column(String(50), nullable=True)

    # Auditoria e vínculo com a tabela importacoes
    idImportacoes = Column(Integer, ForeignKey("importacoes.idImportacoes", ondelete="CASCADE"), nullable=True, index=True)
    data_criacao = Column(DateTime, nullable=False, default=func.now())
    usuario_inclusao = Column(String(100), nullable=True)

    # Relacionamento com importacoes
    importacao = relationship("Importacao")
