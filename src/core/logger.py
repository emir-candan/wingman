import logging
import os
from datetime import datetime

# Logs klasörünün oluşturulması
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Güncel tarihe göre dosya ismi
log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
log_filepath = os.path.join(LOG_DIR, log_filename)

# Logger Yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filepath, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_logger(name: str):
    """
    Belirtilen isimde bir logger objesi döner.
    Kullanım: logger = get_logger(__name__)
    """
    return logging.getLogger(name)
