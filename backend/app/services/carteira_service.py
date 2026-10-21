"""
Carteira do gerente (títulos em atraso por gerente/representante).

- dados_carteira: dados da página "Minha carteira" do usuário Comercial - Vendas (só a
  carteira do gerente vinculado ao usuário logado).
- titulo_da_carteira: garante que um título é da carteira do gerente (rotas de detalhe).
- html_email_compartilhar: e-mail de aviso com a mensagem padrão e o link para a página
  (os dados só aparecem para quem fizer login como o gerente).
"""
import datetime
import html
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.cliente import Cliente
from app.models.gerente import Gerente
from app.models.nf_pendencia import VwNfPendenciaFase
from app.models.representante import Representante

ASSINATURA_URL = (
    "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjFFw0P_XxmH9v5vpY_xD7PMIP1q2rv_5mwb3CaGqd5rnz3ie-"
    "wGL7D8PieowH1fAoQt9AhuT2ehoXRV8AAErbImaEhVWn_qKwytXXoEd5QUK4Ms_fSEOZ7cJTJXmr90qTmNbbj8AcZ7-oBBwH0OXObMEr6wg6"
    "UXfzxgf2ibk8vh6fRGNLl7RRsxA_Jm9k/s1600/Composi%C3%A7%C3%A3o-1-TANIA.gif"
)

class CarteiraInvalidaError(ValueError):
    pass


def dados_carteira(db: Session, gerente: Gerente, id_representante: Optional[int] = None) -> dict:
    """
    Títulos em atraso da carteira do gerente (opcionalmente de um representante dele), com os
    mesmos campos da grade do painel. O representante precisa ser da equipe do gerente.
    Mesmo critério de "vencido" do painel: fase FINANCEIRO com vencimento anterior a hoje.
    """
    hoje = datetime.date.today()

    representante = None
    if id_representante:
        representante = db.query(Representante).filter(Representante.idRepresentante == id_representante).first()
        if not representante or representante.idGerente != gerente.idGerente:
            raise CarteiraInvalidaError("Representante não pertence à sua equipe.")

    filtro = [Representante.idGerente == gerente.idGerente, VwNfPendenciaFase.dtVencimento < hoje]
    if representante:
        filtro.append(Representante.idRepresentante == representante.idRepresentante)

    def base(*colunas):
        return (
            db.query(*colunas)
            .select_from(VwNfPendenciaFase)
            .join(Cliente, Cliente.idclientes == VwNfPendenciaFase.idCliente)
            .join(Representante, Representante.idRepresentante == Cliente.idRepresentante)
            .filter(*filtro)
        )

    titulos = (
        base(
            VwNfPendenciaFase.idnfpendencias,
            VwNfPendenciaFase.titulo,
            VwNfPendenciaFase.dtVencimento,
            VwNfPendenciaFase.valorSaldo,
            VwNfPendenciaFase.status,
            VwNfPendenciaFase.fase,
            Cliente.nome.label("cliente"),
            Representante.idRepresentante,
            Representante.nome.label("representante"),
        )
        .filter(VwNfPendenciaFase.fase == "FINANCEIRO")
        .order_by(VwNfPendenciaFase.dtVencimento.asc(), VwNfPendenciaFase.titulo.asc())
        .all()
    )
    total_protestado = (
        base(func.sum(VwNfPendenciaFase.valorSaldo)).filter(VwNfPendenciaFase.status == "PROTESTADO").scalar() or 0
    )
    # Mesmo "Qtd Títulos" da grade do painel: títulos em atraso do cliente na carteira
    qtd_por_cliente = {}
    for t in titulos:
        qtd_por_cliente[t.cliente] = qtd_por_cliente.get(t.cliente, 0) + 1

    # Filtro de representantes: só os da equipe do gerente que têm títulos em atraso
    representantes = (
        db.query(Representante.idRepresentante, Representante.nome)
        .join(Cliente, Cliente.idRepresentante == Representante.idRepresentante)
        .join(VwNfPendenciaFase, VwNfPendenciaFase.idCliente == Cliente.idclientes)
        .filter(
            Representante.idGerente == gerente.idGerente,
            VwNfPendenciaFase.fase == "FINANCEIRO",
            VwNfPendenciaFase.dtVencimento < hoje,
        )
        .distinct()
        .order_by(Representante.nome.asc())
        .all()
    )

    return {
        "gerente": {"idGerente": gerente.idGerente, "nome": gerente.nome},
        "representantes": [{"idRepresentante": r.idRepresentante, "nome": r.nome} for r in representantes],
        "idRepresentante": representante.idRepresentante if representante else None,
        "dataPosicao": hoje.isoformat(),
        "totalVencido": float(sum(float(t.valorSaldo or 0) for t in titulos)),
        "totalProtestado": float(total_protestado),
        "qtdTitulos": len(titulos),
        "titulos": [
            {
                "id": t.idnfpendencias,
                "titulo": t.titulo,
                "cliente": t.cliente,
                "representante": t.representante,
                "vencimento": t.dtVencimento.isoformat() if t.dtVencimento else None,
                "diasAtraso": (hoje - t.dtVencimento).days if t.dtVencimento else None,
                "status": t.status,
                "fase": t.fase,
                "qtd": qtd_por_cliente.get(t.cliente, 1),
                "valor": float(t.valorSaldo or 0),
            }
            for t in titulos
        ],
    }


def titulo_da_carteira(db: Session, gerente: Gerente, id_nf: int) -> bool:
    """True se o título é de um cliente de algum representante da equipe do gerente."""
    return (
        db.query(VwNfPendenciaFase.idnfpendencias)
        .join(Cliente, Cliente.idclientes == VwNfPendenciaFase.idCliente)
        .join(Representante, Representante.idRepresentante == Cliente.idRepresentante)
        .filter(VwNfPendenciaFase.idnfpendencias == id_nf, Representante.idGerente == gerente.idGerente)
        .first()
        is not None
    )


def html_email_compartilhar(gerente_nome: str, link: str, mensagem_personalizada: Optional[str] = None) -> str:
    """Aviso com a mensagem padrão e o link para a página da carteira (sem dados no e-mail)."""
    extra = ""
    if mensagem_personalizada and mensagem_personalizada.strip():
        extra = (
            '<p style="margin:0 0 16px;font-size:14px;color:#334155;">'
            f"{html.escape(mensagem_personalizada.strip()).replace(chr(10), '<br>')}</p>"
        )
    return f"""<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f1f5f9;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f1f5f9;">
<tr><td align="center" style="padding:24px 12px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;background:#ffffff;border-radius:12px;font-family:Arial,Helvetica,sans-serif;">
  <tr><td style="padding:22px 24px;background:#0f172a;border-radius:12px 12px 0 0;">
    <div style="font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;">STAR · Inadimplência</div>
    <div style="font-size:20px;font-weight:bold;color:#ffffff;margin-top:6px;">Títulos em atraso da sua carteira</div>
    <div style="font-size:13px;color:#cbd5e1;margin-top:6px;">Gerente: <b style="color:#ffffff;">{html.escape(gerente_nome)}</b></div>
  </td></tr>
  <tr><td style="padding:24px;">
    {extra}
    <p style="margin:0 0 20px;font-size:14px;color:#334155;">Prezado(a),<br><br>
      A posição atualizada dos títulos em atraso da sua carteira, com as tratativas e as mensagens trocadas
      com cada cliente, está disponível no portal STAR. Acesse com o seu usuário e senha.</p>
    <p style="margin:0 0 24px;">
      <a href="{html.escape(link)}" style="display:inline-block;padding:12px 24px;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;font-weight:bold;font-size:14px;">
        Acessar minha carteira</a></p>
    <p style="margin:0 0 14px;font-size:14px;color:#334155;">Fico à disposição para quaisquer esclarecimentos ou informações adicionais que se façam necessárias.</p>
    <p style="margin:0;padding-top:12px;border-top:1px solid #e2e8f0;font-size:11px;color:#94a3b8;">
      Os dados só são exibidos após o login. Mensagem gerada automaticamente pelo STAR; por favor, não responda.</p>
    <div style="margin-top:18px;"><img src="{ASSINATURA_URL}" alt="Assinatura Santa Maria" style="max-width:400px;width:100%;"></div>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""
