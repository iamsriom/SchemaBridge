-- Schema for database: northwind

Alphabetical list of products
;


CREATE TABLE `Categories` (
  `CategoryID` int(11) NOT NULL AUTO_INCREMENT,
  `CategoryName` varchar(15) NOT NULL,
  `Description` mediumtext DEFAULT NULL,
  `Picture` longblob DEFAULT NULL,
  PRIMARY KEY (`CategoryID`),
  KEY `Categories_CategoryName` (`CategoryName`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


Category Sales for 1997
;


Current Product List
;


Customer and Suppliers by City
;


CREATE TABLE `CustomerCustomerDemo` (
  `CustomerID` varchar(5) NOT NULL,
  `CustomerTypeID` varchar(10) NOT NULL,
  PRIMARY KEY (`CustomerID`,`CustomerTypeID`),
  KEY `FK_CustomerCustomerDemo` (`CustomerTypeID`),
  CONSTRAINT `FK_CustomerCustomerDemo` FOREIGN KEY (`CustomerTypeID`) REFERENCES `CustomerDemographics` (`CustomerTypeID`),
  CONSTRAINT `FK_CustomerCustomerDemo_Customers` FOREIGN KEY (`CustomerID`) REFERENCES `Customers` (`CustomerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `CustomerDemographics` (
  `CustomerTypeID` varchar(10) NOT NULL,
  `CustomerDesc` mediumtext DEFAULT NULL,
  PRIMARY KEY (`CustomerTypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Customers` (
  `CustomerID` varchar(5) NOT NULL,
  `CompanyName` varchar(40) NOT NULL,
  `ContactName` varchar(30) DEFAULT NULL,
  `ContactTitle` varchar(30) DEFAULT NULL,
  `Address` varchar(60) DEFAULT NULL,
  `City` varchar(15) DEFAULT NULL,
  `Region` varchar(15) DEFAULT NULL,
  `PostalCode` varchar(10) DEFAULT NULL,
  `Country` varchar(15) DEFAULT NULL,
  `Phone` varchar(24) DEFAULT NULL,
  `Fax` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`CustomerID`),
  KEY `Customers_City` (`City`),
  KEY `Customers_CompanyName` (`CompanyName`),
  KEY `Customers_PostalCode` (`PostalCode`),
  KEY `Customers_Region` (`Region`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `EmployeeTerritories` (
  `EmployeeID` int(11) NOT NULL,
  `TerritoryID` varchar(20) NOT NULL,
  PRIMARY KEY (`EmployeeID`,`TerritoryID`),
  KEY `FK_EmployeeTerritories_Territories` (`TerritoryID`),
  CONSTRAINT `FK_EmployeeTerritories_Employees` FOREIGN KEY (`EmployeeID`) REFERENCES `Employees` (`EmployeeID`),
  CONSTRAINT `FK_EmployeeTerritories_Territories` FOREIGN KEY (`TerritoryID`) REFERENCES `Territories` (`TerritoryID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Employees` (
  `EmployeeID` int(11) NOT NULL AUTO_INCREMENT,
  `LastName` varchar(20) NOT NULL,
  `FirstName` varchar(10) NOT NULL,
  `Title` varchar(30) DEFAULT NULL,
  `TitleOfCourtesy` varchar(25) DEFAULT NULL,
  `BirthDate` datetime DEFAULT NULL,
  `HireDate` datetime DEFAULT NULL,
  `Address` varchar(60) DEFAULT NULL,
  `City` varchar(15) DEFAULT NULL,
  `Region` varchar(15) DEFAULT NULL,
  `PostalCode` varchar(10) DEFAULT NULL,
  `Country` varchar(15) DEFAULT NULL,
  `HomePhone` varchar(24) DEFAULT NULL,
  `Extension` varchar(4) DEFAULT NULL,
  `Photo` longblob DEFAULT NULL,
  `Notes` mediumtext NOT NULL,
  `ReportsTo` int(11) DEFAULT NULL,
  `PhotoPath` varchar(255) DEFAULT NULL,
  `Salary` float DEFAULT NULL,
  PRIMARY KEY (`EmployeeID`),
  KEY `FK_Employees_Employees` (`ReportsTo`),
  KEY `Employees_LastName` (`LastName`),
  KEY `Employees_PostalCode` (`PostalCode`),
  CONSTRAINT `FK_Employees_Employees` FOREIGN KEY (`ReportsTo`) REFERENCES `Employees` (`EmployeeID`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


Invoices
;


CREATE TABLE `Order Details` (
  `OrderID` int(11) NOT NULL,
  `ProductID` int(11) NOT NULL,
  `UnitPrice` decimal(10,4) NOT NULL DEFAULT 0.0000,
  `Quantity` smallint(2) NOT NULL DEFAULT 1,
  `Discount` double(8,0) NOT NULL DEFAULT 0,
  PRIMARY KEY (`OrderID`,`ProductID`),
  KEY `FK_Order_Details_Products` (`ProductID`),
  CONSTRAINT `FK_Order_Details_Orders` FOREIGN KEY (`OrderID`) REFERENCES `Orders` (`OrderID`),
  CONSTRAINT `FK_Order_Details_Products` FOREIGN KEY (`ProductID`) REFERENCES `Products` (`ProductID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


Order Details Extended
;


Order Subtotals
;


CREATE TABLE `Orders` (
  `OrderID` int(11) NOT NULL AUTO_INCREMENT,
  `CustomerID` varchar(5) DEFAULT NULL,
  `EmployeeID` int(11) DEFAULT NULL,
  `OrderDate` datetime DEFAULT NULL,
  `RequiredDate` datetime DEFAULT NULL,
  `ShippedDate` datetime DEFAULT NULL,
  `ShipVia` int(11) DEFAULT NULL,
  `Freight` decimal(10,4) DEFAULT 0.0000,
  `ShipName` varchar(40) DEFAULT NULL,
  `ShipAddress` varchar(60) DEFAULT NULL,
  `ShipCity` varchar(15) DEFAULT NULL,
  `ShipRegion` varchar(15) DEFAULT NULL,
  `ShipPostalCode` varchar(10) DEFAULT NULL,
  `ShipCountry` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`OrderID`),
  KEY `FK_Orders_Customers` (`CustomerID`),
  KEY `FK_Orders_Employees` (`EmployeeID`),
  KEY `FK_Orders_Shippers` (`ShipVia`),
  KEY `Orders_OrderDate` (`OrderDate`),
  KEY `Orders_ShippedDate` (`ShippedDate`),
  KEY `Orders_ShipPostalCode` (`ShipPostalCode`),
  CONSTRAINT `FK_Orders_Customers` FOREIGN KEY (`CustomerID`) REFERENCES `Customers` (`CustomerID`),
  CONSTRAINT `FK_Orders_Employees` FOREIGN KEY (`EmployeeID`) REFERENCES `Employees` (`EmployeeID`),
  CONSTRAINT `FK_Orders_Shippers` FOREIGN KEY (`ShipVia`) REFERENCES `Shippers` (`ShipperID`)
) ENGINE=InnoDB AUTO_INCREMENT=11078 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


Orders Qry
;


Product Sales for 1997
;


CREATE TABLE `Products` (
  `ProductID` int(11) NOT NULL AUTO_INCREMENT,
  `ProductName` varchar(40) NOT NULL,
  `SupplierID` int(11) DEFAULT NULL,
  `CategoryID` int(11) DEFAULT NULL,
  `QuantityPerUnit` varchar(20) DEFAULT NULL,
  `UnitPrice` decimal(10,4) DEFAULT 0.0000,
  `UnitsInStock` smallint(2) DEFAULT 0,
  `UnitsOnOrder` smallint(2) DEFAULT 0,
  `ReorderLevel` smallint(2) DEFAULT 0,
  `Discontinued` tinyint(1) NOT NULL,
  PRIMARY KEY (`ProductID`),
  KEY `FK_Products_Categories` (`CategoryID`),
  KEY `FK_Products_Suppliers` (`SupplierID`),
  KEY `Products_ProductName` (`ProductName`),
  CONSTRAINT `FK_Products_Categories` FOREIGN KEY (`CategoryID`) REFERENCES `Categories` (`CategoryID`),
  CONSTRAINT `FK_Products_Suppliers` FOREIGN KEY (`SupplierID`) REFERENCES `Suppliers` (`SupplierID`)
) ENGINE=InnoDB AUTO_INCREMENT=78 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


Products Above Average Price
;


Products by Category
;


Quarterly Orders
;


CREATE TABLE `Region` (
  `RegionID` int(11) NOT NULL,
  `RegionDescription` varchar(50) NOT NULL,
  PRIMARY KEY (`RegionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


Sales Totals by Amount
;


Sales by Category
;


CREATE TABLE `Shippers` (
  `ShipperID` int(11) NOT NULL AUTO_INCREMENT,
  `CompanyName` varchar(40) NOT NULL,
  `Phone` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`ShipperID`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


Summary of Sales by Quarter
;


Summary of Sales by Year
;


CREATE TABLE `Suppliers` (
  `SupplierID` int(11) NOT NULL AUTO_INCREMENT,
  `CompanyName` varchar(40) NOT NULL,
  `ContactName` varchar(30) DEFAULT NULL,
  `ContactTitle` varchar(30) DEFAULT NULL,
  `Address` varchar(60) DEFAULT NULL,
  `City` varchar(15) DEFAULT NULL,
  `Region` varchar(15) DEFAULT NULL,
  `PostalCode` varchar(10) DEFAULT NULL,
  `Country` varchar(15) DEFAULT NULL,
  `Phone` varchar(24) DEFAULT NULL,
  `Fax` varchar(24) DEFAULT NULL,
  `HomePage` mediumtext DEFAULT NULL,
  PRIMARY KEY (`SupplierID`),
  KEY `Suppliers_CompanyName` (`CompanyName`),
  KEY `Suppliers_PostalCode` (`PostalCode`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Territories` (
  `TerritoryID` varchar(20) NOT NULL,
  `TerritoryDescription` varchar(50) NOT NULL,
  `RegionID` int(11) NOT NULL,
  PRIMARY KEY (`TerritoryID`),
  KEY `FK_Territories_Region` (`RegionID`),
  CONSTRAINT `FK_Territories_Region` FOREIGN KEY (`RegionID`) REFERENCES `Region` (`RegionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

