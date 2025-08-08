import logging
import sys
from typing import Dict, Any


def setup_logging(level: str = "INFO") -> None:
    """
    Configura o logging da aplicação.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    
    # Formatador personalizado
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configuração do logger raiz
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=[console_handler],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Configurar loggers específicos
    loggers_config: Dict[str, Dict[str, Any]] = {
        "app": {"level": level.upper()},
        "uvicorn": {"level": "INFO"},
        "uvicorn.access": {"level": "INFO"},
        "sqlalchemy.engine": {"level": "WARNING"},  # Para não logar todas as queries SQL
        "sqlalchemy.pool": {"level": "WARNING"},
    }
    
    for logger_name, config in loggers_config.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, config["level"]))
    
    logging.info("Sistema de logging configurado com sucesso")
