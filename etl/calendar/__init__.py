"""Infraestructura de calendario corporativo (master data)."""

from etl.calendar.calendar_seed import run_calendar_seed_from_env

__all__ = ["run_calendar_seed_from_env"]
