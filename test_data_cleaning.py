"""
Data cleaning test suite
"""
from scrapers.api_scraper import DummyJSONScraper
from scrapers.web_scraper import BooksToScrapeScraper
from utils.data_cleaner import DataCleaner
import json

def test_data_cleaning():
    """Test data cleaning pipeline"""
    
    print("\n" + "="*70)
    print("🧹 DATA CLEANING TEST SUITE")
    print("="*70)
    
    # Initialize cleaners and scrapers
    cleaner = DataCleaner()
    
    # Test 1: Get sample data from API
    print("\n📊 Test 1: Fetching and cleaning API data")
    print("-" * 70)
    
    api_scraper = DummyJSONScraper()
    api_products = api_scraper.get_all_products(max_products=50)
    
    print(f"✅ Fetched {len(api_products)} products from API")
    
    # Clean API data
    df_api = cleaner.clean_api_data(api_products)
    
    print(f"✅ Cleaned API data:")
    print(f"   Shape: {df_api.shape}")
    print(f"   Columns: {list(df_api.columns)[:10]}...")
    print(f"\n   First product sample:")
    print(df_api.head(1).to_dict('records')[0])
    
    # Test 2: Get sample data from web scraping
    print("\n\n📚 Test 2: Fetching and cleaning web scraped data")
    print("-" * 70)
    
    web_scraper = BooksToScrapeScraper()
    web_products = web_scraper.scrape_all_products(max_products=30, max_pages=2)
    
    print(f"✅ Fetched {len(web_products)} products from web scraping")
    
    # Clean web data
    df_web = cleaner.clean_web_scraped_data(web_products)
    
    print(f"✅ Cleaned web data:")
    print(f"   Shape: {df_web.shape}")
    print(f"   Columns: {list(df_web.columns)[:10]}...")
    print(f"\n   First product sample:")
    print(df_web.head(1).to_dict('records')[0])
    
    # Test 3: Merge datasets
    print("\n\n🔗 Test 3: Merging datasets")
    print("-" * 70)
    
    df_merged = cleaner.merge_datasets(df_api, df_web)
    
    print(f"✅ Datasets merged:")
    print(f"   Total products: {len(df_merged)}")
    print(f"   Total columns: {len(df_merged.columns)}")
    print(f"   API products: {len(df_api)}")
    print(f"   Web products: {len(df_web)}")
    
    # Test 4: Add calculated fields
    print("\n\n➕ Test 4: Adding calculated fields")
    print("-" * 70)
    
    df_enriched = cleaner.add_calculated_fields(df_merged.copy())
    
    new_columns = set(df_enriched.columns) - set(df_merged.columns)
    print(f"✅ Added {len(new_columns)} new calculated fields:")
    for col in new_columns:
        print(f"   - {col}")
    
    # Test 5: Generate statistics
    print("\n\n📈 Test 5: Generating statistics")
    print("-" * 70)
    
    stats = cleaner.generate_statistics(df_enriched)
    
    print(f"✅ Statistics generated:")
    print(f"   Total products: {stats['total_products']}")
    print(f"   Total columns: {stats['total_columns']}")
    
    if 'price_stats' in stats:
        print(f"\n   Price statistics:")
        print(f"      Mean: ${stats['price_stats']['mean']:.2f}")
        print(f"      Median: ${stats['price_stats']['median']:.2f}")
        print(f"      Min: ${stats['price_stats']['min']:.2f}")
        print(f"      Max: ${stats['price_stats']['max']:.2f}")
    
    if 'data_source_distribution' in stats:
        print(f"\n   Data source distribution:")
        for source, count in stats['data_source_distribution'].items():
            print(f"      {source}: {count}")
    
    # Test 6: Export to different formats
    print("\n\n💾 Test 6: Exporting cleaned data")
    print("-" * 70)
    
    # Export to CSV
    csv_path = cleaner.export_to_csv(df_enriched, 'cleaned_products.csv')
    print(f"✅ Exported to CSV: {csv_path}")
    
    # Export to Excel
    excel_path = cleaner.export_to_excel(df_enriched, 'cleaned_products.xlsx')
    print(f"✅ Exported to Excel: {excel_path}")
    
    # Export to JSON
    json_path = cleaner.export_to_json(df_enriched, 'cleaned_products.json')
    print(f"✅ Exported to JSON: {json_path}")
    
    # Export statistics
    stats_path = cleaner.export_to_json(
        cleaner.generate_statistics(df_enriched),
        'dataset_statistics.json'
    )
    print(f"✅ Exported statistics: {stats_path}")
    
    print("\n" + "="*70)
    print("✅ ALL DATA CLEANING TESTS COMPLETED")
    print("="*70)
    
    # Summary
    print(f"\n📈 SUMMARY:")
    print(f"   ✓ API data cleaned: {len(df_api)} products")
    print(f"   ✓ Web data cleaned: {len(df_web)} products")
    print(f"   ✓ Merged dataset: {len(df_merged)} products")
    print(f"   ✓ Enriched dataset: {len(df_enriched)} products, {len(df_enriched.columns)} columns")
    print(f"   ✓ Exported to: CSV, Excel, JSON")
    print(f"   ✓ Statistics generated and exported")

if __name__ == "__main__":
    test_data_cleaning()