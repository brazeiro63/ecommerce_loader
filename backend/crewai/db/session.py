# database.py
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
# Importe o logger
from backend.crewai.tools.debug_logger import setup_logger

# Configure o nível do logger
LOG_LEVEL = logging.DEBUG  # Altere para logging.INFO para desativar debug
logger = setup_logger(level=LOG_LEVEL)



DATABASE_URL = os.environ.get("DATABASE_URL")
logger.debug(f"[DATABASE_URL] Parâmetros recebidos: {DATABASE_URL}")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
        # db.commit()  
    except Exception as e:
        db.rollback()
        logger.debug(f"[get_db] Erro: {e}")
        raise
    finally:
        db.close()
