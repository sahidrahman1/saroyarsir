"""Service layer package.
Exports database, sms_service, and AI related helpers.
Handles legacy path where modules were nested under services/services.
"""
import importlib
import sys
from pathlib import Path

_base = Path(__file__).parent
_nested = _base / 'services'

if _nested.is_dir() and str(_nested) not in sys.path:
    sys.path.insert(0, str(_nested))

def _safe_import(name):
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None

database = _safe_import('database') or _safe_import('services.database')
sms_service = _safe_import('sms_service') or _safe_import('services.sms_service')
praggo_ai = _safe_import('praggo_ai') or _safe_import('services.praggo_ai')

__all__ = ['database', 'sms_service', 'praggo_ai']