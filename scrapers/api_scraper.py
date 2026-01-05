"""
DummyJSON API Scraper
"""
import requests
import time
from typing import List, Dict, Optional
from utils.logger import setup_logger
from config.settings import REQUEST_DELAY, RETRY_TIMES, TIMEOUT

logger = setup_logger('api_scraper')

class DummyJSONScraper:
    """Scraper for DummyJSON API"""
    
    def __init__(self):
        self.base_url = 'https://dummyjson.com'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        logger.info("DummyJSONScraper initialized")
    
    def _make_request(self, endpoint: str, params: dict = None, retry: int = 0) -> Optional[dict]:
        """
        Make API request with error handling and retry logic
        
        Args:
            endpoint: API endpoint (e.g., 'products')
            params: Request parameters
            retry: Number of retry attempts made
        
        Returns:
            JSON data or None on error
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(
                url,
                params=params,
                timeout=TIMEOUT
            )
            
            if response.status_code == 200:
                return response.json()
            
            elif response.status_code == 429:  # Rate limit
                logger.warning("Rate limit reached, waiting 60 seconds...")
                time.sleep(60)
                if retry < RETRY_TIMES:
                    return self._make_request(endpoint, params, retry + 1)
            
            elif response.status_code == 404:
                logger.error(f"Endpoint not found: {url}")
                return None
            
            else:
                logger.error(f"API Error: {response.status_code} - {response.text}")
                if retry < RETRY_TIMES:
                    time.sleep(REQUEST_DELAY * (retry + 1))
                    return self._make_request(endpoint, params, retry + 1)
            
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout on request to {url}")
            if retry < RETRY_TIMES:
                time.sleep(REQUEST_DELAY * (retry + 1))
                return self._make_request(endpoint, params, retry + 1)
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {url}")
            if retry < RETRY_TIMES:
                time.sleep(REQUEST_DELAY * (retry + 1))
                return self._make_request(endpoint, params, retry + 1)
            return None
            
        except Exception as e:
            logger.error(f"Exception during request: {str(e)}")
            return None
    
    def get_all_categories(self) -> List[str]:
        """
        Fetch all available categories
        
        Returns:
            List of category names
        """
        logger.info("Fetching categories...")
        
        data = self._make_request('products/categories')
        
        if data and isinstance(data, list):
            # Handle both string and dict formats
            categories = []
            for item in data:
                if isinstance(item, str):
                    categories.append(item)
                elif isinstance(item, dict) and 'slug' in item:
                    categories.append(item['slug'])
                elif isinstance(item, dict) and 'name' in item:
                    categories.append(item['name'])
            
            logger.info(f"✅ {len(categories)} categories retrieved")
            return categories
        
        logger.warning("Unable to fetch categories")
        return []
    
    def get_products_paginated(self, limit: int = 100, skip: int = 0) -> Dict:
        """
        Fetch products with pagination
        
        Args:
            limit: Number of products per page
            skip: Number of products to skip
        
        Returns:
            Dictionary containing products and metadata
        """
        params = {
            'limit': limit,
            'skip': skip
        }
        
        logger.info(f"Fetching {limit} products (skip: {skip})...")
        
        data = self._make_request('products', params)
        
        if data:
            logger.info(f"✅ {len(data.get('products', []))} products retrieved")
            return data
        
        return {'products': [], 'total': 0, 'skip': skip, 'limit': limit}
    
    def get_all_products(self, max_products: int = 1000) -> List[Dict]:
        """
        Fetch all available products up to max_products
        
        Args:
            max_products: Maximum number of products to retrieve
        
        Returns:
            List of all products
        """
        logger.info(f"Starting scraping of all products (max: {max_products})...")
        
        all_products = []
        skip = 0
        limit = 100  # Maximum per request
        
        while len(all_products) < max_products:
            data = self.get_products_paginated(limit=limit, skip=skip)
            
            if not data.get('products'):
                logger.info("No more products available")
                break
            
            products = data['products']
            all_products.extend(products)
            
            total = data.get('total', 0)
            logger.info(f"Progress: {len(all_products)}/{min(total, max_products)} products")
            
            # Check if max reached
            if len(all_products) >= max_products:
                all_products = all_products[:max_products]
                break
            
            # Check if all available products retrieved
            if len(all_products) >= total:
                break
            
            skip += limit
            time.sleep(REQUEST_DELAY)  # Respect rate limits
        
        logger.info(f"✅ Scraping completed: {len(all_products)} products retrieved")
        return all_products
    
    def get_products_by_category(self, category: str, max_products: int = 100) -> List[Dict]:
        """
        Fetch products from a specific category
        
        Args:
            category: Category name
            max_products: Maximum number of products to retrieve
        
        Returns:
            List of products from the category
        """
        logger.info(f"Scraping category '{category}' (max: {max_products})...")
        
        endpoint = f'products/category/{category}'
        data = self._make_request(endpoint)
        
        if data and 'products' in data:
            products = data['products'][:max_products]
            logger.info(f"✅ {len(products)} products retrieved for '{category}'")
            return products
        
        logger.warning(f"No products found for category '{category}'")
        return []
    
    def get_multiple_categories(
        self, 
        categories: List[str], 
        products_per_category: int = 100
    ) -> Dict[str, List[Dict]]:
        """
        Fetch products from multiple categories
        
        Args:
            categories: List of category names
            products_per_category: Number of products per category
        
        Returns:
            Dictionary with category as key and product list as value
        """
        results = {}
        
        for category in categories:
            logger.info(f"\n{'='*50}")
            logger.info(f"Processing category: {category}")
            logger.info(f"{'='*50}")
            
            products = self.get_products_by_category(category, products_per_category)
            results[category] = products
            
            logger.info(f"Pausing between categories...")
            time.sleep(REQUEST_DELAY)
        
        total_products = sum(len(products) for products in results.values())
        logger.info(f"\n✅ Total: {total_products} products retrieved across {len(categories)} categories")
        
        return results
    
    def search_products(self, query: str, max_results: int = 100) -> List[Dict]:
        """
        Search products by search term
        
        Args:
            query: Search term
            max_results: Maximum number of results
        
        Returns:
            List of matching products
        """
        logger.info(f"Searching products: '{query}'")
        
        params = {'q': query}
        data = self._make_request('products/search', params)
        
        if data and 'products' in data:
            products = data['products'][:max_results]
            logger.info(f"✅ {len(products)} products found")
            return products
        
        logger.warning("No products found")
        return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """
        Fetch a specific product by its ID
        
        Args:
            product_id: Product ID
        
        Returns:
            Product dictionary or None
        """
        logger.info(f"Fetching product ID {product_id}...")
        
        endpoint = f'products/{product_id}'
        data = self._make_request(endpoint)
        
        if data:
            logger.info(f"✅ Product '{data.get('title')}' retrieved")
            return data
        
        logger.warning(f"Product ID {product_id} not found")
        return None
    
    def get_statistics(self) -> Dict:
        """
        Fetch API statistics
        
        Returns:
            Dictionary with statistics
        """
        logger.info("Fetching statistics...")
        
        # Fetch all products (just first page for stats)
        data = self.get_products_paginated(limit=1, skip=0)
        categories = self.get_all_categories()
        
        stats = {
            'total_products': data.get('total', 0),
            'total_categories': len(categories),
            'categories': categories
        }
        
        logger.info(f"📊 Statistics: {stats['total_products']} products, {stats['total_categories']} categories")
        
        return stats