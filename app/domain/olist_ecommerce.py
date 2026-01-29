"""
Olist E-Commerce Domain Knowledge
Brazilian marketplace dataset with order, customer, product, and review data.
"""

OLIST_SCHEMA = """
=== OLIST E-COMMERCE DATABASE STRUCTURE ===

CORE TABLES:

1. olist_orders_dataset
   - order_id (PK): Unique order identifier
   - customer_id (FK): Reference to customer
   - order_status: delivered, shipped, canceled, etc.
   - order_purchase_timestamp: When order was placed
   - order_approved_at: When payment was approved
   - order_delivered_carrier_date: When handed to carrier
   - order_delivered_customer_date: When delivered to customer
   - order_estimated_delivery_date: Expected delivery date

2. olist_order_items_dataset
   - order_id (FK): Reference to order
   - order_item_id: Sequential number of items in same order
   - product_id (FK): Reference to product
   - seller_id (FK): Reference to seller
   - shipping_limit_date: Seller shipping deadline
   - price: Item price
   - freight_value: Shipping cost

3. olist_customers_dataset
   - customer_id (PK): Unique customer identifier
   - customer_unique_id: Real customer ID (can have multiple customer_ids)
   - customer_zip_code_prefix: First 5 digits of zip code
   - customer_city: City name
   - customer_state: State abbreviation (SP, RJ, MG, etc.)

4. olist_products_dataset
   - product_id (PK): Unique product identifier
   - product_category_name: Category in Portuguese
   - product_name_lenght: Product name length
   - product_description_lenght: Product description length
   - product_photos_qty: Number of photos
   - product_weight_g: Product weight in grams
   - product_length_cm, product_height_cm, product_width_cm: Dimensions

5. olist_sellers_dataset
   - seller_id (PK): Unique seller identifier
   - seller_zip_code_prefix: First 5 digits of seller zip code
   - seller_city: Seller city
   - seller_state: Seller state

6. olist_order_reviews_dataset
   - review_id (PK): Unique review identifier
   - order_id (FK): Reference to order
   - review_score: 1 to 5 stars
   - review_comment_title: Review title
   - review_comment_message: Review text
   - review_creation_date: When review was created
   - review_answer_timestamp: When review was answered

7. olist_order_payments_dataset
   - order_id (FK): Reference to order
   - payment_sequential: Sequential payment for same order
   - payment_type: credit_card, boleto, voucher, debit_card
   - payment_installments: Number of installments
   - payment_value: Payment amount

8. product_category_name_translation
   - product_category_name (Portuguese)
   - product_category_name_english

9. olist_geolocation_dataset
   - geolocation_zip_code_prefix: Zip code prefix
   - geolocation_lat: Latitude
   - geolocation_lng: Longitude
   - geolocation_city: City name
   - geolocation_state: State abbreviation

=== KEY RELATIONSHIPS ===

Order Flow:
customers.customer_id → orders.customer_id
orders.order_id → order_items.order_id
order_items.product_id → products.product_id
order_items.seller_id → sellers.seller_id
orders.order_id → order_payments.order_id
orders.order_id → order_reviews.order_id

Geographic:
customers.customer_zip_code_prefix → geolocation.geolocation_zip_code_prefix
sellers.seller_zip_code_prefix → geolocation.geolocation_zip_code_prefix

Translation:
products.product_category_name → product_category_name_translation.product_category_name
"""

OLIST_METRICS = """
=== BUSINESS METRICS FOR OLIST ===

REVENUE METRICS:
- GMV (Gross Merchandise Value) = SUM(oi.price + oi.freight_value)
- Product Revenue = SUM(oi.price)
- Freight Revenue = SUM(oi.freight_value)
- Average Order Value (AOV) = GMV / COUNT(DISTINCT order_id)
- Revenue per Customer = GMV / COUNT(DISTINCT customer_unique_id)

OPERATIONAL METRICS:
- Delivery Time = DATEDIFF(order_delivered_customer_date, order_purchase_timestamp)
- Delivery vs Estimated = DATEDIFF(order_delivered_customer_date, order_estimated_delivery_date)
- Delayed Orders % = COUNT(delivery > estimated) / COUNT(orders) * 100
- Order Approval Time = DATEDIFF(order_approved_at, order_purchase_timestamp)
- Shipping Time = DATEDIFF(order_delivered_customer_date, order_delivered_carrier_date)

CUSTOMER METRICS:
- Customer Lifetime Value (LTV) = SUM(gmv) per customer_unique_id
- Repeat Purchase Rate = Customers with 2+ orders / Total customers
- Average Review Score = AVG(review_score)
- NPS Proxy = (5-star reviews - 1-star reviews) / Total reviews * 100

SELLER METRICS:
- Seller GMV = SUM(price + freight) per seller_id
- Average Seller Rating = AVG(review_score) per seller
- Seller Order Volume = COUNT(DISTINCT order_id) per seller
- Top Sellers = Sellers ranked by GMV or volume

PRODUCT METRICS:
- Category Performance = GMV by product_category_name_english
- Best Sellers = Products ranked by units sold or revenue
- Category Conversion = Orders with category / Total orders
- Average Product Price = AVG(price) by category

PAYMENT METRICS:
- Payment Mix = Distribution of payment_type
- Installment Usage = AVG(payment_installments)
- Credit Card Adoption = credit_card payments / total payments
- Boleto Usage = boleto payments / total payments (Brazilian payment method)

GEOGRAPHIC METRICS:
- Revenue by State = GMV by customer_state
- Customer Concentration = COUNT(customers) by state/city
- Seller Distribution = COUNT(sellers) by state
- Cross-State Commerce = Orders where customer_state ≠ seller_state

SATISFACTION METRICS:
- Review Score Distribution = COUNT by review_score (1-5)
- Review Rate = Orders with reviews / Total delivered orders
- Negative Review Rate = (1-2 star reviews) / Total reviews
- Review Response Time = DATEDIFF(review_answer_timestamp, review_creation_date)
"""

OLIST_ANALYTICAL_PATTERNS = """
=== ANALYTICAL FRAMEWORKS ===

1. ORDER FUNNEL ANALYSIS
   Track orders through stages:
   - Placed (order_purchase_timestamp)
   - Approved (order_approved_at)
   - Shipped (order_delivered_carrier_date)
   - Delivered (order_delivered_customer_date)
   - Reviewed (review_creation_date)
   
   Calculate conversion and drop-off at each stage

2. DELIVERY PERFORMANCE
   Segment by:
   - On-time deliveries (delivered <= estimated)
   - Late deliveries (delivered > estimated)
   - Days late/early
   
   Analyze impact on review scores

   IMPORTANT for "atraso" questions:
   - Consider **only late deliveries** (delivered > estimated)
   - Use positive delay days: DATEDIFF(delivered, estimated) > 0
   - If no late deliveries in a segment, report as "sem atraso" instead of negative values

3. CATEGORY PERFORMANCE
   For each product_category_name_english:
   - Revenue contribution
   - Order volume
   - Average price point
   - Review scores
   - Growth trends over time

4. CUSTOMER SEGMENTATION
   RFM Analysis:
   - Recency: Days since last order
   - Frequency: Number of orders
   - Monetary: Total GMV
   
   Geographic Segmentation:
   - By state (SP, RJ, MG are major markets)
   - By city (São Paulo, Rio are key)

5. SELLER PERFORMANCE TIERS
   - Top sellers (80% of GMV)
   - Mid-tier sellers
   - Long-tail sellers
   
   Analyze by:
   - Average review score
   - Delivery performance
   - Product diversity

6. PAYMENT BEHAVIOR
   - Credit card dominance
   - Installment patterns (Brazil-specific)
   - Boleto usage (cash-based, popular in Brazil)
   - Payment method by region/income proxy

7. SEASONAL PATTERNS
   Brazilian calendar considerations:
   - Black Friday (November)
   - Christmas (December)
   - Carnaval (February/March)
   - Mother's Day (May)
   - Father's Day (August)

8. LOGISTICS EFFICIENCY
   - Same-state vs cross-state shipping
   - Distance impact on delivery time
   - Freight cost vs distance correlation
"""

OLIST_QUERY_EXAMPLES = """
=== COMMON QUERY PATTERNS ===

Revenue by Category (with translation):
SELECT 
    t.product_category_name_english,
    COUNT(DISTINCT oi.order_id) as orders,
    SUM(oi.price + oi.freight_value) as gmv,
    AVG(oi.price) as avg_price
FROM olist_order_items_dataset oi
JOIN olist_products_dataset p ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
GROUP BY t.product_category_name_english
ORDER BY gmv DESC
LIMIT 15;

Delivery Performance with Review Impact:
SELECT 
    CASE 
        WHEN DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) <= 0 
        THEN 'On Time' 
        ELSE 'Late' 
    END as delivery_status,
    COUNT(DISTINCT o.order_id) as orders,
    AVG(r.review_score) as avg_review,
    AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)) as avg_delivery_days
FROM olist_orders_dataset o
LEFT JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
GROUP BY delivery_status;

State with Highest Average Delay (late deliveries only):
SELECT
      c.customer_state,
      COUNT(DISTINCT o.order_id) AS late_orders,
      AVG(DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date)) AS avg_days_late
FROM olist_orders_dataset o
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
   AND o.order_delivered_customer_date > o.order_estimated_delivery_date
GROUP BY c.customer_state
ORDER BY avg_days_late DESC
LIMIT 10;

Review Comments by Category (Sample):
SELECT 
    r.review_id,
    r.review_score,
    r.review_comment_title,
    r.review_comment_message,
    c.customer_state
FROM olist_order_reviews_dataset r
JOIN olist_orders_dataset o ON r.order_id = o.order_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
JOIN olist_products_dataset p ON oi.product_id = p.product_id
JOIN product_category_name_translation t ON p.product_category_name = t.product_category_name
JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
WHERE t.product_category_name_english = 'health_beauty'
  AND r.review_comment_message IS NOT NULL 
  AND r.review_comment_message <> ''
ORDER BY r.review_score DESC, r.review_creation_date DESC
LIMIT 15;

Top States by GMV:
SELECT 
    c.customer_state,
    COUNT(DISTINCT c.customer_unique_id) as unique_customers,
    COUNT(DISTINCT o.order_id) as orders,
    SUM(oi.price + oi.freight_value) as gmv,
    AVG(r.review_score) as avg_review
FROM olist_customers_dataset c
JOIN olist_orders_dataset o ON c.customer_id = o.customer_id
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
LEFT JOIN olist_order_reviews_dataset r ON o.order_id = r.order_id
GROUP BY c.customer_state
ORDER BY gmv DESC
LIMIT 15;

Payment Method Distribution:
SELECT 
    payment_type,
    COUNT(DISTINCT order_id) as orders,
    SUM(payment_value) as total_value,
    AVG(payment_installments) as avg_installments
FROM olist_order_payments_dataset
GROUP BY payment_type
ORDER BY total_value DESC;

Monthly GMV Trend:
SELECT 
    DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') as month,
    COUNT(DISTINCT o.order_id) as orders,
    SUM(oi.price + oi.freight_value) as gmv,
    AVG(oi.price + oi.freight_value) as aov
FROM olist_orders_dataset o
JOIN olist_order_items_dataset oi ON o.order_id = oi.order_id
GROUP BY month
ORDER BY month;
"""