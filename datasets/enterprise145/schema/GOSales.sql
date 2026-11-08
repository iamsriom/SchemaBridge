-- Schema for database: GOSales

CREATE TABLE `go_1k` (
  `Retailer code` int(11) NOT NULL,
  `Product number` int(11) NOT NULL,
  `Date` date NOT NULL,
  `Quantity` int(11) NOT NULL,
  PRIMARY KEY (`Retailer code`,`Product number`,`Date`) USING BTREE,
  KEY `Product number` (`Product number`) USING BTREE,
  KEY `Retailer code` (`Retailer code`,`Product number`) USING BTREE,
  CONSTRAINT `go_1k_ibfk_1` FOREIGN KEY (`Retailer code`) REFERENCES `go_retailers` (`Retailer code`),
  CONSTRAINT `go_1k_ibfk_2` FOREIGN KEY (`Product number`) REFERENCES `go_products` (`Product number`),
  CONSTRAINT `go_1k_ibfk_3` FOREIGN KEY (`Retailer code`, `Product number`) REFERENCES `go_daily_sales` (`Retailer code`, `Product number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `go_daily_sales` (
  `Retailer code` int(11) NOT NULL,
  `Product number` int(11) NOT NULL,
  `Order method code` int(11) NOT NULL,
  `Date` date NOT NULL,
  `Quantity` int(11) NOT NULL,
  `Unit price` decimal(10,2) NOT NULL,
  `Unit sale price` decimal(10,2) NOT NULL,
  KEY `Order method code` (`Order method code`) USING BTREE,
  KEY `Retailer code` (`Retailer code`,`Product number`) USING BTREE,
  KEY `Product number` (`Product number`) USING BTREE,
  CONSTRAINT `go_daily_sales_ibfk_3` FOREIGN KEY (`Order method code`) REFERENCES `go_methods` (`Order method code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `go_methods` (
  `Order method code` int(11) NOT NULL,
  `Order method type` varchar(255) NOT NULL,
  PRIMARY KEY (`Order method code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `go_products` (
  `Product number` int(11) NOT NULL,
  `Product line` varchar(255) NOT NULL,
  `Product type` varchar(255) NOT NULL,
  `Product` varchar(255) NOT NULL,
  `Product brand` varchar(255) NOT NULL,
  `Product color` varchar(255) NOT NULL,
  `Unit cost` decimal(10,2) NOT NULL,
  `Unit price` decimal(10,2) NOT NULL,
  PRIMARY KEY (`Product number`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `go_retailers` (
  `Retailer code` int(11) NOT NULL,
  `Retailer name` varchar(255) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Country` varchar(255) NOT NULL,
  PRIMARY KEY (`Retailer code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

