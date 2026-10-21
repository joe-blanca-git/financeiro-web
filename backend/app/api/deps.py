from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/api/v1/auth/login"
)

# Únicas rotas liberadas para o nível Comercial - Vendas (caminho da rota, sem root_path)
ROTAS_NIVEL_COMERCIAL = (
    "/api/v1/auth/me",
    "/api/v1/comercial/minha-carteira",
)


def get_current_user(
    request: Request, db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar as credenciais",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.iduser == int(token_data.sub)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Trava central do nível Comercial - Vendas: só a carteira do próprio gerente
    from app.services.acesso_service import obter_role, ROLE_COMERCIAL
    if obter_role(db, user.iduser) == ROLE_COMERCIAL:
        rota = getattr(request.scope.get("route"), "path", "")
        if not any(rota == r or rota.startswith(r + "/") for r in ROTAS_NIVEL_COMERCIAL):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado para o seu nível de acesso.",
            )
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.active != 'S':
        raise HTTPException(
            status_code=400,
            detail="Usuário bloqueado"
        )
    return current_user

def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    query = text("""
        SELECT r.name 
        FROM roles r 
        JOIN userrole ur ON r.idRole = ur.idRole 
        WHERE ur.idUser = :user_id
    """)
    result = db.execute(query, {"user_id": current_user.iduser}).first()
    if not result or result[0] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado: Requer privilégios de administrador",
        )
    return current_user
