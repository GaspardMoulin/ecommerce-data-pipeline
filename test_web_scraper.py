"""
Web scraper test suite
"""
from scrapers.web_scraper import BooksToScrapeScraper
import json

def test_web_scraper():
    """Test web scraper with different methods"""
    
    scraper = BooksToScrapeScraper()
    
    print("\n" + "="*70)
    print("🚀 WEB SCRAPER TEST SUITE (Books to Scrape)")
    print("="*70)
    
    # Test 1: Scrape a single product list page
    print("\n📄 Test 1: Scraping a product list page")
    print("-" * 70)
    
    test_url = "https://books.toscrape.com/catalogue/page-1.html"
    product_urls = scraper.scrape_product_list_page(test_url)
    
    print(f"\n✅ Result: {len(product_urls)} product URLs found")
    if product_urls:
        print(f"   First product URL: {product_urls[0]}")
        print(f"   Last product URL: {product_urls[-1]}")
    
    # Test 2: Scrape a single product
    print("\n\n📚 Test 2: Scraping a single product details")
    print("-" * 70)
    
    if product_urls:
        single_product = scraper.scrape_product_details(product_urls[0])
        
        if single_product:
            print(f"\n✅ Product details retrieved:")
            print(f"   Title: {single_product.get('title')}")
            print(f"   Price: {single_product.get('price_currency')}{single_product.get('price')}")
            print(f"   Rating: {single_product.get('rating')}/5")
            print(f"   Category: {single_product.get('category')}")
            print(f"   In Stock: {single_product.get('in_stock')}")
            print(f"   Description: {single_product.get('description')[:100]}...")
            
            print(f"\n📄 Complete product data:")
            print(json.dumps(single_product, indent=2, ensure_ascii=False))
    
    # Test 3: Scrape multiple products (limited)
    print("\n\n📦 Test 3: Scraping 10 products")
    print("-" * 70)
    
    products = scraper.scrape_all_products(max_products=10, max_pages=1)
    
    print(f"\n✅ Result: {len(products)} products scraped")
    
    if products:
        print(f"\n📊 Sample statistics:")
        avg_price = sum(p['price'] for p in products if p['price']) / len(products)
        print(f"   Average price: £{avg_price:.2f}")
        
        categories = set(p['category'] for p in products)
        print(f"   Categories found: {', '.join(categories)}")
        
        in_stock_count = sum(1 for p in products if p['in_stock'])
        print(f"   In stock: {in_stock_count}/{len(products)}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED")
    print("="*70)
    
    # Summary
    print(f"\n📈 SUMMARY:")
    print(f"   ✓ Product list scraping: {len(product_urls)} URLs extracted")
    print(f"   ✓ Product details scraping: {'OK' if single_product else 'FAIL'}")
    print(f"   ✓ Multiple products scraping: {len(products)} products")
    print(f"   ✓ Total products in scraper: {scraper.products_scraped}")

if __name__ == "__main__":
    test_web_scraper()