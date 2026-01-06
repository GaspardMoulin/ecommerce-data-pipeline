"""
Predefined configurations for different pipeline runs
"""
from main import DataExtractionPipeline
from datetime import datetime

def run_quick_test():
    """Quick test run with minimal data"""
    print("\n🏃 RUNNING QUICK TEST")
    print("="*70)
    
    pipeline = DataExtractionPipeline()
    pipeline.run_full_pipeline(
        api_max_products=20,
        web_max_products=10,
        web_max_pages=1
    )

def run_medium_extraction():
    """Medium extraction for testing"""
    print("\n📦 RUNNING MEDIUM EXTRACTION")
    print("="*70)
    
    pipeline = DataExtractionPipeline()
    pipeline.run_full_pipeline(
        api_max_products=100,
        web_max_products=50,
        web_max_pages=3
    )

def run_full_extraction():
    """Full extraction - maximum data"""
    print("\n🚀 RUNNING FULL EXTRACTION")
    print("="*70)
    
    pipeline = DataExtractionPipeline()
    pipeline.run_full_pipeline(
        api_max_products=194,  # All available from DummyJSON
        web_max_products=1000,  # All books from Books to Scrape
        web_max_pages=None  # No limit
    )

def run_api_only():
    """Extract only from API"""
    print("\n🔌 RUNNING API ONLY EXTRACTION")
    print("="*70)
    
    pipeline = DataExtractionPipeline()
    pipeline.run_full_pipeline(
        api_max_products=194,
        web_max_products=0,
        web_max_pages=0
    )

def run_web_only():
    """Extract only from web scraping"""
    print("\n🌐 RUNNING WEB ONLY EXTRACTION")
    print("="*70)
    
    pipeline = DataExtractionPipeline()
    pipeline.run_full_pipeline(
        api_max_products=0,
        web_max_products=1000,
        web_max_pages=None
    )

if __name__ == "__main__":
    import sys
    
    configs = {
        'quick': run_quick_test,
        'medium': run_medium_extraction,
        'full': run_full_extraction,
        'api': run_api_only,
        'web': run_web_only
    }
    
    if len(sys.argv) < 2:
        print("Usage: python run_configs.py [quick|medium|full|api|web]")
        print("\nAvailable configurations:")
        print("  quick  - Quick test (20 API + 10 web products)")
        print("  medium - Medium run (100 API + 50 web products)")
        print("  full   - Full extraction (all available products)")
        print("  api    - API only (194 products)")
        print("  web    - Web only (1000 products)")
        sys.exit(1)
    
    config_name = sys.argv[1].lower()
    
    if config_name not in configs:
        print(f"❌ Unknown configuration: {config_name}")
        print(f"Available: {', '.join(configs.keys())}")
        sys.exit(1)
    
    configs[config_name]()