"""
Web scraping helper functions
"""
import random
import time
import requests
from typing import Optional
from pathlib import Path
from fake_useragent import UserAgent
from utils.logger import setup_logger

logger = setup_logger('web_helpers')

class UserAgentRotator:
    """Rotate user agents to avoid detection"""
    
    def __init__(self):
        self.ua = UserAgent()
        logger.info("UserAgentRotator initialized")
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        return self.ua.random
    
    def get_chrome_user_agent(self) -> str:
        """Get a Chrome user agent"""
        return self.ua.chrome
    
    def get_firefox_user_agent(self) -> str:
        """Get a Firefox user agent"""
        return self.ua.firefox


def random_delay(min_delay: float = 1, max_delay: float = 3):
    """
    Add random delay to mimic human behavior
    
    Args:
        min_delay: Minimum delay in seconds
        max_delay: Maximum delay in seconds
    """
    delay = random.uniform(min_delay, max_delay)
    logger.debug(f"Random delay: {delay:.2f} seconds")
    time.sleep(delay)


def download_image(url: str, save_path: Path, timeout: int = 10) -> bool:
    """
    Download image from URL
    
    Args:
        url: Image URL
        save_path: Path to save the image
        timeout: Request timeout
    
    Returns:
        True if successful, False otherwise
    """
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        
        if response.status_code == 200:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.debug(f"Image downloaded: {save_path.name}")
            return True
        else:
            logger.warning(f"Failed to download image: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        return False


def normalize_price(price_text: str) -> Optional[float]:
    """
    Normalize price text to float
    
    Args:
        price_text: Price text (e.g., "£51.77", "$29.99")
    
    Returns:
        Price as float or None
    """
    try:
        # Remove currency symbols and spaces
        clean_price = price_text.replace('£', '').replace('$', '').replace('€', '').strip()
        return float(clean_price)
    except:
        logger.warning(f"Could not normalize price: {price_text}")
        return None


def normalize_rating(rating_class: str) -> Optional[int]:
    """
    Convert rating class to numeric value
    
    Args:
        rating_class: Rating class (e.g., "star-rating Three")
    
    Returns:
        Rating as integer (1-5) or None
    """
    rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }
    
    for word in rating_class.split():
        if word in rating_map:
            return rating_map[word]
    
    logger.warning(f"Could not normalize rating: {rating_class}")
    return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    Args:
        text: Raw text
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = ' '.join(text.split())
    
    # Remove special characters that might cause issues
    cleaned = cleaned.strip()
    
    return cleaned


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid
    
    Args:
        url: URL to check
    
    Returns:
        True if valid, False otherwise
    """
    return url.startswith('http://') or url.startswith('https://')


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Convert relative URL to absolute URL
    
    Args:
        base_url: Base URL (e.g., "https://example.com")
        relative_url: Relative URL (e.g., "/product/123")
    
    Returns:
        Absolute URL
    """
    from urllib.parse import urljoin
    return urljoin(base_url, relative_url)