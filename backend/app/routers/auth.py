from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, ConviteSenha
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário no sistema.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="Já existe um usuário com esse email cadastrado.",
        )
    
    hashed_password = security.get_password_hash(user_in.password)
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        password=hashed_password,
        active='N'
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login_user(user_in: UserLogin, db: Session = Depends(get_db)):
    """
    Autentica um usuário e retorna um token JWT.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    if not security.verify_password(user_in.password, user.password):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    if user.active != 'S':
        raise HTTPException(status_code=400, detail="Usuário bloqueado pelo administrador")
    
    return _resposta_login(db, user)

@router.get("/me", response_model=UserResponse)
def get_user_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retorna os dados do usuário logado atualmente.
    """
    from app.services.acesso_service import obter_role
    role_name = obter_role(db, current_user.iduser)

    return {
        "name": current_user.name,
        "email": current_user.email,
        "iduser": current_user.iduser,
        "createdAt": current_user.createdAt,
        "role": role_name
    }


def _resposta_login(db: Session, user: User) -> dict:
    from app.services.acesso_service import obter_role
    access_token = security.create_access_token(
        subject=user.iduser, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "iduser": user.iduser,
        "name": user.name,
        "email": user.email,
        "createdAt": user.createdAt,
        "role": obter_role(db, user.iduser),
    }


@router.get("/convite/{token}")
def consultar_convite(token: str, db: Session = Depends(get_db)):
    """Primeiro acesso: confere se o link do convite é válido (existe e não expirou)."""
    from app.services.acesso_service import usuario_do_convite, REGRAS_SENHA
    user = usuario_do_convite(db, token)
    if not user:
        raise HTTPException(
            status_code=410,
            detail="Este link de primeiro acesso é inválido ou expirou. Solicite um novo convite ao departamento de T.I.",
        )
    return {"name": user.name, "email": user.email, "regrasSenha": REGRAS_SENHA}


@router.post("/convite", response_model=Token)
def concluir_primeiro_acesso(data: ConviteSenha, db: Session = Depends(get_db)):
    """Primeiro acesso: grava a senha escolhida, inutiliza o link e já devolve o login."""
    from app.services.acesso_service import usuario_do_convite, validar_senha, concluir_convite
    user = usuario_do_convite(db, data.token)
    if not user:
        raise HTTPException(
            status_code=410,
            detail="Este link de primeiro acesso é inválido ou expirou. Solicite um novo convite ao departamento de T.I.",
        )
    erro = validar_senha(data.senha)
    if erro:
        raise HTTPException(status_code=400, detail=erro)
    concluir_convite(db, user, data.senha)
    db.commit()
    db.refresh(user)
    return _resposta_login(db, user)
