from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class PrevisaoAcr(Base):
    __tablename__ = "previsao_acr"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    est = Column(String(20), nullable=True)
    esp = Column(String(20), nullable=True)
    ser = Column(String(20), nullable=True)
    titulo = Column(String(50), nullable=True, index=True)
    parcela = Column(String(20), nullable=True)
    un_neg = Column(String(50), nullable=True)
    nr_pedcli = Column(String(50), nullable=True)
    tipo_pedido = Column(String(20), nullable=True)
    cliente = Column(String(50), nullable=True, index=True)
    nome_abrev = Column(String(100), nullable=True)
    nome_cliente = Column(String(255), nullable=True)
    grp_cliente = Column(String(50), nullable=True)
    cliente_matriz = Column(String(50), nullable=True)
    port = Column(String(50), nullable=True)
    cart = Column(String(50), nullable=True, index=True)
    repres = Column(String(50), nullable=True)
    emissao = Column(Date, nullable=True)
    dt_entrega = Column(Date, nullable=True)
    vencto = Column(Date, nullable=True, index=True)
    dt_agdnto = Column(Date, nullable=True)
    liquidac = Column(Date, nullable=True)
    refer = Column(String(100), nullable=True)
    tit_banco = Column(String(50), nullable=True)
    moeda = Column(String(20), nullable=True)
    val_original = Column(Numeric(15, 2), nullable=True)
    saldo = Column(Numeric(15, 2), nullable=True)
    saldo_apresentacao = Column(Numeric(15, 2), nullable=True)
    cond_pagto = Column(String(50), nullable=True)
    vl_descto = Column(Numeric(15, 2), nullable=True)
    vl_abat = Column(Numeric(15, 2), nullable=True)
    dias = Column(Integer, nullable=True)
    pedido_venda = Column(String(50), nullable=True)
    data_indic = Column(Date, nullable=True)
    cond_cobr = Column(String(50), nullable=True)
    cidade = Column(String(100), nullable=True)
    telefone = Column(String(50), nullable=True)
    cidade_cobranca_cliente = Column(String(100), nullable=True)
    id_federal = Column(String(50), nullable=True)
    unid_federac = Column(String(10), nullable=True)

    # Colunas de auditoria e controle de importação
    idImportacoes = Column(Integer, ForeignKey("importacoes.idImportacoes", ondelete="CASCADE"), nullable=True, index=True)
    data_criacao = Column(DateTime, nullable=False, default=func.now())
    usuario_inclusao = Column(String(100), nullable=True)

    # Relacionamento com a tabela de importacoes
    importacao = relationship("Importacao")
