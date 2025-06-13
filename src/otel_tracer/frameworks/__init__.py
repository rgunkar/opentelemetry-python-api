"""
Framework-specific instrumentation modules.
"""

from . import flask
from . import django
from . import fastapi

__all__ = ["flask", "django", "fastapi"]