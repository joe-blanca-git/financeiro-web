from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_admin_user
from app.core.database import get_db
from app.models.gerente import Gerente
from app.models.user import User
from app.schemas.comercial import GerentePaginatedResponse, RepresentantePaginatedResponse, VincularUsuarioRequest
from app.services import comercial_service
from app.services.carteira_service import dados_carteira, titulo_da_carteira, CarteiraInvalidaError
from app.services.inadimplencia_service import InadimplenciaService

router = APIRouter()


def _gerente_do_usuario(db: Session, user: User) -> Gerente:
    gerente = db.query(Gerente).filter(Gerente.idUser == user.iduser).first()
    if not gerente:
        raise HTTPException(status_code=404, detail="Seu usuário ainda não está vinculado a uma carteira. Procure o departamento de T.I.")
    return gerente


def _titulo_permitido(db: Session, user: User, id_nf: int) -> None:
    """O título precisa ser da carteira do gerente do usuário logado (senão, 404 - sem revelar se existe)."""
    if not titulo_da_carteira(db, _gerente_do_usuario(db, user), id_nf):
        raise HTTPException(status_code=404, detail="Título não encontrado na sua carteira.")


@router.get("/gerentes", response_model=GerentePaginatedResponse)
def listar_gerentes(page: int = 1, page_size: int = 10, search: Optional[str] = None, db: Session = Depends(get_db)):
    return comercial_service.listar_gerentes(db, page=page, page_size=page_size, search=search)


@router.get("/representantes", response_model=RepresentantePaginatedResponse)
def listar_representantes(page: int = 1, page_size: int = 10, search: Optional[str] = None, db: Session = Depends(get_db)):
    return comercial_service.listar_representantes(db, page=page, page_size=page_size, search=search)


@router.get("/gerentes/{id_gerente}/usuario")
def email_usuario_gerente(id_gerente: int, db: Session = Depends(get_db)):
    """E-mail do usuário vinculado ao gerente (pré-preenche o modal de compartilhar)."""
    return {"email": comercial_service.email_usuario_gerente(db, id_gerente)}


@router.put("/gerentes/{id_gerente}/usuario")
def vincular_usuario(
    id_gerente: int,
    data: VincularUsuarioRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    try:
        return comercial_service.vincular_usuario(db, id_gerente, data.email)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/gerentes/{id_gerente}/usuario")
def desvincular_usuario(
    id_gerente: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    try:
        comercial_service.desvincular_usuario(db, id_gerente)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"message": "Usuário desvinculado do gerente."}


@router.get("/minha-carteira")
def minha_carteira(
    id_representante: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Carteira do gerente vinculado ao usuário logado. O gerente vem do login (token), nunca
    de parâmetro; o filtro de representante só aceita representantes da equipe dele.
    """
    gerente = _gerente_do_usuario(db, current_user)
    try:
        return dados_carteira(db, gerente, id_representante)
    except CarteiraInvalidaError as e:
        raise HTTPException(status_code=403, detail=str(e))


# Detalhes do título (modais da grade), sempre conferindo que o título é da carteira do usuário
@router.get("/minha-carteira/titulos/{id_nf}/tratativas")
def tratativas_titulo(id_nf: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _titulo_permitido(db, current_user, id_nf)
    return InadimplenciaService(db).listar_tratativas(id_nf)


@router.get("/minha-carteira/titulos/{id_nf}/historico")
def historico_titulo(id_nf: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _titulo_permitido(db, current_user, id_nf)
    return InadimplenciaService(db).listar_historico(id_nf)


@router.get("/minha-carteira/titulos/{id_nf}/mensagens")
def mensagens_titulo(id_nf: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    _titulo_permitido(db, current_user, id_nf)
    # Só leitura do que está gravado (sem sincronizar com o Gmail de ninguém)
    return InadimplenciaService(db).listar_mensagens_thread(id_nf)
