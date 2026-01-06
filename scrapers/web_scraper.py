"""
Web scraper using BeautifulSoup and Requests
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin
import time

from utils.logger import setup_logger
from utils.web_helpers import (
    UserAgentRotator,
    random_delay,
    normalize_price,
    normalize_rating,
    clean_text,
    download_image,
    make_absolute_url
)
from config.settings import (
    TARGET_WEBSITE,
    REQUEST_DELAY,
    RETRY_TIMES,
    TIMEOUT,
    DOWNLOAD_IMAGES,
    IMAGES_DIR,
    RANDOM_DELAY_MIN,
    RANDOM_DELAY_MAX
)

logger = setup_logger('web_scraper')

class BooksToScrapeScraper:
    """Web scraper for Books to Scrape website"""
    
    def __init__(self):
        self.base_url = TARGET_WEBSITE
        self.session = requests.Session()
        self.ua_rotator = UserAgentRotator()
        self.products_scraped = 0
        
        # Set initial headers
        self.session.headers.update({
            'User-Agent': self.ua_rotator.get_chrome_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        logger.info("BooksToScrapeScraper initialized")
    
    def _rotate_user_agent(self):
        """Rotate user agent for next request"""
        self.session.headers['User-Agent'] = self.ua_rotator.get_random_user_agent()
    
    def _make_request(self, url: str, retry: int = 0) -> Optional[BeautifulSoup]:
        """
        Make HTTP request and return BeautifulSoup object
        
        Args:
            url: URL to scrape
            retry: Number of retry attempts
        
        Returns:
            BeautifulSoup object or None on error
        """
        try:
            self._rotate_user_agent()
            
            logger.debug(f"Requesting: {url}")
            response = self.session.get(url, timeout=TIMEOUT)
            
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'lxml')
            
            elif response.status_code == 429:
                logger.warning("Rate limit hit, waiting 60 seconds...")
                time.sleep(60)
                if retry < RETRY_TIMES:
                    return self._make_request(url, retry + 1)
            
            else:
                logger.error(f"HTTP {response.status_code} for {url}")
                if retry < RETRY_TIMES:
                    time.sleep(REQUEST_DELAY * (retry + 1))
                    return self._make_request(url, retry + 1)
            
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout for {url}")
            if retry < RETRY_TIMES:
                return self._make_request(url, retry + 1)
            return None
            
        except Exception as e:
            logger.error(f"Exception for {url}: {str(e)}")
            return None
    
    def scrape_product_list_page(self, url: str) -> List[str]:
        """
        Scrape a product list page and extract product URLs
        
        Args:
            url: URL of the product list page
        
        Returns:
            List of product URLs
        """
        logger.info(f"Scraping product list: {url}")
        
        soup = self._make_request(url)
        if not soup:
            return []
        
        product_urls = []
        products = soup.select('.product_pod')
        
        for product in products:
            link = product.select_one('h3 a')
            if link and link.get('href'):
                product_url = make_absolute_url(url, link['href'])
                product_urls.append(product_url)
        
        logger.info(f"✅ Found {len(product_urls)} products on page")
        return product_urls
    
    def scrape_product_details(self, url: str) -> Optional[Dict]:
        """
        Scrape detailed information from a product page
        
        Args:
            url: Product page URL
        
        Returns:
            Dictionary with product details or None
        """
        logger.debug(f"Scraping product: {url}")
        
        soup = self._make_request(url)
        if not soup:
            return None
        
        try:
            # Extract basic information
            title = soup.select_one('.product_main h1')
            title = clean_text(title.text) if title else "Unknown"
            
            price = soup.select_one('.product_main .price_color')
            price_text = price.text if price else "£0.00"
            price_value = normalize_price(price_text)
            
            # Extract rating
            rating_element = soup.select_one('.product_main .star-rating')
            rating = normalize_rating(rating_element['class'][1]) if rating_element else None
            
            # Extract availability
            availability = soup.select_one('.product_main .availability')
            in_stock = 'In stock' in availability.text if availability else False
            stock_text = clean_text(availability.text) if availability else "Unknown"
            
            # Extract description
            description_elem = soup.select_one('#product_description + p')
            description = clean_text(description_elem.text) if description_elem else ""
            
            # Extract category
            breadcrumb = soup.select('.breadcrumb li')
            category = breadcrumb[2].text.strip() if len(breadcrumb) > 2 else "Unknown"
            
            # Extract product information table
            product_info = {}
            table_rows = soup.select('.table.table-striped tr')
            for row in table_rows:
                th = row.select_one('th')
                td = row.select_one('td')
                if th and td:
                    key = clean_text(th.text)
                    value = clean_text(td.text)
                    product_info[key] = value
            
            # Extract image URL
            image_elem = soup.select_one('.item.active img')
            image_url = None
            if image_elem and image_elem.get('src'):
                image_url = make_absolute_url(self.base_url, image_elem['src'])
            
            # Extract number of reviews
            reviews_elem = soup.select('.product_main p')
            num_reviews = 0
            for elem in reviews_elem:
                if 'review' in elem.text.lower():
                    import re
                    match = re.search(r'(\d+)', elem.text)
                    if match:
                        num_reviews = int(match.group(1))
            
            product_data = {
                'title': title,
                'price': price_value,
                'price_currency': price_text[0] if price_text else '£',
                'rating': rating,
                'in_stock': in_stock,
                'availability': stock_text,
                'description': description,
                'category': category,
                'image_url': image_url,
                'product_url': url,
                'num_reviews': num_reviews,
                'upc': product_info.get('UPC', ''),
                'product_type': product_info.get('Product Type', ''),
                'tax': product_info.get('Tax', ''),
                'num_available': product_info.get('Availability', '')
            }
            
            # Download image if enabled
            if DOWNLOAD_IMAGES and image_url:
                image_filename = f"book_{self.products_scraped + 1}.jpg"
                image_path = IMAGES_DIR / image_filename
                if download_image(image_url, image_path):
                    product_data['local_image_path'] = str(image_path)
            
            self.products_scraped += 1
            logger.info(f"✅ Product scraped: {title}")
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error parsing product page {url}: {str(e)}")
            return None
    
    def get_next_page_url(self, soup: BeautifulSoup, current_url: str) -> Optional[str]:
        """
        Extract next page URL from pagination
        
        Args:
            soup: BeautifulSoup object of current page
            current_url: Current page URL
        
        Returns:
            Next page URL or None
        """
        next_button = soup.select_one('.pager .next a')
        if next_button and next_button.get('href'):
            return make_absolute_url(current_url, next_button['href'])
        return None
    
    def scrape_all_products(self, max_products: int = 1000, max_pages: int = None) -> List[Dict]:
        """
        Scrape all products from the website
        
        Args:
            max_products: Maximum number of products to scrape
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of product dictionaries
        """
        logger.info(f"Starting full website scraping (max products: {max_products})")
        
        all_products = []
        current_url = f"{self.base_url}/catalogue/page-1.html"
        page_count = 0
        
        while current_url and len(all_products) < max_products:
            page_count += 1
            
            if max_pages and page_count > max_pages:
                logger.info(f"Reached max pages limit: {max_pages}")
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Scraping page {page_count}: {current_url}")
            logger.info(f"{'='*60}")
            
            # Get product URLs from list page
            product_urls = self.scrape_product_list_page(current_url)
            
            if not product_urls:
                logger.warning("No products found on page, stopping")
                break
            
            # Scrape each product
            for i, product_url in enumerate(product_urls, 1):
                if len(all_products) >= max_products:
                    break
                
                logger.info(f"[{len(all_products)+1}/{max_products}] Scraping product {i}/{len(product_urls)}")
                
                product_data = self.scrape_product_details(product_url)
                
                if product_data:
                    all_products.append(product_data)
                    logger.info(f"Progress: {len(all_products)}/{max_products} products scraped")
                
                # Random delay between products
                random_delay(RANDOM_DELAY_MIN, RANDOM_DELAY_MAX)
            
            # Get next page
            soup = self._make_request(current_url)
            if soup:
                current_url = self.get_next_page_url(soup, current_url)
                if current_url:
                    logger.info(f"Moving to next page: {current_url}")
                    time.sleep(REQUEST_DELAY)
            else:
                break
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ SCRAPING COMPLETED")
        logger.info(f"{'='*60}")
        logger.info(f"Total products scraped: {len(all_products)}")
        logger.info(f"Total pages visited: {page_count}")
        
        return all_products
    
    def scrape_category(self, category_url: str, max_products: int = 100) -> List[Dict]:
        """
        Scrape products from a specific category
        
        Args:
            category_url: Category page URL
            max_products: Maximum products to scrape
        
        Returns:
            List of product dictionaries
        """
        logger.info(f"Scraping category: {category_url}")
        
        products = []
        current_url = category_url
        
        while current_url and len(products) < max_products:
            product_urls = self.scrape_product_list_page(current_url)
            
            for product_url in product_urls:
                if len(products) >= max_products:
                    break
                
                product_data = self.scrape_product_details(product_url)
                if product_data:
                    products.append(product_data)
                
                random_delay(RANDOM_DELAY_MIN, RANDOM_DELAY_MAX)
            
            # Get next page
            soup = self._make_request(current_url)
            if soup:
                current_url = self.get_next_page_url(soup, current_url)
                if current_url:
                    time.sleep(REQUEST_DELAY)
            else:
                break
        
        logger.info(f"✅ Category scraping completed: {len(products)} products")
        return products