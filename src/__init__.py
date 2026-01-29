# src/__init__.py
"""
MindWorx SOR Automation System
Automated Statement of Results generation for Pluto LMS
"""

__version__ = '1.0.0'
__author__ = 'MindWorx Academy'

# Make modules easily importable
from .config import config
from .database import db
from .validation import validator

__all__ = ['config', 'db', 'validator']


# tests/__init__.py
"""
Test package for MindWorx SOR Automation System
"""