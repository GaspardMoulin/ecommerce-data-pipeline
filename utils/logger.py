"""
Configuration du système de logging
"""
import logging
from pathlib import Path
from datetime import datetime
from config.settings import LOGS_DIR

def setup_logger(name: str, level=logging.INFO):
    """Configure et retourne un logger"""
    
    # Créer un logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler pour fichier
    log_file = LOGS_DIR / f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger