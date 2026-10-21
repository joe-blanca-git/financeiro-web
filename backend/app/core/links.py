from app.core.config import settings

URL_PRODUCAO = "https://stamaria.cloud"


def url_frontend(caminho: str = "") -> str:
    """
    Endereço do frontend para links enviados por e-mail, conforme o ambiente:
      - produção: https://stamaria.cloud
      - teste (ROOT_PATH=/teste): https://stamaria.cloud/teste
      - desenvolvimento local: FRONTEND_URL (padrão http://localhost:4200)
    """
    if settings.ROOT_PATH:
        base = URL_PRODUCAO + settings.ROOT_PATH.rstrip("/")
    elif settings.ENVIRONMENT == "development":
        base = settings.FRONTEND_URL.rstrip("/")
    else:
        base = URL_PRODUCAO
    return base + "/" + caminho.lstrip("/")
