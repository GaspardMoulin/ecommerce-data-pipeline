"""
Main pipeline for e-commerce data extraction
Orchestrates API scraping, web scraping, data cleaning, and export
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from scrapers.api_scraper import DummyJSONScraper
from scrapers.web_scraper import BooksToScrapeScraper
from utils.data_cleaner import DataCleaner
from utils.logger import setup_logger
from config.settings import PROCESSED_DATA_DIR

logger = setup_logger('main_pipeline')

class DataExtractionPipeline:
    """Main data extraction pipeline"""
    
    def __init__(self):
        self.api_scraper = DummyJSONScraper()
        self.web_scraper = BooksToScrapeScraper()
        self.data_cleaner = DataCleaner()
        
        logger.info("="*70)
        logger.info("DATA EXTRACTION PIPELINE INITIALIZED")
        logger.info("="*70)
    
    def run_api_extraction(self, max_products: int = 100) -> list:
        """
        Run API data extraction
        
        Args:
            max_products: Maximum products to extract
        
        Returns:
            List of products
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 1: API DATA EXTRACTION")
        logger.info("="*70)
        
        try:
            products = self.api_scraper.get_all_products(max_products=max_products)
            logger.info(f"✅ API extraction completed: {len(products)} products")
            return products
        except Exception as e:
            logger.error(f"❌ API extraction failed: {str(e)}")
            return []
    
    def run_web_scraping(self, max_products: int = 100, max_pages: int = None) -> list:
        """
        Run web scraping
        
        Args:
            max_products: Maximum products to scrape
            max_pages: Maximum pages to scrape
        
        Returns:
            List of products
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 2: WEB SCRAPING")
        logger.info("="*70)
        
        try:
            products = self.web_scraper.scrape_all_products(
                max_products=max_products,
                max_pages=max_pages
            )
            logger.info(f"✅ Web scraping completed: {len(products)} products")
            return products
        except Exception as e:
            logger.error(f"❌ Web scraping failed: {str(e)}")
            return []
    
    def run_data_cleaning(self, api_products: list, web_products: list):
        """
        Run data cleaning and processing
        
        Args:
            api_products: Products from API
            web_products: Products from web scraping
        
        Returns:
            Cleaned and merged DataFrame
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 3: DATA CLEANING & PROCESSING")
        logger.info("="*70)
        
        try:
            # Clean API data
            logger.info("Cleaning API data...")
            df_api = self.data_cleaner.clean_api_data(api_products)
            logger.info(f"✅ API data cleaned: {len(df_api)} products")
            
            # Clean web data
            logger.info("\nCleaning web scraped data...")
            df_web = self.data_cleaner.clean_web_scraped_data(web_products)
            logger.info(f"✅ Web data cleaned: {len(df_web)} products")
            
            # Merge datasets
            logger.info("\nMerging datasets...")
            df_merged = self.data_cleaner.merge_datasets(df_api, df_web)
            logger.info(f"✅ Datasets merged: {len(df_merged)} total products")
            
            # Add calculated fields
            logger.info("\nAdding calculated fields...")
            df_enriched = self.data_cleaner.add_calculated_fields(df_merged)
            logger.info(f"✅ Data enriched: {len(df_enriched.columns)} columns")
            
            return df_enriched
            
        except Exception as e:
            logger.error(f"❌ Data cleaning failed: {str(e)}")
            return None
    
    def run_export(self, df, timestamp: str):
        """
        Export data to multiple formats
        
        Args:
            df: DataFrame to export
            timestamp: Timestamp string for filenames
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 4: DATA EXPORT")
        logger.info("="*70)
        
        try:
            # Export to CSV
            csv_path = self.data_cleaner.export_to_csv(
                df, 
                f'ecommerce_products_{timestamp}.csv'
            )
            logger.info(f"✅ CSV exported: {csv_path}")
            
            # Export to Excel
            excel_path = self.data_cleaner.export_to_excel(
                df,
                f'ecommerce_products_{timestamp}.xlsx'
            )
            logger.info(f"✅ Excel exported: {excel_path}")
            
            # Export to JSON
            json_path = self.data_cleaner.export_to_json(
                df,
                f'ecommerce_products_{timestamp}.json'
            )
            logger.info(f"✅ JSON exported: {json_path}")
            
            # Generate and export statistics
            logger.info("\nGenerating statistics...")
            stats = self.data_cleaner.generate_statistics(df)
            stats_path = self.data_cleaner.export_to_json(
                stats,
                f'statistics_{timestamp}.json'
            )
            logger.info(f"✅ Statistics exported: {stats_path}")
            
            return {
                'csv': csv_path,
                'excel': excel_path,
                'json': json_path,
                'stats': stats_path
            }
            
        except Exception as e:
            logger.error(f"❌ Data export failed: {str(e)}")
            return None
    
    def run_full_pipeline(
        self,
        api_max_products: int = 100,
        web_max_products: int = 100,
        web_max_pages: int = None
    ):
        """
        Run the complete data extraction pipeline
        
        Args:
            api_max_products: Max products from API
            web_max_products: Max products from web
            web_max_pages: Max pages to scrape
        """
        start_time = datetime.now()
        timestamp = start_time.strftime('%Y%m%d_%H%M%S')
        
        logger.info("\n" + "="*70)
        logger.info("🚀 STARTING FULL DATA EXTRACTION PIPELINE")
        logger.info("="*70)
        logger.info(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Configuration:")
        logger.info(f"  - API products: {api_max_products}")
        logger.info(f"  - Web products: {web_max_products}")
        logger.info(f"  - Web pages: {web_max_pages if web_max_pages else 'unlimited'}")
        
        # Phase 1: API Extraction
        api_products = self.run_api_extraction(max_products=api_max_products)
        
        # Phase 2: Web Scraping
        web_products = self.run_web_scraping(
            max_products=web_max_products,
            max_pages=web_max_pages
        )
        
        # Check if we have data
        if not api_products and not web_products:
            logger.error("❌ No data extracted from any source. Pipeline failed.")
            return False
        
        # Phase 3: Data Cleaning
        df_final = self.run_data_cleaning(api_products, web_products)
        
        if df_final is None or len(df_final) == 0:
            logger.error("❌ Data cleaning failed or produced empty dataset.")
            return False
        
        # Phase 4: Export
        export_paths = self.run_export(df_final, timestamp)
        
        if export_paths is None:
            logger.error("❌ Data export failed.")
            return False
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "="*70)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"End time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Duration: {duration}")
        logger.info(f"\n📊 FINAL RESULTS:")
        logger.info(f"  - API products: {len(api_products)}")
        logger.info(f"  - Web products: {len(web_products)}")
        logger.info(f"  - Total products: {len(df_final)}")
        logger.info(f"  - Total columns: {len(df_final.columns)}")
        logger.info(f"\n📁 EXPORTED FILES:")
        for file_type, path in export_paths.items():
            logger.info(f"  - {file_type.upper()}: {path.name}")
        logger.info("="*70)
        
        return True


def main():
    """Main entry point with command-line arguments"""
    
    parser = argparse.ArgumentParser(
        description='E-commerce Data Extraction Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with default settings (100 products each)
  python main.py
  
  # Extract 500 products from API and 200 from web
  python main.py --api-products 500 --web-products 200
  
  # Limit web scraping to 5 pages
  python main.py --web-pages 5
  
  # Extract only from API
  python main.py --api-only --api-products 1000
  
  # Extract only from web
  python main.py --web-only --web-products 500
        """
    )
    
    parser.add_argument(
        '--api-products',
        type=int,
        default=100,
        help='Maximum products to extract from API (default: 100)'
    )
    
    parser.add_argument(
        '--web-products',
        type=int,
        default=100,
        help='Maximum products to scrape from web (default: 100)'
    )
    
    parser.add_argument(
        '--web-pages',
        type=int,
        default=None,
        help='Maximum pages to scrape from web (default: unlimited)'
    )
    
    parser.add_argument(
        '--api-only',
        action='store_true',
        help='Extract only from API'
    )
    
    parser.add_argument(
        '--web-only',
        action='store_true',
        help='Extract only from web scraping'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.api_only and args.web_only:
        print("❌ Error: Cannot use both --api-only and --web-only")
        sys.exit(1)
    
    # Adjust quantities based on flags
    api_products = args.api_products if not args.web_only else 0
    web_products = args.web_products if not args.api_only else 0
    
    # Create and run pipeline
    pipeline = DataExtractionPipeline()
    
    success = pipeline.run_full_pipeline(
        api_max_products=api_products,
        web_max_products=web_products,
        web_max_pages=args.web_pages
    )
    
    if success:
        print("\n✅ Pipeline completed successfully!")
        print(f"📁 Check results in: {PROCESSED_DATA_DIR}")
        sys.exit(0)
    else:
        print("\n❌ Pipeline failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()