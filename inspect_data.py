"""
Detailed data inspection
"""
from scrapers.api_scraper import DummyJSONScraper
import json

def inspect_data_structure():
    """Inspect data structure to understand all available fields"""
    
    scraper = DummyJSONScraper()
    
    print("="*70)
    print("🔍 DATA STRUCTURE INSPECTION")
    print("="*70)
    
    # Fetch a complete product
    product = scraper.get_product_by_id(1)
    
    if product:
        print("\n📋 Available fields for a product:")
        print("-" * 70)
        
        for key, value in product.items():
            value_type = type(value).__name__
            value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"   {key:20} ({value_type:10}) : {value_preview}")
        
        print("\n\n📄 Complete JSON structure of a product:")
        print("-" * 70)
        print(json.dumps(product, indent=2, ensure_ascii=False))
        
        # Analyze dimensions if present
        if 'dimensions' in product:
            print("\n\n📏 Dimension details:")
            print("-" * 70)
            for dim_key, dim_value in product['dimensions'].items():
                print(f"   {dim_key}: {dim_value}")
        
        # Analyze reviews if present
        if 'reviews' in product:
            print(f"\n\n⭐ Reviews ({len(product['reviews'])} reviews):")
            print("-" * 70)
            for i, review in enumerate(product['reviews'][:2], 1):
                print(f"\n   Review {i}:")
                for rev_key, rev_value in review.items():
                    print(f"      {rev_key}: {rev_value}")
        
        # Analyze images
        if 'images' in product:
            print(f"\n\n🖼️ Images ({len(product['images'])} images):")
            print("-" * 70)
            for i, img_url in enumerate(product['images'][:3], 1):
                print(f"   Image {i}: {img_url}")
    
    print("\n" + "="*70)
    print("✅ INSPECTION COMPLETED")
    print("="*70)

if __name__ == "__main__":
    inspect_data_structure()