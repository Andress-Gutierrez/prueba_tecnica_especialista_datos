"""
Cliente HTTP para API oficial de festivos.com.co.

No calcula festivos localmente. Toda la informacion de festivos proviene de la API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class FestivosApiError(RuntimeError):
    """Error generico de consumo de API de festivos."""


class FestivosApiAuthError(FestivosApiError):
    """Error de autenticacion/autorizacion de la API."""


@dataclass(frozen=True)
class FestivoItem:
    """Representa un festivo devuelto por la API."""

    fecha: date
    nombre_festivo: str


def fetch_festivos_by_year(
    *,
    base_url: str,
    api_key: str,
    year: int,
    timeout_seconds: int = 30,
) -> list[FestivoItem]:
    """
    Consulta todos los festivos de un anio.

    Endpoint documentado: GET /api/v1/festivos?year=YYYY.
    """
    clean_base = base_url.rstrip("/")
    endpoint = f"{clean_base}/api/v1/festivos?{urlencode({'year': year})}"
    request = Request(
        endpoint,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "prueba-tecnica-especialista-datos/1.0 (+calendar_seed)",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = "<sin cuerpo>"
        if exc.code in {401, 403}:
            raise FestivosApiAuthError(
                f"Error de autenticacion API festivos (HTTP {exc.code}): {body}"
            ) from exc
        raise FestivosApiError(
            f"Error HTTP API festivos (HTTP {exc.code}): {body}"
        ) from exc
    except URLError as exc:
        raise FestivosApiError(f"Error de red API festivos: {exc}") from exc

    data = payload.get("data", [])
    items: list[FestivoItem] = []
    for row in data:
        date_text = row.get("date")
        name_es = row.get("name_es")
        if not date_text or not name_es:
            continue
        items.append(
            FestivoItem(
                fecha=date.fromisoformat(str(date_text)),
                nombre_festivo=str(name_es).strip(),
            )
        )
    return items
