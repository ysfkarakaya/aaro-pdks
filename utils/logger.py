"""
AARO ERP - PDKS Logger Modülü
"""

import logging
import os
from datetime import datetime

def setup_logger(log_level='INFO', log_file='aaro_pdks.log'):
    """Logger'ı ayarla"""
    
    # Log seviyesini belirle
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    # Log formatını belirle
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Root logger'ı ayarla
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Mevcut handler'ları temizle
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    try:
        # Logs klasörü oluştur
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        log_path = os.path.join('logs', log_file)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logger başlatıldı - Seviye: {log_level}, Dosya: {log_path}")
        
    except Exception as e:
        logger.warning(f"Log dosyası oluşturulamadı: {str(e)}")
    
    return logger

def get_logger(name):
    """Belirli bir modül için logger al"""
    return logging.getLogger(name)
