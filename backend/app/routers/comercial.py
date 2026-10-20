from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.comercial import GerentePaginatedResponse, RepresentantePaginatedResponse
from app.services import comercial_service

router = APIRouter()


@router.get("/gerentes", response_model=GerentePaginatedResponse)
def listar_gerentes(page: int = 1, page_size: int = 10, search: Optional[str] = None, db: Session = Depends(get_db)):
    return comercial_service.listar_gerentes(db, page=page, page_size=page_size, search=search)


@router.get("/representantes", response_model=RepresentantePaginatedResponse)
def listar_representantes(page: int = 1, page_size: int = 10, search: Optional[str] = None, db: Session = Depends(get_db)):
    return comercial_service.listar_representantes(db, page=page, page_size=page_size, search=search)
