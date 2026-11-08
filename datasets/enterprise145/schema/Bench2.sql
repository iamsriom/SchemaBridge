-- Schema for database: Bench2

Alphabetical list of products
;


CREATE TABLE `Categories` (
  `CategoryID` int(11) NOT NULL AUTO_INCREMENT,
  `CategoryName` varchar(15) NOT NULL,
  `Description` mediumtext DEFAULT NULL,
  `Picture` longblob DEFAULT NULL,
  PRIMARY KEY (`CategoryID`),
  KEY `Categories_CategoryName` (`CategoryName`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `CustomerCustomerDemo` (
  `CustomerID` varchar(5) NOT NULL,
  `CustomerTypeID` varchar(10) NOT NULL,
  PRIMARY KEY (`CustomerID`,`CustomerTypeID`),
  KEY `FK_CustomerCustomerDemo` (`CustomerTypeID`),
  CONSTRAINT `FK_CustomerCustomerDemo` FOREIGN KEY (`CustomerTypeID`) REFERENCES `CustomerDemographics` (`CustomerTypeID`),
  CONSTRAINT `FK_CustomerCustomerDemo_Customers` FOREIGN KEY (`CustomerID`) REFERENCES `Customers` (`CustomerID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `CustomerDemographics` (
  `CustomerTypeID` varchar(10) NOT NULL,
  `CustomerDesc` mediumtext DEFAULT NULL,
  PRIMARY KEY (`CustomerTypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `EmployeeTerritories` (
  `EmployeeID` int(11) NOT NULL,
  `TerritoryID` varchar(20) NOT NULL,
  PRIMARY KEY (`EmployeeID`,`TerritoryID`),
  KEY `FK_EmployeeTerritories_Territories` (`TerritoryID`),
  CONSTRAINT `FK_EmployeeTerritories_Employees` FOREIGN KEY (`EmployeeID`) REFERENCES `Employees` (`EmployeeID`),
  CONSTRAINT `FK_EmployeeTerritories_Territories` FOREIGN KEY (`TerritoryID`) REFERENCES `Territories` (`TerritoryID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `Region` (
  `RegionID` int(11) NOT NULL,
  `RegionDescription` varchar(50) NOT NULL,
  PRIMARY KEY (`RegionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `Shippers` (
  `ShipperID` int(11) NOT NULL AUTO_INCREMENT,
  `CompanyName` varchar(40) NOT NULL,
  `Phone` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`ShipperID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `Territories` (
  `TerritoryID` varchar(20) NOT NULL,
  `TerritoryDescription` varchar(50) NOT NULL,
  `RegionID` int(11) NOT NULL,
  PRIMARY KEY (`TerritoryID`),
  KEY `FK_Territories_Region` (`RegionID`),
  CONSTRAINT `FK_Territories_Region` FOREIGN KEY (`RegionID`) REFERENCES `Region` (`RegionID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `nesreca` (
  `id_nesreca` char(6) NOT NULL,
  `klas_nesreca` char(1) NOT NULL,
  `upravna_enota` char(4) NOT NULL,
  `cas_nesreca` datetime NOT NULL,
  `naselje_ali_izven` char(1) NOT NULL,
  `kategorija_cesta` char(1) DEFAULT NULL,
  `oznaka_cesta_ali_naselje` char(5) NOT NULL,
  `tekst_cesta_ali_naselje` varchar(25) NOT NULL,
  `oznaka_odsek_ali_ulica` char(5) NOT NULL,
  `tekst_odsek_ali_ulica` varchar(25) NOT NULL,
  `stacionazna_ali_hisna_st` varchar(9) DEFAULT NULL,
  `opis_prizorisce` char(1) NOT NULL,
  `vzrok_nesreca` char(2) NOT NULL,
  `tip_nesreca` char(2) NOT NULL,
  `vreme_nesreca` char(1) NOT NULL,
  `stanje_promet` char(1) NOT NULL,
  `stanje_vozisce` char(2) NOT NULL,
  `stanje_povrsina_vozisce` char(2) NOT NULL,
  `x` int(11) DEFAULT NULL,
  `y` int(11) DEFAULT NULL,
  `x_wgs84` double DEFAULT NULL,
  `y_wgs84` double DEFAULT NULL,
  PRIMARY KEY (`id_nesreca`),
  KEY `nesreca_cas_nesreca_idx` (`cas_nesreca`),
  KEY `nesreca_pos_idx` (`x`,`y`),
  KEY `nesreca_pos_wgs_84` (`x_wgs84`,`y_wgs84`),
  KEY `upravna_enota` (`upravna_enota`),
  CONSTRAINT `nesreca_ibfk_1` FOREIGN KEY (`upravna_enota`) REFERENCES `upravna_enota` (`id_upravna_enota`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `oseba` (
  `id_nesreca` char(6) NOT NULL,
  `povzrocitelj_ali_udelezenec` char(1) DEFAULT NULL,
  `starost` tinyint(3) unsigned DEFAULT NULL,
  `spol` char(1) DEFAULT NULL,
  `upravna_enota` char(4) NOT NULL,
  `drzavljanstvo` char(3) NOT NULL,
  `poskodba` char(1) DEFAULT NULL,
  `vrsta_udelezenca` char(2) DEFAULT NULL,
  `varnostni_pas_ali_celada` char(1) DEFAULT NULL,
  `vozniski_staz_LL` tinyint(3) unsigned DEFAULT NULL,
  `vozniski_staz_MM` tinyint(3) unsigned DEFAULT NULL,
  `alkotest` decimal(3,2) DEFAULT NULL,
  `strokovni_pregled` decimal(3,2) DEFAULT NULL,
  `starost_d` char(1) DEFAULT NULL,
  `vozniski_staz_d` char(1) DEFAULT NULL,
  `alkotest_d` char(1) DEFAULT NULL,
  `strokovni_pregled_d` char(1) DEFAULT NULL,
  KEY `oseba_id_nesreca` (`id_nesreca`),
  KEY `upravna_enota` (`upravna_enota`),
  CONSTRAINT `oseba_ibfk_1` FOREIGN KEY (`id_nesreca`) REFERENCES `nesreca` (`id_nesreca`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `oseba_ibfk_2` FOREIGN KEY (`upravna_enota`) REFERENCES `upravna_enota` (`id_upravna_enota`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `upravna_enota` (
  `id_upravna_enota` char(4) NOT NULL,
  `ime_upravna_enota` varchar(255) NOT NULL,
  `st_prebivalcev` int(10) unsigned DEFAULT NULL,
  `povrsina` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`id_upravna_enota`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

