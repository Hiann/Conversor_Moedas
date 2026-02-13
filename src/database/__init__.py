"""Módulo de persistência com SQLAlchemy."""

from .db import Database, get_db
from .models import ConversaoDB, ConversaoMultiplaDB
from .repository import ConversaoRepository

__all__ = ["Database", "get_db", "ConversaoDB", "ConversaoMultiplaDB", "ConversaoRepository"]
