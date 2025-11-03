"""Shim module for sms_service.
Allows `from services.sms_service import ...` when original file is nested under services/services.
"""
from .services.sms_service import *  # noqa: F401,F403