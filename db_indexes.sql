-- =====================================================
-- ÍNDICES RECOMENDADOS PARA OLIST E-COMMERCE DATABASE
-- Aplicar estes índices no MySQL para melhorar performance
-- =====================================================

-- ORDERS TABLE
-- Índice composto para filtros por data e status
CREATE INDEX idx_orders_timestamp_status 
ON orders(order_purchase_timestamp, order_status);

-- Índice para joins frequentes
CREATE INDEX idx_orders_customer_id 
ON orders(customer_id);

-- CUSTOMERS TABLE  
-- Índice para agregações por estado
CREATE INDEX idx_customers_state 
ON customers(customer_state);

-- Índice para identificação única de clientes
CREATE INDEX idx_customers_unique_id 
ON customers(customer_unique_id);

-- ORDER_ITEMS TABLE
-- Índice composto para aggregações de GMV
CREATE INDEX idx_order_items_product_order 
ON order_items(product_id, order_id);

-- Índice para joins com sellers
CREATE INDEX idx_order_items_seller 
ON order_items(seller_id);

-- PRODUCTS TABLE
-- Índice para joins com categorias
CREATE INDEX idx_products_category 
ON products(product_category_name);

-- ORDER_PAYMENTS TABLE
-- Índice para análise de métodos de pagamento
CREATE INDEX idx_payments_order_type 
ON order_payments(order_id, payment_type);

-- ORDER_REVIEWS TABLE
-- Índice para correlação de reviews com delivery
CREATE INDEX idx_reviews_order_score 
ON order_reviews(order_id, review_score);

-- SELLERS TABLE
-- Índice para agregações geográficas
CREATE INDEX idx_sellers_state 
ON sellers(seller_state);

-- GEOLOCATION TABLE (se usada)
-- Índice para lookups por CEP
CREATE INDEX idx_geo_zip 
ON geolocation(geolocation_zip_code_prefix);

-- =====================================================
-- VERIFICAR ÍNDICES EXISTENTES
-- =====================================================
-- Execute este comando para ver índices atuais:
-- SHOW INDEX FROM orders;
-- SHOW INDEX FROM order_items;
-- SHOW INDEX FROM customers;
-- etc.

-- =====================================================
-- ESTATÍSTICAS E MANUTENÇÃO
-- =====================================================
-- Atualizar estatísticas das tabelas (executar mensalmente):
-- ANALYZE TABLE orders, order_items, customers, products, sellers, order_payments, order_reviews;

-- =====================================================
-- QUERY OPTIMIZATION TIPS
-- =====================================================
-- 1. Sempre use LIMIT em queries
-- 2. Filtre por data (order_purchase_timestamp >= '2017-01-01')
-- 3. Use EXPLAIN para verificar plano de execução
-- 4. Evite SELECT * (especifique colunas necessárias)
-- 5. Use índices compostos quando filtrar por múltiplas colunas
