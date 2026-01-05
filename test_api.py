"""
DummyJSON API connection test
"""
import requests
import json

BASE_URL = 'https://dummyjson.com'

def test_connection():
    """Simple API connection test"""
    
    print("="*60)
    print("🔄 Testing DummyJSON API connection")
    print("="*60)
    
    # Test 1: Fetch some products
    print("\n📦 Test 1: Fetching 5 products...")
    try:
        response = requests.get(f'{BASE_URL}/products?limit=5', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Connection successful!")
            print(f"📊 Products retrieved: {len(data.get('products', []))}")
            print(f"📦 Total available: {data.get('total', 0)}")
            
            # Display first product
            if data.get('products'):
                product = data['products'][0]
                print(f"\n🛍️ Sample product:")
                print(f"   ID: {product.get('id')}")
                print(f"   Title: {product.get('title')}")
                print(f"   Price: ${product.get('price')}")
                print(f"   Category: {product.get('category')}")
                print(f"   Stock: {product.get('stock')}")
                print(f"   Rating: {product.get('rating')}")
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False
    
    # Test 2: Fetch categories
    print("\n\n📂 Test 2: Fetching categories...")
    try:
        response = requests.get(f'{BASE_URL}/products/categories', timeout=10)
        
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ {len(categories)} categories available:")
            for i, cat in enumerate(categories[:10], 1):
                print(f"   {i}. {cat}")
            if len(categories) > 10:
                print(f"   ... and {len(categories) - 10} more")
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False
    
    # Test 3: Search products
    print("\n\n🔍 Test 3: Searching products (phone)...")
    try:
        response = requests.get(f'{BASE_URL}/products/search?q=phone', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data.get('products', []))} products found")
            
            if data.get('products'):
                product = data['products'][0]
                print(f"\n📱 First result:")
                print(f"   Title: {product.get('title')}")
                print(f"   Price: ${product.get('price')}")
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60)
    return True

if __name__ == "__main__":
    test_connection()