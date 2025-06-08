# backend/crewai/tools/debug_logger.py

import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(level=logging.INFO):
    logger = logging.getLogger("ecommerce_loader")
    logger.setLevel(level)

    # Evitar duplicação de handlers
    if not logger.handlers:
        # Formato dos logs com timestamp e nível
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

        # Handler para console
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # Handler para arquivo
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        fh = RotatingFileHandler(os.path.join(log_dir, "debug.log"), maxBytes=5*1024*1024, backupCount=3)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger