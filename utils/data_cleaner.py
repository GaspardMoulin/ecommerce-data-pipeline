"""
Data cleaning and processing utilities
"""
import pandas as pd
import re
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from utils.logger import setup_logger
from config.settings import PROCESSED_DATA_DIR, RAW_DATA_DIR

logger = setup_logger('data_cleaner')

class DataCleaner:
    """Clean and process scraped data"""
    
    def __init__(self):
        logger.info("DataCleaner initialized")
    
    def clean_api_data(self, products: List[Dict]) -> pd.DataFrame:
        """
        Clean and normalize API data (DummyJSON)
        
        Args:
            products: List of product dictionaries from API
        
        Returns:
            Cleaned pandas DataFrame
        """
        logger.info(f"Cleaning {len(products)} products from API...")
        
        if not products:
            logger.warning("No products to clean")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(products)
        
        # Flatten nested structures if they exist
        if 'dimensions' in df.columns:
            dimensions_df = pd.json_normalize(df['dimensions'])
            dimensions_df.columns = ['dimension_' + col for col in dimensions_df.columns]
            df = pd.concat([df.drop('dimensions', axis=1), dimensions_df], axis=1)
        
        if 'meta' in df.columns:
            df = df.drop('meta', axis=1)
        
        if 'reviews' in df.columns:
            # Calculate average review rating if reviews exist
            df['avg_review_rating'] = df['reviews'].apply(
                lambda x: sum(r.get('rating', 0) for r in x) / len(x) if isinstance(x, list) and len(x) > 0 else None
            )
            df['num_reviews'] = df['reviews'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            )
            df = df.drop('reviews', axis=1)
        
        # Handle images (keep only first image or thumbnail)
        if 'images' in df.columns:
            df['main_image'] = df['images'].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else None
            )
            df['num_images'] = df['images'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            )
            df = df.drop('images', axis=1)
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Add data source
        df['data_source'] = 'DummyJSON_API'
        
        # Add scraping timestamp
        df['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Remove duplicates based on product ID
        initial_count = len(df)
        df = df.drop_duplicates(subset=['id'], keep='first')
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate products")
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Validate data types
        df = self._validate_data_types(df)
        
        logger.info(f"✅ API data cleaned: {len(df)} products")
        
        return df
    
    def clean_web_scraped_data(self, products: List[Dict]) -> pd.DataFrame:
        """
        Clean and normalize web scraped data (Books to Scrape)
        
        Args:
            products: List of product dictionaries from web scraping
        
        Returns:
            Cleaned pandas DataFrame
        """
        logger.info(f"Cleaning {len(products)} products from web scraping...")
        
        if not products:
            logger.warning("No products to clean")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(products)
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.replace(' ', '_')
        
        # Create unique ID based on title and URL
        df['id'] = df.apply(
            lambda row: hash(f"{row.get('title', '')}_{row.get('product_url', '')}") % 1000000,
            axis=1
        )
        
        # Add data source
        df['data_source'] = 'BooksToScrape_Web'
        
        # Add scraping timestamp
        df['scraped_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['id'], keep='first')
        duplicates_removed = initial_count - len(df)
        
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicate products")
        
        # Handle missing values
        df = self._handle_missing_values(df)
        
        # Validate data types
        df = self._validate_data_types(df)
        
        logger.info(f"✅ Web scraped data cleaned: {len(df)} products")
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in DataFrame
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with handled missing values
        """
        # Fill numeric columns with 0 or median
        numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_columns:
            if df[col].isna().sum() > 0:
                if col in ['price', 'rating', 'stock']:
                    df[col].fillna(0, inplace=True)
                else:
                    median_val = df[col].median()
                    df[col].fillna(median_val, inplace=True)
        
        # Fill string columns with empty string or 'Unknown'
        string_columns = df.select_dtypes(include=['object']).columns
        for col in string_columns:
            if df[col].isna().sum() > 0:
                if col in ['description', 'title', 'category', 'brand']:
                    df[col].fillna('Unknown', inplace=True)
                else:
                    df[col].fillna('', inplace=True)
        
        # Fill boolean columns with False
        bool_columns = df.select_dtypes(include=['bool']).columns
        for col in bool_columns:
            df[col].fillna(False, inplace=True)
        
        return df
    
    def _validate_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and convert data types
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with corrected data types
        """
        # Ensure price is float
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Ensure rating is numeric
        if 'rating' in df.columns:
            df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
        
        # Ensure stock is numeric
        if 'stock' in df.columns:
            df['stock'] = pd.to_numeric(df['stock'], errors='coerce')
        
        # Ensure ID is integer
        if 'id' in df.columns:
            df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
        
        # Ensure boolean columns are boolean
        bool_candidates = ['in_stock', 'onsale', 'returnable']
        for col in bool_candidates:
            if col in df.columns:
                df[col] = df[col].astype(bool)
        
        return df
    
    def merge_datasets(self, df_api: pd.DataFrame, df_web: pd.DataFrame) -> pd.DataFrame:
        """
        Merge API and web scraped datasets
        
        Args:
            df_api: Cleaned API data
            df_web: Cleaned web scraped data
        
        Returns:
            Merged DataFrame
        """
        logger.info("Merging datasets...")
        
        # Find common columns
        common_columns = list(set(df_api.columns) & set(df_web.columns))
        logger.info(f"Common columns: {len(common_columns)}")
        
        # Concatenate vertically
        df_merged = pd.concat([df_api, df_web], axis=0, ignore_index=True, sort=False)
        
        # Remove duplicates again after merging
        initial_count = len(df_merged)
        df_merged = df_merged.drop_duplicates(subset=['id', 'data_source'], keep='first')
        duplicates_removed = initial_count - len(df_merged)
        
        if duplicates_removed > 0:
            logger.info(f"Removed {duplicates_removed} duplicates after merging")
        
        logger.info(f"✅ Datasets merged: {len(df_merged)} total products")
        logger.info(f"   - API products: {len(df_api)}")
        logger.info(f"   - Web products: {len(df_web)}")
        
        return df_merged
    
    def add_calculated_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add calculated/derived fields
        
        Args:
            df: Input DataFrame
        
        Returns:
            DataFrame with additional fields
        """
        logger.info("Adding calculated fields...")
        
        # Price category
        if 'price' in df.columns:
            df['price_category'] = pd.cut(
                df['price'],
                bins=[0, 20, 50, 100, float('inf')],
                labels=['Budget', 'Mid-Range', 'Premium', 'Luxury']
            )
        
        # Rating category
        if 'rating' in df.columns:
            df['rating_category'] = pd.cut(
                df['rating'],
                bins=[0, 2, 3, 4, 5],
                labels=['Poor', 'Fair', 'Good', 'Excellent']
            )
        
        # Title length
        if 'title' in df.columns:
            df['title_length'] = df['title'].str.len()
            df['title_word_count'] = df['title'].str.split().str.len()
        
        # Description length
        if 'description' in df.columns:
            df['description_length'] = df['description'].str.len()
            df['description_word_count'] = df['description'].str.split().str.len()
            df['has_description'] = df['description'].str.len() > 0
        
        # Discount percentage if both prices available
        if 'price' in df.columns and 'regularprice' in df.columns:
            df['discount_percentage'] = (
                ((df['regularprice'] - df['price']) / df['regularprice']) * 100
            ).round(2)
        
        logger.info("✅ Calculated fields added")
        
        return df
    
    def generate_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Generate statistics about the dataset
        
        Args:
            df: DataFrame to analyze
        
        Returns:
            Dictionary with statistics
        """
        logger.info("Generating dataset statistics...")
        
        stats = {
            'total_products': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isna().sum().to_dict(),
            'data_types': df.dtypes.astype(str).to_dict(),
        }
        
        # Price statistics
        if 'price' in df.columns:
            stats['price_stats'] = {
                'mean': float(df['price'].mean()),
                'median': float(df['price'].median()),
                'min': float(df['price'].min()),
                'max': float(df['price'].max()),
                'std': float(df['price'].std())
            }
        
        # Rating statistics
        if 'rating' in df.columns:
            stats['rating_stats'] = {
                'mean': float(df['rating'].mean()),
                'median': float(df['rating'].median()),
                'min': float(df['rating'].min()),
                'max': float(df['rating'].max())
            }
        
        # Category distribution
        if 'category' in df.columns:
            stats['category_distribution'] = df['category'].value_counts().to_dict()
        
        # Data source distribution
        if 'data_source' in df.columns:
            stats['data_source_distribution'] = df['data_source'].value_counts().to_dict()
        
        # Stock availability
        if 'in_stock' in df.columns:
            # Convert to boolean if not already
            in_stock_bool = df['in_stock'].fillna(False).astype(bool)
            
            stats['stock_stats'] = {
                'in_stock': int(in_stock_bool.sum()),
                'out_of_stock': int((~in_stock_bool).sum()),
                'in_stock_percentage': float((in_stock_bool.sum() / len(df)) * 100)
            }
        
        logger.info("✅ Statistics generated")
        
        return stats
    
    def export_to_csv(self, df: pd.DataFrame, filename: str) -> Path:
        """
        Export DataFrame to CSV
        
        Args:
            df: DataFrame to export
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        output_path = PROCESSED_DATA_DIR / filename
        
        logger.info(f"Exporting to CSV: {output_path}")
        
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        logger.info(f"✅ Exported {len(df)} rows to {output_path}")
        
        return output_path
    
    def export_to_excel(self, df: pd.DataFrame, filename: str, sheet_name: str = 'Products') -> Path:
        """
        Export DataFrame to Excel
        
        Args:
            df: DataFrame to export
            filename: Output filename
            sheet_name: Sheet name
        
        Returns:
            Path to exported file
        """
        output_path = PROCESSED_DATA_DIR / filename
        
        logger.info(f"Exporting to Excel: {output_path}")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        logger.info(f"✅ Exported {len(df)} rows to {output_path}")
        
        return output_path
    
    def export_to_json(self, data, filename: str) -> Path:
        """
        Export DataFrame or dict to JSON
        
        Args:
            data: DataFrame or dictionary to export
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        output_path = PROCESSED_DATA_DIR / filename
        
        logger.info(f"Exporting to JSON: {output_path}")
        
        if isinstance(data, pd.DataFrame):
            # If it's a DataFrame, use pandas to_json
            data.to_json(output_path, orient='records', indent=2, force_ascii=False)
            logger.info(f"✅ Exported {len(data)} rows to {output_path}")
        else:
            # If it's a dict or other object, use json.dump
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"✅ Exported data to {output_path}")
        
        return output_path  
    





    