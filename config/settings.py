"""
Configuration centralisée du projet
"""
import os
from pathlib import Path

# Chemins du projet
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DATA_DIR = DATA_DIR / 'raw'
PROCESSED_DATA_DIR = DATA_DIR / 'processed'
LOGS_DIR = BASE_DIR / 'logs'

# Créer les dossiers s'ils n'existent pas
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Configuration scraping
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
]

REQUEST_DELAY = 2  # secondes entre chaque requête
RETRY_TIMES = 3
TIMEOUT = 30

# Base de données
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///ecommerce_data.db')

# Limites
MAX_PRODUCTS = 1000
CONCURRENT_REQUESTS = 5

# Web Scraping Configuration
TARGET_WEBSITE = 'https://books.toscrape.com'

# Selenium Configuration
SELENIUM_HEADLESS = True
SELENIUM_WAIT_TIME = 10
SELENIUM_PAGE_LOAD_TIMEOUT = 30

# Playwright Configuration
PLAYWRIGHT_HEADLESS = True
PLAYWRIGHT_TIMEOUT = 30000  # milliseconds

# Anti-detection
ENABLE_STEALTH = True
RANDOM_DELAY_MIN = 1  # seconds
RANDOM_DELAY_MAX = 3  # seconds

# Scraping limits
MAX_RETRIES_PER_PAGE = 3
DOWNLOAD_IMAGES = True
IMAGES_DIR = DATA_DIR / 'images'

# Create images directory
IMAGES_DIR.mkdir(parents=True, exist_ok=True)