# Usage Guide - E-commerce Data Extraction Pipeline

This guide provides detailed instructions for using the data extraction pipeline.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Running the Pipeline](#running-the-pipeline)
3. [Understanding the Output](#understanding-the-output)
4. [Advanced Usage](#advanced-usage)
5. [Troubleshooting](#troubleshooting)

## Getting Started

### First Time Setup

1. **Install Python 3.9 or higher**
```bash
   python --version
```

2. **Clone and setup**
```bash
   git clone <repository-url>
   cd ecommerce-scraper
   python -m venv venv
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
```

3. **Verify installation**
```bash
   python main.py --help
```

## Running the Pipeline

### Basic Commands

**Default run (100 products from each source):**
```bash
python main.py
```

**Quick test run:**
```bash
python run_configs.py quick
```

**Custom quantities:**
```bash
python main.py --api-products 200 --web-products 150
```

### Command-Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--api-products N` | Max products from API | `--api-products 500` |
| `--web-products N` | Max products from web | `--web-products 200` |
| `--web-pages N` | Max pages to scrape | `--web-pages 10` |
| `--api-only` | Extract from API only | `--api-only` |
| `--web-only` | Extract from web only | `--web-only` |
| `--help` | Show help message | `--help` |

### Predefined Configurations

Use `run_configs.py` for predefined scenarios:
```bash
# Quick test (20 API + 10 web products, ~30 seconds)
python run_configs.py quick

# Medium extraction (100 API + 50 web products, ~5 minutes)
python run_configs.py medium

# Full extraction (all available products, ~30 minutes)
python run_configs.py full

# API only (194 products, ~2 minutes)
python run_configs.py api

# Web only (1000 products, ~1 hour)
python run_configs.py web
```

## Understanding the Output

### Pipeline Phases

The pipeline executes in 4 phases:

**Phase 1: API Data Extraction**
- Connects to DummyJSON API
- Extracts product information
- Handles pagination automatically
- Implements rate limiting

**Phase 2: Web Scraping**
- Scrapes Books to Scrape website
- Visits each product page for details
- Downloads product images
- Implements anti-detection measures

**Phase 3: Data Cleaning & Processing**
- Cleans both datasets
- Merges data from multiple sources
- Adds calculated fields
- Validates data quality

**Phase 4: Data Export**
- Exports to CSV, Excel, JSON
- Generates statistics
- Creates analysis report

### Output Files

All files are saved in `data/processed/` with timestamps:

**Main datasets:**
- `ecommerce_products_YYYYMMDD_HHMMSS.csv` - CSV format
- `ecommerce_products_YYYYMMDD_HHMMSS.xlsx` - Excel format
- `ecommerce_products_YYYYMMDD_HHMMSS.json` - JSON format

**Metadata:**
- `statistics_YYYYMMDD_HHMMSS.json` - Dataset statistics
- `DATA_ANALYSIS_REPORT.md` - Comprehensive analysis

**Logs:**
- `logs/main_pipeline_YYYYMMDD.log` - Pipeline execution log
- `logs/api_scraper_YYYYMMDD.log` - API scraping log
- `logs/web_scraper_YYYYMMDD.log` - Web scraping log
- `logs/data_cleaner_YYYYMMDD.log` - Data cleaning log

### Data Structure

**CSV/Excel columns include:**
- `id` - Unique product identifier
- `title` - Product name
- `price` - Product price
- `category` - Product category
- `rating` - Customer rating (1-5)
- `description` - Product description
- `in_stock` - Availability status
- `data_source` - Source of data (API or Web)
- `scraped_at` - Extraction timestamp
- Plus 20+ additional fields

### Statistics File

The statistics JSON includes:
- Total products count
- Price statistics (mean, median, min, max)
- Rating distribution
- Category breakdown
- Stock availability
- Data quality metrics
- Missing values analysis

## Advanced Usage

### Custom Data Sources

To add a new data source:

1. Create a new scraper in `scrapers/`
2. Inherit from base classes or create new
3. Implement required methods
4. Add to `main.py` pipeline

### Modifying Extraction Logic

**API Scraper (`scrapers/api_scraper.py`):**
```python
# Modify max products per request
params = {
    'limit': 50,  # Change this value
    'skip': skip
}
```

**Web Scraper (`scrapers/web_scraper.py`):**
```python
# Modify delay between requests
from config.settings import RANDOM_DELAY_MIN, RANDOM_DELAY_MAX

# Edit config/settings.py:
RANDOM_DELAY_MIN = 2  # Increase for slower scraping
RANDOM_DELAY_MAX = 5
```

### Data Cleaning Customization

Edit `utils/data_cleaner.py` to:
- Add custom validation rules
- Modify missing value handling
- Add new calculated fields
- Change export formats

Example - Add custom field:
```python
def add_calculated_fields(self, df):
    # Existing code...
    
    # Add custom field
    df['is_premium'] = df['price'] > 100
    
    return df
```

### Scheduling Automated Runs

**Windows Task Scheduler:**
```bash
# Create a batch file: run_pipeline.bat
@echo off
cd C:\path\to\ecommerce-scraper
call venv\Scripts\activate
python main.py --api-products 200 --web-products 100
```

**Linux Cron:**
```bash
# Add to crontab
0 2 * * * cd /path/to/ecommerce-scraper && ./venv/bin/python main.py
```

## Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError**
```
Solution: Ensure virtual environment is activated
venv\Scripts\activate
pip install -r requirements.txt
```

**Issue: Connection timeout**
```
Solution: Check internet connection, increase timeout in config/settings.py
TIMEOUT = 60  # Increase value
```

**Issue: Rate limiting (429 errors)**
```
Solution: Increase delays in config/settings.py
REQUEST_DELAY = 5  # Increase delay between requests
```

**Issue: Missing images**
```
Solution: Ensure DOWNLOAD_IMAGES is True in config/settings.py
DOWNLOAD_IMAGES = True
```

**Issue: Empty dataset**
```
Solution: Check logs for errors
type logs\main_pipeline_*.log  # Windows
cat logs/main_pipeline_*.log   # Linux/Mac
```

### Performance Tips

**Faster execution:**
- Reduce product counts
- Limit web pages
- Disable image downloads
- Increase concurrent requests (with caution)

**Better data quality:**
- Increase retry attempts
- Add longer delays
- Enable all validation checks

**Lower resource usage:**
- Reduce concurrent requests
- Disable image downloads
- Use CSV instead of Excel

### Getting Help

1. Check logs in `logs/` directory
2. Review error messages carefully
3. Consult this guide
4. Check GitHub issues
5. Contact maintainer

## Best Practices

### Respectful Scraping

- ✅ Always check `robots.txt`
- ✅ Implement rate limiting
- ✅ Use appropriate delays
- ✅ Rotate user agents
- ✅ Handle errors gracefully
- ❌ Don't overwhelm servers
- ❌ Don't scrape sensitive data

### Data Management

- Run pipeline during off-peak hours
- Archive old datasets regularly
- Monitor disk space usage
- Back up important extractions
- Document custom modifications

### Production Deployment

For production use:
1. Set up proper monitoring
2. Implement alerting for failures
3. Use environment variables for sensitive data
4. Schedule regular runs
5. Set up automatic backups
6. Monitor resource usage

## Examples

### Example 1: Daily Product Updates
```bash
# Morning run - get latest data
python main.py --api-products 200 --web-products 100

# Check output
cd data\processed
dir
```

### Example 2: Category-Specific Extraction
```python
# Custom script
from scrapers.api_scraper import DummyJSONScraper

scraper = DummyJSONScraper()
smartphones = scraper.get_products_by_category('smartphones', 50)
print(f"Found {len(smartphones)} smartphones")
```

### Example 3: Data Analysis
```python
# Load and analyze data
import pandas as pd

df = pd.read_csv('data/processed/ecommerce_products_latest.csv')
print(f"Average price: ${df['price'].mean():.2f}")
print(f"Top category: {df['category'].value_counts().index[0]}")
```

## Conclusion

This pipeline provides a robust foundation for e-commerce data extraction. Customize it to your needs and always scrape responsibly.

For questions or issues, please refer to the main README.md or contact the maintainer.