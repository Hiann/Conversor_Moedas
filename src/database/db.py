"""Configuração do banco de dados SQLAlchemy."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.engine import Engine

# Cria diretório de dados se não existir
Path("data").mkdir(exist_ok=True)

Base = declarative_base()


class Database:
    """Gerenciador de conexão com banco de dados."""
    
    _instance = None
    
    def __new__(cls, database_url: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, database_url: str = None):
        if self._initialized:
            return
            
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "sqlite:///data/conversor.db"
        )
        
        self.engine = create_engine(
            self.database_url,
            echo=False,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Configura SQLite
        if "sqlite" in self.database_url:
            self._configurar_sqlite()
        
        self._initialized = True
    
    def _configurar_sqlite(self):
        """Configurações específicas para SQLite."""
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    def criar_tabelas(self):
        """Cria todas as tabelas."""
        from .models import ConversaoDB, ConversaoMultiplaDB
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Retorna uma nova sessão."""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Context manager para sessões."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def close(self):
        """Fecha conexão."""
        self.engine.dispose()


# Instância global
db = Database()


def get_db() -> Database:
    """Retorna instância do banco de dados."""
    return db
