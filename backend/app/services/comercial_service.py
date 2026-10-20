import math
from typing import Optional

from sqlalchemy import func, or_, cast, String
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.gerente import Gerente
from app.models.representante import Representante
from app.models.user import User


def _paginar(query, page: int, page_size: int):
    total = query.count()
    linhas = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if page_size > 0 else 1
    return linhas, total, total_pages


def listar_gerentes(db: Session, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> dict:
    qtd_representantes = (
        db.query(Representante.idGerente, func.count(Representante.idRepresentante).label("qtd"))
        .group_by(Representante.idGerente)
        .subquery()
    )
    query = (
        db.query(Gerente, func.coalesce(qtd_representantes.c.qtd, 0).label("qtd"), User.email.label("usuario_email"))
        .outerjoin(qtd_representantes, qtd_representantes.c.idGerente == Gerente.idGerente)
        .outerjoin(User, User.iduser == Gerente.idUser)
    )
    if search:
        termo = f"%{search.strip()}%"
        query = query.filter(or_(Gerente.nome.ilike(termo), cast(Gerente.codigo, String).ilike(termo)))

    linhas, total, total_pages = _paginar(query.order_by(Gerente.nome.asc()), page, page_size)
    items = [
        {"idGerente": g.idGerente, "codigo": g.codigo, "nome": g.nome, "obs": g.obs, "qtdRepresentantes": qtd,
         "idUser": g.idUser, "usuarioEmail": usuario_email}
        for g, qtd, usuario_email in linhas
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "total_pages": total_pages}


def listar_representantes(db: Session, page: int = 1, page_size: int = 10, search: Optional[str] = None) -> dict:
    qtd_clientes = (
        db.query(Cliente.idRepresentante, func.count(Cliente.idclientes).label("qtd"))
        .group_by(Cliente.idRepresentante)
        .subquery()
    )
    query = (
        db.query(Representante, Gerente.nome.label("gerente_nome"), func.coalesce(qtd_clientes.c.qtd, 0).label("qtd"))
        .outerjoin(Gerente, Gerente.idGerente == Representante.idGerente)
        .outerjoin(qtd_clientes, qtd_clientes.c.idRepresentante == Representante.idRepresentante)
    )
    if search:
        termo = f"%{search.strip()}%"
        query = query.filter(or_(
            Representante.nome.ilike(termo),
            cast(Representante.codigo, String).ilike(termo),
            Gerente.nome.ilike(termo),
        ))

    linhas, total, total_pages = _paginar(query.order_by(Representante.nome.asc()), page, page_size)
    items = [
        {
            "idRepresentante": r.idRepresentante,
            "codigo": r.codigo,
            "nome": r.nome,
            "obs": r.obs,
            "idGerente": r.idGerente,
            "gerenteNome": gerente_nome,
            "qtdClientes": qtd,
        }
        for r, gerente_nome, qtd in linhas
    ]
    return {"items": items, "page": page, "page_size": page_size, "total": total, "total_pages": total_pages}


def vincular_usuario(db: Session, id_gerente: int, email: str) -> dict:
    """Liga o usuário (pelo e-mail) ao gerente. Um usuário só pode ser de um gerente."""
    from app.services.acesso_service import obter_role, ROLE_COMERCIAL

    gerente = db.query(Gerente).filter(Gerente.idGerente == id_gerente).first()
    if not gerente:
        raise LookupError("Gerente não encontrado.")
    user = db.query(User).filter(func.lower(User.email) == (email or "").strip().lower()).first()
    if not user:
        raise ValueError("Nenhum usuário cadastrado com esse e-mail. Cadastre o usuário em Acesso antes de vincular.")
    outro = db.query(Gerente).filter(Gerente.idUser == user.iduser, Gerente.idGerente != id_gerente).first()
    if outro:
        raise ValueError(f"Este usuário já está vinculado ao gerente {outro.nome}.")

    gerente.idUser = user.iduser
    db.commit()
    aviso = None
    if obter_role(db, user.iduser) != ROLE_COMERCIAL:
        aviso = (f"O usuário {user.name} não está no nível \"Comercial - Vendas\". Ajuste o nível em Acesso "
                 "para ele entrar direto na carteira e ver só os dados dele.")
    return {"idUser": user.iduser, "usuarioEmail": user.email, "aviso": aviso}


def desvincular_usuario(db: Session, id_gerente: int) -> None:
    gerente = db.query(Gerente).filter(Gerente.idGerente == id_gerente).first()
    if not gerente:
        raise LookupError("Gerente não encontrado.")
    gerente.idUser = None
    db.commit()


def email_usuario_gerente(db: Session, id_gerente: int) -> Optional[str]:
    return (
        db.query(User.email)
        .join(Gerente, Gerente.idUser == User.iduser)
        .filter(Gerente.idGerente == id_gerente)
        .scalar()
    )
