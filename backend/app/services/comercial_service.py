import math
from typing import Optional

from sqlalchemy import func, or_, cast, String
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.gerente import Gerente
from app.models.representante import Representante


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
        db.query(Gerente, func.coalesce(qtd_representantes.c.qtd, 0).label("qtd"))
        .outerjoin(qtd_representantes, qtd_representantes.c.idGerente == Gerente.idGerente)
    )
    if search:
        termo = f"%{search.strip()}%"
        query = query.filter(or_(Gerente.nome.ilike(termo), cast(Gerente.codigo, String).ilike(termo)))

    linhas, total, total_pages = _paginar(query.order_by(Gerente.nome.asc()), page, page_size)
    items = [
        {"idGerente": g.idGerente, "codigo": g.codigo, "nome": g.nome, "obs": g.obs, "qtdRepresentantes": qtd}
        for g, qtd in linhas
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
