from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class PrevisaoApbItemSchema(BaseModel):
    id: Optional[int] = None
    arquivo: Optional[str] = None
    data: Optional[date] = None
    cod_tp_fluxo: Optional[str] = None
    ent_sai: Optional[str] = None
    prev_real: Optional[str] = None
    modulo: Optional[str] = None
    vlr_cam_2: Optional[float] = None
    trans: Optional[str] = None
    emp: Optional[str] = None
    estab: Optional[str] = None
    esp: Optional[str] = None
    serie: Optional[str] = None
    n_titulo: Optional[str] = None
    parcela: Optional[str] = None
    numero_fornecedor: Optional[str] = None
    nome_abrev: Optional[str] = None
    valor_fluxo: Optional[float] = None
    valor: Optional[float] = None
    nome_emitente: Optional[str] = None
    idImportacoes: Optional[int] = None
    data_criacao: Optional[datetime] = None
    usuario_inclusao: Optional[str] = None

    class Config:
        from_attributes = True

class ImportacaoApbResponse(BaseModel):
    sucesso: bool
    mensagem: str
    idImportacoes: int
    nomeArquivo: str
    totalRegistros: int
    totalValor: float

class PrevisaoAcrItemSchema(BaseModel):
    id: Optional[int] = None
    est: Optional[str] = None
    esp: Optional[str] = None
    ser: Optional[str] = None
    titulo: Optional[str] = None
    parcela: Optional[str] = None
    un_neg: Optional[str] = None
    nr_pedcli: Optional[str] = None
    tipo_pedido: Optional[str] = None
    cliente: Optional[str] = None
    nome_abrev: Optional[str] = None
    nome_cliente: Optional[str] = None
    grp_cliente: Optional[str] = None
    cliente_matriz: Optional[str] = None
    port: Optional[str] = None
    cart: Optional[str] = None
    repres: Optional[str] = None
    emissao: Optional[date] = None
    dt_entrega: Optional[date] = None
    vencto: Optional[date] = None
    dt_agdnto: Optional[date] = None
    liquidac: Optional[date] = None
    refer: Optional[str] = None
    tit_banco: Optional[str] = None
    moeda: Optional[str] = None
    val_original: Optional[float] = None
    saldo: Optional[float] = None
    saldo_apresentacao: Optional[float] = None
    cond_pagto: Optional[str] = None
    vl_descto: Optional[float] = None
    vl_abat: Optional[float] = None
    dias: Optional[int] = None
    pedido_venda: Optional[str] = None
    data_indic: Optional[date] = None
    cond_cobr: Optional[str] = None
    cidade: Optional[str] = None
    telefone: Optional[str] = None
    cidade_cobranca_cliente: Optional[str] = None
    id_federal: Optional[str] = None
    unid_federac: Optional[str] = None
    idImportacoes: Optional[int] = None
    data_criacao: Optional[datetime] = None
    usuario_inclusao: Optional[str] = None

    class Config:
        from_attributes = True

class ImportacaoAcrResponse(BaseModel):
    sucesso: bool
    mensagem: str
    idImportacoes: int
    nomeArquivo: str
    totalRegistros: int
    totalValor: float

class ImportacaoTitulosLiquidadosResponse(BaseModel):
    sucesso: bool
    mensagem: str
    idImportacoes: int
    nomeArquivo: str
    totalRegistros: int
    totalValor: float
