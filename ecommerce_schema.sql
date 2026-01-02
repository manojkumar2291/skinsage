-- E-commerce Tables for SkinSage

-- 1. Products Table (With Fulfillment Type)
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `price` decimal(10,2) NOT NULL,
  `discount_price` decimal(10,2) DEFAULT NULL,
  `stock_quantity` int DEFAULT '0',
  `image_url` varchar(255) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  
  -- NEW: Constraint for shipping/pickup
  `fulfillment_type` enum('shipping','pickup','both') DEFAULT 'both',
  
  `is_active` tinyint(1) DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Carts Table (Unchanged)
CREATE TABLE `carts` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Cart Items Table (Unchanged)
CREATE TABLE `cart_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `cart_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_cart_product` (`cart_id`,`product_id`),
  CONSTRAINT `fk_item_cart` FOREIGN KEY (`cart_id`) REFERENCES `carts` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_item_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Shop Orders Table (Unchanged)
CREATE TABLE `shop_orders` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `total_amount` decimal(10,2) NOT NULL,
  
  `order_status` enum('pending','confirmed','processing','ready_to_pickup','shipped','delivered','cancelled') DEFAULT 'pending',
  `payment_status` enum('pending','paid','failed','refunded') DEFAULT 'pending',
  
  `delivery_method` enum('shipping','pickup') DEFAULT 'shipping',
  `shipping_address` text, 
  `tracking_number` varchar(100) DEFAULT NULL,
  
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_order_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Shop Order Items Table (Unchanged)
CREATE TABLE `shop_order_items` (
  `id` int NOT NULL AUTO_INCREMENT,
  `order_id` int NOT NULL,
  `product_id` int NOT NULL,
  `quantity` int NOT NULL,
  `price_at_purchase` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_order_item_order` FOREIGN KEY (`order_id`) REFERENCES `shop_orders` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_order_item_product` FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. ALTER Existing Payments Table
/*
ALTER TABLE `payments` MODIFY `appointment_id` int NULL;
ALTER TABLE `payments` ADD `shop_order_id` int NULL;
ALTER TABLE `payments` ADD CONSTRAINT `fk_payment_shop_order` FOREIGN KEY (`shop_order_id`) REFERENCES `shop_orders` (`id`);
*/
