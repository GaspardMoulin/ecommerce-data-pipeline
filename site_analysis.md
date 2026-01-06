# Website Analysis: Books to Scrape

## General Information
- URL: https://books.toscrape.com/
- Type: Static HTML (no JavaScript required for basic scraping)
- robots.txt: Allows scraping
- Purpose: E-commerce bookstore (test site)

## Data Structure

### Homepage/Category Pages
- Product cards: `.product_pod`
- Title: `h3 > a` (title attribute)
- Price: `.price_color`
- Rating: `.star-rating` class (One, Two, Three, Four, Five)
- Availability: `.availability`
- Image: `.image_container img` (src attribute)
- Product URL: `h3 > a` (href attribute)

### Product Detail Pages
- Title: `.product_main h1`
- Price: `.product_main .price_color`
- Availability: `.product_main .availability`
- Product Description: `#product_description + p`
- Product Information: `.table.table-striped`
- Category: `.breadcrumb li:nth-child(3) a`
- Number of reviews: `.product_main` (last p tag)

### Pagination
- Next page: `.pager .next a` (href)
- 50 pages total
- 20 products per page
- Total: ~1000 products

## Scraping Strategy
1. Scrape all category pages with pagination
2. For each product, visit detail page for complete info
3. Handle rate limiting with delays
4. Implement retry logic for failed requests
5. Use rotating user agents

## Technical Challenges
- Multi-page scraping (pagination)
- Need to visit each product page for full details
- Image downloading
- Data normalization (ratings as numbers)