-- Schema for database: ccs

CREATE TABLE `customers` (
  `CustomerID` int(11) NOT NULL,
  `Segment` varchar(255) DEFAULT NULL,
  `Currency` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CustomerID`),
  UNIQUE KEY `customer_staged_CustomerID_key` (`CustomerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gasstations` (
  `GasStationID` int(11) NOT NULL,
  `ChainID` int(11) DEFAULT NULL,
  `Country` varchar(255) DEFAULT NULL,
  `Segment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`GasStationID`),
  UNIQUE KEY `gasstations_GasStationID_key` (`GasStationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `products` (
  `ProductID` int(11) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ProductID`),
  UNIQUE KEY `products_ProductID_key` (`ProductID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `transactions` (
  `Date` date DEFAULT NULL,
  `Time` time DEFAULT NULL,
  `CustomerID` int(11) DEFAULT NULL,
  `CardID` int(11) DEFAULT NULL,
  `GasStationID` int(11) DEFAULT NULL,
  `ProductID` int(11) DEFAULT NULL,
  `Amount` int(11) DEFAULT NULL,
  `Price` decimal(12,2) DEFAULT NULL,
  KEY `transactions_large_staged_CustomerID_fkey` (`CustomerID`),
  KEY `transactions_large_staged_GasStationID_fkey` (`GasStationID`),
  KEY `transactions_large_staged_ProductID_fkey` (`ProductID`),
  CONSTRAINT `transactions_large_staged_CustomerID_fkey` FOREIGN KEY (`CustomerID`) REFERENCES `customers` (`CustomerID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transactions_large_staged_GasStationID_fkey` FOREIGN KEY (`GasStationID`) REFERENCES `gasstations` (`GasStationID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transactions_large_staged_ProductID_fkey` FOREIGN KEY (`ProductID`) REFERENCES `products` (`ProductID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `transactions_1k` (
  `TransactionID` int(11) NOT NULL AUTO_INCREMENT,
  `Date` date DEFAULT NULL,
  `Time` time DEFAULT NULL,
  `CustomerID` int(11) DEFAULT NULL,
  `CardID` int(11) DEFAULT NULL,
  `GasStationID` int(11) DEFAULT NULL,
  `ProductID` int(11) DEFAULT NULL,
  `Amount` int(11) DEFAULT NULL,
  `Price` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`TransactionID`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `yearmonth` (
  `CustomerID` int(11) NOT NULL,
  `Date` int(11) NOT NULL,
  `Consumption` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`CustomerID`,`Date`),
  CONSTRAINT `yearmonth_staged_CustomerID_fkey` FOREIGN KEY (`CustomerID`) REFERENCES `customers` (`CustomerID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

