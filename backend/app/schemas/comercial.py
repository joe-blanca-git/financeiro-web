from pydantic import BaseModel
from typing import List, Optional


class GerenteResponse(BaseModel):
    idGerente: int
    codigo: int
    nome: str
    obs: Optional[str] = None
    qtdRepresentantes: int = 0
    idUser: Optional[int] = None
    usuarioEmail: Optional[str] = None


class GerentePaginatedResponse(BaseModel):
    items: List[GerenteResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class RepresentanteResponse(BaseModel):
    idRepresentante: int
    codigo: int
    nome: str
    obs: Optional[str] = None
    idGerente: Optional[int] = None
    gerenteNome: Optional[str] = None
    qtdClientes: int = 0


class RepresentantePaginatedResponse(BaseModel):
    items: List[RepresentanteResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class VincularUsuarioRequest(BaseModel):
    email: str
