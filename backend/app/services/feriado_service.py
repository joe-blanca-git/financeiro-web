import datetime
import logging

import httpx
from sqlalchemy import extract, text
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.feriado import Feriado

logger = logging.getLogger("santamaria")

BRASILAPI_FERIADOS_URL = "https://brasilapi.com.br/api/feriados/v1/{ano}"


def sincronizar_feriados_nacionais(hoje: datetime.date) -> None:
    """
    Garante que a tabela `feriados` tenha os feriados nacionais do ano anterior, do atual e do
    próximo, buscando na BrasilAPI apenas os anos que ainda não estão gravados.

    Nunca interrompe quem chama: se a API falhar, registra um aviso e o sistema segue usando
    os feriados já gravados (na pior das hipóteses, só sábado e domingo são pulados).
    Usa uma sessão própria para não misturar o commit com a transação de quem chamou.
    """
    db = SessionLocal()
    try:
        for ano in (hoje.year - 1, hoje.year, hoje.year + 1):
            ja_carregado = db.query(Feriado).filter(extract("year", Feriado.data) == ano).first()
            if ja_carregado:
                continue
            try:
                with httpx.Client(timeout=10.0) as client:
                    resposta = client.get(BRASILAPI_FERIADOS_URL.format(ano=ano))
                    resposta.raise_for_status()
                    itens = resposta.json()
            except (httpx.HTTPError, ValueError) as e:
                logger.warning("Não foi possível baixar os feriados de %s na BrasilAPI: %s", ano, e)
                continue

            for item in itens:
                db.merge(Feriado(
                    data=datetime.date.fromisoformat(item["date"]),
                    descricao=(item.get("name") or "")[:100],
                ))
            db.commit()
            logger.info("Feriados nacionais de %s carregados da BrasilAPI (%s datas).", ano, len(itens))
    except Exception as e:
        db.rollback()
        logger.warning("Falha ao sincronizar feriados nacionais: %s", e)
    finally:
        db.close()


def data_corte_vencimento(db: Session, data_ref: datetime.date) -> datetime.date:
    """
    Último dia útil antes de `data_ref` (pula sábado, domingo e feriados da tabela `feriados`).
    Título com vencimento até essa data está vencido. A conta é feita pela função do banco
    `fn_data_corte_vencimento` - a mesma usada pela view vw_nfpendencias_fase - para que a
    regra exista em um lugar só.
    """
    return db.execute(
        text("SELECT fn_data_corte_vencimento(:data_ref)"), {"data_ref": data_ref}
    ).scalar()
