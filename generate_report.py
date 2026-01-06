"""
Generate data analysis report
"""
import pandas as pd
import json
from pathlib import Path
from config.settings import PROCESSED_DATA_DIR

def generate_markdown_report():
    """Generate a markdown report of the dataset"""
    
    print("\n" + "="*70)
    print("📊 GENERATING DATA ANALYSIS REPORT")
    print("="*70)
    
    # Load cleaned data
    csv_path = PROCESSED_DATA_DIR / 'cleaned_products.csv'
    
    if not csv_path.exists():
        print("❌ Error: cleaned_products.csv not found. Run test_data_cleaning.py first.")
        return
    
    df = pd.read_csv(csv_path)
    
    print(f"✅ Loaded {len(df)} products from {csv_path}")
    
    # Load statistics
    stats_path = PROCESSED_DATA_DIR / 'dataset_statistics.json'
    with open(stats_path, 'r') as f:
        stats = json.load(f)
    
    # Generate report
    report = []
    
    report.append("# E-commerce Product Data Extraction - Analysis Report")
    report.append("")
    report.append(f"**Generated on:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    report.append("")
    report.append(f"This report presents the results of an automated data extraction project that collected product information from multiple sources including API endpoints and web scraping.")
    report.append("")
    report.append(f"- **Total Products Extracted:** {stats['total_products']:,}")
    report.append(f"- **Data Sources:** {len(stats.get('data_source_distribution', {}))}")
    report.append(f"- **Total Attributes:** {stats['total_columns']}")
    report.append("")
    
    # Data Sources
    report.append("## Data Sources")
    report.append("")
    if 'data_source_distribution' in stats:
        for source, count in stats['data_source_distribution'].items():
            percentage = (count / stats['total_products']) * 100
            report.append(f"- **{source}:** {count:,} products ({percentage:.1f}%)")
    report.append("")
    
    # Price Analysis
    if 'price_stats' in stats:
        report.append("## Price Analysis")
        report.append("")
        ps = stats['price_stats']
        report.append(f"- **Average Price:** ${ps['mean']:.2f}")
        report.append(f"- **Median Price:** ${ps['median']:.2f}")
        report.append(f"- **Price Range:** ${ps['min']:.2f} - ${ps['max']:.2f}")
        report.append(f"- **Standard Deviation:** ${ps['std']:.2f}")
        report.append("")
        
        # Price distribution
        if 'price_category' in df.columns:
            price_dist = df['price_category'].value_counts()
            report.append("### Price Distribution by Category")
            report.append("")
            for category, count in price_dist.items():
                percentage = (count / len(df)) * 100
                report.append(f"- **{category}:** {count} products ({percentage:.1f}%)")
            report.append("")
    
    # Rating Analysis
    if 'rating_stats' in stats:
        report.append("## Rating Analysis")
        report.append("")
        rs = stats['rating_stats']
        report.append(f"- **Average Rating:** {rs['mean']:.2f}/5.0")
        report.append(f"- **Median Rating:** {rs['median']:.2f}/5.0")
        report.append(f"- **Rating Range:** {rs['min']:.1f} - {rs['max']:.1f}")
        report.append("")
        
        # Rating distribution
        if 'rating_category' in df.columns:
            rating_dist = df['rating_category'].value_counts()
            report.append("### Rating Distribution")
            report.append("")
            for category, count in rating_dist.items():
                percentage = (count / len(df)) * 100
                report.append(f"- **{category}:** {count} products ({percentage:.1f}%)")
            report.append("")
    
    # Category Analysis
    if 'category_distribution' in stats:
        report.append("## Category Analysis")
        report.append("")
        report.append(f"**Total Categories:** {len(stats['category_distribution'])}")
        report.append("")
        report.append("### Top 10 Categories by Product Count")
        report.append("")
        
        sorted_categories = sorted(
            stats['category_distribution'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        for i, (category, count) in enumerate(sorted_categories, 1):
            percentage = (count / stats['total_products']) * 100
            report.append(f"{i}. **{category}:** {count} products ({percentage:.1f}%)")
        report.append("")
    
    # Stock Availability
    if 'stock_stats' in stats:
        report.append("## Stock Availability")
        report.append("")
        ss = stats['stock_stats']
        report.append(f"- **In Stock:** {ss['in_stock']:,} products ({ss['in_stock_percentage']:.1f}%)")
        report.append(f"- **Out of Stock:** {ss['out_of_stock']:,} products ({100-ss['in_stock_percentage']:.1f}%)")
        report.append("")
    
    # Data Quality
    report.append("## Data Quality")
    report.append("")
    report.append("### Missing Values Analysis")
    report.append("")
    
    missing_values = {k: v for k, v in stats['missing_values'].items() if v > 0}
    if missing_values:
        for column, count in sorted(missing_values.items(), key=lambda x: x[1], reverse=True)[:10]:
            percentage = (count / stats['total_products']) * 100
            report.append(f"- **{column}:** {count} missing ({percentage:.1f}%)")
    else:
        report.append("✅ No missing values detected in the dataset.")
    report.append("")
    
    # Data Completeness
    total_cells = stats['total_products'] * stats['total_columns']
    total_missing = sum(stats['missing_values'].values())
    completeness = ((total_cells - total_missing) / total_cells) * 100
    
    report.append(f"**Overall Data Completeness:** {completeness:.2f}%")
    report.append("")
    
    # Key Insights
    report.append("## Key Insights")
    report.append("")
    report.append(f"1. Successfully extracted **{stats['total_products']:,}+ products** from multiple sources")
    report.append(f"2. Data completeness rate of **{completeness:.1f}%** indicates high-quality extraction")
    
    if 'price_stats' in stats:
        report.append(f"3. Average product price is **${stats['price_stats']['mean']:.2f}** with significant variation")
    
    if 'rating_stats' in stats:
        report.append(f"4. Products maintain an average rating of **{stats['rating_stats']['mean']:.2f}/5.0**")
    
    if 'stock_stats' in stats:
        report.append(f"5. **{stats['stock_stats']['in_stock_percentage']:.1f}%** of products are currently in stock")
    
    report.append("")
    
    # Technical Details
    report.append("## Technical Implementation")
    report.append("")
    report.append("### Technologies Used")
    report.append("")
    report.append("- **API Scraping:** Python Requests, JSON parsing")
    report.append("- **Web Scraping:** BeautifulSoup4, Requests, User-Agent rotation")
    report.append("- **Data Processing:** Pandas, NumPy")
    report.append("- **Anti-Detection:** Random delays, User-Agent rotation, Respectful scraping")
    report.append("")
    
    report.append("### Data Processing Pipeline")
    report.append("")
    report.append("1. **Data Collection:** Multi-source extraction (API + Web)")
    report.append("2. **Data Cleaning:** Handling missing values, type validation")
    report.append("3. **Data Normalization:** Standardizing formats, creating derived fields")
    report.append("4. **Data Merging:** Combining datasets from multiple sources")
    report.append("5. **Quality Assurance:** Duplicate removal, validation checks")
    report.append("6. **Export:** Multiple formats (CSV, Excel, JSON)")
    report.append("")
    
    # Conclusion
    report.append("## Conclusion")
    report.append("")
    report.append("This data extraction project successfully demonstrates:")
    report.append("")
    report.append("✅ **Multi-source data collection** capabilities")
    report.append("✅ **Robust error handling** and retry mechanisms")
    report.append("✅ **Professional data cleaning** and normalization")
    report.append("✅ **Scalable architecture** for future enhancements")
    report.append("✅ **Production-ready code** with logging and monitoring")
    report.append("")
    
    # Save report
    report_text = "\n".join(report)
    report_path = PROCESSED_DATA_DIR / 'DATA_ANALYSIS_REPORT.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"✅ Report generated: {report_path}")
    print(f"   Total lines: {len(report)}")
    print(f"   File size: {report_path.stat().st_size:,} bytes")
    
    print("\n" + "="*70)
    print("✅ REPORT GENERATION COMPLETED")
    print("="*70)
    
    return report_path

if __name__ == "__main__":
    generate_markdown_report()