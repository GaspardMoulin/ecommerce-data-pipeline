# E-commerce Data Pipeline

Advanced multi-source e-commerce scraping pipeline with anti-bot handling, data cleaning, and automated monitoring.

## Features
- Multi-source scraping (API + Web)
- Anti-bot mechanisms (proxy rotation, user-agent rotation)
- Data cleaning and validation
- Automated scheduling
- Comprehensive logging
- Export to multiple formats (CSV, JSON, Database)

## Tech Stack
- Python 3.x
- Scrapy, Selenium, Playwright
- Pandas for data processing
- SQLAlchemy for database operations

## Installation
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
playwright install chromium
```

## Usage
```bash
python main.py
```

## Project Structure
```
ecommerce-scraper/
├── scrapers/          # Scraping modules
├── data/             # Data storage
├── config/           # Configuration files
├── utils/            # Utility functions
├── logs/             # Log files
└── main.py           # Entry point
```

## License
MIT