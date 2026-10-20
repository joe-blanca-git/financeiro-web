from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# Propriedades compartilhadas
class UserBase(BaseModel):
    name: str
    email: EmailStr

# Usado para criar usuário via API
class UserCreate(UserBase):
    password: str

# Usado para fazer login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Retornado pela API
class UserResponse(UserBase):
    iduser: int
    active: Optional[str] = 'S'
    createdAt: Optional[datetime] = None
    role: Optional[str] = 'user'
    convitePendente: bool = False

    class Config:
        from_attributes = True

# Token response
class Token(BaseModel):
    access_token: str
    expires_in: int
    name: str
    email: EmailStr
    createdAt: Optional[datetime] = None
    role: Optional[str] = 'user'

class TokenPayload(BaseModel):
    sub: Optional[str] = None

# Operações Administrativas
class UserPasswordUpdate(BaseModel):
    novaSenha: str

class UserStatusUpdate(BaseModel):
    bloqueado: bool

class UserAdminUpdate(BaseModel):
    admin: bool

# Cadastro por convite (admin): só nome, e-mail e nível de acesso
class UserConviteCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = 'user'

class UserRoleUpdate(BaseModel):
    role: str

# Primeiro acesso pelo link do convite
class ConviteSenha(BaseModel):
    token: str
    senha: str
