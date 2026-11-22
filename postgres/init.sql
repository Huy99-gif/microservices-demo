-- Moi service mot user + mot database rieng (chi chay lan dau khi volume rong)
CREATE USER user_svc WITH PASSWORD 'user_pass';
CREATE DATABASE users_db OWNER user_svc;

CREATE USER product_svc WITH PASSWORD 'product_pass';
CREATE DATABASE products_db OWNER product_svc;
