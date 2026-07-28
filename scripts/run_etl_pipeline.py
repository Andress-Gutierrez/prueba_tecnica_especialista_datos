"""
Entrada operativa del pipeline ETL + validación DW (Subfase 4.6 / 4.6.1).

Uso (desde la raíz del proyecto):
  python -m scripts.run_etl_pipeline
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Asegura import del paquete del proyecto.
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    """Ejecuta pipeline integrado y validación final con logging operacional."""
    _load_dotenv(_ROOT / ".env")
    from etl.utils.logger import get_logger
    from repository.postgres import PostgresSettings
    from etl.pipeline import run_etl_pipeline
    from etl.validation import validate_data_warehouse

    logger = get_logger("run")
    settings = PostgresSettings.from_env()

    try:
        result = run_etl_pipeline(
            settings,
            max_rows=None,
        )
        # Validación explícita adicional (post-pipeline).
        report = validate_data_warehouse(settings)
        for check in report.checks:
            mark = "OK" if check.ok else "ERROR"
            detail = f" — {check.detail}" if check.detail else ""
            level = logger.info if check.ok else logger.error
            level("[%s] %s%s", mark, check.name, detail)
        logger.info("%s", report.summary().replace("\n", " | "))
        return 0 if result.validation.ok and report.ok else 1
    except Exception:
        logger.exception("Fallo operativo en run_etl_pipeline")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
