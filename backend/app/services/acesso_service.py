"""
Níveis de acesso, convite de primeiro acesso e política de senha.

Níveis (tabela roles): 'admin' (Administrador), 'comercial_vendas' (Comercial - Vendas) e
qualquer outro valor/ausência = Padrão. O nível Comercial - Vendas só acessa a carteira do
gerente vinculado ao usuário (gerente.idUser) - a trava fica em deps.get_current_user.
"""
import datetime
import hashlib
import html
import re
import secrets
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core import security
from app.core.links import url_frontend
from app.models.user import User

ROLE_ADMIN = "admin"
ROLE_COMERCIAL = "comercial_vendas"
ROLE_PADRAO = "user"
ROLES_VALIDOS = (ROLE_ADMIN, ROLE_COMERCIAL, ROLE_PADRAO)

VALIDADE_CONVITE = datetime.timedelta(hours=8)


# ------------------------------------------------------------------ níveis de acesso
def obter_role(db: Session, id_user: int) -> str:
    nome = db.execute(
        text("SELECT r.name FROM roles r JOIN userrole ur ON r.idRole = ur.idRole WHERE ur.idUser = :id"),
        {"id": id_user},
    ).scalar()
    return nome if nome in (ROLE_ADMIN, ROLE_COMERCIAL) else ROLE_PADRAO


def definir_role(db: Session, id_user: int, role: str) -> None:
    """Grava o nível do usuário (sem commit). Padrão = sem linha em userrole."""
    if role not in ROLES_VALIDOS:
        raise ValueError("Nível de acesso inválido.")
    db.execute(text("DELETE FROM userrole WHERE idUser = :id"), {"id": id_user})
    if role == ROLE_PADRAO:
        return
    id_role = db.execute(text("SELECT idRole FROM roles WHERE name = :n"), {"n": role}).scalar()
    if not id_role:
        raise ValueError(f"Nível '{role}' não cadastrado no banco (rode o script de níveis de acesso).")
    db.execute(text("INSERT INTO userrole (idUser, idRole) VALUES (:u, :r)"), {"u": id_user, "r": id_role})


# ------------------------------------------------------------------ senha
REGRAS_SENHA = "A senha deve ter pelo menos 8 caracteres, um número, uma letra maiúscula e um caractere especial."


def validar_senha(senha: str) -> Optional[str]:
    """Retorna a mensagem de erro, ou None se a senha atende à política."""
    if (
        len(senha or "") < 8
        or not re.search(r"\d", senha)
        or not re.search(r"[A-Z]", senha)
        or not re.search(r"[^A-Za-z0-9]", senha)
    ):
        return REGRAS_SENHA
    return None


def senha_aleatoria() -> str:
    """Senha inicial que ninguém conhece: o acesso só é possível pelo link do convite."""
    return secrets.token_urlsafe(32)


# ------------------------------------------------------------------ convite
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def gerar_convite(user: User) -> str:
    """Gera um token novo (invalida o anterior) válido por 8 horas. Grava só o hash (sem commit)."""
    token = secrets.token_urlsafe(32)
    user.convite_token_hash = _hash_token(token)
    user.convite_expira_em = datetime.datetime.now() + VALIDADE_CONVITE
    return token


def usuario_do_convite(db: Session, token: str) -> Optional[User]:
    """Usuário do convite, se o token existe e não expirou."""
    if not token:
        return None
    user = db.query(User).filter(User.convite_token_hash == _hash_token(token)).first()
    if not user or not user.convite_expira_em or user.convite_expira_em < datetime.datetime.now():
        return None
    return user


def concluir_convite(db: Session, user: User, senha: str) -> None:
    """Grava a senha escolhida e inutiliza o link (uso único). Sem commit."""
    user.password = security.get_password_hash(senha)
    user.convite_token_hash = None
    user.convite_expira_em = None
    user.active = "S"


def html_convite(nome: str, link: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;font-family:Arial,Helvetica,sans-serif;">
  <tr><td style="padding:22px 24px;background:#0f172a;border-radius:12px 12px 0 0;">
    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;">STAR · Sistemas Integrados Santa Maria</div>
    <div style="font-size:20px;font-weight:bold;color:#ffffff;margin-top:6px;">Bem-vindo(a) ao STAR</div>
  </td></tr>
  <tr><td style="padding:24px;">
    <p style="margin:0 0 16px;font-size:14px;color:#334155;">Olá, {html.escape(nome)}!</p>
    <p style="margin:0 0 20px;font-size:14px;color:#334155;">
      Bem-vindo(a) ao <b>STAR - Sistemas Integrados Santa Maria</b>. Clique no botão abaixo para fazer o seu
      primeiro acesso ao portal e criar a sua senha.</p>
    <p style="margin:0 0 24px;">
      <a href="{html.escape(link)}" style="display:inline-block;padding:12px 24px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;font-weight:bold;font-size:14px;">
        Fazer meu primeiro acesso</a></p>
    <p style="margin:0 0 8px;font-size:13px;color:#475569;">
      O link é válido por <b>8 horas</b> a partir do envio desta mensagem. Caso o link tenha expirado,
      solicite um novo convite ao departamento de T.I.</p>
    <p style="margin:16px 0 0;padding-top:12px;border-top:1px solid #e2e8f0;font-size:11px;color:#94a3b8;">
      Se o botão não funcionar, copie e cole este endereço no navegador:<br>{html.escape(link)}<br><br>
      Mensagem automática do STAR. Por favor, não responda.</p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


def enviar_convite(db: Session, user: User, admin: User) -> None:
    """Gera um token novo e envia o convite pela conta Google do administrador.
    Faz commit do token antes de enviar: se o envio falhar, o admin usa "Reenviar convite"."""
    from app.services.google_auth_service import GoogleAuthService
    from app.services.gmail_service import GmailService

    access_token = GoogleAuthService.obter_access_token_valido(admin, db)
    token = gerar_convite(user)
    db.commit()
    link = url_frontend(f"primeiro-acesso?token={token}")
    GmailService.enviar_email(
        access_token=access_token,
        destinatarios=user.email,
        assunto="Bem-vindo(a) ao STAR - Sistemas Integrados Santa Maria",
        corpo_html=html_convite(user.name, link),
        copia=None,
        anexos=[],
        remetente_email=admin.email,
    )
