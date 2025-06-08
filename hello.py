# Importe o logger
import logging
from backend.crewai.tools.debug_logger import setup_logger

# Configure o nível do logger
LOG_LEVEL = logging.DEBUG  # Altere para logging.INFO para desativar debug
logger = setup_logger(level=LOG_LEVEL)

def main():
    print("Hello from ecommerce-loader!")
    logger.debug(f"[main] Mensagem: {"Hello from ecommerce-loader!"}")



if __name__ == "__main__":
    main()
