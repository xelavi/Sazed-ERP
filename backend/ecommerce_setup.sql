-- Activa el Webservice de PrestaShop y crea una API key para el ERP.
-- Idempotente: se puede reejecutar sin duplicar.

SET @apikey = '2323678FEAE34363501AE3461F0DC6F4';

-- 1. Activar el webservice
DELETE FROM ps_configuration WHERE name IN ('PS_WEBSERVICE', 'PS_WEBSERVICE_CGI_HOST');
INSERT INTO ps_configuration (name, value, date_add, date_upd) VALUES ('PS_WEBSERVICE', '1', NOW(), NOW());
INSERT INTO ps_configuration (name, value, date_add, date_upd) VALUES ('PS_WEBSERVICE_CGI_HOST', '1', NOW(), NOW());

-- 2. Limpiar cuenta previa con esa key (idempotencia)
DELETE p FROM ps_webservice_permission p
  JOIN ps_webservice_account a ON a.id_webservice_account = p.id_webservice_account
  WHERE a.`key` = @apikey;
DELETE s FROM ps_webservice_account_shop s
  JOIN ps_webservice_account a ON a.id_webservice_account = s.id_webservice_account
  WHERE a.`key` = @apikey;
DELETE FROM ps_webservice_account WHERE `key` = @apikey;

-- 3. Crear la cuenta
INSERT INTO ps_webservice_account (`key`, description, class_name, is_module, active)
  VALUES (@apikey, 'ERP TFG sync', 'WebserviceRequest', 0, 1);
SET @aid = LAST_INSERT_ID();

-- 4. Vincular a la tienda 1
INSERT INTO ps_webservice_account_shop (id_webservice_account, id_shop) VALUES (@aid, 1);

-- 5. Permisos completos sobre los recursos que usará la sincronización
INSERT INTO ps_webservice_permission (resource, method, id_webservice_account)
SELECT r.resource, m.method, @aid
FROM (
  SELECT 'products' AS resource UNION SELECT 'categories' UNION SELECT 'customers'
  UNION SELECT 'addresses' UNION SELECT 'orders' UNION SELECT 'order_details'
  UNION SELECT 'order_states' UNION SELECT 'order_histories'
  UNION SELECT 'stock_availables' UNION SELECT 'images' UNION SELECT 'combinations'
  UNION SELECT 'manufacturers' UNION SELECT 'tax_rule_groups' UNION SELECT 'taxes'
  UNION SELECT 'product_options' UNION SELECT 'product_option_values'
  UNION SELECT 'languages' UNION SELECT 'currencies' UNION SELECT 'countries'
  UNION SELECT 'carriers' UNION SELECT 'price_rules'
) r
CROSS JOIN (
  SELECT 'GET' AS method UNION SELECT 'POST' UNION SELECT 'PUT'
  UNION SELECT 'DELETE' UNION SELECT 'HEAD'
) m;

SELECT 'account' AS step, id_webservice_account, `key`, active
  FROM ps_webservice_account WHERE `key` = @apikey;
SELECT 'permissions' AS step, COUNT(*) AS total
  FROM ps_webservice_permission WHERE id_webservice_account = @aid;
