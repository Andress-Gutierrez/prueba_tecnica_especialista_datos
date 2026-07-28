"""
Entrada operativa para poblar calendario corporativo en dim_tiempo.

Uso:
  python -m scripts.run_calendar_seed
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

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
    _load_dotenv(_ROOT / ".env")
    from etl.calendar import run_calendar_seed_from_env

    try:
        run_calendar_seed_from_env()
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
