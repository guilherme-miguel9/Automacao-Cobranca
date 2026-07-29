import logging
import sys
from pathlib import Path
from datetime import datetime
from config.settings import settings

def setup_logger(name: str = "CobrançaBot") -> logging.Logger:
    """
    Configura e retorna um logger padronizado para o sistema de cobranças.
    Exibe logs no console e grava em arquivo local na pasta data/output/.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Garantir suporte UTF-8 no sys.stdout do Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    # Handler para Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para Arquivo de Log
    log_dir = settings.OUTPUT_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    filename = log_dir / f"cobranca_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(filename, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
