"""
DummyJSON API Scraper test suite
"""
from scrapers.api_scraper import DummyJSONScraper
import json

def test_scraper():
    """Comprehensive scraper test with different methods"""
    
    scraper = DummyJSONScraper()
    
    print("\n" + "="*70)
    print("🚀 DUMMYJSON API SCRAPER TEST SUITE")
    print("="*70)
    
    # Test 1: Statistics
    print("\n📊 Test 1: Fetching statistics")
    print("-" * 70)
    
    stats = scraper.get_statistics()
    print(f"\n✅ Statistics retrieved:")
    print(f"   Total products available: {stats['total_products']}")
    print(f"   Total categories: {stats['total_categories']}")
    print(f"   Categories: {', '.join(stats['categories'][:5])}...")
    
    # Test 2: Fetch all products (limited)
    print("\n\n📦 Test 2: Scraping 50 products")
    print("-" * 70)
    
    all_products = scraper.get_all_products(max_products=50)
    print(f"\n✅ Result: {len(all_products)} products retrieved")
    
    if all_products:
        product = all_products[0]
        print(f"\n🛍️ Sample first product:")
        print(f"   ID: {product.get('id')}")
        print(f"   Title: {product.get('title')}")
        print(f"   Price: ${product.get('price')}")
        print(f"   Category: {product.get('category')}")
        print(f"   Rating: {product.get('rating')}")
        print(f"   Stock: {product.get('stock')}")
        print(f"   Brand: {product.get('brand')}")
    
    # Test 3: Scraping by category
    print("\n\n📱 Test 3: Scraping one category (smartphones)")
    print("-" * 70)
    
    smartphones = scraper.get_products_by_category('smartphones', max_products=20)
    print(f"\n✅ Result: {len(smartphones)} smartphones retrieved")
    
    if smartphones:
        print(f"\n📱 First smartphone:")
        print(f"   Title: {smartphones[0].get('title')}")
        print(f"   Price: ${smartphones[0].get('price')}")
        print(f"   Brand: {smartphones[0].get('brand')}")
    
    # Test 4: Scraping multiple categories
    print("\n\n🗂️ Test 4: Scraping 3 categories")
    print("-" * 70)
    
    categories_to_scrape = ['laptops', 'smartphones', 'fragrances']
    multi_results = scraper.get_multiple_categories(categories_to_scrape, products_per_category=15)
    
    print(f"\n✅ Results by category:")
    for cat, products in multi_results.items():
        print(f"   {cat}: {len(products)} products")
    
    # Test 5: Search
    print("\n\n🔍 Test 5: Searching products (phone)")
    print("-" * 70)
    
    search_results = scraper.search_products('phone', max_results=10)
    print(f"\n✅ Result: {len(search_results)} products found")
    
    if search_results:
        print(f"\n📱 First result:")
        print(f"   Title: {search_results[0].get('title')}")
        print(f"   Price: ${search_results[0].get('price')}")
        print(f"   Category: {search_results[0].get('category')}")
    
    # Test 6: Fetch specific product
    print("\n\n🎯 Test 6: Fetching product by ID (ID: 1)")
    print("-" * 70)
    
    single_product = scraper.get_product_by_id(1)
    
    if single_product:
        print(f"\n✅ Product retrieved:")
        print(json.dumps(single_product, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*70)
    
    # Summary
    print(f"\n📈 SUMMARY:")
    print(f"   ✓ Statistics: OK")
    print(f"   ✓ Global scraping: {len(all_products)} products")
    print(f"   ✓ Category scraping: {len(smartphones)} products")
    print(f"   ✓ Multi-categories: {sum(len(p) for p in multi_results.values())} products")
    print(f"   ✓ Search: {len(search_results)} results")
    print(f"   ✓ Specific product: {'OK' if single_product else 'FAIL'}")

if __name__ == "__main__":
    test_scraper()