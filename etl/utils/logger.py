"""
Logger operacional único del ETL (Subfase 4.6.1).

Configura un logger reutilizable con salida a consola y a un archivo por
ejecución ``logs/etl_YYYYMMDD_HHMMSS.log``, más ``logs/latest.log``.
No altera la lógica de negocio ni los resultados del pipeline.
"""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path

from etl.utils.paths import get_project_root

LOGGER_NAME = "etl"
_CONFIGURED = False
_CURRENT_LOG_FILE: Path | None = None


def configure_logging(
    *,
    log_dir: Path | None = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configura una sola vez el logger del proyecto por proceso/ejecución.

    Handlers:
    - StreamHandler (consola)
    - FileHandler ``logs/etl_YYYYMMDD_HHMMSS.log`` (archivo de la ejecución)
    - FileHandler ``logs/latest.log`` (última ejecución; modo escritura)

    Niveles operativos: INFO / WARNING / ERROR (sin DEBUG).
    """
    global _CONFIGURED, _CURRENT_LOG_FILE
    logger = logging.getLogger(LOGGER_NAME)
    if _CONFIGURED:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logs_path = log_dir if log_dir is not None else get_project_root() / "logs"
    logs_path.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_log = logs_path / f"etl_{stamp}.log"
    latest_log = logs_path / "latest.log"
    _CURRENT_LOG_FILE = run_log

    run_handler = logging.FileHandler(run_log, encoding="utf-8")
    run_handler.setLevel(level)
    run_handler.setFormatter(formatter)

    # Recrea latest.log en cada ejecución (sin enlaces simbólicos).
    latest_handler = logging.FileHandler(latest_log, mode="w", encoding="utf-8")
    latest_handler.setLevel(level)
    latest_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    logger.addHandler(run_handler)
    logger.addHandler(latest_handler)
    logger.addHandler(console_handler)

    _CONFIGURED = True
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Devuelve el logger del proyecto (configurado si aún no lo está).

    Parameters
    ----------
    name:
        Sufijo opcional (p. ej. ``pipeline`` → ``etl.pipeline``).
    """
    configure_logging()
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)


def get_current_log_file() -> Path | None:
    """Ruta del archivo ``etl_YYYYMMDD_HHMMSS.log`` de la ejecución actual."""
    return _CURRENT_LOG_FILE
