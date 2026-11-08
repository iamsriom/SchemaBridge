-- Schema for database: Bench

CREATE TABLE `ADDRESS` (
  `ADDRESSID` int(11) NOT NULL COMMENT 'Primary key for Address records.',
  `ADDRESSLINE1` varchar(60) NOT NULL COMMENT 'First street address line.',
  `ADDRESSLINE2` varchar(60) DEFAULT NULL COMMENT 'Second street address line.',
  `CITY` varchar(30) NOT NULL COMMENT 'Name of the city.',
  `STATEPROVINCEID` int(11) NOT NULL COMMENT 'Unique identification number for the state or province. Foreign key to StateProvince table.',
  `POSTALCODE` varchar(15) NOT NULL COMMENT 'Postal code for the street address.',
  `SPATIALLOCATION` geometry DEFAULT NULL COMMENT 'Latitude and longitude of this address.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ADDRESSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Street address information for customers, employees, and vendors.'
;


CREATE TABLE `ADDRESSTYPE` (
  `ADDRESSTYPEID` int(11) NOT NULL COMMENT 'Primary key for AddressType records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Address type description. For example, Billing, Home, or Shipping.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ADDRESSTYPEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Types of addresses stored in the Address table. '
;


CREATE TABLE `ALL_PLUGINS` (
  `PLUGIN_NAME` varchar(64) NOT NULL DEFAULT '',
  `PLUGIN_VERSION` varchar(20) NOT NULL DEFAULT '',
  `PLUGIN_STATUS` varchar(16) NOT NULL DEFAULT '',
  `PLUGIN_TYPE` varchar(80) NOT NULL DEFAULT '',
  `PLUGIN_TYPE_VERSION` varchar(20) NOT NULL DEFAULT '',
  `PLUGIN_LIBRARY` varchar(64) DEFAULT NULL,
  `PLUGIN_LIBRARY_VERSION` varchar(20) DEFAULT NULL,
  `PLUGIN_AUTHOR` varchar(64) DEFAULT NULL,
  `PLUGIN_DESCRIPTION` longtext DEFAULT NULL,
  `PLUGIN_LICENSE` varchar(80) NOT NULL DEFAULT '',
  `LOAD_OPTION` varchar(64) NOT NULL DEFAULT '',
  `PLUGIN_MATURITY` varchar(12) NOT NULL DEFAULT '',
  `PLUGIN_AUTH_VERSION` varchar(80) DEFAULT NULL
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1208488 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `APPLICABLE_ROLES` (
  `GRANTEE` varchar(190) NOT NULL DEFAULT '',
  `ROLE_NAME` varchar(128) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=2216185 ROW_FORMAT=FIXED
;


CREATE TABLE `AWBUILDVERSION` (
  `SYSTEMINFORMATIONID` tinyint(3) unsigned NOT NULL COMMENT 'Primary key for AWBuildVersion records.',
  `DATABASE VERSION` varchar(25) NOT NULL COMMENT 'Version number of the database in 9.yy.mm.dd.00 format.',
  `VERSIONDATE` datetime NOT NULL COMMENT 'Date and time the record was last updated.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SYSTEMINFORMATIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Current version number of the AdventureWorks 2014 sample database. '
;


CREATE TABLE `AWBuildVersion` (
  `SystemInformationID` tinyint(3) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Primary key for AWBuildVersion records.',
  `Database Version` varchar(25) NOT NULL COMMENT 'Version number of the database in 9.yy.mm.dd.00 format.',
  `VersionDate` datetime NOT NULL COMMENT 'Date and time the record was last updated.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SystemInformationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Current version number of the AdventureWorks 2014 sample database. '
;


CREATE TABLE `Address` (
  `AddressID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for Address records.',
  `AddressLine1` varchar(60) NOT NULL COMMENT 'First street address line.',
  `AddressLine2` varchar(60) DEFAULT NULL COMMENT 'Second street address line.',
  `City` varchar(30) NOT NULL COMMENT 'Name of the city.',
  `StateProvinceID` int(11) NOT NULL COMMENT 'Unique identification number for the state or province. Foreign key to StateProvince table.',
  `PostalCode` varchar(15) NOT NULL COMMENT 'Postal code for the street address.',
  `SpatialLocation` geometry DEFAULT NULL COMMENT 'Latitude and longitude of this address.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`AddressID`),
  UNIQUE KEY `AK_Address_rowguid` (`rowguid`),
  UNIQUE KEY `IX_Address_AddressLine1_AddressLine2_City_StateProvinceID_Post1` (`AddressLine1`,`AddressLine2`,`City`,`StateProvinceID`,`PostalCode`),
  KEY `IX_Address_StateProvinceID` (`StateProvinceID`),
  KEY `GUID_Address` (`rowguid`),
  CONSTRAINT `FK_Address_StateProvince_StateProvinceID` FOREIGN KEY (`StateProvinceID`) REFERENCES `StateProvince` (`StateProvinceID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Street address information for customers, employees, and vendors.'
;


CREATE TABLE `AddressType` (
  `AddressTypeID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for AddressType records.',
  `Name` varchar(100) NOT NULL COMMENT 'Address type description. For example, Billing, Home, or Shipping.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`AddressTypeID`),
  UNIQUE KEY `AK_AddressType_rowguid` (`rowguid`),
  UNIQUE KEY `AK_AddressType_Name` (`Name`),
  KEY `GUID_AddressType` (`rowguid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Types of addresses stored in the Address table. '
;


CREATE TABLE `Attributes` (
  `attribute_id` int(11) NOT NULL AUTO_INCREMENT,
  `attribute_name` varchar(280) DEFAULT NULL,
  PRIMARY KEY (`attribute_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `BILLOFMATERIALS` (
  `BILLOFMATERIALSID` int(11) NOT NULL COMMENT 'Primary key for BillOfMaterials records.',
  `PRODUCTASSEMBLYID` int(11) DEFAULT NULL COMMENT 'Parent product identification number. Foreign key to Product.ProductID.',
  `COMPONENTID` int(11) NOT NULL COMMENT 'Component identification number. Foreign key to Product.ProductID.',
  `STARTDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date the component started being used in the assembly item.',
  `ENDDATE` datetime DEFAULT NULL COMMENT 'Date the component stopped being used in the assembly item.',
  `UNITMEASURECODE` char(3) NOT NULL COMMENT 'Standard code identifying the unit of measure for the quantity.',
  `BOMLEVEL` smallint(6) NOT NULL COMMENT 'Indicates the depth the component is from its parent (AssemblyID).',
  `PERASSEMBLYQTY` decimal(8,2) NOT NULL DEFAULT 1.00 COMMENT 'Quantity of the component needed to create the assembly.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BILLOFMATERIALSID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Items required to make bicycles and bicycle subassemblies. It identifies the heirarchical relationship between a parent product and its components.'
;


CREATE TABLE `BUSINESSENTITY` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key for all customers, vendors, and employees.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Source of the ID that connects vendors, customers, and employees with address and contact information.'
;


CREATE TABLE `BUSINESSENTITYADDRESS` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to BusinessEntity.BusinessEntityID.',
  `ADDRESSID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Address.AddressID.',
  `ADDRESSTYPEID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to AddressType.AddressTypeID.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`ADDRESSID`,`ADDRESSTYPEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping customers, vendors, and employees to their addresses.'
;


CREATE TABLE `BUSINESSENTITYCONTACT` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to BusinessEntity.BusinessEntityID.',
  `PERSONID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Person.BusinessEntityID.',
  `CONTACTTYPEID` int(11) NOT NULL COMMENT 'Primary key.  Foreign key to ContactType.ContactTypeID.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`PERSONID`,`CONTACTTYPEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping stores, vendors, and employees to people'
;


CREATE TABLE `BillOfMaterials` (
  `BillOfMaterialsID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for BillOfMaterials records.',
  `ProductAssemblyID` int(11) DEFAULT NULL COMMENT 'Parent product identification number. Foreign key to Product.ProductID.',
  `ComponentID` int(11) NOT NULL COMMENT 'Component identification number. Foreign key to Product.ProductID.',
  `StartDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date the component started being used in the assembly item.',
  `EndDate` datetime DEFAULT NULL COMMENT 'Date the component stopped being used in the assembly item.',
  `UnitMeasureCode` char(3) NOT NULL COMMENT 'Standard code identifying the unit of measure for the quantity.',
  `BOMLevel` smallint(6) NOT NULL COMMENT 'Indicates the depth the component is from its parent (AssemblyID).',
  `PerAssemblyQty` decimal(8,2) NOT NULL DEFAULT 1.00 COMMENT 'Quantity of the component needed to create the assembly.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BillOfMaterialsID`),
  UNIQUE KEY `AK_BillOfMaterials_ProductAssemblyID_ComponentID_StartDate` (`ProductAssemblyID`,`ComponentID`,`StartDate`),
  KEY `IX_BillOfMaterials_UnitMeasureCode` (`UnitMeasureCode`),
  KEY `FK_BillOfMaterials_Product_ComponentID` (`ComponentID`),
  CONSTRAINT `FK_BillOfMaterials_Product_ComponentID` FOREIGN KEY (`ComponentID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_BillOfMaterials_Product_ProductAssemblyID` FOREIGN KEY (`ProductAssemblyID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_BillOfMaterials_UnitMeasure_UnitMeasureCode` FOREIGN KEY (`UnitMeasureCode`) REFERENCES `UnitMeasure` (`UnitMeasureCode`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Items required to make bicycles and bicycle subassemblies. It identifies the heirarchical relationship between a parent product and its components.'
;


CREATE TABLE `Business` (
  `business_id` varchar(30) NOT NULL DEFAULT '',
  `full_address` varchar(200) DEFAULT NULL,
  `active` varchar(10) DEFAULT NULL,
  `categories` varchar(200) DEFAULT NULL,
  `city` varchar(30) DEFAULT NULL,
  `review_count` int(11) DEFAULT NULL,
  `business_name` varchar(100) DEFAULT NULL,
  `neighborhoods` varchar(200) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `state` varchar(5) DEFAULT NULL,
  `stars` double DEFAULT NULL,
  PRIMARY KEY (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `BusinessEntity` (
  `BusinessEntityID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for all customers, vendors, and employees.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`),
  UNIQUE KEY `AK_BusinessEntity_rowguid` (`rowguid`),
  KEY `GUID_BusinessEntity` (`rowguid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Source of the ID that connects vendors, customers, and employees with address and contact information.'
;


CREATE TABLE `BusinessEntityAddress` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to BusinessEntity.BusinessEntityID.',
  `AddressID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Address.AddressID.',
  `AddressTypeID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to AddressType.AddressTypeID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`AddressID`,`AddressTypeID`),
  UNIQUE KEY `AK_BusinessEntityAddress_rowguid` (`rowguid`),
  KEY `IX_BusinessEntityAddress_AddressID` (`AddressID`),
  KEY `IX_BusinessEntityAddress_AddressTypeID` (`AddressTypeID`),
  KEY `GUID_BusinessEntityAddress` (`rowguid`),
  CONSTRAINT `FK_BusinessEntityAddress_AddressType_AddressTypeID` FOREIGN KEY (`AddressTypeID`) REFERENCES `AddressType` (`AddressTypeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_BusinessEntityAddress_Address_AddressID` FOREIGN KEY (`AddressID`) REFERENCES `Address` (`AddressID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_BusinessEntityAddress_BusinessEntity_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `BusinessEntity` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping customers, vendors, and employees to their addresses.'
;


CREATE TABLE `BusinessEntityContact` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to BusinessEntity.BusinessEntityID.',
  `PersonID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Person.BusinessEntityID.',
  `ContactTypeID` int(11) NOT NULL COMMENT 'Primary key.  Foreign key to ContactType.ContactTypeID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`PersonID`,`ContactTypeID`),
  UNIQUE KEY `AK_BusinessEntityContact_rowguid` (`rowguid`),
  KEY `IX_BusinessEntityContact_PersonID` (`PersonID`),
  KEY `IX_BusinessEntityContact_ContactTypeID` (`ContactTypeID`),
  KEY `GUID_BusinessEntityContact` (`rowguid`),
  CONSTRAINT `FK_BusinessEntityContact_BusinessEntity_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `BusinessEntity` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_BusinessEntityContact_ContactType_ContactTypeID` FOREIGN KEY (`ContactTypeID`) REFERENCES `ContactType` (`ContactTypeID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_BusinessEntityContact_Person_PersonID` FOREIGN KEY (`PersonID`) REFERENCES `Person` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping stores, vendors, and employees to people'
;


CREATE TABLE `CHARACTER_SETS` (
  `CHARACTER_SET_NAME` varchar(32) NOT NULL DEFAULT '',
  `DEFAULT_COLLATE_NAME` varchar(32) NOT NULL DEFAULT '',
  `DESCRIPTION` varchar(60) NOT NULL DEFAULT '',
  `MAXLEN` bigint(3) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=5592405 ROW_FORMAT=FIXED
;


CREATE TABLE `CLIENT_STATISTICS` (
  `CLIENT` varchar(64) NOT NULL DEFAULT '',
  `TOTAL_CONNECTIONS` bigint(21) NOT NULL DEFAULT 0,
  `CONCURRENT_CONNECTIONS` bigint(21) NOT NULL DEFAULT 0,
  `CONNECTED_TIME` bigint(21) NOT NULL DEFAULT 0,
  `BUSY_TIME` double NOT NULL DEFAULT 0,
  `CPU_TIME` double NOT NULL DEFAULT 0,
  `BYTES_RECEIVED` bigint(21) NOT NULL DEFAULT 0,
  `BYTES_SENT` bigint(21) NOT NULL DEFAULT 0,
  `BINLOG_BYTES_WRITTEN` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_READ` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_SENT` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_DELETED` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_INSERTED` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_UPDATED` bigint(21) NOT NULL DEFAULT 0,
  `SELECT_COMMANDS` bigint(21) NOT NULL DEFAULT 0,
  `UPDATE_COMMANDS` bigint(21) NOT NULL DEFAULT 0,
  `OTHER_COMMANDS` bigint(21) NOT NULL DEFAULT 0,
  `COMMIT_TRANSACTIONS` bigint(21) NOT NULL DEFAULT 0,
  `ROLLBACK_TRANSACTIONS` bigint(21) NOT NULL DEFAULT 0,
  `DENIED_CONNECTIONS` bigint(21) NOT NULL DEFAULT 0,
  `LOST_CONNECTIONS` bigint(21) NOT NULL DEFAULT 0,
  `ACCESS_DENIED` bigint(21) NOT NULL DEFAULT 0,
  `EMPTY_QUERIES` bigint(21) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=5804009 ROW_FORMAT=FIXED
;


CREATE TABLE `COLLATIONS` (
  `COLLATION_NAME` varchar(32) NOT NULL DEFAULT '',
  `CHARACTER_SET_NAME` varchar(32) NOT NULL DEFAULT '',
  `ID` bigint(11) NOT NULL DEFAULT 0,
  `IS_DEFAULT` varchar(3) NOT NULL DEFAULT '',
  `IS_COMPILED` varchar(3) NOT NULL DEFAULT '',
  `SORTLEN` bigint(3) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=9296466 ROW_FORMAT=FIXED
;


CREATE TABLE `COLLATION_CHARACTER_SET_APPLICABILITY` (
  `COLLATION_NAME` varchar(32) NOT NULL DEFAULT '',
  `CHARACTER_SET_NAME` varchar(32) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=11012736 ROW_FORMAT=FIXED
;


CREATE TABLE `COLUMNS` (
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `ORDINAL_POSITION` bigint(21) unsigned NOT NULL DEFAULT 0,
  `COLUMN_DEFAULT` longtext DEFAULT NULL,
  `IS_NULLABLE` varchar(3) NOT NULL DEFAULT '',
  `DATA_TYPE` varchar(64) NOT NULL DEFAULT '',
  `CHARACTER_MAXIMUM_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `CHARACTER_OCTET_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `NUMERIC_PRECISION` bigint(21) unsigned DEFAULT NULL,
  `NUMERIC_SCALE` bigint(21) unsigned DEFAULT NULL,
  `DATETIME_PRECISION` bigint(21) unsigned DEFAULT NULL,
  `CHARACTER_SET_NAME` varchar(32) DEFAULT NULL,
  `COLLATION_NAME` varchar(32) DEFAULT NULL,
  `COLUMN_TYPE` longtext NOT NULL,
  `COLUMN_KEY` varchar(3) NOT NULL DEFAULT '',
  `EXTRA` varchar(27) NOT NULL DEFAULT '',
  `PRIVILEGES` varchar(80) NOT NULL DEFAULT '',
  `COLUMN_COMMENT` varchar(1024) NOT NULL DEFAULT ''
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=358272 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `COLUMN_PRIVILEGES` (
  `GRANTEE` varchar(190) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=742303 ROW_FORMAT=FIXED
;


CREATE TABLE `CONTACTTYPE` (
  `CONTACTTYPEID` int(11) NOT NULL COMMENT 'Primary key for ContactType records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Contact type description.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CONTACTTYPEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the types of business entity contacts.'
;


CREATE TABLE `CONTR` (
  `ICO` int(11) NOT NULL,
  `ROKVYS` int(11) DEFAULT NULL,
  `MESVYS` int(11) DEFAULT NULL,
  `PORADK` int(11) NOT NULL,
  `ZMCHARZA` int(11) DEFAULT NULL,
  `ZMTELAKT` int(11) DEFAULT NULL,
  `AKTPOZAM` int(11) DEFAULT NULL,
  `ZMDIET` int(11) DEFAULT NULL,
  `LEKCHOL` varchar(255) DEFAULT NULL,
  `LEKTLAK` int(11) DEFAULT NULL,
  `ZMKOUR` int(11) DEFAULT NULL,
  `POCCIG` int(11) DEFAULT NULL,
  `PRACNES` int(11) DEFAULT NULL,
  `SRDCE` varchar(255) DEFAULT NULL,
  `HYPERT` varchar(255) DEFAULT NULL,
  `CEVMOZ` varchar(255) DEFAULT NULL,
  `DIAB` varchar(255) DEFAULT NULL,
  `JINAONE` int(11) DEFAULT NULL,
  `BOLHR` int(11) DEFAULT NULL,
  `BOLDK` int(11) DEFAULT NULL,
  `DUSN` int(11) DEFAULT NULL,
  `HODNSK` int(11) DEFAULT NULL,
  `HODN0` int(11) DEFAULT NULL,
  `ROK0` int(11) DEFAULT NULL,
  `HODN1` varchar(255) DEFAULT NULL,
  `ROK1` varchar(255) DEFAULT NULL,
  `HODN2` varchar(255) DEFAULT NULL,
  `ROK2` varchar(255) DEFAULT NULL,
  `HODN3` varchar(255) DEFAULT NULL,
  `ROK3` varchar(255) DEFAULT NULL,
  `HODN4` varchar(255) DEFAULT NULL,
  `ROK4` varchar(255) DEFAULT NULL,
  `HODN11` varchar(255) DEFAULT NULL,
  `ROK11` varchar(255) DEFAULT NULL,
  `HODN12` varchar(255) DEFAULT NULL,
  `ROK12` varchar(255) DEFAULT NULL,
  `HODN13` varchar(255) DEFAULT NULL,
  `ROK13` varchar(255) DEFAULT NULL,
  `HODN14` varchar(255) DEFAULT NULL,
  `ROK14` varchar(255) DEFAULT NULL,
  `HODN15` varchar(255) DEFAULT NULL,
  `ROK15` varchar(255) DEFAULT NULL,
  `HODN21` varchar(255) DEFAULT NULL,
  `ROK21` varchar(255) DEFAULT NULL,
  `HODN23` varchar(255) DEFAULT NULL,
  `ROK23` varchar(255) DEFAULT NULL,
  `HMOT` int(11) DEFAULT NULL,
  `SYST` int(11) DEFAULT NULL,
  `DIAST` int(11) DEFAULT NULL,
  `TRIC` int(11) DEFAULT NULL,
  `SUBSC` int(11) DEFAULT NULL,
  `HYPERSD` int(11) DEFAULT NULL,
  `HYPERS` int(11) DEFAULT NULL,
  `HYPERD` int(11) DEFAULT NULL,
  `HYPCHL` int(11) DEFAULT NULL,
  `HYPTGL` int(11) DEFAULT NULL,
  `CHLST` float DEFAULT NULL,
  `CHLSTMG` int(11) DEFAULT NULL,
  `TRIGL` float DEFAULT NULL,
  `TRIGLMG` int(11) DEFAULT NULL,
  `HDL` varchar(255) DEFAULT NULL,
  `HDLMG` varchar(255) DEFAULT NULL,
  `MOC` int(11) DEFAULT NULL,
  `GLYKEMIE` varchar(255) DEFAULT NULL,
  `KYSMOC` varchar(255) DEFAULT NULL,
  `LDL` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ICO`,`PORADK`),
  KEY `ICO` (`ICO`),
  CONSTRAINT `CONTR_IBFK_1` FOREIGN KEY (`ICO`) REFERENCES `ENTRY` (`ICO`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `COUNTRYREGION` (
  `COUNTRYREGIONCODE` varchar(3) NOT NULL COMMENT 'ISO standard code for countries and regions.',
  `NAME` varchar(100) NOT NULL COMMENT 'Country or region name.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`COUNTRYREGIONCODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the ISO standard codes for countries and regions.'
;


CREATE TABLE `COUNTRYREGIONCURRENCY` (
  `COUNTRYREGIONCODE` varchar(3) NOT NULL COMMENT 'ISO code for countries and regions. Foreign key to CountryRegion.CountryRegionCode.',
  `CURRENCYCODE` char(3) NOT NULL COMMENT 'ISO standard currency code. Foreign key to Currency.CurrencyCode.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`COUNTRYREGIONCODE`,`CURRENCYCODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping ISO currency codes to a country or region.'
;


CREATE TABLE `CREDITCARD` (
  `CREDITCARDID` int(11) NOT NULL COMMENT 'Primary key for CreditCard records.',
  `CARDTYPE` varchar(50) NOT NULL COMMENT 'Credit card name.',
  `CARDNUMBER` varchar(25) NOT NULL COMMENT 'Credit card number.',
  `EXPMONTH` tinyint(3) unsigned NOT NULL COMMENT 'Credit card expiration month.',
  `EXPYEAR` smallint(6) NOT NULL COMMENT 'Credit card expiration year.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CREDITCARDID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customer credit card information.'
;


CREATE TABLE `CULTURE` (
  `CULTUREID` char(6) NOT NULL COMMENT 'Primary key for Culture records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Culture description.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CULTUREID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the languages in which some AdventureWorks data is stored.'
;


CREATE TABLE `CURRENCY` (
  `CURRENCYCODE` char(3) NOT NULL COMMENT 'The ISO code for the Currency.',
  `NAME` varchar(100) NOT NULL COMMENT 'Currency name.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CURRENCYCODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing standard ISO currencies.'
;


CREATE TABLE `CURRENCYRATE` (
  `CURRENCYRATEID` int(11) NOT NULL COMMENT 'Primary key for CurrencyRate records.',
  `CURRENCYRATEDATE` datetime NOT NULL COMMENT 'Date and time the exchange rate was obtained.',
  `FROMCURRENCYCODE` char(3) NOT NULL COMMENT 'Exchange rate was converted from this currency code.',
  `TOCURRENCYCODE` char(3) NOT NULL COMMENT 'Exchange rate was converted to this currency code.',
  `AVERAGERATE` decimal(19,4) NOT NULL COMMENT 'Average exchange rate for the day.',
  `ENDOFDAYRATE` decimal(19,4) NOT NULL COMMENT 'Final exchange rate for the day.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CURRENCYRATEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Currency exchange rates.'
;


CREATE TABLE `CUSTOMER` (
  `CUSTOMERID` int(11) NOT NULL COMMENT 'Primary key.',
  `PERSONID` int(11) DEFAULT NULL COMMENT 'Foreign key to Person.BusinessEntityID',
  `STOREID` int(11) DEFAULT NULL COMMENT 'Foreign key to Store.BusinessEntityID',
  `TERRITORYID` int(11) DEFAULT NULL COMMENT 'ID of the territory in which the customer is located. Foreign key to SalesTerritory.SalesTerritoryID.',
  `ACCOUNTNUMBER` varchar(10) NOT NULL COMMENT 'Unique number identifying the customer assigned by the accounting system.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CUSTOMERID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Current customer information. Also see the Person and Store tables.'
;


CREATE TABLE `C_Customer` (
  `c_id` int(11) NOT NULL,
  `c_d_id` int(11) NOT NULL,
  `c_w_id` int(11) NOT NULL,
  `c_first` char(16) DEFAULT NULL,
  `c_middle` char(2) DEFAULT NULL,
  `c_last` char(16) DEFAULT NULL,
  `c_street_1` char(20) DEFAULT NULL,
  `c_street_2` char(20) DEFAULT NULL,
  `c_city` char(20) DEFAULT NULL,
  `c_state` char(2) DEFAULT NULL,
  `c_zip` char(9) DEFAULT NULL,
  `c_phone` char(16) DEFAULT NULL,
  `c_since` datetime DEFAULT NULL,
  `c_credit` char(2) DEFAULT NULL,
  `c_credit_lim` float DEFAULT NULL,
  `c_discount` float DEFAULT NULL,
  `c_balance` float DEFAULT NULL,
  `c_ytd_payment` float DEFAULT NULL,
  `c_payment_cnt` int(11) DEFAULT NULL,
  `c_delivery_cnt` int(11) DEFAULT NULL,
  `c_data1` char(250) DEFAULT NULL,
  `c_data2` char(250) DEFAULT NULL,
  PRIMARY KEY (`c_id`,`c_d_id`,`c_w_id`),
  UNIQUE KEY `C_Customer_I1` (`c_w_id`,`c_d_id`,`c_id`),
  UNIQUE KEY `C_Customer_I2` (`c_w_id`,`c_d_id`,`c_last`,`c_first`,`c_id`),
  KEY `c_d_id` (`c_d_id`),
  KEY `c_d_id_2` (`c_d_id`,`c_id`,`c_w_id`),
  CONSTRAINT `C_Customer_ibfk_1` FOREIGN KEY (`c_d_id`) REFERENCES `C_District` (`d_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_District` (
  `d_id` int(11) NOT NULL,
  `d_w_id` int(11) NOT NULL,
  `d_name` char(10) DEFAULT NULL,
  `d_street_1` char(20) DEFAULT NULL,
  `d_street_2` char(20) DEFAULT NULL,
  `d_city` char(20) DEFAULT NULL,
  `d_state` char(2) DEFAULT NULL,
  `d_zip` char(9) DEFAULT NULL,
  `d_tax` float DEFAULT NULL,
  `d_ytd` float DEFAULT NULL,
  `d_next_o_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`d_id`,`d_w_id`),
  UNIQUE KEY `C_District_I1` (`d_w_id`,`d_id`),
  CONSTRAINT `C_District_ibfk_1` FOREIGN KEY (`d_w_id`) REFERENCES `C_Warehouse` (`w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_History` (
  `h_c_id` int(11) DEFAULT NULL,
  `h_c_d_id` int(11) DEFAULT NULL,
  `h_c_w_id` int(11) DEFAULT NULL,
  `h_d_id` int(11) DEFAULT NULL,
  `h_w_id` int(11) DEFAULT NULL,
  `h_date` datetime DEFAULT NULL,
  `h_amount` float DEFAULT NULL,
  `h_data` char(24) DEFAULT NULL,
  KEY `h_c_w_id` (`h_c_w_id`),
  KEY `h_d_id` (`h_d_id`),
  KEY `h_c_id` (`h_c_id`,`h_c_d_id`,`h_c_w_id`),
  KEY `h_d_id_2` (`h_d_id`,`h_w_id`),
  CONSTRAINT `C_History_ibfk_3` FOREIGN KEY (`h_c_id`, `h_c_d_id`, `h_c_w_id`) REFERENCES `C_Customer` (`c_id`, `c_d_id`, `c_w_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `C_History_ibfk_4` FOREIGN KEY (`h_d_id`, `h_w_id`) REFERENCES `C_District` (`d_id`, `d_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Item` (
  `i_id` int(11) NOT NULL,
  `i_im_id` int(11) DEFAULT NULL,
  `i_name` char(24) DEFAULT NULL,
  `i_price` float DEFAULT NULL,
  `i_data` char(50) DEFAULT NULL,
  PRIMARY KEY (`i_id`),
  UNIQUE KEY `C_Item_I1` (`i_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_New_Order` (
  `no_o_id` int(11) NOT NULL,
  `no_d_id` int(11) NOT NULL,
  `no_w_id` int(11) NOT NULL,
  PRIMARY KEY (`no_o_id`,`no_d_id`,`no_w_id`),
  UNIQUE KEY `C_New_Order_I1` (`no_w_id`,`no_d_id`,`no_o_id`),
  CONSTRAINT `C_New_Order_ibfk_1` FOREIGN KEY (`no_o_id`, `no_d_id`, `no_w_id`) REFERENCES `C_Order` (`o_id`, `o_d_id`, `o_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Order` (
  `o_id` int(11) NOT NULL,
  `o_d_id` int(11) NOT NULL,
  `o_w_id` int(11) NOT NULL,
  `o_c_id` int(11) DEFAULT NULL,
  `o_entry_d` datetime DEFAULT NULL,
  `o_carrier_id` int(11) DEFAULT NULL,
  `o_ol_cnt` int(11) DEFAULT NULL,
  `o_all_local` int(11) DEFAULT NULL,
  PRIMARY KEY (`o_id`,`o_d_id`,`o_w_id`),
  UNIQUE KEY `C_Order_I1` (`o_w_id`,`o_d_id`,`o_id`),
  KEY `o_d_id` (`o_d_id`,`o_c_id`,`o_w_id`),
  CONSTRAINT `C_Order_ibfk_1` FOREIGN KEY (`o_d_id`, `o_c_id`, `o_w_id`) REFERENCES `C_Customer` (`c_d_id`, `c_id`, `c_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Order_Line` (
  `ol_o_id` int(11) NOT NULL,
  `ol_d_id` int(11) NOT NULL,
  `ol_w_id` int(11) NOT NULL,
  `ol_number` int(11) NOT NULL,
  `ol_i_id` int(11) DEFAULT NULL,
  `ol_supply_w_id` int(11) DEFAULT NULL,
  `ol_delivery_d` datetime DEFAULT NULL,
  `ol_quantity` int(11) DEFAULT NULL,
  `ol_amount` float DEFAULT NULL,
  `ol_dist_info` char(24) DEFAULT NULL,
  PRIMARY KEY (`ol_o_id`,`ol_d_id`,`ol_w_id`,`ol_number`),
  UNIQUE KEY `C_Order_Line_I1` (`ol_w_id`,`ol_d_id`,`ol_o_id`,`ol_number`),
  KEY `ol_o_id` (`ol_o_id`,`ol_d_id`,`ol_w_id`),
  KEY `ol_i_id` (`ol_i_id`),
  KEY `ol_i_id_2` (`ol_i_id`,`ol_supply_w_id`),
  CONSTRAINT `C_Order_Line_ibfk_1` FOREIGN KEY (`ol_o_id`, `ol_d_id`, `ol_w_id`) REFERENCES `C_Order` (`o_id`, `o_d_id`, `o_w_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `C_Order_Line_ibfk_2` FOREIGN KEY (`ol_i_id`, `ol_supply_w_id`) REFERENCES `C_Stock` (`s_i_id`, `s_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Stock` (
  `s_i_id` int(11) NOT NULL,
  `s_w_id` int(11) NOT NULL,
  `s_quantity` int(11) DEFAULT NULL,
  `s_dist_01` char(24) DEFAULT NULL,
  `s_dist_02` char(24) DEFAULT NULL,
  `s_dist_03` char(24) DEFAULT NULL,
  `s_dist_04` char(24) DEFAULT NULL,
  `s_dist_05` char(24) DEFAULT NULL,
  `s_dist_06` char(24) DEFAULT NULL,
  `s_dist_07` char(24) DEFAULT NULL,
  `s_dist_08` char(24) DEFAULT NULL,
  `s_dist_09` char(24) DEFAULT NULL,
  `s_dist_10` char(24) DEFAULT NULL,
  `s_ytd` int(11) DEFAULT NULL,
  `s_order_cnt` int(11) DEFAULT NULL,
  `s_remote_cnt` int(11) DEFAULT NULL,
  `s_data` char(50) DEFAULT NULL,
  PRIMARY KEY (`s_i_id`,`s_w_id`),
  UNIQUE KEY `C_Stock_I1` (`s_i_id`,`s_w_id`),
  KEY `s_w_id` (`s_w_id`),
  CONSTRAINT `C_Stock_ibfk_1` FOREIGN KEY (`s_i_id`) REFERENCES `C_Item` (`i_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `C_Stock_ibfk_2` FOREIGN KEY (`s_w_id`) REFERENCES `C_Warehouse` (`w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Warehouse` (
  `w_id` int(11) NOT NULL,
  `w_name` char(10) DEFAULT NULL,
  `w_street_1` char(20) DEFAULT NULL,
  `w_street_2` char(20) DEFAULT NULL,
  `w_city` char(20) DEFAULT NULL,
  `w_state` char(2) DEFAULT NULL,
  `w_zip` char(9) DEFAULT NULL,
  `w_tax` float DEFAULT NULL,
  `w_ytd` float DEFAULT NULL,
  PRIMARY KEY (`w_id`),
  UNIQUE KEY `C_Warehouse_I1` (`w_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Checkins` (
  `business_id` varchar(30) NOT NULL DEFAULT '',
  `Sunday_0` int(11) DEFAULT NULL,
  `Sunday_1` int(11) DEFAULT NULL,
  `Sunday_2` int(11) DEFAULT NULL,
  `Sunday_3` int(11) DEFAULT NULL,
  `Sunday_4` int(11) DEFAULT NULL,
  `Sunday_5` int(11) DEFAULT NULL,
  `Sunday_6` int(11) DEFAULT NULL,
  `Sunday_7` int(11) DEFAULT NULL,
  `Sunday_8` int(11) DEFAULT NULL,
  `Sunday_9` int(11) DEFAULT NULL,
  `Sunday_10` int(11) DEFAULT NULL,
  `Sunday_11` int(11) DEFAULT NULL,
  `Sunday_12` int(11) DEFAULT NULL,
  `Sunday_13` int(11) DEFAULT NULL,
  `Sunday_14` int(11) DEFAULT NULL,
  `Sunday_15` int(11) DEFAULT NULL,
  `Sunday_16` int(11) DEFAULT NULL,
  `Sunday_17` int(11) DEFAULT NULL,
  `Sunday_18` int(11) DEFAULT NULL,
  `Sunday_19` int(11) DEFAULT NULL,
  `Sunday_20` int(11) DEFAULT NULL,
  `Sunday_21` int(11) DEFAULT NULL,
  `Sunday_22` int(11) DEFAULT NULL,
  `Sunday_23` int(11) DEFAULT NULL,
  `Monday_0` int(11) DEFAULT NULL,
  `Monday_1` int(11) DEFAULT NULL,
  `Monday_2` int(11) DEFAULT NULL,
  `Monday_3` int(11) DEFAULT NULL,
  `Monday_4` int(11) DEFAULT NULL,
  `Monday_5` int(11) DEFAULT NULL,
  `Monday_6` int(11) DEFAULT NULL,
  `Monday_7` int(11) DEFAULT NULL,
  `Monday_8` int(11) DEFAULT NULL,
  `Monday_9` int(11) DEFAULT NULL,
  `Monday_10` int(11) DEFAULT NULL,
  `Monday_11` int(11) DEFAULT NULL,
  `Monday_12` int(11) DEFAULT NULL,
  `Monday_13` int(11) DEFAULT NULL,
  `Monday_14` int(11) DEFAULT NULL,
  `Monday_15` int(11) DEFAULT NULL,
  `Monday_16` int(11) DEFAULT NULL,
  `Monday_17` int(11) DEFAULT NULL,
  `Monday_18` int(11) DEFAULT NULL,
  `Monday_19` int(11) DEFAULT NULL,
  `Monday_20` int(11) DEFAULT NULL,
  `Monday_21` int(11) DEFAULT NULL,
  `Monday_22` int(11) DEFAULT NULL,
  `Monday_23` int(11) DEFAULT NULL,
  `Tuesday_0` int(11) DEFAULT NULL,
  `Tuesday_1` int(11) DEFAULT NULL,
  `Tuesday_2` int(11) DEFAULT NULL,
  `Tuesday_3` int(11) DEFAULT NULL,
  `Tuesday_4` int(11) DEFAULT NULL,
  `Tuesday_5` int(11) DEFAULT NULL,
  `Tuesday_6` int(11) DEFAULT NULL,
  `Tuesday_7` int(11) DEFAULT NULL,
  `Tuesday_8` int(11) DEFAULT NULL,
  `Tuesday_9` int(11) DEFAULT NULL,
  `Tuesday_10` int(11) DEFAULT NULL,
  `Tuesday_11` int(11) DEFAULT NULL,
  `Tuesday_12` int(11) DEFAULT NULL,
  `Tuesday_13` int(11) DEFAULT NULL,
  `Tuesday_14` int(11) DEFAULT NULL,
  `Tuesday_15` int(11) DEFAULT NULL,
  `Tuesday_16` int(11) DEFAULT NULL,
  `Tuesday_17` int(11) DEFAULT NULL,
  `Tuesday_18` int(11) DEFAULT NULL,
  `Tuesday_19` int(11) DEFAULT NULL,
  `Tuesday_20` int(11) DEFAULT NULL,
  `Tuesday_21` int(11) DEFAULT NULL,
  `Tuesday_22` int(11) DEFAULT NULL,
  `Tuesday_23` int(11) DEFAULT NULL,
  `Wednesday_0` int(11) DEFAULT NULL,
  `Wednesday_1` int(11) DEFAULT NULL,
  `Wednesday_2` int(11) DEFAULT NULL,
  `Wednesday_3` int(11) DEFAULT NULL,
  `Wednesday_4` int(11) DEFAULT NULL,
  `Wednesday_5` int(11) DEFAULT NULL,
  `Wednesday_6` int(11) DEFAULT NULL,
  `Wednesday_7` int(11) DEFAULT NULL,
  `Wednesday_8` int(11) DEFAULT NULL,
  `Wednesday_9` int(11) DEFAULT NULL,
  `Wednesday_10` int(11) DEFAULT NULL,
  `Wednesday_11` int(11) DEFAULT NULL,
  `Wednesday_12` int(11) DEFAULT NULL,
  `Wednesday_13` int(11) DEFAULT NULL,
  `Wednesday_14` int(11) DEFAULT NULL,
  `Wednesday_15` int(11) DEFAULT NULL,
  `Wednesday_16` int(11) DEFAULT NULL,
  `Wednesday_17` int(11) DEFAULT NULL,
  `Wednesday_18` int(11) DEFAULT NULL,
  `Wednesday_19` int(11) DEFAULT NULL,
  `Wednesday_20` int(11) DEFAULT NULL,
  `Wednesday_21` int(11) DEFAULT NULL,
  `Wednesday_22` int(11) DEFAULT NULL,
  `Wednesday_23` int(11) DEFAULT NULL,
  `Thursday_0` int(11) DEFAULT NULL,
  `Thursday_1` int(11) DEFAULT NULL,
  `Thursday_2` int(11) DEFAULT NULL,
  `Thursday_3` int(11) DEFAULT NULL,
  `Thursday_4` int(11) DEFAULT NULL,
  `Thursday_5` int(11) DEFAULT NULL,
  `Thursday_6` int(11) DEFAULT NULL,
  `Thursday_7` int(11) DEFAULT NULL,
  `Thursday_8` int(11) DEFAULT NULL,
  `Thursday_9` int(11) DEFAULT NULL,
  `Thursday_10` int(11) DEFAULT NULL,
  `Thursday_11` int(11) DEFAULT NULL,
  `Thursday_12` int(11) DEFAULT NULL,
  `Thursday_13` int(11) DEFAULT NULL,
  `Thursday_14` int(11) DEFAULT NULL,
  `Thursday_15` int(11) DEFAULT NULL,
  `Thursday_16` int(11) DEFAULT NULL,
  `Thursday_17` int(11) DEFAULT NULL,
  `Thursday_18` int(11) DEFAULT NULL,
  `Thursday_19` int(11) DEFAULT NULL,
  `Thursday_20` int(11) DEFAULT NULL,
  `Thursday_21` int(11) DEFAULT NULL,
  `Thursday_22` int(11) DEFAULT NULL,
  `Thursday_23` int(11) DEFAULT NULL,
  `Friday_0` int(11) DEFAULT NULL,
  `Friday_1` int(11) DEFAULT NULL,
  `Friday_2` int(11) DEFAULT NULL,
  `Friday_3` int(11) DEFAULT NULL,
  `Friday_4` int(11) DEFAULT NULL,
  `Friday_5` int(11) DEFAULT NULL,
  `Friday_6` int(11) DEFAULT NULL,
  `Friday_7` int(11) DEFAULT NULL,
  `Friday_8` int(11) DEFAULT NULL,
  `Friday_9` int(11) DEFAULT NULL,
  `Friday_10` int(11) DEFAULT NULL,
  `Friday_11` int(11) DEFAULT NULL,
  `Friday_12` int(11) DEFAULT NULL,
  `Friday_13` int(11) DEFAULT NULL,
  `Friday_14` int(11) DEFAULT NULL,
  `Friday_15` int(11) DEFAULT NULL,
  `Friday_16` int(11) DEFAULT NULL,
  `Friday_17` int(11) DEFAULT NULL,
  `Friday_18` int(11) DEFAULT NULL,
  `Friday_19` int(11) DEFAULT NULL,
  `Friday_20` int(11) DEFAULT NULL,
  `Friday_21` int(11) DEFAULT NULL,
  `Friday_22` int(11) DEFAULT NULL,
  `Friday_23` int(11) DEFAULT NULL,
  `Saturday_0` int(11) DEFAULT NULL,
  `Saturday_1` int(11) DEFAULT NULL,
  `Saturday_2` int(11) DEFAULT NULL,
  `Saturday_3` int(11) DEFAULT NULL,
  `Saturday_4` int(11) DEFAULT NULL,
  `Saturday_5` int(11) DEFAULT NULL,
  `Saturday_6` int(11) DEFAULT NULL,
  `Saturday_7` int(11) DEFAULT NULL,
  `Saturday_8` int(11) DEFAULT NULL,
  `Saturday_9` int(11) DEFAULT NULL,
  `Saturday_10` int(11) DEFAULT NULL,
  `Saturday_11` int(11) DEFAULT NULL,
  `Saturday_12` int(11) DEFAULT NULL,
  `Saturday_13` int(11) DEFAULT NULL,
  `Saturday_14` int(11) DEFAULT NULL,
  `Saturday_15` int(11) DEFAULT NULL,
  `Saturday_16` int(11) DEFAULT NULL,
  `Saturday_17` int(11) DEFAULT NULL,
  `Saturday_18` int(11) DEFAULT NULL,
  `Saturday_19` int(11) DEFAULT NULL,
  `Saturday_20` int(11) DEFAULT NULL,
  `Saturday_21` int(11) DEFAULT NULL,
  `Saturday_22` int(11) DEFAULT NULL,
  `Saturday_23` int(11) DEFAULT NULL,
  PRIMARY KEY (`business_id`),
  CONSTRAINT `Checkins_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `City` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` char(35) NOT NULL DEFAULT '',
  `CountryCode` char(3) NOT NULL DEFAULT '',
  `District` char(20) NOT NULL DEFAULT '',
  `Population` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`ID`),
  KEY `City_CountryCode` (`CountryCode`),
  CONSTRAINT `city_ibfk_1` FOREIGN KEY (`CountryCode`) REFERENCES `Country` (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `ContactType` (
  `ContactTypeID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ContactType records.',
  `Name` varchar(100) NOT NULL COMMENT 'Contact type description.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ContactTypeID`),
  UNIQUE KEY `AK_ContactType_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the types of business entity contacts.'
;


CREATE TABLE `Country` (
  `Code` char(3) NOT NULL DEFAULT '',
  `Name` char(52) NOT NULL DEFAULT '',
  `Continent` enum('Asia','Europe','North America','Africa','Oceania','Antarctica','South America') NOT NULL DEFAULT 'Asia',
  `Region` char(26) NOT NULL DEFAULT '',
  `SurfaceArea` float(10,2) NOT NULL DEFAULT 0.00,
  `IndepYear` smallint(6) DEFAULT NULL,
  `Population` int(11) NOT NULL DEFAULT 0,
  `LifeExpectancy` float(3,1) DEFAULT NULL,
  `GNP` float(10,2) DEFAULT NULL,
  `GNPOld` float(10,2) DEFAULT NULL,
  `LocalName` char(45) NOT NULL DEFAULT '',
  `GovernmentForm` char(45) NOT NULL DEFAULT '',
  `HeadOfState` char(60) DEFAULT NULL,
  `Capital` int(11) DEFAULT NULL,
  `Code2` char(2) NOT NULL DEFAULT '',
  PRIMARY KEY (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `CountryLanguage` (
  `CountryCode` char(3) NOT NULL DEFAULT '',
  `Language` char(30) NOT NULL DEFAULT '',
  `IsOfficial` enum('T','F') NOT NULL DEFAULT 'F',
  `Percentage` float(4,1) NOT NULL DEFAULT 0.0,
  PRIMARY KEY (`CountryCode`,`Language`),
  KEY `CountryLanguage_CountryCode` (`CountryCode`),
  CONSTRAINT `countryLanguage_ibfk_1` FOREIGN KEY (`CountryCode`) REFERENCES `Country` (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `CountryRegion` (
  `CountryRegionCode` varchar(3) NOT NULL COMMENT 'ISO standard code for countries and regions.',
  `Name` varchar(100) NOT NULL COMMENT 'Country or region name.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CountryRegionCode`),
  UNIQUE KEY `AK_CountryRegion_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the ISO standard codes for countries and regions.'
;


CREATE TABLE `CountryRegionCurrency` (
  `CountryRegionCode` varchar(3) NOT NULL COMMENT 'ISO code for countries and regions. Foreign key to CountryRegion.CountryRegionCode.',
  `CurrencyCode` char(3) NOT NULL COMMENT 'ISO standard currency code. Foreign key to Currency.CurrencyCode.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CountryRegionCode`,`CurrencyCode`),
  KEY `IX_CountryRegionCurrency_CurrencyCode` (`CurrencyCode`),
  CONSTRAINT `FK_CountryRegionCurrency_CountryRegion_CountryRegionCode` FOREIGN KEY (`CountryRegionCode`) REFERENCES `CountryRegion` (`CountryRegionCode`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_CountryRegionCurrency_Currency_CurrencyCode` FOREIGN KEY (`CurrencyCode`) REFERENCES `Currency` (`CurrencyCode`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping ISO currency codes to a country or region.'
;


CREATE TABLE `CreditCard` (
  `CreditCardID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for CreditCard records.',
  `CardType` varchar(50) NOT NULL COMMENT 'Credit card name.',
  `CardNumber` varchar(25) NOT NULL COMMENT 'Credit card number.',
  `ExpMonth` tinyint(3) unsigned NOT NULL COMMENT 'Credit card expiration month.',
  `ExpYear` smallint(6) NOT NULL COMMENT 'Credit card expiration year.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CreditCardID`),
  UNIQUE KEY `AK_CreditCard_CardNumber` (`CardNumber`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customer credit card information.'
;


CREATE TABLE `Culture` (
  `CultureID` char(6) NOT NULL COMMENT 'Primary key for Culture records.',
  `Name` varchar(100) NOT NULL COMMENT 'Culture description.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CultureID`),
  UNIQUE KEY `AK_Culture_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the languages in which some AdventureWorks data is stored.'
;


CREATE TABLE `Currency` (
  `CurrencyCode` char(3) NOT NULL COMMENT 'The ISO code for the Currency.',
  `Name` varchar(100) NOT NULL COMMENT 'Currency name.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CurrencyCode`),
  UNIQUE KEY `AK_Currency_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing standard ISO currencies.'
;


CREATE TABLE `CurrencyRate` (
  `CurrencyRateID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for CurrencyRate records.',
  `CurrencyRateDate` datetime NOT NULL COMMENT 'Date and time the exchange rate was obtained.',
  `FromCurrencyCode` char(3) NOT NULL COMMENT 'Exchange rate was converted from this currency code.',
  `ToCurrencyCode` char(3) NOT NULL COMMENT 'Exchange rate was converted to this currency code.',
  `AverageRate` decimal(19,4) NOT NULL COMMENT 'Average exchange rate for the day.',
  `EndOfDayRate` decimal(19,4) NOT NULL COMMENT 'Final exchange rate for the day.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CurrencyRateID`),
  UNIQUE KEY `AK_CurrencyRate_CurrencyRateDate_FromCurrencyCode_ToCurrencyCode` (`CurrencyRateDate`,`FromCurrencyCode`,`ToCurrencyCode`),
  KEY `FK_CurrencyRate_Currency_FromCurrencyCode` (`FromCurrencyCode`),
  KEY `FK_CurrencyRate_Currency_ToCurrencyCode` (`ToCurrencyCode`),
  CONSTRAINT `FK_CurrencyRate_Currency_FromCurrencyCode` FOREIGN KEY (`FromCurrencyCode`) REFERENCES `Currency` (`CurrencyCode`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_CurrencyRate_Currency_ToCurrencyCode` FOREIGN KEY (`ToCurrencyCode`) REFERENCES `Currency` (`CurrencyCode`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Currency exchange rates.'
;


CREATE TABLE `Customer` (
  `CustomerID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key.',
  `PersonID` int(11) DEFAULT NULL COMMENT 'Foreign key to Person.BusinessEntityID',
  `StoreID` int(11) DEFAULT NULL COMMENT 'Foreign key to Store.BusinessEntityID',
  `TerritoryID` int(11) DEFAULT NULL COMMENT 'ID of the territory in which the customer is located. Foreign key to SalesTerritory.SalesTerritoryID.',
  `AccountNumber` varchar(10) NOT NULL COMMENT 'Unique number identifying the customer assigned by the accounting system.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`CustomerID`),
  UNIQUE KEY `AK_Customer_rowguid` (`rowguid`),
  UNIQUE KEY `AK_Customer_AccountNumber` (`AccountNumber`),
  KEY `IX_Customer_TerritoryID` (`TerritoryID`),
  KEY `FK_Customer_Person_PersonID` (`PersonID`),
  KEY `FK_Customer_Store_StoreID` (`StoreID`),
  KEY `GUID_Customer` (`rowguid`),
  CONSTRAINT `FK_Customer_Person_PersonID` FOREIGN KEY (`PersonID`) REFERENCES `Person` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Customer_SalesTerritory_TerritoryID` FOREIGN KEY (`TerritoryID`) REFERENCES `SalesTerritory` (`TerritoryID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Customer_Store_StoreID` FOREIGN KEY (`StoreID`) REFERENCES `Store` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Current customer information. Also see the Person and Store tables.'
;


CREATE TABLE `Customers` (
  `ID` int(11) NOT NULL,
  `SEX` varchar(255) DEFAULT NULL,
  `MARITAL_STATUS` varchar(255) DEFAULT NULL,
  `GEOID` int(11) DEFAULT NULL,
  `EDUCATIONNUM` int(11) DEFAULT NULL,
  `OCCUPATION` varchar(255) DEFAULT NULL,
  `DATA1` float DEFAULT NULL,
  `DATA2` float DEFAULT NULL,
  `DATA3` float DEFAULT NULL,
  `NOM1` varchar(255) DEFAULT NULL,
  `NOM2` varchar(255) DEFAULT NULL,
  `NOM3` varchar(255) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `Customers_GEOID` (`GEOID`),
  CONSTRAINT `Customers_ibfk_1` FOREIGN KEY (`GEOID`) REFERENCES `Demog` (`GEOID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `DATABASELOG` (
  `DATABASELOGID` int(11) NOT NULL COMMENT 'Primary key for DatabaseLog records.',
  `POSTTIME` datetime NOT NULL COMMENT 'The date and time the DDL change occurred.',
  `DATABASEUSER` varchar(160) NOT NULL COMMENT 'The user who implemented the DDL change.',
  `EVENT` varchar(160) NOT NULL COMMENT 'The type of DDL statement that was executed.',
  `SCHEMA` varchar(160) DEFAULT NULL COMMENT 'The schema to which the changed object belongs.',
  `OBJECT` varchar(160) DEFAULT NULL COMMENT 'The object that was changed by the DDL statment.',
  `TSQL` longtext NOT NULL COMMENT 'The exact Transact-SQL statement that was executed.',
  `XMLEVENT` text NOT NULL COMMENT 'The raw XML data generated by database trigger.',
  PRIMARY KEY (`DATABASELOGID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Audit table tracking all DDL changes made to the AdventureWorks database. Data is captured by the database trigger ddlDatabaseTriggerLog.'
;


CREATE TABLE `DEATH` (
  `ICO` int(11) NOT NULL,
  `DENUMR` varchar(255) DEFAULT NULL,
  `MESUMR` varchar(255) DEFAULT NULL,
  `ROKUMR` int(11) DEFAULT NULL,
  `PRICUMR` int(11) DEFAULT NULL,
  PRIMARY KEY (`ICO`),
  KEY `ICO` (`ICO`),
  CONSTRAINT `DEATH_IBFK_1` FOREIGN KEY (`ICO`) REFERENCES `ENTRY` (`ICO`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `DEPARTMENT` (
  `DEPARTMENTID` smallint(6) NOT NULL COMMENT 'Primary key for Department records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Name of the department.',
  `GROUPNAME` varchar(100) NOT NULL COMMENT 'Name of the group to which the department belongs.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`DEPARTMENTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the departments within the Adventure Works Cycles company.'
;


CREATE TABLE `DOCUMENT` (
  `DOCUMENTNODE` varchar(255) NOT NULL COMMENT 'Primary key for Document records.',
  `DOCUMENTLEVEL` smallint(6) DEFAULT NULL COMMENT 'Depth in the document hierarchy.',
  `TITLE` varchar(50) NOT NULL COMMENT 'Title of the document.',
  `OWNER` int(11) NOT NULL COMMENT 'Employee who controls the document.  Foreign key to Employee.BusinessEntityID',
  `FOLDERFLAG` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = This is a folder, 1 = This is a document.',
  `FILENAME` varchar(400) NOT NULL COMMENT 'File name of the document',
  `FILEEXTENSION` varchar(8) NOT NULL COMMENT 'File extension indicating the document type. For example, .doc or .txt.',
  `REVISION` char(5) NOT NULL COMMENT 'Revision number of the document. ',
  `CHANGENUMBER` int(11) NOT NULL DEFAULT 0 COMMENT 'Engineering change approval number.',
  `STATUS` tinyint(3) unsigned NOT NULL COMMENT '1 = Pending approval, 2 = Approved, 3 = Obsolete',
  `DOCUMENTSUMMARY` longtext DEFAULT NULL COMMENT 'Document abstract.',
  `DOCUMENT` longblob DEFAULT NULL COMMENT 'Complete document.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Required for FileStream.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`DOCUMENTNODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product maintenance documents.'
;


CREATE TABLE `DatabaseLog` (
  `DatabaseLogID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for DatabaseLog records.',
  `PostTime` datetime NOT NULL COMMENT 'The date and time the DDL change occurred.',
  `DatabaseUser` varchar(160) NOT NULL COMMENT 'The user who implemented the DDL change.',
  `Event` varchar(160) NOT NULL COMMENT 'The type of DDL statement that was executed.',
  `Schema` varchar(160) DEFAULT NULL COMMENT 'The schema to which the changed object belongs.',
  `Object` varchar(160) DEFAULT NULL COMMENT 'The object that was changed by the DDL statment.',
  `TSQL` longtext NOT NULL COMMENT 'The exact Transact-SQL statement that was executed.',
  `XmlEvent` text NOT NULL COMMENT 'The raw XML data generated by database trigger.',
  PRIMARY KEY (`DatabaseLogID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Audit table tracking all DDL changes made to the AdventureWorks database. Data is captured by the database trigger ddlDatabaseTriggerLog.'
;


CREATE TABLE `Demog` (
  `GEOID` int(11) NOT NULL,
  `INHABITANTS_K` float DEFAULT NULL,
  `INCOME_K` decimal(10,2) DEFAULT NULL,
  `A_VAR1` float DEFAULT NULL,
  `A_VAR2` float DEFAULT NULL,
  `A_VAR3` float DEFAULT NULL,
  `A_VAR4` float DEFAULT NULL,
  `A_VAR5` float DEFAULT NULL,
  `A_VAR6` float DEFAULT NULL,
  `A_VAR7` float DEFAULT NULL,
  `A_VAR8` float DEFAULT NULL,
  `A_VAR9` float DEFAULT NULL,
  `A_VAR10` float DEFAULT NULL,
  `A_VAR11` float DEFAULT NULL,
  `A_VAR12` float DEFAULT NULL,
  `A_VAR13` float DEFAULT NULL,
  `A_VAR14` float DEFAULT NULL,
  `A_VAR15` float DEFAULT NULL,
  `A_VAR16` float DEFAULT NULL,
  `A_VAR17` float DEFAULT NULL,
  `A_VAR18` float DEFAULT NULL,
  PRIMARY KEY (`GEOID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Department` (
  `DepartmentID` smallint(6) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for Department records.',
  `Name` varchar(100) NOT NULL COMMENT 'Name of the department.',
  `GroupName` varchar(100) NOT NULL COMMENT 'Name of the group to which the department belongs.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`DepartmentID`),
  UNIQUE KEY `AK_Department_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the departments within the Adventure Works Cycles company.'
;


CREATE TABLE `Document` (
  `DocumentNode` varchar(255) NOT NULL COMMENT 'Primary key for Document records.',
  `DocumentLevel` smallint(6) DEFAULT NULL COMMENT 'Depth in the document hierarchy.',
  `Title` varchar(50) NOT NULL COMMENT 'Title of the document.',
  `Owner` int(11) NOT NULL COMMENT 'Employee who controls the document.  Foreign key to Employee.BusinessEntityID',
  `FolderFlag` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = This is a folder, 1 = This is a document.',
  `FileName` varchar(400) NOT NULL COMMENT 'File name of the document',
  `FileExtension` varchar(8) NOT NULL COMMENT 'File extension indicating the document type. For example, .doc or .txt.',
  `Revision` char(5) NOT NULL COMMENT 'Revision number of the document. ',
  `ChangeNumber` int(11) NOT NULL DEFAULT 0 COMMENT 'Engineering change approval number.',
  `Status` tinyint(3) unsigned NOT NULL COMMENT '1 = Pending approval, 2 = Approved, 3 = Obsolete',
  `DocumentSummary` longtext DEFAULT NULL COMMENT 'Document abstract.',
  `Document` longblob DEFAULT NULL COMMENT 'Complete document.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Required for FileStream.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`DocumentNode`),
  UNIQUE KEY `UQ__Document__F73921F763026E5E` (`rowguid`),
  UNIQUE KEY `AK_Document_rowguid` (`rowguid`),
  UNIQUE KEY `AK_Document_DocumentLevel_DocumentNode` (`DocumentLevel`,`DocumentNode`),
  KEY `IX_Document_FileName_Revision` (`FileName`(255),`Revision`),
  KEY `FK_Document_Employee_Owner` (`Owner`),
  KEY `GUID_Document` (`rowguid`),
  CONSTRAINT `FK_Document_Employee_Owner` FOREIGN KEY (`Owner`) REFERENCES `Employee` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product maintenance documents.'
;


CREATE TABLE `EMAILADDRESS` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key. Person associated with this email address.  Foreign key to Person.BusinessEntityID',
  `EMAILADDRESSID` int(11) NOT NULL COMMENT 'Primary key. ID of this email address.',
  `EMAILADDRESS` varchar(50) DEFAULT NULL COMMENT 'E-mail address for the person.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`EMAILADDRESSID`,`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Where to send a person email.'
;


CREATE TABLE `EMPLOYEE` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key for Employee records.  Foreign key to BusinessEntity.BusinessEntityID.',
  `NATIONALIDNUMBER` varchar(15) NOT NULL COMMENT 'Unique national identification number such as a social security number.',
  `LOGINID` varchar(256) NOT NULL COMMENT 'Network login.',
  `ORGANIZATIONNODE` varchar(255) DEFAULT NULL COMMENT 'Where the employee is located in corporate hierarchy.',
  `ORGANIZATIONLEVEL` smallint(6) DEFAULT NULL COMMENT 'The depth of the employee in the corporate hierarchy.',
  `JOBTITLE` varchar(50) NOT NULL COMMENT 'Work title such as Buyer or Sales Representative.',
  `BIRTHDATE` date NOT NULL COMMENT 'Date of birth.',
  `MARITALSTATUS` char(1) NOT NULL COMMENT 'M = Married, S = Single',
  `GENDER` char(1) NOT NULL COMMENT 'M = Male, F = Female',
  `HIREDATE` date NOT NULL COMMENT 'Employee hired on this date.',
  `SALARIEDFLAG` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Job classification. 0 = Hourly, not exempt from collective bargaining. 1 = Salaried, exempt from collective bargaining.',
  `VACATIONHOURS` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Number of available vacation hours.',
  `SICKLEAVEHOURS` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Number of available sick leave hours.',
  `CURRENTFLAG` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Inactive, 1 = Active',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee information such as salary, department, and title.'
;


CREATE TABLE `EMPLOYEEDEPARTMENTHISTORY` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Employee identification number. Foreign key to Employee.BusinessEntityID.',
  `DEPARTMENTID` smallint(6) NOT NULL COMMENT 'Department in which the employee worked including currently. Foreign key to Department.DepartmentID.',
  `SHIFTID` tinyint(3) unsigned NOT NULL COMMENT 'Identifies which 8-hour shift the employee works. Foreign key to Shift.Shift.ID.',
  `STARTDATE` date NOT NULL COMMENT 'Date the employee started work in the department.',
  `ENDDATE` date DEFAULT NULL COMMENT 'Date the employee left the department. NULL = Current department.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`STARTDATE`,`DEPARTMENTID`,`SHIFTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee department transfers.'
;


CREATE TABLE `EMPLOYEEPAYHISTORY` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Employee identification number. Foreign key to Employee.BusinessEntityID.',
  `RATECHANGEDATE` datetime NOT NULL COMMENT 'Date the change in pay is effective',
  `RATE` decimal(19,4) NOT NULL COMMENT 'Salary hourly rate.',
  `PAYFREQUENCY` tinyint(3) unsigned NOT NULL COMMENT '1 = Salary received monthly, 2 = Salary received biweekly',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`RATECHANGEDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee pay history.'
;


CREATE TABLE `ENABLED_ROLES` (
  `ROLE_NAME` varchar(128) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=5549053 ROW_FORMAT=FIXED
;


CREATE TABLE `ENGINES` (
  `ENGINE` varchar(64) NOT NULL DEFAULT '',
  `SUPPORT` varchar(8) NOT NULL DEFAULT '',
  `COMMENT` varchar(160) NOT NULL DEFAULT '',
  `TRANSACTIONS` varchar(3) DEFAULT NULL,
  `XA` varchar(3) DEFAULT NULL,
  `SAVEPOINTS` varchar(3) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=2937734 ROW_FORMAT=FIXED
;


CREATE TABLE `ENTRY` (
  `ICO` int(11) NOT NULL,
  `KONSKUP` int(11) DEFAULT NULL,
  `ROKNAR` int(11) DEFAULT NULL,
  `ROKVSTUP` int(11) DEFAULT NULL,
  `MESVSTUP` int(11) DEFAULT NULL,
  `STAV` int(11) DEFAULT NULL,
  `VZDELANI` int(11) DEFAULT NULL,
  `ZODPOV` int(11) DEFAULT NULL,
  `TELAKTZA` int(11) DEFAULT NULL,
  `AKTPOZAM` int(11) DEFAULT NULL,
  `DOPRAVA` int(11) DEFAULT NULL,
  `DOPRATRV` int(11) DEFAULT NULL,
  `KOURENI` int(11) DEFAULT NULL,
  `DOBAKOUR` varchar(255) DEFAULT NULL,
  `BYVKURAK` varchar(255) DEFAULT NULL,
  `ALKOHOL` int(11) DEFAULT NULL,
  `PIVO7` varchar(255) DEFAULT NULL,
  `PIVO10` int(11) DEFAULT NULL,
  `PIVO12` varchar(255) DEFAULT NULL,
  `VINO` int(11) DEFAULT NULL,
  `LIHOV` int(11) DEFAULT NULL,
  `PIVOMN` int(11) DEFAULT NULL,
  `VINOMN` int(11) DEFAULT NULL,
  `LIHMN` int(11) DEFAULT NULL,
  `KAVA` int(11) DEFAULT NULL,
  `CAJ` int(11) DEFAULT NULL,
  `CUKR` int(11) DEFAULT NULL,
  `IM` int(11) DEFAULT NULL,
  `IML` varchar(255) DEFAULT NULL,
  `HT` int(11) DEFAULT NULL,
  `HTD` varchar(255) DEFAULT NULL,
  `HTL` varchar(255) DEFAULT NULL,
  `ICT` int(11) DEFAULT NULL,
  `ICTL` varchar(255) DEFAULT NULL,
  `DIABET` int(11) DEFAULT NULL,
  `DIABD` int(11) DEFAULT NULL,
  `DIABL` int(11) DEFAULT NULL,
  `HYPLIP` int(11) DEFAULT NULL,
  `HYPLD` varchar(255) DEFAULT NULL,
  `HYPLL` varchar(255) DEFAULT NULL,
  `IMTRV` varchar(255) DEFAULT NULL,
  `HTTRV` varchar(255) DEFAULT NULL,
  `ICTTRV` varchar(255) DEFAULT NULL,
  `DIABTRV` int(11) DEFAULT NULL,
  `HYPLTRV` varchar(255) DEFAULT NULL,
  `BOLHR` int(11) DEFAULT NULL,
  `BOLDK` int(11) DEFAULT NULL,
  `DUSNOST` int(11) DEFAULT NULL,
  `VYSKA` int(11) DEFAULT NULL,
  `VAHA` int(11) DEFAULT NULL,
  `SYST1` int(11) DEFAULT NULL,
  `DIAST1` int(11) DEFAULT NULL,
  `SYST2` varchar(255) DEFAULT NULL,
  `DIAST2` varchar(255) DEFAULT NULL,
  `TRIC` int(11) DEFAULT NULL,
  `SUBSC` int(11) DEFAULT NULL,
  `CHLST` int(11) DEFAULT NULL,
  `TRIGL` int(11) DEFAULT NULL,
  `MOC` int(11) DEFAULT NULL,
  `RARISK` int(11) DEFAULT NULL,
  `OBEZRISK` int(11) DEFAULT NULL,
  `KOURRISK` int(11) DEFAULT NULL,
  `HTRISK` int(11) DEFAULT NULL,
  `CHOLRISK` int(11) DEFAULT NULL,
  PRIMARY KEY (`ICO`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ERRORLOG` (
  `ERRORLOGID` int(11) NOT NULL COMMENT 'Primary key for ErrorLog records.',
  `ERRORTIME` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'The date and time at which the error occurred.',
  `USERNAME` varchar(160) NOT NULL COMMENT 'The user who executed the batch in which the error occurred.',
  `ERRORNUMBER` int(11) NOT NULL COMMENT 'The error number of the error that occurred.',
  `ERRORSEVERITY` int(11) DEFAULT NULL COMMENT 'The severity of the error that occurred.',
  `ERRORSTATE` int(11) DEFAULT NULL COMMENT 'The state number of the error that occurred.',
  `ERRORPROCEDURE` varchar(126) DEFAULT NULL COMMENT 'The name of the stored procedure or trigger where the error occurred.',
  `ERRORLINE` int(11) DEFAULT NULL COMMENT 'The line number at which the error occurred.',
  `ERRORMESSAGE` varchar(4000) NOT NULL COMMENT 'The message text of the error that occurred.',
  PRIMARY KEY (`ERRORLOGID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Audit table tracking errors in the the AdventureWorks database that are caught by the CATCH block of a TRY...CATCH construct. Data is inserted by stored procedure dbo.uspLogError when it is executed from inside the CATCH block of a TRY...CATCH construct.'
;


CREATE TABLE `EVENTS` (
  `EVENT_CATALOG` varchar(64) NOT NULL DEFAULT '',
  `EVENT_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `EVENT_NAME` varchar(64) NOT NULL DEFAULT '',
  `DEFINER` varchar(189) NOT NULL DEFAULT '',
  `TIME_ZONE` varchar(64) NOT NULL DEFAULT '',
  `EVENT_BODY` varchar(8) NOT NULL DEFAULT '',
  `EVENT_DEFINITION` longtext NOT NULL,
  `EVENT_TYPE` varchar(9) NOT NULL DEFAULT '',
  `EXECUTE_AT` datetime DEFAULT NULL,
  `INTERVAL_VALUE` varchar(256) DEFAULT NULL,
  `INTERVAL_FIELD` varchar(18) DEFAULT NULL,
  `SQL_MODE` varchar(8192) NOT NULL DEFAULT '',
  `STARTS` datetime DEFAULT NULL,
  `ENDS` datetime DEFAULT NULL,
  `STATUS` varchar(18) NOT NULL DEFAULT '',
  `ON_COMPLETION` varchar(12) NOT NULL DEFAULT '',
  `CREATED` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `LAST_ALTERED` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `LAST_EXECUTED` datetime DEFAULT NULL,
  `EVENT_COMMENT` varchar(64) NOT NULL DEFAULT '',
  `ORIGINATOR` bigint(10) NOT NULL DEFAULT 0,
  `CHARACTER_SET_CLIENT` varchar(32) NOT NULL DEFAULT '',
  `COLLATION_CONNECTION` varchar(32) NOT NULL DEFAULT '',
  `DATABASE_COLLATION` varchar(32) NOT NULL DEFAULT ''
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=78255 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `E_ACCOUNT_PERMISSION` (
  `AP_CA_ID` decimal(11,0) NOT NULL,
  `AP_ACL` char(4) NOT NULL,
  `AP_TAX_ID` char(20) NOT NULL,
  `AP_L_NAME` char(30) NOT NULL,
  `AP_F_NAME` char(30) NOT NULL,
  PRIMARY KEY (`AP_CA_ID`,`AP_TAX_ID`),
  UNIQUE KEY `PK_E_ACCOUNT_PERMISSION` (`AP_CA_ID`,`AP_TAX_ID`),
  CONSTRAINT `E_ACCOUNT_PERMISSION_ibfk_1` FOREIGN KEY (`AP_CA_ID`) REFERENCES `E_CUSTOMER_ACCOUNT` (`CA_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_ADDRESS` (
  `AD_ID` decimal(11,0) NOT NULL,
  `AD_LINE1` char(80) DEFAULT NULL,
  `AD_LINE2` char(80) DEFAULT NULL,
  `AD_ZC_CODE` char(12) NOT NULL,
  `AD_CTRY` char(80) DEFAULT NULL,
  PRIMARY KEY (`AD_ID`),
  UNIQUE KEY `PK_E_ADDRESS` (`AD_ID`),
  KEY `AD_ZC_CODE` (`AD_ZC_CODE`),
  CONSTRAINT `E_ADDRESS_ibfk_1` FOREIGN KEY (`AD_ZC_CODE`) REFERENCES `E_ZIP_CODE` (`ZC_CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_BROKER` (
  `B_ID` decimal(11,0) NOT NULL,
  `B_ST_ID` char(4) NOT NULL,
  `B_NAME` char(100) NOT NULL,
  `B_NUM_TRADES` decimal(9,0) NOT NULL,
  `B_COMM_TOTAL` decimal(12,2) NOT NULL,
  PRIMARY KEY (`B_ID`),
  UNIQUE KEY `PK_E_BROKER` (`B_ID`),
  UNIQUE KEY `E_BROKER_INDX1` (`B_NAME`,`B_ID`),
  UNIQUE KEY `E_BROKER_INDX2` (`B_ID`,`B_NAME`),
  KEY `B_ST_ID` (`B_ST_ID`),
  CONSTRAINT `E_BROKER_ibfk_1` FOREIGN KEY (`B_ST_ID`) REFERENCES `E_STATUS_TYPE` (`ST_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_CASH_TRANSACTION` (
  `CT_T_ID` decimal(15,0) NOT NULL,
  `CT_DTS` date DEFAULT NULL,
  `CT_AMT` decimal(10,2) NOT NULL,
  `CT_NAME` char(100) DEFAULT NULL,
  PRIMARY KEY (`CT_T_ID`),
  UNIQUE KEY `PK_E_CASH_TRANSACTION` (`CT_T_ID`),
  CONSTRAINT `E_CASH_TRANSACTION_ibfk_1` FOREIGN KEY (`CT_T_ID`) REFERENCES `E_TRADE` (`T_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_CHARGE` (
  `CH_TT_ID` char(3) NOT NULL,
  `CH_C_TIER` decimal(1,0) NOT NULL,
  `CH_CHRG` decimal(10,2) NOT NULL,
  PRIMARY KEY (`CH_TT_ID`,`CH_C_TIER`),
  UNIQUE KEY `PK_E_CHARGE` (`CH_TT_ID`,`CH_C_TIER`),
  CONSTRAINT `E_CHARGE_ibfk_1` FOREIGN KEY (`CH_TT_ID`) REFERENCES `E_TRADE_TYPE` (`TT_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_COMMISSION_RATE` (
  `CR_C_TIER` decimal(1,0) NOT NULL,
  `CR_TT_ID` char(3) NOT NULL,
  `CR_EX_ID` char(6) NOT NULL,
  `CR_FROM_QTY` decimal(9,0) NOT NULL,
  `CR_TO_QTY` decimal(9,0) NOT NULL,
  `CR_RATE` decimal(5,2) NOT NULL,
  PRIMARY KEY (`CR_C_TIER`,`CR_TT_ID`,`CR_EX_ID`,`CR_FROM_QTY`),
  UNIQUE KEY `PK_E_COMMISSION_RATE` (`CR_C_TIER`,`CR_TT_ID`,`CR_EX_ID`,`CR_FROM_QTY`),
  KEY `CR_EX_ID` (`CR_EX_ID`),
  KEY `CR_TT_ID` (`CR_TT_ID`),
  CONSTRAINT `E_COMMISSION_RATE_ibfk_1` FOREIGN KEY (`CR_EX_ID`) REFERENCES `E_EXCHANGE` (`EX_ID`),
  CONSTRAINT `E_COMMISSION_RATE_ibfk_2` FOREIGN KEY (`CR_TT_ID`) REFERENCES `E_TRADE_TYPE` (`TT_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_COMPANY` (
  `CO_ID` decimal(11,0) NOT NULL,
  `CO_ST_ID` char(4) NOT NULL,
  `CO_NAME` char(60) NOT NULL,
  `CO_IN_ID` char(2) NOT NULL,
  `CO_SP_RATE` char(4) NOT NULL,
  `CO_CEO` char(100) NOT NULL,
  `CO_AD_ID` decimal(11,0) NOT NULL,
  `CO_DESC` char(150) NOT NULL,
  `CO_OPEN_DATE` date DEFAULT NULL,
  PRIMARY KEY (`CO_ID`),
  UNIQUE KEY `PK_E_COMPANY` (`CO_ID`),
  UNIQUE KEY `E_COMPANY_INDX1` (`CO_NAME`,`CO_ID`),
  UNIQUE KEY `E_COMPANY_INDX2` (`CO_IN_ID`,`CO_ID`),
  KEY `CO_AD_ID` (`CO_AD_ID`),
  KEY `CO_ST_ID` (`CO_ST_ID`),
  CONSTRAINT `E_COMPANY_ibfk_1` FOREIGN KEY (`CO_AD_ID`) REFERENCES `E_ADDRESS` (`AD_ID`),
  CONSTRAINT `E_COMPANY_ibfk_2` FOREIGN KEY (`CO_IN_ID`) REFERENCES `E_INDUSTRY` (`IN_ID`),
  CONSTRAINT `E_COMPANY_ibfk_3` FOREIGN KEY (`CO_ST_ID`) REFERENCES `E_STATUS_TYPE` (`ST_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_COMPANY_COMPETITOR` (
  `CP_CO_ID` decimal(11,0) NOT NULL,
  `CP_COMP_CO_ID` decimal(11,0) NOT NULL,
  `CP_IN_ID` char(2) NOT NULL,
  PRIMARY KEY (`CP_CO_ID`,`CP_COMP_CO_ID`,`CP_IN_ID`),
  UNIQUE KEY `PK_E_COMPANY_COMPETITOR` (`CP_CO_ID`,`CP_COMP_CO_ID`,`CP_IN_ID`),
  KEY `CP_COMP_CO_ID` (`CP_COMP_CO_ID`),
  KEY `CP_IN_ID` (`CP_IN_ID`),
  KEY `E_COMPANY_COMPETITOR_INDX1` (`CP_CO_ID`),
  CONSTRAINT `E_COMPANY_COMPETITOR_ibfk_1` FOREIGN KEY (`CP_COMP_CO_ID`) REFERENCES `E_COMPANY` (`CO_ID`),
  CONSTRAINT `E_COMPANY_COMPETITOR_ibfk_2` FOREIGN KEY (`CP_CO_ID`) REFERENCES `E_COMPANY` (`CO_ID`),
  CONSTRAINT `E_COMPANY_COMPETITOR_ibfk_3` FOREIGN KEY (`CP_IN_ID`) REFERENCES `E_INDUSTRY` (`IN_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_CUSTOMER` (
  `C_ID` decimal(11,0) NOT NULL,
  `C_TAX_ID` char(20) NOT NULL,
  `C_ST_ID` char(4) NOT NULL,
  `C_L_NAME` char(30) NOT NULL,
  `C_F_NAME` char(30) NOT NULL,
  `C_M_NAME` char(1) DEFAULT NULL,
  `C_GNDR` char(1) DEFAULT NULL,
  `C_TIER` decimal(1,0) NOT NULL,
  `C_DOB` date DEFAULT NULL,
  `C_AD_ID` decimal(11,0) NOT NULL,
  `C_CTRY_1` char(3) DEFAULT NULL,
  `C_AREA_1` char(3) DEFAULT NULL,
  `C_LOCAL_1` char(10) DEFAULT NULL,
  `C_EXT_1` char(5) DEFAULT NULL,
  `C_CTRY_2` char(3) DEFAULT NULL,
  `C_AREA_2` char(3) DEFAULT NULL,
  `C_LOCAL_2` char(10) DEFAULT NULL,
  `C_EXT_2` char(5) DEFAULT NULL,
  `C_CTRY_3` char(3) DEFAULT NULL,
  `C_AREA_3` char(3) DEFAULT NULL,
  `C_LOCAL_3` char(10) DEFAULT NULL,
  `C_EXT_3` char(5) DEFAULT NULL,
  `C_EMAIL_1` char(50) DEFAULT NULL,
  `C_EMAIL_2` char(50) DEFAULT NULL,
  PRIMARY KEY (`C_ID`),
  UNIQUE KEY `PK_E_CUSTOMER` (`C_ID`),
  UNIQUE KEY `E_CUSTOMER_INDX1` (`C_TAX_ID`,`C_ID`),
  UNIQUE KEY `E_CUSTOMER_INDX2` (`C_ID`,`C_TIER`),
  KEY `C_ST_ID` (`C_ST_ID`),
  KEY `C_AD_ID` (`C_AD_ID`),
  CONSTRAINT `E_CUSTOMER_ibfk_1` FOREIGN KEY (`C_ST_ID`) REFERENCES `E_STATUS_TYPE` (`ST_ID`),
  CONSTRAINT `E_CUSTOMER_ibfk_2` FOREIGN KEY (`C_AD_ID`) REFERENCES `E_ADDRESS` (`AD_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_CUSTOMER_ACCOUNT` (
  `CA_ID` decimal(11,0) NOT NULL,
  `CA_B_ID` decimal(11,0) NOT NULL,
  `CA_C_ID` decimal(11,0) NOT NULL,
  `CA_NAME` char(50) NOT NULL,
  `CA_TAX_ST` decimal(1,0) NOT NULL,
  `CA_BAL` decimal(12,2) NOT NULL,
  PRIMARY KEY (`CA_ID`),
  UNIQUE KEY `PK_E_CUSTOMER_ACCOUNT` (`CA_ID`),
  UNIQUE KEY `E_CUSTOMER_ACCOUNT_INDX1` (`CA_C_ID`,`CA_ID`),
  UNIQUE KEY `E_CUSTOMER_ACCOUNT_INDX2` (`CA_B_ID`,`CA_ID`,`CA_C_ID`),
  UNIQUE KEY `E_CUSTOMER_ACCOUNT_INDX3` (`CA_ID`,`CA_B_ID`,`CA_C_ID`,`CA_TAX_ST`,`CA_NAME`),
  CONSTRAINT `E_CUSTOMER_ACCOUNT_ibfk_1` FOREIGN KEY (`CA_B_ID`) REFERENCES `E_BROKER` (`B_ID`),
  CONSTRAINT `E_CUSTOMER_ACCOUNT_ibfk_2` FOREIGN KEY (`CA_C_ID`) REFERENCES `E_CUSTOMER` (`C_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_CUSTOMER_TAXRATE` (
  `CX_TX_ID` char(4) NOT NULL,
  `CX_C_ID` decimal(11,0) NOT NULL,
  PRIMARY KEY (`CX_TX_ID`,`CX_C_ID`),
  UNIQUE KEY `PK_E_CUSTOMER_TAXRATE` (`CX_C_ID`,`CX_TX_ID`),
  CONSTRAINT `E_CUSTOMER_TAXRATE_ibfk_1` FOREIGN KEY (`CX_C_ID`) REFERENCES `E_CUSTOMER` (`C_ID`),
  CONSTRAINT `E_CUSTOMER_TAXRATE_ibfk_2` FOREIGN KEY (`CX_TX_ID`) REFERENCES `E_TAXRATE` (`TX_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_DAILY_MARKET` (
  `DM_DATE` date NOT NULL,
  `DM_S_SYMB` char(15) NOT NULL,
  `DM_CLOSE` decimal(8,2) NOT NULL,
  `DM_HIGH` decimal(8,2) NOT NULL,
  `DM_LOW` decimal(8,2) NOT NULL,
  `DM_VOL` decimal(12,0) NOT NULL,
  PRIMARY KEY (`DM_DATE`,`DM_S_SYMB`),
  UNIQUE KEY `PK_E_DAILY_MARKET` (`DM_S_SYMB`,`DM_DATE`),
  UNIQUE KEY `E_DAILY_MARKET_INDX1` (`DM_DATE`,`DM_S_SYMB`),
  CONSTRAINT `E_DAILY_MARKET_ibfk_1` FOREIGN KEY (`DM_S_SYMB`) REFERENCES `E_SECURITY` (`S_SYMB`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_EXCHANGE` (
  `EX_ID` char(6) NOT NULL,
  `EX_NAME` char(100) NOT NULL,
  `EX_NUM_SYMB` decimal(6,0) NOT NULL,
  `EX_OPEN` decimal(4,0) NOT NULL,
  `EX_CLOSE` decimal(4,0) NOT NULL,
  `EX_DESC` char(150) DEFAULT NULL,
  `EX_AD_ID` decimal(11,0) NOT NULL,
  PRIMARY KEY (`EX_ID`),
  UNIQUE KEY `PK_E_EXCHANGE` (`EX_ID`),
  KEY `EX_AD_ID` (`EX_AD_ID`),
  CONSTRAINT `E_EXCHANGE_ibfk_1` FOREIGN KEY (`EX_AD_ID`) REFERENCES `E_ADDRESS` (`AD_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_FINANCIAL` (
  `FI_CO_ID` decimal(11,0) NOT NULL,
  `FI_YEAR` decimal(4,0) NOT NULL,
  `FI_QTR` decimal(1,0) NOT NULL,
  `FI_QTR_START_DATE` date DEFAULT NULL,
  `FI_REVENUE` decimal(15,2) NOT NULL,
  `FI_NET_EARN` decimal(15,2) NOT NULL,
  `FI_BASIC_EPS` decimal(10,2) NOT NULL,
  `FI_DILUT_EPS` decimal(10,2) NOT NULL,
  `FI_MARGIN` decimal(10,2) NOT NULL,
  `FI_INVENTORY` decimal(15,2) NOT NULL,
  `FI_ASSETS` decimal(15,2) NOT NULL,
  `FI_LIABILITY` decimal(15,2) NOT NULL,
  `FI_OUT_BASIC` decimal(12,0) NOT NULL,
  `FI_OUT_DILUT` decimal(12,0) NOT NULL,
  PRIMARY KEY (`FI_CO_ID`,`FI_YEAR`,`FI_QTR`),
  UNIQUE KEY `PK_E_FINANCIAL` (`FI_CO_ID`,`FI_YEAR`,`FI_QTR`),
  CONSTRAINT `E_FINANCIAL_ibfk_1` FOREIGN KEY (`FI_CO_ID`) REFERENCES `E_COMPANY` (`CO_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_HOLDING` (
  `H_T_ID` decimal(15,0) NOT NULL,
  `H_CA_ID` decimal(11,0) NOT NULL,
  `H_S_SYMB` char(15) NOT NULL,
  `H_DTS` date DEFAULT NULL,
  `H_PRICE` decimal(8,2) NOT NULL,
  `H_QTY` decimal(9,0) NOT NULL,
  PRIMARY KEY (`H_T_ID`),
  UNIQUE KEY `PK_E_HOLDING` (`H_T_ID`),
  UNIQUE KEY `E_HOLDING_INDX1` (`H_CA_ID`,`H_S_SYMB`,`H_DTS`,`H_T_ID`),
  CONSTRAINT `E_HOLDING_ibfk_1` FOREIGN KEY (`H_CA_ID`, `H_S_SYMB`) REFERENCES `E_HOLDING_SUMMARY` (`HS_CA_ID`, `HS_S_SYMB`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `E_HOLDING_ibfk_2` FOREIGN KEY (`H_T_ID`) REFERENCES `E_TRADE` (`T_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_HOLDING_HISTORY` (
  `HH_H_T_ID` decimal(15,0) NOT NULL,
  `HH_T_ID` decimal(15,0) NOT NULL,
  `HH_BEFORE_QTY` decimal(9,0) NOT NULL,
  `HH_AFTER_QTY` decimal(9,0) NOT NULL,
  PRIMARY KEY (`HH_H_T_ID`,`HH_T_ID`),
  UNIQUE KEY `PK_E_HOLDING_HISTORY` (`HH_H_T_ID`,`HH_T_ID`),
  UNIQUE KEY `E_HOLDING_HISTORY_INDX1` (`HH_T_ID`,`HH_H_T_ID`),
  CONSTRAINT `E_HOLDING_HISTORY_ibfk_1` FOREIGN KEY (`HH_T_ID`) REFERENCES `E_TRADE` (`T_ID`),
  CONSTRAINT `E_HOLDING_HISTORY_ibfk_2` FOREIGN KEY (`HH_H_T_ID`) REFERENCES `E_HOLDING` (`H_T_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_HOLDING_SUMMARY` (
  `HS_CA_ID` decimal(11,0) NOT NULL,
  `HS_S_SYMB` char(15) NOT NULL,
  `HS_QTY` decimal(9,0) NOT NULL,
  PRIMARY KEY (`HS_CA_ID`,`HS_S_SYMB`),
  UNIQUE KEY `PK_E_HOLDING_SUMMARY` (`HS_CA_ID`,`HS_S_SYMB`),
  KEY `HS_S_SYMB` (`HS_S_SYMB`),
  CONSTRAINT `E_HOLDING_SUMMARY_ibfk_1` FOREIGN KEY (`HS_CA_ID`) REFERENCES `E_CUSTOMER_ACCOUNT` (`CA_ID`),
  CONSTRAINT `E_HOLDING_SUMMARY_ibfk_2` FOREIGN KEY (`HS_S_SYMB`) REFERENCES `E_SECURITY` (`S_SYMB`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_INDUSTRY` (
  `IN_ID` char(2) NOT NULL,
  `IN_NAME` char(50) NOT NULL,
  `IN_SC_ID` char(2) NOT NULL,
  PRIMARY KEY (`IN_ID`),
  UNIQUE KEY `PK_E_INDUSTRY` (`IN_ID`),
  UNIQUE KEY `E_INDUSTRY_INDX1` (`IN_NAME`,`IN_ID`),
  UNIQUE KEY `E_INDUSTRY_INDX2` (`IN_SC_ID`,`IN_ID`),
  CONSTRAINT `E_INDUSTRY_ibfk_1` FOREIGN KEY (`IN_SC_ID`) REFERENCES `E_SECTOR` (`SC_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_LAST_TRADE` (
  `LT_S_SYMB` char(15) NOT NULL,
  `LT_DTS` date DEFAULT NULL,
  `LT_PRICE` decimal(8,2) NOT NULL,
  `LT_OPEN_PRICE` decimal(8,2) NOT NULL,
  `LT_VOL` decimal(12,0) NOT NULL,
  PRIMARY KEY (`LT_S_SYMB`),
  UNIQUE KEY `PK_E_LAST_TRADE` (`LT_S_SYMB`),
  CONSTRAINT `E_LAST_TRADE_ibfk_1` FOREIGN KEY (`LT_S_SYMB`) REFERENCES `E_SECURITY` (`S_SYMB`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_NEWS_ITEM` (
  `NI_ID` decimal(11,0) NOT NULL,
  `NI_HEADLINE` char(80) NOT NULL,
  `NI_SUMMARY` char(255) NOT NULL,
  `NI_ITEM` longtext NOT NULL,
  `NI_DTS` date DEFAULT NULL,
  `NI_SOURCE` char(30) NOT NULL,
  `NI_AUTHOR` char(30) DEFAULT NULL,
  PRIMARY KEY (`NI_ID`),
  UNIQUE KEY `PK_E_NEWS_ITEM` (`NI_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_NEWS_XREF` (
  `NX_NI_ID` decimal(11,0) NOT NULL,
  `NX_CO_ID` decimal(11,0) NOT NULL,
  PRIMARY KEY (`NX_NI_ID`,`NX_CO_ID`),
  UNIQUE KEY `PK_E_NEWS_XREF` (`NX_CO_ID`,`NX_NI_ID`),
  KEY `NX_NI_ID` (`NX_NI_ID`),
  CONSTRAINT `E_NEWS_XREF_ibfk_1` FOREIGN KEY (`NX_CO_ID`) REFERENCES `E_COMPANY` (`CO_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `E_NEWS_XREF_ibfk_2` FOREIGN KEY (`NX_NI_ID`) REFERENCES `E_NEWS_ITEM` (`NI_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_SECTOR` (
  `SC_ID` char(2) NOT NULL,
  `SC_NAME` char(30) NOT NULL,
  PRIMARY KEY (`SC_ID`),
  UNIQUE KEY `PK_E_SECTOR` (`SC_ID`),
  UNIQUE KEY `E_SECTOR_INDX1` (`SC_NAME`,`SC_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_SECURITY` (
  `S_SYMB` char(15) NOT NULL,
  `S_ISSUE` char(6) NOT NULL,
  `S_ST_ID` char(4) NOT NULL,
  `S_NAME` char(70) NOT NULL,
  `S_EX_ID` char(6) NOT NULL,
  `S_CO_ID` decimal(11,0) NOT NULL,
  `S_NUM_OUT` decimal(12,0) NOT NULL,
  `S_START_DATE` date DEFAULT NULL,
  `S_EXCH_DATE` date DEFAULT NULL,
  `S_PE` decimal(10,2) NOT NULL,
  `S_52WK_HIGH` decimal(8,2) NOT NULL,
  `S_52WK_HIGH_DATE` date DEFAULT NULL,
  `S_52WK_LOW` decimal(8,2) NOT NULL,
  `S_52WK_LOW_DATE` date DEFAULT NULL,
  `S_DIVIDEND` decimal(10,2) NOT NULL,
  `S_YIELD` decimal(5,2) NOT NULL,
  PRIMARY KEY (`S_SYMB`),
  UNIQUE KEY `PK_E_SECURITY` (`S_SYMB`),
  UNIQUE KEY `E_SECURITY_INDX1` (`S_CO_ID`,`S_ISSUE`,`S_EX_ID`,`S_SYMB`),
  UNIQUE KEY `E_SECURITY_INDX2` (`S_CO_ID`,`S_NUM_OUT`,`S_SYMB`),
  KEY `S_EX_ID` (`S_EX_ID`),
  KEY `S_ST_ID` (`S_ST_ID`),
  CONSTRAINT `E_SECURITY_ibfk_1` FOREIGN KEY (`S_CO_ID`) REFERENCES `E_COMPANY` (`CO_ID`),
  CONSTRAINT `E_SECURITY_ibfk_2` FOREIGN KEY (`S_EX_ID`) REFERENCES `E_EXCHANGE` (`EX_ID`),
  CONSTRAINT `E_SECURITY_ibfk_3` FOREIGN KEY (`S_ST_ID`) REFERENCES `E_STATUS_TYPE` (`ST_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_SETTLEMENT` (
  `SE_T_ID` decimal(15,0) NOT NULL,
  `SE_CASH_TYPE` char(40) NOT NULL,
  `SE_CASH_DUE_DATE` date DEFAULT NULL,
  `SE_AMT` decimal(10,2) NOT NULL,
  PRIMARY KEY (`SE_T_ID`),
  UNIQUE KEY `PK_E_SETTLEMENT` (`SE_T_ID`),
  CONSTRAINT `E_SETTLEMENT_ibfk_1` FOREIGN KEY (`SE_T_ID`) REFERENCES `E_TRADE` (`T_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_STATUS_TYPE` (
  `ST_ID` char(4) NOT NULL,
  `ST_NAME` char(10) NOT NULL,
  PRIMARY KEY (`ST_ID`),
  UNIQUE KEY `PK_E_STATUS_TYPE` (`ST_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_TAXRATE` (
  `TX_ID` char(4) NOT NULL,
  `TX_NAME` char(50) NOT NULL,
  `TX_RATE` decimal(6,5) NOT NULL,
  PRIMARY KEY (`TX_ID`),
  UNIQUE KEY `PK_E_TAXRATE` (`TX_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_TRADE` (
  `T_ID` decimal(15,0) NOT NULL,
  `T_DTS` date DEFAULT NULL,
  `T_ST_ID` char(4) NOT NULL,
  `T_TT_ID` char(3) NOT NULL,
  `T_IS_CASH` char(1) NOT NULL,
  `T_S_SYMB` char(15) NOT NULL,
  `T_QTY` decimal(9,0) NOT NULL,
  `T_BID_PRICE` decimal(8,2) NOT NULL,
  `T_CA_ID` decimal(11,0) NOT NULL,
  `T_EXEC_NAME` char(64) NOT NULL,
  `T_TRADE_PRICE` decimal(8,2) DEFAULT NULL,
  `T_CHRG` decimal(10,2) NOT NULL,
  `T_COMM` decimal(10,2) NOT NULL,
  `T_TAX` decimal(10,2) NOT NULL,
  `T_LIFO` char(1) NOT NULL,
  PRIMARY KEY (`T_ID`),
  UNIQUE KEY `PK_E_TRADE` (`T_ID`),
  UNIQUE KEY `E_TRADE_INDX1` (`T_CA_ID`,`T_DTS`,`T_ID`),
  UNIQUE KEY `E_TRADE_INDX2` (`T_S_SYMB`,`T_DTS`,`T_ID`),
  KEY `T_ST_ID` (`T_ST_ID`),
  KEY `E_TRADE_INDX3` (`T_CA_ID`),
  KEY `T_TT_ID` (`T_TT_ID`),
  CONSTRAINT `E_TRADE_ibfk_1` FOREIGN KEY (`T_CA_ID`) REFERENCES `E_CUSTOMER_ACCOUNT` (`CA_ID`),
  CONSTRAINT `E_TRADE_ibfk_2` FOREIGN KEY (`T_ST_ID`) REFERENCES `E_STATUS_TYPE` (`ST_ID`),
  CONSTRAINT `E_TRADE_ibfk_3` FOREIGN KEY (`T_S_SYMB`) REFERENCES `E_SECURITY` (`S_SYMB`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `E_TRADE_ibfk_4` FOREIGN KEY (`T_TT_ID`) REFERENCES `E_TRADE_TYPE` (`TT_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_TRADE_HISTORY` (
  `TH_T_ID` decimal(15,0) NOT NULL,
  `TH_DTS` date DEFAULT NULL,
  `TH_ST_ID` char(4) NOT NULL,
  PRIMARY KEY (`TH_T_ID`,`TH_ST_ID`),
  UNIQUE KEY `PK_E_TRADE_HISTORY` (`TH_T_ID`,`TH_ST_ID`),
  KEY `TH_ST_ID` (`TH_ST_ID`),
  CONSTRAINT `E_TRADE_HISTORY_ibfk_1` FOREIGN KEY (`TH_ST_ID`) REFERENCES `E_STATUS_TYPE` (`ST_ID`),
  CONSTRAINT `E_TRADE_HISTORY_ibfk_2` FOREIGN KEY (`TH_T_ID`) REFERENCES `E_TRADE` (`T_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_TRADE_REQUEST` (
  `TR_T_ID` decimal(15,0) NOT NULL,
  `TR_TT_ID` char(3) NOT NULL,
  `TR_S_SYMB` char(15) NOT NULL,
  `TR_QTY` decimal(9,0) NOT NULL,
  `TR_BID_PRICE` decimal(8,2) NOT NULL,
  `TR_CA_ID` decimal(11,0) NOT NULL,
  PRIMARY KEY (`TR_T_ID`,`TR_TT_ID`,`TR_CA_ID`),
  UNIQUE KEY `PK_E_TRADE_REQUEST` (`TR_T_ID`),
  UNIQUE KEY `E_TRADE_REQUEST_INDX1` (`TR_CA_ID`,`TR_S_SYMB`,`TR_T_ID`),
  UNIQUE KEY `E_TRADE_REQUEST_INDX2` (`TR_S_SYMB`,`TR_T_ID`,`TR_TT_ID`,`TR_BID_PRICE`,`TR_QTY`),
  KEY `TR_TT_ID` (`TR_TT_ID`),
  CONSTRAINT `E_TRADE_REQUEST_ibfk_1` FOREIGN KEY (`TR_T_ID`) REFERENCES `E_TRADE` (`T_ID`),
  CONSTRAINT `E_TRADE_REQUEST_ibfk_4` FOREIGN KEY (`TR_TT_ID`) REFERENCES `E_TRADE_TYPE` (`TT_ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `E_TRADE_REQUEST_ibfk_5` FOREIGN KEY (`TR_S_SYMB`) REFERENCES `E_SECURITY` (`S_SYMB`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `E_TRADE_REQUEST_ibfk_6` FOREIGN KEY (`TR_CA_ID`) REFERENCES `E_CUSTOMER_ACCOUNT` (`CA_ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_TRADE_TYPE` (
  `TT_ID` char(3) NOT NULL,
  `TT_NAME` char(12) NOT NULL,
  `TT_IS_SELL` char(1) NOT NULL,
  `TT_IS_MRKT` char(1) NOT NULL,
  PRIMARY KEY (`TT_ID`),
  UNIQUE KEY `PK_E_TRADE_TYPE` (`TT_ID`),
  UNIQUE KEY `E_TRADE_TYPE_INDX` (`TT_ID`,`TT_IS_MRKT`,`TT_IS_SELL`,`TT_NAME`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_WATCH_ITEM` (
  `WI_WL_ID` decimal(11,0) NOT NULL,
  `WI_S_SYMB` char(15) NOT NULL,
  PRIMARY KEY (`WI_WL_ID`,`WI_S_SYMB`),
  UNIQUE KEY `PK_E_WATCH_ITEM` (`WI_WL_ID`,`WI_S_SYMB`),
  KEY `WI_S_SYMB` (`WI_S_SYMB`),
  CONSTRAINT `E_WATCH_ITEM_ibfk_1` FOREIGN KEY (`WI_S_SYMB`) REFERENCES `E_SECURITY` (`S_SYMB`),
  CONSTRAINT `E_WATCH_ITEM_ibfk_2` FOREIGN KEY (`WI_WL_ID`) REFERENCES `E_WATCH_LIST` (`WL_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_WATCH_LIST` (
  `WL_ID` decimal(11,0) NOT NULL,
  `WL_C_ID` decimal(11,0) NOT NULL,
  PRIMARY KEY (`WL_ID`),
  UNIQUE KEY `PK_E_WATCH_LIST` (`WL_ID`),
  UNIQUE KEY `E_WATCH_LIST_INDX1` (`WL_C_ID`,`WL_ID`),
  CONSTRAINT `E_WATCH_LIST_ibfk_1` FOREIGN KEY (`WL_C_ID`) REFERENCES `E_CUSTOMER` (`C_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `E_ZIP_CODE` (
  `ZC_CODE` char(12) NOT NULL,
  `ZC_TOWN` char(80) NOT NULL,
  `ZC_DIV` char(80) NOT NULL,
  PRIMARY KEY (`ZC_CODE`),
  UNIQUE KEY `PK_E_ZIP_CODE` (`ZC_CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `EmailAddress` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key. Person associated with this email address.  Foreign key to Person.BusinessEntityID',
  `EmailAddressID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key. ID of this email address.',
  `EmailAddress` varchar(50) DEFAULT NULL COMMENT 'E-mail address for the person.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`EmailAddressID`,`BusinessEntityID`),
  KEY `IX_EmailAddress_EmailAddress` (`EmailAddress`),
  KEY `FK_EmailAddress_Person_BusinessEntityID` (`BusinessEntityID`),
  KEY `GUID_EmailAddress` (`rowguid`),
  CONSTRAINT `FK_EmailAddress_Person_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Person` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Where to send a person email.'
;


CREATE TABLE `Employee` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key for Employee records.  Foreign key to BusinessEntity.BusinessEntityID.',
  `NationalIDNumber` varchar(15) NOT NULL COMMENT 'Unique national identification number such as a social security number.',
  `LoginID` varchar(256) NOT NULL COMMENT 'Network login.',
  `OrganizationNode` varchar(255) DEFAULT NULL COMMENT 'Where the employee is located in corporate hierarchy.',
  `OrganizationLevel` smallint(6) DEFAULT NULL COMMENT 'The depth of the employee in the corporate hierarchy.',
  `JobTitle` varchar(50) NOT NULL COMMENT 'Work title such as Buyer or Sales Representative.',
  `BirthDate` date NOT NULL COMMENT 'Date of birth.',
  `MaritalStatus` char(1) NOT NULL COMMENT 'M = Married, S = Single',
  `Gender` char(1) NOT NULL COMMENT 'M = Male, F = Female',
  `HireDate` date NOT NULL COMMENT 'Employee hired on this date.',
  `SalariedFlag` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Job classification. 0 = Hourly, not exempt from collective bargaining. 1 = Salaried, exempt from collective bargaining.',
  `VacationHours` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Number of available vacation hours.',
  `SickLeaveHours` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Number of available sick leave hours.',
  `CurrentFlag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Inactive, 1 = Active',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`),
  UNIQUE KEY `AK_Employee_NationalIDNumber` (`NationalIDNumber`),
  UNIQUE KEY `AK_Employee_rowguid` (`rowguid`),
  UNIQUE KEY `AK_Employee_LoginID` (`LoginID`(255)),
  KEY `IX_Employee_OrganizationNode` (`OrganizationNode`),
  KEY `IX_Employee_OrganizationLevel_OrganizationNode` (`OrganizationLevel`,`OrganizationNode`),
  KEY `GUID_Employee` (`rowguid`),
  CONSTRAINT `FK_Employee_Person_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Person` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee information such as salary, department, and title.'
;


CREATE TABLE `EmployeeDepartmentHistory` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Employee identification number. Foreign key to Employee.BusinessEntityID.',
  `DepartmentID` smallint(6) NOT NULL COMMENT 'Department in which the employee worked including currently. Foreign key to Department.DepartmentID.',
  `ShiftID` tinyint(3) unsigned NOT NULL COMMENT 'Identifies which 8-hour shift the employee works. Foreign key to Shift.Shift.ID.',
  `StartDate` date NOT NULL COMMENT 'Date the employee started work in the department.',
  `EndDate` date DEFAULT NULL COMMENT 'Date the employee left the department. NULL = Current department.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`StartDate`,`DepartmentID`,`ShiftID`),
  KEY `IX_EmployeeDepartmentHistory_DepartmentID` (`DepartmentID`),
  KEY `IX_EmployeeDepartmentHistory_ShiftID` (`ShiftID`),
  CONSTRAINT `FK_EmployeeDepartmentHistory_Department_DepartmentID` FOREIGN KEY (`DepartmentID`) REFERENCES `Department` (`DepartmentID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_EmployeeDepartmentHistory_Employee_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Employee` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_EmployeeDepartmentHistory_Shift_ShiftID` FOREIGN KEY (`ShiftID`) REFERENCES `Shift` (`ShiftID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee department transfers.'
;


CREATE TABLE `EmployeePayHistory` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Employee identification number. Foreign key to Employee.BusinessEntityID.',
  `RateChangeDate` datetime NOT NULL COMMENT 'Date the change in pay is effective',
  `Rate` decimal(19,4) NOT NULL COMMENT 'Salary hourly rate.',
  `PayFrequency` tinyint(3) unsigned NOT NULL COMMENT '1 = Salary received monthly, 2 = Salary received biweekly',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`RateChangeDate`),
  CONSTRAINT `FK_EmployeePayHistory_Employee_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Employee` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee pay history.'
;


CREATE TABLE `ErrorLog` (
  `ErrorLogID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ErrorLog records.',
  `ErrorTime` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'The date and time at which the error occurred.',
  `UserName` varchar(160) NOT NULL COMMENT 'The user who executed the batch in which the error occurred.',
  `ErrorNumber` int(11) NOT NULL COMMENT 'The error number of the error that occurred.',
  `ErrorSeverity` int(11) DEFAULT NULL COMMENT 'The severity of the error that occurred.',
  `ErrorState` int(11) DEFAULT NULL COMMENT 'The state number of the error that occurred.',
  `ErrorProcedure` varchar(126) DEFAULT NULL COMMENT 'The name of the stored procedure or trigger where the error occurred.',
  `ErrorLine` int(11) DEFAULT NULL COMMENT 'The line number at which the error occurred.',
  `ErrorMessage` varchar(4000) NOT NULL COMMENT 'The message text of the error that occurred.',
  PRIMARY KEY (`ErrorLogID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Audit table tracking errors in the the AdventureWorks database that are caught by the CATCH block of a TRY...CATCH construct. Data is inserted by stored procedure dbo.uspLogError when it is executed from inside the CATCH block of a TRY...CATCH construct.'
;


CREATE TABLE `FILES` (
  `FILE_ID` bigint(4) NOT NULL DEFAULT 0,
  `FILE_NAME` varchar(64) DEFAULT NULL,
  `FILE_TYPE` varchar(20) NOT NULL DEFAULT '',
  `TABLESPACE_NAME` varchar(64) DEFAULT NULL,
  `TABLE_CATALOG` varchar(64) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) DEFAULT NULL,
  `TABLE_NAME` varchar(64) DEFAULT NULL,
  `LOGFILE_GROUP_NAME` varchar(64) DEFAULT NULL,
  `LOGFILE_GROUP_NUMBER` bigint(4) DEFAULT NULL,
  `ENGINE` varchar(64) NOT NULL DEFAULT '',
  `FULLTEXT_KEYS` varchar(64) DEFAULT NULL,
  `DELETED_ROWS` bigint(4) DEFAULT NULL,
  `UPDATE_COUNT` bigint(4) DEFAULT NULL,
  `FREE_EXTENTS` bigint(4) DEFAULT NULL,
  `TOTAL_EXTENTS` bigint(4) DEFAULT NULL,
  `EXTENT_SIZE` bigint(4) NOT NULL DEFAULT 0,
  `INITIAL_SIZE` bigint(21) unsigned DEFAULT NULL,
  `MAXIMUM_SIZE` bigint(21) unsigned DEFAULT NULL,
  `AUTOEXTEND_SIZE` bigint(21) unsigned DEFAULT NULL,
  `CREATION_TIME` datetime DEFAULT NULL,
  `LAST_UPDATE_TIME` datetime DEFAULT NULL,
  `LAST_ACCESS_TIME` datetime DEFAULT NULL,
  `RECOVER_TIME` bigint(4) DEFAULT NULL,
  `TRANSACTION_COUNTER` bigint(4) DEFAULT NULL,
  `VERSION` bigint(21) unsigned DEFAULT NULL,
  `ROW_FORMAT` varchar(10) DEFAULT NULL,
  `TABLE_ROWS` bigint(21) unsigned DEFAULT NULL,
  `AVG_ROW_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `DATA_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `MAX_DATA_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `INDEX_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `DATA_FREE` bigint(21) unsigned DEFAULT NULL,
  `CREATE_TIME` datetime DEFAULT NULL,
  `UPDATE_TIME` datetime DEFAULT NULL,
  `CHECK_TIME` datetime DEFAULT NULL,
  `CHECKSUM` bigint(21) unsigned DEFAULT NULL,
  `STATUS` varchar(20) NOT NULL DEFAULT '',
  `EXTRA` varchar(255) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=802197 ROW_FORMAT=FIXED
;


CREATE TABLE `GLOBAL_STATUS` (
  `VARIABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `VARIABLE_VALUE` varchar(1024) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=657124 ROW_FORMAT=FIXED
;


CREATE TABLE `GLOBAL_VARIABLES` (
  `VARIABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `VARIABLE_VALUE` varchar(1024) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=657124 ROW_FORMAT=FIXED
;


CREATE TABLE `ILLUSTRATION` (
  `ILLUSTRATIONID` int(11) NOT NULL COMMENT 'Primary key for Illustration records.',
  `DIAGRAM` text DEFAULT NULL COMMENT 'Illustrations used in manufacturing instructions. Stored as XML.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ILLUSTRATIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Bicycle assembly diagrams.'
;


CREATE TABLE `INDEX_STATISTICS` (
  `TABLE_SCHEMA` varchar(192) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(192) NOT NULL DEFAULT '',
  `INDEX_NAME` varchar(192) NOT NULL DEFAULT '',
  `ROWS_READ` bigint(21) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1232061 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_BUFFER_PAGE` (
  `POOL_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `BLOCK_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `SPACE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGE_NUMBER` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGE_TYPE` varchar(64) DEFAULT NULL,
  `FLUSH_TYPE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `FIX_COUNT` bigint(21) unsigned NOT NULL DEFAULT 0,
  `IS_HASHED` varchar(3) DEFAULT NULL,
  `NEWEST_MODIFICATION` bigint(21) unsigned NOT NULL DEFAULT 0,
  `OLDEST_MODIFICATION` bigint(21) unsigned NOT NULL DEFAULT 0,
  `ACCESS_TIME` bigint(21) unsigned NOT NULL DEFAULT 0,
  `TABLE_NAME` varchar(1024) DEFAULT NULL,
  `INDEX_NAME` varchar(1024) DEFAULT NULL,
  `NUMBER_RECORDS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DATA_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `COMPRESSED_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGE_STATE` varchar(64) DEFAULT NULL,
  `IO_FIX` varchar(64) DEFAULT NULL,
  `IS_OLD` varchar(3) DEFAULT NULL,
  `FREE_PAGE_CLOCK` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=313409 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_BUFFER_PAGE_LRU` (
  `POOL_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `LRU_POSITION` bigint(21) unsigned NOT NULL DEFAULT 0,
  `SPACE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGE_NUMBER` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGE_TYPE` varchar(64) DEFAULT NULL,
  `FLUSH_TYPE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `FIX_COUNT` bigint(21) unsigned NOT NULL DEFAULT 0,
  `IS_HASHED` varchar(3) DEFAULT NULL,
  `NEWEST_MODIFICATION` bigint(21) unsigned NOT NULL DEFAULT 0,
  `OLDEST_MODIFICATION` bigint(21) unsigned NOT NULL DEFAULT 0,
  `ACCESS_TIME` bigint(21) unsigned NOT NULL DEFAULT 0,
  `TABLE_NAME` varchar(1024) DEFAULT NULL,
  `INDEX_NAME` varchar(1024) DEFAULT NULL,
  `NUMBER_RECORDS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DATA_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `COMPRESSED_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `COMPRESSED` varchar(3) DEFAULT NULL,
  `IO_FIX` varchar(64) DEFAULT NULL,
  `IS_OLD` varchar(3) DEFAULT NULL,
  `FREE_PAGE_CLOCK` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=322009 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_BUFFER_POOL_STATS` (
  `POOL_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `POOL_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `FREE_BUFFERS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DATABASE_PAGES` bigint(21) unsigned NOT NULL DEFAULT 0,
  `OLD_DATABASE_PAGES` bigint(21) unsigned NOT NULL DEFAULT 0,
  `MODIFIED_DATABASE_PAGES` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PENDING_DECOMPRESS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PENDING_READS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PENDING_FLUSH_LRU` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PENDING_FLUSH_LIST` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGES_MADE_YOUNG` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGES_NOT_MADE_YOUNG` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGES_MADE_YOUNG_RATE` double NOT NULL DEFAULT 0,
  `PAGES_MADE_NOT_YOUNG_RATE` double NOT NULL DEFAULT 0,
  `NUMBER_PAGES_READ` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NUMBER_PAGES_CREATED` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NUMBER_PAGES_WRITTEN` bigint(21) unsigned NOT NULL DEFAULT 0,
  `PAGES_READ_RATE` double NOT NULL DEFAULT 0,
  `PAGES_CREATE_RATE` double NOT NULL DEFAULT 0,
  `PAGES_WRITTEN_RATE` double NOT NULL DEFAULT 0,
  `NUMBER_PAGES_GET` bigint(21) unsigned NOT NULL DEFAULT 0,
  `HIT_RATE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `YOUNG_MAKE_PER_THOUSAND_GETS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NOT_YOUNG_MAKE_PER_THOUSAND_GETS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NUMBER_PAGES_READ_AHEAD` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NUMBER_READ_AHEAD_EVICTED` bigint(21) unsigned NOT NULL DEFAULT 0,
  `READ_AHEAD_RATE` double NOT NULL DEFAULT 0,
  `READ_AHEAD_EVICTED_RATE` double NOT NULL DEFAULT 0,
  `LRU_IO_TOTAL` bigint(21) unsigned NOT NULL DEFAULT 0,
  `LRU_IO_CURRENT` bigint(21) unsigned NOT NULL DEFAULT 0,
  `UNCOMPRESS_TOTAL` bigint(21) unsigned NOT NULL DEFAULT 0,
  `UNCOMPRESS_CURRENT` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=8355967 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_CHANGED_PAGES` (
  `space_id` int(11) unsigned NOT NULL DEFAULT 0,
  `page_id` int(11) unsigned NOT NULL DEFAULT 0,
  `start_lsn` bigint(21) unsigned NOT NULL DEFAULT 0,
  `end_lsn` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=85899345 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_CMP` (
  `page_size` int(5) NOT NULL DEFAULT 0,
  `compress_ops` int(11) NOT NULL DEFAULT 0,
  `compress_ops_ok` int(11) NOT NULL DEFAULT 0,
  `compress_time` int(11) NOT NULL DEFAULT 0,
  `uncompress_ops` int(11) NOT NULL DEFAULT 0,
  `uncompress_time` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=85899345 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_CMPMEM` (
  `page_size` int(5) NOT NULL DEFAULT 0,
  `buffer_pool_instance` int(11) NOT NULL DEFAULT 0,
  `pages_used` int(11) NOT NULL DEFAULT 0,
  `pages_free` int(11) NOT NULL DEFAULT 0,
  `relocation_ops` bigint(21) NOT NULL DEFAULT 0,
  `relocation_time` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=74051160 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_CMPMEM_RESET` (
  `page_size` int(5) NOT NULL DEFAULT 0,
  `buffer_pool_instance` int(11) NOT NULL DEFAULT 0,
  `pages_used` int(11) NOT NULL DEFAULT 0,
  `pages_free` int(11) NOT NULL DEFAULT 0,
  `relocation_ops` bigint(21) NOT NULL DEFAULT 0,
  `relocation_time` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=74051160 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_CMP_PER_INDEX` (
  `database_name` varchar(192) NOT NULL DEFAULT '',
  `table_name` varchar(192) NOT NULL DEFAULT '',
  `index_name` varchar(192) NOT NULL DEFAULT '',
  `compress_ops` int(11) NOT NULL DEFAULT 0,
  `compress_ops_ok` int(11) NOT NULL DEFAULT 0,
  `compress_time` int(11) NOT NULL DEFAULT 0,
  `uncompress_ops` int(11) NOT NULL DEFAULT 0,
  `uncompress_time` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1223637 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_CMP_PER_INDEX_RESET` (
  `database_name` varchar(192) NOT NULL DEFAULT '',
  `table_name` varchar(192) NOT NULL DEFAULT '',
  `index_name` varchar(192) NOT NULL DEFAULT '',
  `compress_ops` int(11) NOT NULL DEFAULT 0,
  `compress_ops_ok` int(11) NOT NULL DEFAULT 0,
  `compress_time` int(11) NOT NULL DEFAULT 0,
  `uncompress_ops` int(11) NOT NULL DEFAULT 0,
  `uncompress_time` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1223637 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_CMP_RESET` (
  `page_size` int(5) NOT NULL DEFAULT 0,
  `compress_ops` int(11) NOT NULL DEFAULT 0,
  `compress_ops_ok` int(11) NOT NULL DEFAULT 0,
  `compress_time` int(11) NOT NULL DEFAULT 0,
  `uncompress_ops` int(11) NOT NULL DEFAULT 0,
  `uncompress_time` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=85899345 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_FT_BEING_DELETED` (
  `DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=238609294 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_FT_CONFIG` (
  `KEY` varchar(193) NOT NULL DEFAULT '',
  `VALUE` varchar(193) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1846503 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_FT_DEFAULT_STOPWORD` (
  `value` varchar(18) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=38347922 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_FT_DELETED` (
  `DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=238609294 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_FT_INDEX_CACHE` (
  `WORD` varchar(255) NOT NULL DEFAULT '',
  `FIRST_DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `LAST_DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DOC_COUNT` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `POSITION` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=2657776 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_FT_INDEX_TABLE` (
  `WORD` varchar(255) NOT NULL DEFAULT '',
  `FIRST_DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `LAST_DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DOC_COUNT` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DOC_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `POSITION` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=2657776 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_LOCKS` (
  `lock_id` varchar(81) NOT NULL DEFAULT '',
  `lock_trx_id` varchar(18) NOT NULL DEFAULT '',
  `lock_mode` varchar(32) NOT NULL DEFAULT '',
  `lock_type` varchar(32) NOT NULL DEFAULT '',
  `lock_table` varchar(1024) NOT NULL DEFAULT '',
  `lock_index` varchar(1024) DEFAULT NULL,
  `lock_space` bigint(21) unsigned DEFAULT NULL,
  `lock_page` bigint(21) unsigned DEFAULT NULL,
  `lock_rec` bigint(21) unsigned DEFAULT NULL,
  `lock_data` varchar(8192) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=68732 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_LOCK_WAITS` (
  `requesting_trx_id` varchar(18) NOT NULL DEFAULT '',
  `requested_lock_id` varchar(81) NOT NULL DEFAULT '',
  `blocking_trx_id` varchar(18) NOT NULL DEFAULT '',
  `blocking_lock_id` varchar(81) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=3585114 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_METRICS` (
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `SUBSYSTEM` varchar(193) NOT NULL DEFAULT '',
  `COUNT` bigint(21) NOT NULL DEFAULT 0,
  `MAX_COUNT` bigint(21) DEFAULT NULL,
  `MIN_COUNT` bigint(21) DEFAULT NULL,
  `AVG_COUNT` double DEFAULT NULL,
  `COUNT_RESET` bigint(21) NOT NULL DEFAULT 0,
  `MAX_COUNT_RESET` bigint(21) DEFAULT NULL,
  `MIN_COUNT_RESET` bigint(21) DEFAULT NULL,
  `AVG_COUNT_RESET` double DEFAULT NULL,
  `TIME_ENABLED` datetime DEFAULT NULL,
  `TIME_DISABLED` datetime DEFAULT NULL,
  `TIME_ELAPSED` bigint(21) DEFAULT NULL,
  `TIME_RESET` datetime DEFAULT NULL,
  `STATUS` varchar(193) NOT NULL DEFAULT '',
  `TYPE` varchar(193) NOT NULL DEFAULT '',
  `COMMENT` varchar(193) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=715112 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_COLUMNS` (
  `TABLE_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `POS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `MTYPE` int(11) NOT NULL DEFAULT 0,
  `PRTYPE` int(11) NOT NULL DEFAULT 0,
  `LEN` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=3520464 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_DATAFILES` (
  `SPACE` int(11) unsigned NOT NULL DEFAULT 0,
  `PATH` varchar(4000) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=178852 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_FIELDS` (
  `INDEX_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `POS` int(11) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=3615292 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_FOREIGN` (
  `ID` varchar(193) NOT NULL DEFAULT '',
  `FOR_NAME` varchar(193) NOT NULL DEFAULT '',
  `REF_NAME` varchar(193) NOT NULL DEFAULT '',
  `N_COLS` int(11) unsigned NOT NULL DEFAULT 0,
  `TYPE` int(11) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1225732 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_FOREIGN_COLS` (
  `ID` varchar(193) NOT NULL DEFAULT '',
  `FOR_COL_NAME` varchar(193) NOT NULL DEFAULT '',
  `REF_COL_NAME` varchar(193) NOT NULL DEFAULT '',
  `POS` int(11) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1228537 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_INDEXES` (
  `INDEX_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `TABLE_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `TYPE` int(11) NOT NULL DEFAULT 0,
  `N_FIELDS` int(11) NOT NULL DEFAULT 0,
  `PAGE_NO` int(11) NOT NULL DEFAULT 0,
  `SPACE` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=3497530 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_TABLES` (
  `TABLE_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NAME` varchar(655) NOT NULL DEFAULT '',
  `FLAG` int(11) NOT NULL DEFAULT 0,
  `N_COLS` int(11) NOT NULL DEFAULT 0,
  `SPACE` int(11) NOT NULL DEFAULT 0,
  `FILE_FORMAT` varchar(10) DEFAULT NULL,
  `ROW_FORMAT` varchar(12) DEFAULT NULL,
  `ZIP_PAGE_SIZE` int(11) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1042467 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_TABLESPACES` (
  `SPACE` int(11) unsigned NOT NULL DEFAULT 0,
  `NAME` varchar(655) NOT NULL DEFAULT '',
  `FLAG` int(11) unsigned NOT NULL DEFAULT 0,
  `FILE_FORMAT` varchar(10) DEFAULT NULL,
  `ROW_FORMAT` varchar(22) DEFAULT NULL,
  `PAGE_SIZE` int(11) unsigned NOT NULL DEFAULT 0,
  `ZIP_PAGE_SIZE` int(11) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1031452 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_SYS_TABLESTATS` (
  `TABLE_ID` bigint(21) unsigned NOT NULL DEFAULT 0,
  `NAME` varchar(193) NOT NULL DEFAULT '',
  `STATS_INITIALIZED` varchar(193) NOT NULL DEFAULT '',
  `NUM_ROWS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `CLUST_INDEX_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `OTHER_INDEX_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `MODIFIED_COUNTER` bigint(21) unsigned NOT NULL DEFAULT 0,
  `AUTOINC` bigint(21) unsigned NOT NULL DEFAULT 0,
  `REF_COUNT` int(11) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1767476 ROW_FORMAT=FIXED
;


CREATE TABLE `INNODB_TRX` (
  `trx_id` varchar(18) NOT NULL DEFAULT '',
  `trx_state` varchar(13) NOT NULL DEFAULT '',
  `trx_started` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `trx_requested_lock_id` varchar(81) DEFAULT NULL,
  `trx_wait_started` datetime DEFAULT NULL,
  `trx_weight` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_mysql_thread_id` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_query` varchar(1024) DEFAULT NULL,
  `trx_operation_state` varchar(64) DEFAULT NULL,
  `trx_tables_in_use` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_tables_locked` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_lock_structs` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_lock_memory_bytes` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_rows_locked` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_rows_modified` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_concurrency_tickets` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_isolation_level` varchar(16) NOT NULL DEFAULT '',
  `trx_unique_checks` int(1) NOT NULL DEFAULT 0,
  `trx_foreign_key_checks` int(1) NOT NULL DEFAULT 0,
  `trx_last_foreign_key_error` varchar(256) DEFAULT NULL,
  `trx_adaptive_hash_latched` int(1) NOT NULL DEFAULT 0,
  `trx_adaptive_hash_timeout` bigint(21) unsigned NOT NULL DEFAULT 0,
  `trx_is_read_only` int(1) NOT NULL DEFAULT 0,
  `trx_autocommit_non_locking` int(1) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=472805 ROW_FORMAT=FIXED
;


CREATE TABLE `Illustration` (
  `IllustrationID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for Illustration records.',
  `Diagram` text DEFAULT NULL COMMENT 'Illustrations used in manufacturing instructions. Stored as XML.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`IllustrationID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Bicycle assembly diagrams.'
;


CREATE TABLE `JOBCANDIDATE` (
  `JOBCANDIDATEID` int(11) NOT NULL COMMENT 'Primary key for JobCandidate records.',
  `BUSINESSENTITYID` int(11) DEFAULT NULL COMMENT 'Employee identification number if applicant was hired. Foreign key to Employee.BusinessEntityID.',
  `RESUME` text DEFAULT NULL COMMENT 'Résumé in XML format.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`JOBCANDIDATEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Résumés submitted to Human Resources by job applicants.'
;


CREATE TABLE `JobCandidate` (
  `JobCandidateID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for JobCandidate records.',
  `BusinessEntityID` int(11) DEFAULT NULL COMMENT 'Employee identification number if applicant was hired. Foreign key to Employee.BusinessEntityID.',
  `Resume` text DEFAULT NULL COMMENT 'Résumé in XML format.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`JobCandidateID`),
  KEY `IX_JobCandidate_BusinessEntityID` (`BusinessEntityID`),
  CONSTRAINT `FK_JobCandidate_Employee_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Employee` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Résumés submitted to Human Resources by job applicants.'
;


CREATE TABLE `KEY_CACHES` (
  `KEY_CACHE_NAME` varchar(192) NOT NULL DEFAULT '',
  `SEGMENTS` int(3) unsigned DEFAULT NULL,
  `SEGMENT_NUMBER` int(3) unsigned DEFAULT NULL,
  `FULL_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `BLOCK_SIZE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `USED_BLOCKS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `UNUSED_BLOCKS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DIRTY_BLOCKS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `READ_REQUESTS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `READS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `WRITE_REQUESTS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `WRITES` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=3258700 ROW_FORMAT=FIXED
;


CREATE TABLE `KEY_COLUMN_USAGE` (
  `CONSTRAINT_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `CONSTRAINT_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `CONSTRAINT_NAME` varchar(64) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `ORDINAL_POSITION` bigint(10) NOT NULL DEFAULT 0,
  `POSITION_IN_UNIQUE_CONSTRAINT` bigint(10) DEFAULT NULL,
  `REFERENCED_TABLE_SCHEMA` varchar(64) DEFAULT NULL,
  `REFERENCED_TABLE_NAME` varchar(64) DEFAULT NULL,
  `REFERENCED_COLUMN_NAME` varchar(64) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=463119 ROW_FORMAT=FIXED
;


CREATE TABLE `LETTER` (
  `ICO` int(11) NOT NULL,
  `MESDOT` varchar(255) DEFAULT NULL,
  `ROKDOT` int(11) DEFAULT NULL,
  `LEKCHOL` int(11) DEFAULT NULL,
  `LEKTK` int(11) DEFAULT NULL,
  `NEMOC1` int(11) DEFAULT NULL,
  `ROK1` int(11) DEFAULT NULL,
  `NEMOC2` varchar(255) DEFAULT NULL,
  `ROK2` varchar(255) DEFAULT NULL,
  `NEMOC3` varchar(255) DEFAULT NULL,
  `ROK3` varchar(255) DEFAULT NULL,
  `NEMOC4` varchar(255) DEFAULT NULL,
  `ROK4` varchar(255) DEFAULT NULL,
  `NEMOC5` varchar(255) DEFAULT NULL,
  `ROK5` varchar(255) DEFAULT NULL,
  `HYPTK` int(11) DEFAULT NULL,
  `ROKHYPTK` varchar(255) DEFAULT NULL,
  `HYPLP` int(11) DEFAULT NULL,
  `ROKHYPLP` varchar(255) DEFAULT NULL,
  `CUKROVKA` int(11) DEFAULT NULL,
  `ROKCUKR` varchar(255) DEFAULT NULL,
  `CUKRTAB` varchar(255) DEFAULT NULL,
  `ODCUTAB` varchar(255) DEFAULT NULL,
  `DOCUTAB` varchar(255) DEFAULT NULL,
  `CUKRINS` varchar(255) DEFAULT NULL,
  `ODCUINS` varchar(255) DEFAULT NULL,
  `DOCUINS` varchar(255) DEFAULT NULL,
  `AP` int(11) DEFAULT NULL,
  `SI` int(11) DEFAULT NULL,
  `ROKSI` varchar(255) DEFAULT NULL,
  `MM` varchar(255) DEFAULT NULL,
  `ROKMM` varchar(255) DEFAULT NULL,
  `BDK` int(11) DEFAULT NULL,
  `ROKBDK1` varchar(255) DEFAULT NULL,
  `DUSNOST` varchar(255) DEFAULT NULL,
  `ROKDUS` varchar(255) DEFAULT NULL,
  `DUSCHUZE` varchar(255) DEFAULT NULL,
  `DUSBEH` varchar(255) DEFAULT NULL,
  `DUSROVIN` varchar(255) DEFAULT NULL,
  `DUKLID` varchar(255) DEFAULT NULL,
  `DUSNOC` varchar(255) DEFAULT NULL,
  `KURAK` varchar(255) DEFAULT NULL,
  `KURAKBYV` varchar(255) DEFAULT NULL,
  `ROKPRKOUR` varchar(255) DEFAULT NULL,
  `KOURLET` varchar(255) DEFAULT NULL,
  `CIGDENMIN` varchar(255) DEFAULT NULL,
  `CIGDEN` varchar(255) DEFAULT NULL,
  `KOURODLET` varchar(255) DEFAULT NULL,
  `DYMKA` varchar(255) DEFAULT NULL,
  `PASED` varchar(255) DEFAULT NULL,
  `PAMIRNA` varchar(255) DEFAULT NULL,
  `PAVELKA` varchar(255) DEFAULT NULL,
  `PAPRED10` varchar(255) DEFAULT NULL,
  `DIETA` varchar(255) DEFAULT NULL,
  `DIECUOD` varchar(255) DEFAULT NULL,
  `DIETUKOD` varchar(255) DEFAULT NULL,
  `JINADIE` varchar(255) DEFAULT NULL,
  `JINADIEOD` varchar(255) DEFAULT NULL,
  `VAHA` varchar(255) DEFAULT NULL,
  `VAHAPRED10` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ICO`),
  KEY `ICO` (`ICO`),
  CONSTRAINT `LETTER_IBFK_1` FOREIGN KEY (`ICO`) REFERENCES `ENTRY` (`ICO`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `LOCATION` (
  `LOCATIONID` smallint(6) NOT NULL COMMENT 'Primary key for Location records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Location description.',
  `COSTRATE` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Standard hourly cost of the manufacturing location.',
  `AVAILABILITY` decimal(8,2) NOT NULL DEFAULT 0.00 COMMENT 'Work capacity (in hours) of the manufacturing location.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`LOCATIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product inventory and manufacturing locations.'
;


CREATE TABLE `L_AIRLINE_ID` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_AIRLINE_ID_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_AIRPORT` (
  `CODE` varchar(255) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_AIRPORT_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_AIRPORT_ID` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_AIRPORT_ID_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_AIRPORT_SEQ_ID` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_AIRPORT_SEQ_ID_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_CANCELLATION` (
  `CODE` varchar(255) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_CANCELLATION_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_CITY_MARKET_ID` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_CITY_MARKET_ID_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_DEPARRBLK` (
  `CODE` varchar(255) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_DEPARRBLK_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_DISTANCE_GROUP_250` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_DISTANCE_GROUP_250_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_DIVERSIONS` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_DIVERSIONS_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_MONTHS` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_MONTHS_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_ONTIME_DELAY_GROUPS` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_ONTIME_DELAY_GROUPS_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_QUARTERS` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_QUARTERS_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_STATE_ABR_AVIATION` (
  `CODE` varchar(255) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_STATE_ABR_AVIATION_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_STATE_FIPS` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_STATE_FIPS_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_UNIQUE_CARRIERS` (
  `CODE` varchar(255) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_UNIQUE_CARRIERS_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_WEEKDAYS` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_WEEKDAYS_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_WORLD_AREA_CODES` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_WORLD_AREA_CODES_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `L_YESNO_RESP` (
  `CODE` int(11) NOT NULL,
  `DESCRIPTION` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`CODE`),
  UNIQUE KEY `L_YESNO_RESP_CODE_KEY` (`CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Location` (
  `LocationID` smallint(6) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for Location records.',
  `Name` varchar(100) NOT NULL COMMENT 'Location description.',
  `CostRate` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Standard hourly cost of the manufacturing location.',
  `Availability` decimal(8,2) NOT NULL DEFAULT 0.00 COMMENT 'Work capacity (in hours) of the manufacturing location.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`LocationID`),
  UNIQUE KEY `AK_Location_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product inventory and manufacturing locations.'
;


CREATE TABLE `MAINSAMPLE` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100085` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100106` int(11) DEFAULT NULL,
  `order_account_id_aggregate_stddev_samp_100008` double(26,4) DEFAULT NULL,
  `trans_amount_aggregate_min_100046` int(11) DEFAULT NULL,
  `trans_balance_aggregate_min_100047` int(11) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  `client_district_id_aggregate_avg_100020` decimal(14,4) DEFAULT NULL,
  `loan_date_directField_timeColumn_100111` date DEFAULT NULL,
  `card_card_id_directField_numericalColumn_100088` int(11) DEFAULT 0,
  `order_account_to_aggregate_avg_100025` decimal(14,4) DEFAULT NULL,
  `trans_account_aggregate_avg_100028` decimal(15,4) DEFAULT NULL,
  `district_A3_directField_nominalColumn_100084` varchar(15) DEFAULT NULL,
  `trans_account_aggregate_stddev_samp_100012` double(28,4) DEFAULT NULL,
  `account_date_directField_timeColumn_100109` date DEFAULT NULL,
  `loan_account_id_directField_numericalColumn_100104` int(11) DEFAULT NULL,
  `client_client_id_aggregate_sum_100067` decimal(32,0) DEFAULT NULL,
  `trans_amount_aggregate_stddev_samp_100014` double(26,4) DEFAULT NULL,
  `order_amount_aggregate_sum_100074` decimal(28,1) DEFAULT NULL,
  `order_amount_aggregate_avg_100026` decimal(10,5) DEFAULT NULL,
  `order_amount_aggregate_min_100042` decimal(6,1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100105` int(11) DEFAULT NULL,
  `order_amount_aggregate_max_100058` decimal(6,1) DEFAULT NULL,
  `trans_amount_aggregate_max_100062` int(11) DEFAULT NULL,
  `district_A15_directField_numericalColumn_100095` int(5) DEFAULT NULL,
  `district_A6_directField_numericalColumn_100099` int(11) DEFAULT NULL,
  `district_A12_directField_numericalColumn_100092` decimal(4,1) DEFAULT NULL,
  `district_A10_directField_numericalColumn_100090` decimal(4,1) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `district_A13_directField_numericalColumn_100093` decimal(3,2) DEFAULT NULL,
  `card_type_directField_nominalColumn_100082` varchar(7) DEFAULT NULL,
  `loan_payments_directField_numericalColumn_100108` decimal(6,2) DEFAULT NULL,
  `client_district_id_aggregate_sum_100068` decimal(32,0) DEFAULT NULL,
  `order_order_id_aggregate_stddev_samp_100011` double(26,4) DEFAULT NULL,
  `district_A14_directField_numericalColumn_100094` int(11) DEFAULT NULL,
  `district_A5_directField_numericalColumn_100098` int(11) DEFAULT NULL,
  `trans_account_aggregate_min_100044` int(11) unsigned DEFAULT NULL,
  `district_A7_directField_numericalColumn_100100` int(11) DEFAULT NULL,
  `district_A9_directField_numericalColumn_100102` int(11) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100009` double(26,4) DEFAULT NULL,
  `district_A8_directField_numericalColumn_100101` int(6) DEFAULT NULL,
  `account_frequency_directField_nominalColumn_100081` varchar(18) DEFAULT '',
  `client_district_id_aggregate_stddev_samp_100002` double(26,4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `MAINSAMPLE_temp100` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100085` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100106` int(11) DEFAULT NULL,
  `order_account_id_aggregate_stddev_samp_100008` double(26,4) DEFAULT NULL,
  `trans_amount_aggregate_min_100046` int(11) DEFAULT NULL,
  `trans_balance_aggregate_min_100047` int(11) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  `client_district_id_aggregate_avg_100020` decimal(14,4) DEFAULT NULL,
  `loan_date_directField_timeColumn_100111` date DEFAULT NULL,
  `card_card_id_directField_numericalColumn_100088` int(11) DEFAULT 0,
  `order_account_to_aggregate_avg_100025` decimal(14,4) DEFAULT NULL,
  `trans_account_aggregate_avg_100028` decimal(15,4) DEFAULT NULL,
  `district_A3_directField_nominalColumn_100084` varchar(15) DEFAULT NULL,
  `trans_account_aggregate_stddev_samp_100012` double(28,4) DEFAULT NULL,
  `account_date_directField_timeColumn_100109` date DEFAULT NULL,
  `loan_account_id_directField_numericalColumn_100104` int(11) DEFAULT NULL,
  `client_client_id_aggregate_sum_100067` decimal(32,0) DEFAULT NULL,
  `trans_amount_aggregate_stddev_samp_100014` double(26,4) DEFAULT NULL,
  `order_amount_aggregate_sum_100074` decimal(28,1) DEFAULT NULL,
  `order_amount_aggregate_avg_100026` decimal(10,5) DEFAULT NULL,
  `order_amount_aggregate_min_100042` decimal(6,1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100105` int(11) DEFAULT NULL,
  `order_amount_aggregate_max_100058` decimal(6,1) DEFAULT NULL,
  `trans_amount_aggregate_max_100062` int(11) DEFAULT NULL,
  `district_A15_directField_numericalColumn_100095` int(5) DEFAULT NULL,
  `district_A6_directField_numericalColumn_100099` int(11) DEFAULT NULL,
  `district_A12_directField_numericalColumn_100092` decimal(4,1) DEFAULT NULL,
  `district_A10_directField_numericalColumn_100090` decimal(4,1) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `district_A13_directField_numericalColumn_100093` decimal(3,2) DEFAULT NULL,
  `card_type_directField_nominalColumn_100082` varchar(7) DEFAULT NULL,
  `loan_payments_directField_numericalColumn_100108` decimal(6,2) DEFAULT NULL,
  `client_district_id_aggregate_sum_100068` decimal(32,0) DEFAULT NULL,
  `order_order_id_aggregate_stddev_samp_100011` double(26,4) DEFAULT NULL,
  `district_A14_directField_numericalColumn_100094` int(11) DEFAULT NULL,
  `district_A5_directField_numericalColumn_100098` int(11) DEFAULT NULL,
  `trans_account_aggregate_min_100044` int(11) unsigned DEFAULT NULL,
  `district_A7_directField_numericalColumn_100100` int(11) DEFAULT NULL,
  `district_A9_directField_numericalColumn_100102` int(11) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100009` double(26,4) DEFAULT NULL,
  `district_A8_directField_numericalColumn_100101` int(6) DEFAULT NULL,
  `account_frequency_directField_nominalColumn_100081` varchar(18) DEFAULT '',
  `client_district_id_aggregate_stddev_samp_100002` double(26,4) DEFAULT NULL,
  KEY `ix_temp100` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `MATCHES` (
  `MID` varchar(255) NOT NULL DEFAULT '',
  `SEASON` int(11) DEFAULT NULL,
  `ROUND` varchar(255) DEFAULT NULL,
  `TID1` int(11) DEFAULT NULL,
  `TID2` int(11) DEFAULT NULL,
  `TID1_LOC` varchar(255) DEFAULT NULL,
  `TID2_LOC` varchar(255) DEFAULT NULL,
  `START_DT` datetime DEFAULT NULL,
  `VENUE` varchar(255) DEFAULT NULL,
  `ATT` int(11) DEFAULT NULL,
  `MARGIN` int(11) DEFAULT NULL,
  `WIN_SCORE` int(11) DEFAULT NULL,
  `WIN_TID` int(11) DEFAULT NULL,
  `WIN_LOC` varchar(255) DEFAULT NULL,
  `LOSE_SCORE` int(11) DEFAULT NULL,
  `LOSE_LOC` varchar(255) DEFAULT NULL,
  `LOSE_TID` int(11) DEFAULT NULL,
  `H_TID` int(11) DEFAULT NULL,
  `H_SCORE` int(11) DEFAULT NULL,
  `H_Q1G` int(11) DEFAULT NULL,
  `H_Q2G` int(11) DEFAULT NULL,
  `H_Q3G` int(11) DEFAULT NULL,
  `H_Q4G` int(11) DEFAULT NULL,
  `H_ETG` int(11) DEFAULT NULL,
  `H_Q1B` int(11) DEFAULT NULL,
  `H_Q2B` int(11) DEFAULT NULL,
  `H_Q3B` int(11) DEFAULT NULL,
  `H_Q4B` int(11) DEFAULT NULL,
  `H_ETB` int(11) DEFAULT NULL,
  `A_TID` int(11) DEFAULT NULL,
  `A_SCORE` int(11) DEFAULT NULL,
  `A_Q1G` int(11) DEFAULT NULL,
  `A_Q2G` int(11) DEFAULT NULL,
  `A_Q3G` int(11) DEFAULT NULL,
  `A_Q4G` int(11) DEFAULT NULL,
  `A_ETG` int(11) DEFAULT NULL,
  `A_Q1B` int(11) DEFAULT NULL,
  `A_Q2B` int(11) DEFAULT NULL,
  `A_Q3B` int(11) DEFAULT NULL,
  `A_Q4B` int(11) DEFAULT NULL,
  `A_ETB` int(11) DEFAULT NULL,
  `TARGET` int(1) DEFAULT NULL,
  PRIMARY KEY (`MID`),
  KEY `TID1` (`TID1`),
  KEY `TID2` (`TID2`),
  CONSTRAINT `MATCHES_IBFK_1` FOREIGN KEY (`TID1`) REFERENCES `TEAMS` (`TID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `MATCHES_IBFK_2` FOREIGN KEY (`TID2`) REFERENCES `TEAMS` (`TID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `MATCH_STATS` (
  `MID` varchar(255) NOT NULL,
  `PID` int(11) NOT NULL,
  `TID` int(11) DEFAULT NULL,
  `LOC` varchar(255) DEFAULT NULL,
  `KI` int(11) DEFAULT NULL,
  `MK` int(11) DEFAULT NULL,
  `HB` int(11) DEFAULT NULL,
  `DI` int(11) DEFAULT NULL,
  `GL` int(11) DEFAULT NULL,
  `BH` int(11) DEFAULT NULL,
  `HO` int(11) DEFAULT NULL,
  `TK` int(11) DEFAULT NULL,
  `RB` int(11) DEFAULT NULL,
  `IF` int(11) DEFAULT NULL,
  `CL` int(11) DEFAULT NULL,
  `CG` int(11) DEFAULT NULL,
  `FF` int(11) DEFAULT NULL,
  `FA` int(11) DEFAULT NULL,
  `BR` int(11) DEFAULT NULL,
  `CP` int(11) DEFAULT NULL,
  `UP` int(11) DEFAULT NULL,
  `CM` int(11) DEFAULT NULL,
  `MI` int(11) DEFAULT NULL,
  `1P` float DEFAULT NULL,
  `BO` int(11) DEFAULT NULL,
  `GA` int(11) DEFAULT NULL,
  `PP` float DEFAULT NULL,
  PRIMARY KEY (`MID`,`PID`),
  KEY `MID` (`MID`),
  KEY `PID` (`PID`),
  KEY `TID` (`TID`),
  CONSTRAINT `MATCH_STATS_IBFK_1` FOREIGN KEY (`PID`) REFERENCES `PLAYERS` (`PID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `MATCH_STATS_IBFK_2` FOREIGN KEY (`TID`) REFERENCES `TEAMS` (`TID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `MATCH_STATS_IBFK_3` FOREIGN KEY (`MID`) REFERENCES `MATCHES` (`MID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `Mailings1_2` (
  `REFID` int(11) NOT NULL,
  `KxIndex` int(11) DEFAULT NULL,
  `REF_DATE` datetime DEFAULT NULL,
  `RESPONSE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`REFID`),
  KEY `Mailings1_2_REFID` (`REFID`),
  CONSTRAINT `Mailings1_2_ibfk_1` FOREIGN KEY (`REFID`) REFERENCES `Customers` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `NESRECA` (
  `ID_NESRECA` char(6) NOT NULL,
  `KLAS_NESRECA` char(1) NOT NULL,
  `UPRAVNA_ENOTA` char(4) NOT NULL,
  `CAS_NESRECA` datetime NOT NULL,
  `NASELJE_ALI_IZVEN` char(1) NOT NULL,
  `KATEGORIJA_CESTA` char(1) DEFAULT NULL,
  `OZNAKA_CESTA_ALI_NASELJE` char(5) NOT NULL,
  `TEKST_CESTA_ALI_NASELJE` varchar(25) NOT NULL,
  `OZNAKA_ODSEK_ALI_ULICA` char(5) NOT NULL,
  `TEKST_ODSEK_ALI_ULICA` varchar(25) NOT NULL,
  `STACIONAZNA_ALI_HISNA_ST` varchar(9) DEFAULT NULL,
  `OPIS_PRIZORISCE` char(1) NOT NULL,
  `VZROK_NESRECA` char(2) NOT NULL,
  `TIP_NESRECA` char(2) NOT NULL,
  `VREME_NESRECA` char(1) NOT NULL,
  `STANJE_PROMET` char(1) NOT NULL,
  `STANJE_VOZISCE` char(2) NOT NULL,
  `STANJE_POVRSINA_VOZISCE` char(2) NOT NULL,
  `X` int(11) DEFAULT NULL,
  `Y` int(11) DEFAULT NULL,
  `X_WGS84` double DEFAULT NULL,
  `Y_WGS84` double DEFAULT NULL,
  PRIMARY KEY (`ID_NESRECA`),
  KEY `NESRECA_CAS_NESRECA_IDX` (`CAS_NESRECA`),
  KEY `NESRECA_POS_IDX` (`X`,`Y`),
  KEY `NESRECA_POS_WGS_84` (`X_WGS84`,`Y_WGS84`),
  KEY `UPRAVNA_ENOTA` (`UPRAVNA_ENOTA`),
  CONSTRAINT `NESRECA_IBFK_1` FOREIGN KEY (`UPRAVNA_ENOTA`) REFERENCES `UPRAVNA_ENOTA` (`ID_UPRAVNA_ENOTA`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ON_TIME_ON_TIME_PERFORMANCE_2016_1` (
  `YEAR` int(11) DEFAULT NULL,
  `QUARTER` int(11) DEFAULT NULL,
  `MONTH` int(11) DEFAULT NULL,
  `DAYOFMONTH` int(11) DEFAULT NULL,
  `DAYOFWEEK` int(11) DEFAULT NULL,
  `FLIGHTDATE` date DEFAULT NULL,
  `UNIQUECARRIER` char(2) DEFAULT NULL,
  `AIRLINEID` int(11) NOT NULL,
  `CARRIER` char(2) DEFAULT NULL,
  `TAILNUM` varchar(6) DEFAULT NULL,
  `FLIGHTNUM` int(11) DEFAULT NULL,
  `ORIGINAIRPORTID` int(11) DEFAULT NULL,
  `ORIGINAIRPORTSEQID` int(11) DEFAULT NULL,
  `ORIGINCITYMARKETID` int(11) DEFAULT NULL,
  `ORIGIN` char(3) DEFAULT NULL,
  `ORIGINCITYNAME` varchar(34) DEFAULT NULL,
  `ORIGINSTATE` char(2) DEFAULT NULL,
  `ORIGINSTATEFIPS` int(11) DEFAULT NULL,
  `ORIGINSTATENAME` varchar(46) DEFAULT NULL,
  `ORIGINWAC` int(11) DEFAULT NULL,
  `DESTAIRPORTID` int(11) DEFAULT NULL,
  `DESTAIRPORTSEQID` int(11) DEFAULT NULL,
  `DESTCITYMARKETID` int(11) DEFAULT NULL,
  `DEST` char(3) DEFAULT NULL,
  `DESTCITYNAME` varchar(34) DEFAULT NULL,
  `DESTSTATE` char(2) DEFAULT NULL,
  `DESTSTATEFIPS` int(11) DEFAULT NULL,
  `DESTSTATENAME` varchar(46) DEFAULT NULL,
  `DESTWAC` int(11) DEFAULT NULL,
  `CRSDEPTIME` int(11) DEFAULT NULL,
  `DEPTIME` int(11) DEFAULT NULL,
  `DEPDELAY` decimal(65,2) DEFAULT NULL,
  `DEPDELAYMINUTES` float DEFAULT NULL,
  `DEPDEL15` int(11) DEFAULT NULL,
  `DEPARTUREDELAYGROUPS` int(11) DEFAULT NULL,
  `DEPTIMEBLK` char(9) DEFAULT NULL,
  `TAXIOUT` float DEFAULT NULL,
  `WHEELSOFF` int(11) DEFAULT NULL,
  `WHEELSON` int(11) DEFAULT NULL,
  `TAXIIN` float DEFAULT NULL,
  `CRSARRTIME` int(11) DEFAULT NULL,
  `ARRTIME` int(11) DEFAULT NULL,
  `ARRDELAY` decimal(65,2) DEFAULT NULL,
  `ARRDELAYMINUTES` float DEFAULT NULL,
  `ARRDEL15` int(11) DEFAULT NULL,
  `ARRIVALDELAYGROUPS` int(11) DEFAULT NULL,
  `ARRTIMEBLK` char(9) DEFAULT NULL,
  `CANCELLED` int(11) DEFAULT NULL,
  `CANCELLATIONCODE` char(1) DEFAULT NULL,
  `DIVERTED` int(11) DEFAULT NULL,
  `CRSELAPSEDTIME` float DEFAULT NULL,
  `ACTUALELAPSEDTIME` float DEFAULT NULL,
  `AIRTIME` float DEFAULT NULL,
  `FLIGHTS` float DEFAULT NULL,
  `DISTANCE` float DEFAULT NULL,
  `DISTANCEGROUP` int(11) DEFAULT NULL,
  `CARRIERDELAY` decimal(65,2) DEFAULT NULL,
  `WEATHERDELAY` decimal(65,2) DEFAULT NULL,
  `NASDELAY` decimal(65,2) DEFAULT NULL,
  `SECURITYDELAY` decimal(65,2) DEFAULT NULL,
  `LATEAIRCRAFTDELAY` decimal(65,2) DEFAULT NULL,
  `FIRSTDEPTIME` decimal(65,2) DEFAULT NULL,
  `TOTALADDGTIME` decimal(65,2) DEFAULT NULL,
  `LONGESTADDGTIME` decimal(65,2) DEFAULT NULL,
  `DIVAIRPORTLANDINGS` int(11) DEFAULT NULL,
  `DIVREACHEDDEST` decimal(65,2) DEFAULT NULL,
  `DIVACTUALELAPSEDTIME` decimal(65,2) DEFAULT NULL,
  `DIVARRDELAY` decimal(65,2) DEFAULT NULL,
  `DIVDISTANCE` decimal(65,2) DEFAULT NULL,
  `DIV1AIRPORT` char(3) DEFAULT NULL,
  `DIV1AIRPORTID` int(11) DEFAULT NULL,
  `DIV1AIRPORTSEQID` int(11) DEFAULT NULL,
  `DIV1WHEELSON` decimal(65,2) DEFAULT NULL,
  `DIV1TOTALGTIME` decimal(65,2) DEFAULT NULL,
  `DIV1LONGESTGTIME` decimal(65,2) DEFAULT NULL,
  `DIV1WHEELSOFF` decimal(65,2) DEFAULT NULL,
  `DIV1TAILNUM` varchar(6) DEFAULT NULL,
  `DIV2AIRPORT` char(3) DEFAULT NULL,
  `DIV2AIRPORTID` int(11) DEFAULT NULL,
  `DIV2AIRPORTSEQID` int(11) DEFAULT NULL,
  `DIV2WHEELSON` decimal(65,2) DEFAULT NULL,
  `DIV2TOTALGTIME` decimal(65,2) DEFAULT NULL,
  `DIV2LONGESTGTIME` decimal(65,2) DEFAULT NULL,
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIVAIRPORTLANDINGS_FKEY` (`DIVAIRPORTLANDINGS`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEPARTUREDELAYGROUPS_FKEY` (`DEPARTUREDELAYGROUPS`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ARRIVALDELAYGROUPS_FKEY` (`ARRIVALDELAYGROUPS`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV1AIRPORTSEQID_FKEY` (`DIV1AIRPORTSEQID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV2AIRPORTSEQID_FKEY` (`DIV2AIRPORTSEQID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV1AIRPORTID_FKEY` (`DIV1AIRPORTID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV2AIRPORTID_FKEY` (`DIV2AIRPORTID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIVERTED_FKEY` (`DIVERTED`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_CANCELLED_FKEY` (`CANCELLED`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ARRDEL15_FKEY` (`ARRDEL15`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEPDEL15_FKEY` (`DEPDEL15`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_CANCELLATIONCODE_FKEY` (`CANCELLATIONCODE`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEPTIMEBLK_FKEY` (`DEPTIMEBLK`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTSTATE_FKEY` (`DESTSTATE`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEST_FKEY` (`DEST`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINSTATE_FKEY` (`ORIGINSTATE`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGIN_FKEY` (`ORIGIN`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_UNIQUECARRIER_FKEY` (`UNIQUECARRIER`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTSTATEFIPS_FKEY` (`DESTSTATEFIPS`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINSTATEFIPS_FKEY` (`ORIGINSTATEFIPS`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINWAC_FKEY` (`ORIGINWAC`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTWAC_FKEY` (`DESTWAC`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DAYOFWEEK_FKEY` (`DAYOFWEEK`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DISTANCEGROUP_FKEY` (`DISTANCEGROUP`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_QUARTER_FKEY` (`QUARTER`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_MONTH_FKEY` (`MONTH`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTCITYMARKETID_FKEY` (`DESTCITYMARKETID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINCITYMARKETID_FKEY` (`ORIGINCITYMARKETID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTAIRPORTSEQID_FKEY` (`DESTAIRPORTSEQID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINAIRPORTSEQID_FKEY` (`ORIGINAIRPORTSEQID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTAIRPORTID_FKEY` (`DESTAIRPORTID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINAIRPORTID_FKEY` (`ORIGINAIRPORTID`),
  KEY `ON_TIME_ON_TIME_PERFORMANCE_2016_1_AIRLINEID_FKEY` (`AIRLINEID`),
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_AIRLINEID_FKEY` FOREIGN KEY (`AIRLINEID`) REFERENCES `L_AIRLINE_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ARRDEL15_FKEY` FOREIGN KEY (`ARRDEL15`) REFERENCES `L_YESNO_RESP` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ARRIVALDELAYGROUPS_FKEY` FOREIGN KEY (`ARRIVALDELAYGROUPS`) REFERENCES `L_ONTIME_DELAY_GROUPS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_CANCELLATIONCODE_FKEY` FOREIGN KEY (`CANCELLATIONCODE`) REFERENCES `L_CANCELLATION` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_CANCELLED_FKEY` FOREIGN KEY (`CANCELLED`) REFERENCES `L_YESNO_RESP` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DAYOFWEEK_FKEY` FOREIGN KEY (`DAYOFWEEK`) REFERENCES `L_WEEKDAYS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEPARTUREDELAYGROUPS_FKEY` FOREIGN KEY (`DEPARTUREDELAYGROUPS`) REFERENCES `L_ONTIME_DELAY_GROUPS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEPDEL15_FKEY` FOREIGN KEY (`DEPDEL15`) REFERENCES `L_YESNO_RESP` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEPTIMEBLK_FKEY` FOREIGN KEY (`DEPTIMEBLK`) REFERENCES `L_DEPARRBLK` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTAIRPORTID_FKEY` FOREIGN KEY (`DESTAIRPORTID`) REFERENCES `L_AIRPORT_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTAIRPORTSEQID_FKEY` FOREIGN KEY (`DESTAIRPORTSEQID`) REFERENCES `L_AIRPORT_SEQ_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTCITYMARKETID_FKEY` FOREIGN KEY (`DESTCITYMARKETID`) REFERENCES `L_CITY_MARKET_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTSTATEFIPS_FKEY` FOREIGN KEY (`DESTSTATEFIPS`) REFERENCES `L_STATE_FIPS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTSTATE_FKEY` FOREIGN KEY (`DESTSTATE`) REFERENCES `L_STATE_ABR_AVIATION` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DESTWAC_FKEY` FOREIGN KEY (`DESTWAC`) REFERENCES `L_WORLD_AREA_CODES` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DEST_FKEY` FOREIGN KEY (`DEST`) REFERENCES `L_AIRPORT` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DISTANCEGROUP_FKEY` FOREIGN KEY (`DISTANCEGROUP`) REFERENCES `L_DISTANCE_GROUP_250` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV1AIRPORTID_FKEY` FOREIGN KEY (`DIV1AIRPORTID`) REFERENCES `L_AIRPORT_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV1AIRPORTSEQID_FKEY` FOREIGN KEY (`DIV1AIRPORTSEQID`) REFERENCES `L_AIRPORT_SEQ_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV2AIRPORTID_FKEY` FOREIGN KEY (`DIV2AIRPORTID`) REFERENCES `L_AIRPORT_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIV2AIRPORTSEQID_FKEY` FOREIGN KEY (`DIV2AIRPORTSEQID`) REFERENCES `L_AIRPORT_SEQ_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIVAIRPORTLANDINGS_FKEY` FOREIGN KEY (`DIVAIRPORTLANDINGS`) REFERENCES `L_DIVERSIONS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_DIVERTED_FKEY` FOREIGN KEY (`DIVERTED`) REFERENCES `L_YESNO_RESP` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_MONTH_FKEY` FOREIGN KEY (`MONTH`) REFERENCES `L_MONTHS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINAIRPORTID_FKEY` FOREIGN KEY (`ORIGINAIRPORTID`) REFERENCES `L_AIRPORT_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINAIRPORTSEQID_FKEY` FOREIGN KEY (`ORIGINAIRPORTSEQID`) REFERENCES `L_AIRPORT_SEQ_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINCITYMARKETID_FKEY` FOREIGN KEY (`ORIGINCITYMARKETID`) REFERENCES `L_CITY_MARKET_ID` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINSTATEFIPS_FKEY` FOREIGN KEY (`ORIGINSTATEFIPS`) REFERENCES `L_STATE_FIPS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINSTATE_FKEY` FOREIGN KEY (`ORIGINSTATE`) REFERENCES `L_STATE_ABR_AVIATION` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGINWAC_FKEY` FOREIGN KEY (`ORIGINWAC`) REFERENCES `L_WORLD_AREA_CODES` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_ORIGIN_FKEY` FOREIGN KEY (`ORIGIN`) REFERENCES `L_AIRPORT` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_QUARTER_FKEY` FOREIGN KEY (`QUARTER`) REFERENCES `L_QUARTERS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `ON_TIME_ON_TIME_PERFORMANCE_2016_1_UNIQUECARRIER_FKEY` FOREIGN KEY (`UNIQUECARRIER`) REFERENCES `L_UNIQUE_CARRIERS` (`CODE`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `OSEBA` (
  `ID_NESRECA` char(6) NOT NULL,
  `POVZROCITELJ_ALI_UDELEZENEC` char(1) DEFAULT NULL,
  `STAROST` tinyint(3) unsigned DEFAULT NULL,
  `SPOL` char(1) NOT NULL,
  `UPRAVNA_ENOTA` char(4) NOT NULL,
  `DRZAVLJANSTVO` char(3) NOT NULL,
  `POSKODBA` char(1) DEFAULT NULL,
  `VRSTA_UDELEZENCA` char(2) DEFAULT NULL,
  `VARNOSTNI_PAS_ALI_CELADA` char(1) DEFAULT NULL,
  `VOZNISKI_STAZ_LL` tinyint(3) unsigned DEFAULT NULL,
  `VOZNISKI_STAZ_MM` tinyint(3) unsigned DEFAULT NULL,
  `ALKOTEST` decimal(3,2) DEFAULT NULL,
  `STROKOVNI_PREGLED` decimal(3,2) DEFAULT NULL,
  `STAROST_D` char(1) DEFAULT NULL,
  `VOZNISKI_STAZ_D` char(1) NOT NULL,
  `ALKOTEST_D` char(1) NOT NULL,
  `STROKOVNI_PREGLED_D` char(1) NOT NULL,
  KEY `OSEBA_ID_NESRECA` (`ID_NESRECA`),
  KEY `UPRAVNA_ENOTA` (`UPRAVNA_ENOTA`),
  CONSTRAINT `OSEBA_IBFK_1` FOREIGN KEY (`ID_NESRECA`) REFERENCES `NESRECA` (`ID_NESRECA`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `OSEBA_IBFK_2` FOREIGN KEY (`UPRAVNA_ENOTA`) REFERENCES `UPRAVNA_ENOTA` (`ID_UPRAVNA_ENOTA`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PARAMETERS` (
  `SPECIFIC_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `SPECIFIC_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `SPECIFIC_NAME` varchar(64) NOT NULL DEFAULT '',
  `ORDINAL_POSITION` int(21) NOT NULL DEFAULT 0,
  `PARAMETER_MODE` varchar(5) DEFAULT NULL,
  `PARAMETER_NAME` varchar(64) DEFAULT NULL,
  `DATA_TYPE` varchar(64) NOT NULL DEFAULT '',
  `CHARACTER_MAXIMUM_LENGTH` int(21) DEFAULT NULL,
  `CHARACTER_OCTET_LENGTH` int(21) DEFAULT NULL,
  `NUMERIC_PRECISION` int(21) DEFAULT NULL,
  `NUMERIC_SCALE` int(21) DEFAULT NULL,
  `DATETIME_PRECISION` bigint(21) unsigned DEFAULT NULL,
  `CHARACTER_SET_NAME` varchar(64) DEFAULT NULL,
  `COLLATION_NAME` varchar(64) DEFAULT NULL,
  `DTD_IDENTIFIER` longtext NOT NULL,
  `ROUTINE_TYPE` varchar(9) NOT NULL DEFAULT ''
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=771920 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `PARTITIONS` (
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `PARTITION_NAME` varchar(64) DEFAULT NULL,
  `SUBPARTITION_NAME` varchar(64) DEFAULT NULL,
  `PARTITION_ORDINAL_POSITION` bigint(21) unsigned DEFAULT NULL,
  `SUBPARTITION_ORDINAL_POSITION` bigint(21) unsigned DEFAULT NULL,
  `PARTITION_METHOD` varchar(18) DEFAULT NULL,
  `SUBPARTITION_METHOD` varchar(12) DEFAULT NULL,
  `PARTITION_EXPRESSION` longtext DEFAULT NULL,
  `SUBPARTITION_EXPRESSION` longtext DEFAULT NULL,
  `PARTITION_DESCRIPTION` longtext DEFAULT NULL,
  `TABLE_ROWS` bigint(21) unsigned NOT NULL DEFAULT 0,
  `AVG_ROW_LENGTH` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DATA_LENGTH` bigint(21) unsigned NOT NULL DEFAULT 0,
  `MAX_DATA_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `INDEX_LENGTH` bigint(21) unsigned NOT NULL DEFAULT 0,
  `DATA_FREE` bigint(21) unsigned NOT NULL DEFAULT 0,
  `CREATE_TIME` datetime DEFAULT NULL,
  `UPDATE_TIME` datetime DEFAULT NULL,
  `CHECK_TIME` datetime DEFAULT NULL,
  `CHECKSUM` bigint(21) unsigned DEFAULT NULL,
  `PARTITION_COMMENT` varchar(80) NOT NULL DEFAULT '',
  `NODEGROUP` varchar(12) NOT NULL DEFAULT '',
  `TABLESPACE_NAME` varchar(64) DEFAULT NULL
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=714161 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `PASSWORD` (
  `BUSINESSENTITYID` int(11) NOT NULL,
  `PASSWORDHASH` varchar(128) NOT NULL COMMENT 'Password for the e-mail account.',
  `PASSWORDSALT` varchar(10) NOT NULL COMMENT 'Random value concatenated with the password string before the password is hashed.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='One way hashed authentication information'
;


CREATE TABLE `PERSON` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key for Person records.',
  `PERSONTYPE` char(2) NOT NULL COMMENT 'Primary type of person: SC = Store Contact, IN = Individual (retail) customer, SP = Sales person, EM = Employee (non-sales), VC = Vendor contact, GC = General contact',
  `NAMESTYLE` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = The data in FirstName and LastName are stored in western style (first name, last name) order.  1 = Eastern style (last name, first name) order.',
  `TITLE` varchar(8) DEFAULT NULL COMMENT 'A courtesy title. For example, Mr. or Ms.',
  `FIRSTNAME` varchar(100) NOT NULL COMMENT 'First name of the person.',
  `MIDDLENAME` varchar(100) DEFAULT NULL COMMENT 'Middle name or middle initial of the person.',
  `LASTNAME` varchar(100) NOT NULL COMMENT 'Last name of the person.',
  `SUFFIX` varchar(10) DEFAULT NULL COMMENT 'Surname suffix. For example, Sr. or Jr.',
  `EMAILPROMOTION` int(11) NOT NULL DEFAULT 0 COMMENT '0 = Contact does not wish to receive e-mail promotions, 1 = Contact does wish to receive e-mail promotions from AdventureWorks, 2 = Contact does wish to receive e-mail promotions from AdventureWorks and selected partners. ',
  `ADDITIONALCONTACTINFO` text DEFAULT NULL COMMENT 'Additional contact information about the person stored in xml format. ',
  `DEMOGRAPHICS` text DEFAULT NULL COMMENT 'Personal information such as hobbies, and income collected from online shoppers. Used for sales analysis.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Human beings involved with AdventureWorks: employees, customer contacts, and vendor contacts.'
;


CREATE TABLE `PERSONCREDITCARD` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Business entity identification number. Foreign key to Person.BusinessEntityID.',
  `CREDITCARDID` int(11) NOT NULL COMMENT 'Credit card identification number. Foreign key to CreditCard.CreditCardID.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`CREDITCARDID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping people to their credit card information in the CreditCard table. '
;


CREATE TABLE `PERSONPHONE` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Business entity identification number. Foreign key to Person.BusinessEntityID.',
  `PHONENUMBER` varchar(50) NOT NULL COMMENT 'Telephone number identification number.',
  `PHONENUMBERTYPEID` int(11) NOT NULL COMMENT 'Kind of phone number. Foreign key to PhoneNumberType.PhoneNumberTypeID.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`PHONENUMBER`,`PHONENUMBERTYPEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Telephone number and type of a person.'
;


CREATE TABLE `PHONENUMBERTYPE` (
  `PHONENUMBERTYPEID` int(11) NOT NULL COMMENT 'Primary key for telephone number type records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Name of the telephone number type',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PHONENUMBERTYPEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Type of phone number of a person.'
;


CREATE TABLE `PLAYERS` (
  `PID` int(11) NOT NULL,
  `DOB` datetime DEFAULT NULL,
  `FIRST_NAME` varchar(255) DEFAULT NULL,
  `LAST_NAME` varchar(255) DEFAULT NULL,
  `HEIGHT` int(11) DEFAULT NULL,
  `WEIGHT` int(11) DEFAULT NULL,
  PRIMARY KEY (`PID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `PLUGINS` (
  `PLUGIN_NAME` varchar(64) NOT NULL DEFAULT '',
  `PLUGIN_VERSION` varchar(20) NOT NULL DEFAULT '',
  `PLUGIN_STATUS` varchar(16) NOT NULL DEFAULT '',
  `PLUGIN_TYPE` varchar(80) NOT NULL DEFAULT '',
  `PLUGIN_TYPE_VERSION` varchar(20) NOT NULL DEFAULT '',
  `PLUGIN_LIBRARY` varchar(64) DEFAULT NULL,
  `PLUGIN_LIBRARY_VERSION` varchar(20) DEFAULT NULL,
  `PLUGIN_AUTHOR` varchar(64) DEFAULT NULL,
  `PLUGIN_DESCRIPTION` longtext DEFAULT NULL,
  `PLUGIN_LICENSE` varchar(80) NOT NULL DEFAULT '',
  `LOAD_OPTION` varchar(64) NOT NULL DEFAULT '',
  `PLUGIN_MATURITY` varchar(12) NOT NULL DEFAULT '',
  `PLUGIN_AUTH_VERSION` varchar(80) DEFAULT NULL
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1208488 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `PREDICTOR100001` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100002` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `client_district_id_aggregate_stddev_samp_100002` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100003` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100008` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_account_id_aggregate_stddev_samp_100008` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100009` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100009` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100011` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_order_id_aggregate_stddev_samp_100011` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100012` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_stddev_samp_100012` double(28,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100014` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_amount_aggregate_stddev_samp_100014` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100020` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `client_district_id_aggregate_avg_100020` decimal(14,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100025` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_account_to_aggregate_avg_100025` decimal(14,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100026` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_avg_100026` decimal(10,5) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100028` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_avg_100028` decimal(15,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100042` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_min_100042` decimal(6,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100044` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_min_100044` int(11) unsigned DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100046` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_amount_aggregate_min_100046` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100047` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_balance_aggregate_min_100047` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100058` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_max_100058` decimal(6,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100062` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_amount_aggregate_max_100062` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100067` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `client_client_id_aggregate_sum_100067` decimal(32,0) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100068` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `client_district_id_aggregate_sum_100068` decimal(32,0) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100074` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_sum_100074` decimal(28,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100081` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `account_frequency_directField_nominalColumn_100081` varchar(18) DEFAULT '',
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100082` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `card_type_directField_nominalColumn_100082` varchar(7) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100084` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A3_directField_nominalColumn_100084` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100085` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100085` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100088` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `card_card_id_directField_numericalColumn_100088` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100090` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A10_directField_numericalColumn_100090` decimal(4,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100092` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A12_directField_numericalColumn_100092` decimal(4,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100093` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A13_directField_numericalColumn_100093` decimal(3,2) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100094` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A14_directField_numericalColumn_100094` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100095` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A15_directField_numericalColumn_100095` int(5) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100098` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A5_directField_numericalColumn_100098` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100099` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A6_directField_numericalColumn_100099` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100100` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A7_directField_numericalColumn_100100` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100101` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A8_directField_numericalColumn_100101` int(6) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100102` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_A9_directField_numericalColumn_100102` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100104` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_account_id_directField_numericalColumn_100104` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100105` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100105` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100106` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100106` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100108` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_payments_directField_numericalColumn_100108` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100109` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `account_date_directField_timeColumn_100109` date DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PREDICTOR100111` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_date_directField_timeColumn_100111` date DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `PROCESSLIST` (
  `ID` bigint(4) NOT NULL DEFAULT 0,
  `USER` varchar(128) NOT NULL DEFAULT '',
  `HOST` varchar(64) NOT NULL DEFAULT '',
  `DB` varchar(64) DEFAULT NULL,
  `COMMAND` varchar(16) NOT NULL DEFAULT '',
  `TIME` int(7) NOT NULL DEFAULT 0,
  `STATE` varchar(64) DEFAULT NULL,
  `INFO` longtext DEFAULT NULL,
  `TIME_MS` decimal(22,3) NOT NULL DEFAULT 0.000,
  `STAGE` tinyint(2) NOT NULL DEFAULT 0,
  `MAX_STAGE` tinyint(2) NOT NULL DEFAULT 0,
  `PROGRESS` decimal(7,3) NOT NULL DEFAULT 0.000,
  `MEMORY_USED` int(7) NOT NULL DEFAULT 0,
  `EXAMINED_ROWS` int(7) NOT NULL DEFAULT 0,
  `QUERY_ID` bigint(4) NOT NULL DEFAULT 0
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=2003249 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `PRODUCT` (
  `PRODUCTID` int(11) NOT NULL COMMENT 'Primary key for Product records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Name of the product.',
  `PRODUCTNUMBER` varchar(25) NOT NULL COMMENT 'Unique product identification number.',
  `MAKEFLAG` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Product is purchased, 1 = Product is manufactured in-house.',
  `FINISHEDGOODSFLAG` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Product is not a salable item. 1 = Product is salable.',
  `COLOR` varchar(15) DEFAULT NULL COMMENT 'Product color.',
  `SAFETYSTOCKLEVEL` smallint(6) NOT NULL COMMENT 'Minimum inventory quantity. ',
  `REORDERPOINT` smallint(6) NOT NULL COMMENT 'Inventory level that triggers a purchase order or work order. ',
  `STANDARDCOST` decimal(19,4) NOT NULL COMMENT 'Standard cost of the product.',
  `LISTPRICE` decimal(19,4) NOT NULL COMMENT 'Selling price.',
  `SIZE` varchar(5) DEFAULT NULL COMMENT 'Product size.',
  `SIZEUNITMEASURECODE` char(3) DEFAULT NULL COMMENT 'Unit of measure for Size column.',
  `WEIGHTUNITMEASURECODE` char(3) DEFAULT NULL COMMENT 'Unit of measure for Weight column.',
  `WEIGHT` decimal(8,2) DEFAULT NULL COMMENT 'Product weight.',
  `DAYSTOMANUFACTURE` int(11) NOT NULL COMMENT 'Number of days required to manufacture the product.',
  `PRODUCTLINE` char(2) DEFAULT NULL COMMENT 'R = Road, M = Mountain, T = Touring, S = Standard',
  `CLASS` char(2) DEFAULT NULL COMMENT 'H = High, M = Medium, L = Low',
  `STYLE` char(2) DEFAULT NULL COMMENT 'W = Womens, M = Mens, U = Universal',
  `PRODUCTSUBCATEGORYID` int(11) DEFAULT NULL COMMENT 'Product is a member of this product subcategory. Foreign key to ProductSubCategory.ProductSubCategoryID. ',
  `PRODUCTMODELID` int(11) DEFAULT NULL COMMENT 'Product is a member of this product model. Foreign key to ProductModel.ProductModelID.',
  `SELLSTARTDATE` datetime NOT NULL COMMENT 'Date the product was available for sale.',
  `SELLENDDATE` datetime DEFAULT NULL COMMENT 'Date the product was no longer available for sale.',
  `DISCONTINUEDDATE` datetime DEFAULT NULL COMMENT 'Date the product was discontinued.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Products sold or used in the manfacturing of sold products.'
;


CREATE TABLE `PRODUCTCATEGORY` (
  `PRODUCTCATEGORYID` int(11) NOT NULL COMMENT 'Primary key for ProductCategory records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Category description.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTCATEGORYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='High-level product categorization.'
;


CREATE TABLE `PRODUCTCOSTHISTORY` (
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID',
  `STARTDATE` datetime NOT NULL COMMENT 'Product cost start date.',
  `ENDDATE` datetime DEFAULT NULL COMMENT 'Product cost end date.',
  `STANDARDCOST` decimal(19,4) NOT NULL COMMENT 'Standard cost of the product.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTID`,`STARTDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Changes in the cost of a product over time.'
;


CREATE TABLE `PRODUCTDESCRIPTION` (
  `PRODUCTDESCRIPTIONID` int(11) NOT NULL COMMENT 'Primary key for ProductDescription records.',
  `DESCRIPTION` varchar(400) NOT NULL COMMENT 'Description of the product.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTDESCRIPTIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product descriptions in several languages.'
;


CREATE TABLE `PRODUCTDOCUMENT` (
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `DOCUMENTNODE` varchar(255) NOT NULL COMMENT 'Document identification number. Foreign key to Document.DocumentNode.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTID`,`DOCUMENTNODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products to related product documents.'
;


CREATE TABLE `PRODUCTINVENTORY` (
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `LOCATIONID` smallint(6) NOT NULL COMMENT 'Inventory location identification number. Foreign key to Location.LocationID. ',
  `SHELF` varchar(10) NOT NULL COMMENT 'Storage compartment within an inventory location.',
  `BIN` tinyint(3) unsigned NOT NULL COMMENT 'Storage container on a shelf in an inventory location.',
  `QUANTITY` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Quantity of products in the inventory location.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTID`,`LOCATIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product inventory information.'
;


CREATE TABLE `PRODUCTLISTPRICEHISTORY` (
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID',
  `STARTDATE` datetime NOT NULL COMMENT 'List price start date.',
  `ENDDATE` datetime DEFAULT NULL COMMENT 'List price end date',
  `LISTPRICE` decimal(19,4) NOT NULL COMMENT 'Product list price.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTID`,`STARTDATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Changes in the list price of a product over time.'
;


CREATE TABLE `PRODUCTMODEL` (
  `PRODUCTMODELID` int(11) NOT NULL COMMENT 'Primary key for ProductModel records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Product model description.',
  `CATALOGDESCRIPTION` text DEFAULT NULL COMMENT 'Detailed product catalog information in xml format.',
  `INSTRUCTIONS` text DEFAULT NULL COMMENT 'Manufacturing instructions in xml format.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTMODELID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product model classification.'
;


CREATE TABLE `PRODUCTMODELILLUSTRATION` (
  `PRODUCTMODELID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductModel.ProductModelID.',
  `ILLUSTRATIONID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Illustration.IllustrationID.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTMODELID`,`ILLUSTRATIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping product models and illustrations.'
;


CREATE TABLE `PRODUCTMODELPRODUCTDESCRIPTIONCULTURE` (
  `PRODUCTMODELID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductModel.ProductModelID.',
  `PRODUCTDESCRIPTIONID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductDescription.ProductDescriptionID.',
  `CULTUREID` char(6) NOT NULL COMMENT 'Culture identification number. Foreign key to Culture.CultureID.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTMODELID`,`PRODUCTDESCRIPTIONID`,`CULTUREID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping product descriptions and the language the description is written in.'
;


CREATE TABLE `PRODUCTPHOTO` (
  `PRODUCTPHOTOID` int(11) NOT NULL COMMENT 'Primary key for ProductPhoto records.',
  `THUMBNAILPHOTO` longblob DEFAULT NULL COMMENT 'Small image of the product.',
  `THUMBNAILPHOTOFILENAME` varchar(50) DEFAULT NULL COMMENT 'Small image file name.',
  `LARGEPHOTO` longblob DEFAULT NULL COMMENT 'Large image of the product.',
  `LARGEPHOTOFILENAME` varchar(50) DEFAULT NULL COMMENT 'Large image file name.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTPHOTOID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product images.'
;


CREATE TABLE `PRODUCTPRODUCTPHOTO` (
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `PRODUCTPHOTOID` int(11) NOT NULL COMMENT 'Product photo identification number. Foreign key to ProductPhoto.ProductPhotoID.',
  `PRIMARY` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = Photo is not the principal image. 1 = Photo is the principal image.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTID`,`PRODUCTPHOTOID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products and product photos.'
;


CREATE TABLE `PRODUCTREVIEW` (
  `PRODUCTREVIEWID` int(11) NOT NULL COMMENT 'Primary key for ProductReview records.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `REVIEWERNAME` varchar(100) NOT NULL COMMENT 'Name of the reviewer.',
  `REVIEWDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date review was submitted.',
  `EMAILADDRESS` varchar(50) NOT NULL COMMENT 'Reviewer''s e-mail address.',
  `RATING` int(11) NOT NULL COMMENT 'Product rating given by the reviewer. Scale is 1 to 5 with 5 as the highest rating.',
  `COMMENTS` varchar(3850) DEFAULT NULL COMMENT 'Reviewer''s comments',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTREVIEWID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customer reviews of products they have purchased.'
;


CREATE TABLE `PRODUCTSUBCATEGORY` (
  `PRODUCTSUBCATEGORYID` int(11) NOT NULL COMMENT 'Primary key for ProductSubcategory records.',
  `PRODUCTCATEGORYID` int(11) NOT NULL COMMENT 'Product category identification number. Foreign key to ProductCategory.ProductCategoryID.',
  `NAME` varchar(100) NOT NULL COMMENT 'Subcategory description.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTSUBCATEGORYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product subcategories. See ProductCategory table.'
;


CREATE TABLE `PRODUCTVENDOR` (
  `PRODUCTID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Product.ProductID.',
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Vendor.BusinessEntityID.',
  `AVERAGELEADTIME` int(11) NOT NULL COMMENT 'The average span of time (in days) between placing an order with the vendor and receiving the purchased product.',
  `STANDARDPRICE` decimal(19,4) NOT NULL COMMENT 'The vendor''s usual selling price.',
  `LASTRECEIPTCOST` decimal(19,4) DEFAULT NULL COMMENT 'The selling price when last purchased.',
  `LASTRECEIPTDATE` datetime DEFAULT NULL COMMENT 'Date the product was last received by the vendor.',
  `MINORDERQTY` int(11) NOT NULL COMMENT 'The maximum quantity that should be ordered.',
  `MAXORDERQTY` int(11) NOT NULL COMMENT 'The minimum quantity that should be ordered.',
  `ONORDERQTY` int(11) DEFAULT NULL COMMENT 'The quantity currently on order.',
  `UNITMEASURECODE` char(3) NOT NULL COMMENT 'The product''s unit of measure.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PRODUCTID`,`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping vendors with the products they supply.'
;


CREATE TABLE `PROFILING` (
  `QUERY_ID` int(20) NOT NULL DEFAULT 0,
  `SEQ` int(20) NOT NULL DEFAULT 0,
  `STATE` varchar(30) NOT NULL DEFAULT '',
  `DURATION` decimal(9,6) NOT NULL DEFAULT 0.000000,
  `CPU_USER` decimal(9,6) DEFAULT NULL,
  `CPU_SYSTEM` decimal(9,6) DEFAULT NULL,
  `CONTEXT_VOLUNTARY` int(20) DEFAULT NULL,
  `CONTEXT_INVOLUNTARY` int(20) DEFAULT NULL,
  `BLOCK_OPS_IN` int(20) DEFAULT NULL,
  `BLOCK_OPS_OUT` int(20) DEFAULT NULL,
  `MESSAGES_SENT` int(20) DEFAULT NULL,
  `MESSAGES_RECEIVED` int(20) DEFAULT NULL,
  `PAGE_FAULTS_MAJOR` int(20) DEFAULT NULL,
  `PAGE_FAULTS_MINOR` int(20) DEFAULT NULL,
  `SWAPS` int(20) DEFAULT NULL,
  `SOURCE_FUNCTION` varchar(30) DEFAULT NULL,
  `SOURCE_FILE` varchar(20) DEFAULT NULL,
  `SOURCE_LINE` int(20) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=6972349 ROW_FORMAT=FIXED
;


CREATE TABLE `PURCHASEORDERDETAIL` (
  `PURCHASEORDERID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to PurchaseOrderHeader.PurchaseOrderID.',
  `PURCHASEORDERDETAILID` int(11) NOT NULL COMMENT 'Primary key. One line number per purchased product.',
  `DUEDATE` datetime NOT NULL COMMENT 'Date the product is expected to be received.',
  `ORDERQTY` smallint(6) NOT NULL COMMENT 'Quantity ordered.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `UNITPRICE` decimal(19,4) NOT NULL COMMENT 'Vendor''s selling price of a single product.',
  `LINETOTAL` decimal(19,4) NOT NULL COMMENT 'Per product subtotal. Computed as OrderQty * UnitPrice.',
  `RECEIVEDQTY` decimal(8,2) NOT NULL COMMENT 'Quantity actually received from the vendor.',
  `REJECTEDQTY` decimal(8,2) NOT NULL COMMENT 'Quantity rejected during inspection.',
  `STOCKEDQTY` decimal(9,2) NOT NULL COMMENT 'Quantity accepted into inventory. Computed as ReceivedQty - RejectedQty.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PURCHASEORDERDETAILID`,`PURCHASEORDERID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Individual products associated with a specific purchase order. See PurchaseOrderHeader.'
;


CREATE TABLE `PURCHASEORDERHEADER` (
  `PURCHASEORDERID` int(11) NOT NULL COMMENT 'Primary key.',
  `REVISIONNUMBER` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Incremental number to track changes to the purchase order over time.',
  `STATUS` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Order current status. 1 = Pending; 2 = Approved; 3 = Rejected; 4 = Complete',
  `EMPLOYEEID` int(11) NOT NULL COMMENT 'Employee who created the purchase order. Foreign key to Employee.BusinessEntityID.',
  `VENDORID` int(11) NOT NULL COMMENT 'Vendor with whom the purchase order is placed. Foreign key to Vendor.BusinessEntityID.',
  `SHIPMETHODID` int(11) NOT NULL COMMENT 'Shipping method. Foreign key to ShipMethod.ShipMethodID.',
  `ORDERDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Purchase order creation date.',
  `SHIPDATE` datetime DEFAULT NULL COMMENT 'Estimated shipment date from the vendor.',
  `SUBTOTAL` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Purchase order subtotal. Computed as SUM(PurchaseOrderDetail.LineTotal)for the appropriate PurchaseOrderID.',
  `TAXAMT` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax amount.',
  `FREIGHT` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping cost.',
  `TOTALDUE` decimal(19,4) NOT NULL COMMENT 'Total due to vendor. Computed as Subtotal + TaxAmt + Freight.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PURCHASEORDERID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='General purchase order information. See PurchaseOrderDetail.'
;


CREATE TABLE `Password` (
  `BusinessEntityID` int(11) NOT NULL,
  `PasswordHash` varchar(128) NOT NULL COMMENT 'Password for the e-mail account.',
  `PasswordSalt` varchar(10) NOT NULL COMMENT 'Random value concatenated with the password string before the password is hashed.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`),
  KEY `GUID_Password` (`rowguid`),
  CONSTRAINT `FK_Password_Person_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Person` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='One way hashed authentication information'
;


CREATE TABLE `Person` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key for Person records.',
  `PersonType` char(2) NOT NULL COMMENT 'Primary type of person: SC = Store Contact, IN = Individual (retail) customer, SP = Sales person, EM = Employee (non-sales), VC = Vendor contact, GC = General contact',
  `NameStyle` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = The data in FirstName and LastName are stored in western style (first name, last name) order.  1 = Eastern style (last name, first name) order.',
  `Title` varchar(8) DEFAULT NULL COMMENT 'A courtesy title. For example, Mr. or Ms.',
  `FirstName` varchar(100) NOT NULL COMMENT 'First name of the person.',
  `MiddleName` varchar(100) DEFAULT NULL COMMENT 'Middle name or middle initial of the person.',
  `LastName` varchar(100) NOT NULL COMMENT 'Last name of the person.',
  `Suffix` varchar(10) DEFAULT NULL COMMENT 'Surname suffix. For example, Sr. or Jr.',
  `EmailPromotion` int(11) NOT NULL DEFAULT 0 COMMENT '0 = Contact does not wish to receive e-mail promotions, 1 = Contact does wish to receive e-mail promotions from AdventureWorks, 2 = Contact does wish to receive e-mail promotions from AdventureWorks and selected partners. ',
  `AdditionalContactInfo` text DEFAULT NULL COMMENT 'Additional contact information about the person stored in xml format. ',
  `Demographics` text DEFAULT NULL COMMENT 'Personal information such as hobbies, and income collected from online shoppers. Used for sales analysis.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`),
  UNIQUE KEY `AK_Person_rowguid` (`rowguid`),
  KEY `IX_Person_LastName_FirstName_MiddleName` (`LastName`,`FirstName`,`MiddleName`),
  KEY `PXML_Person_AddContact` (`AdditionalContactInfo`(255)),
  KEY `PXML_Person_Demographics` (`Demographics`(255)),
  KEY `XMLPATH_Person_Demographics` (`Demographics`(255)),
  KEY `XMLPROPERTY_Person_Demographics` (`Demographics`(255)),
  KEY `XMLVALUE_Person_Demographics` (`Demographics`(255)),
  KEY `GUID_Person` (`rowguid`),
  CONSTRAINT `FK_Person_BusinessEntity_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `BusinessEntity` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Human beings involved with AdventureWorks: employees, customer contacts, and vendor contacts.'
;


CREATE TABLE `PersonCreditCard` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Business entity identification number. Foreign key to Person.BusinessEntityID.',
  `CreditCardID` int(11) NOT NULL COMMENT 'Credit card identification number. Foreign key to CreditCard.CreditCardID.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`CreditCardID`),
  KEY `FK_PersonCreditCard_CreditCard_CreditCardID` (`CreditCardID`),
  CONSTRAINT `FK_PersonCreditCard_CreditCard_CreditCardID` FOREIGN KEY (`CreditCardID`) REFERENCES `CreditCard` (`CreditCardID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_PersonCreditCard_Person_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Person` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping people to their credit card information in the CreditCard table. '
;


CREATE TABLE `PersonPhone` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Business entity identification number. Foreign key to Person.BusinessEntityID.',
  `PhoneNumber` varchar(50) NOT NULL COMMENT 'Telephone number identification number.',
  `PhoneNumberTypeID` int(11) NOT NULL COMMENT 'Kind of phone number. Foreign key to PhoneNumberType.PhoneNumberTypeID.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`PhoneNumber`,`PhoneNumberTypeID`),
  KEY `IX_PersonPhone_PhoneNumber` (`PhoneNumber`),
  KEY `FK_PersonPhone_PhoneNumberType_PhoneNumberTypeID` (`PhoneNumberTypeID`),
  CONSTRAINT `FK_PersonPhone_Person_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Person` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_PersonPhone_PhoneNumberType_PhoneNumberTypeID` FOREIGN KEY (`PhoneNumberTypeID`) REFERENCES `PhoneNumberType` (`PhoneNumberTypeID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Telephone number and type of a person.'
;


CREATE TABLE `PhoneNumberType` (
  `PhoneNumberTypeID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for telephone number type records.',
  `Name` varchar(100) NOT NULL COMMENT 'Name of the telephone number type',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PhoneNumberTypeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Type of phone number of a person.'
;


CREATE TABLE `Product` (
  `ProductID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for Product records.',
  `Name` varchar(100) NOT NULL COMMENT 'Name of the product.',
  `ProductNumber` varchar(25) NOT NULL COMMENT 'Unique product identification number.',
  `MakeFlag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Product is purchased, 1 = Product is manufactured in-house.',
  `FinishedGoodsFlag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Product is not a salable item. 1 = Product is salable.',
  `Color` varchar(15) DEFAULT NULL COMMENT 'Product color.',
  `SafetyStockLevel` smallint(6) NOT NULL COMMENT 'Minimum inventory quantity. ',
  `ReorderPoint` smallint(6) NOT NULL COMMENT 'Inventory level that triggers a purchase order or work order. ',
  `StandardCost` decimal(19,4) NOT NULL COMMENT 'Standard cost of the product.',
  `ListPrice` decimal(19,4) NOT NULL COMMENT 'Selling price.',
  `Size` varchar(5) DEFAULT NULL COMMENT 'Product size.',
  `SizeUnitMeasureCode` char(3) DEFAULT NULL COMMENT 'Unit of measure for Size column.',
  `WeightUnitMeasureCode` char(3) DEFAULT NULL COMMENT 'Unit of measure for Weight column.',
  `Weight` decimal(8,2) DEFAULT NULL COMMENT 'Product weight.',
  `DaysToManufacture` int(11) NOT NULL COMMENT 'Number of days required to manufacture the product.',
  `ProductLine` char(2) DEFAULT NULL COMMENT 'R = Road, M = Mountain, T = Touring, S = Standard',
  `Class` char(2) DEFAULT NULL COMMENT 'H = High, M = Medium, L = Low',
  `Style` char(2) DEFAULT NULL COMMENT 'W = Womens, M = Mens, U = Universal',
  `ProductSubcategoryID` int(11) DEFAULT NULL COMMENT 'Product is a member of this product subcategory. Foreign key to ProductSubCategory.ProductSubCategoryID. ',
  `ProductModelID` int(11) DEFAULT NULL COMMENT 'Product is a member of this product model. Foreign key to ProductModel.ProductModelID.',
  `SellStartDate` datetime NOT NULL COMMENT 'Date the product was available for sale.',
  `SellEndDate` datetime DEFAULT NULL COMMENT 'Date the product was no longer available for sale.',
  `DiscontinuedDate` datetime DEFAULT NULL COMMENT 'Date the product was discontinued.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductID`),
  UNIQUE KEY `AK_Product_ProductNumber` (`ProductNumber`),
  UNIQUE KEY `AK_Product_Name` (`Name`),
  UNIQUE KEY `AK_Product_rowguid` (`rowguid`),
  KEY `FK_Product_UnitMeasure_SizeUnitMeasureCode` (`SizeUnitMeasureCode`),
  KEY `FK_Product_UnitMeasure_WeightUnitMeasureCode` (`WeightUnitMeasureCode`),
  KEY `FK_Product_ProductModel_ProductModelID` (`ProductModelID`),
  KEY `FK_Product_ProductSubcategory_ProductSubcategoryID` (`ProductSubcategoryID`),
  KEY `GUID_Product` (`rowguid`),
  CONSTRAINT `FK_Product_ProductModel_ProductModelID` FOREIGN KEY (`ProductModelID`) REFERENCES `ProductModel` (`ProductModelID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Product_ProductSubcategory_ProductSubcategoryID` FOREIGN KEY (`ProductSubcategoryID`) REFERENCES `ProductSubcategory` (`ProductSubcategoryID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Product_UnitMeasure_SizeUnitMeasureCode` FOREIGN KEY (`SizeUnitMeasureCode`) REFERENCES `UnitMeasure` (`UnitMeasureCode`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Product_UnitMeasure_WeightUnitMeasureCode` FOREIGN KEY (`WeightUnitMeasureCode`) REFERENCES `UnitMeasure` (`UnitMeasureCode`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Products sold or used in the manfacturing of sold products.'
;


CREATE TABLE `ProductCategory` (
  `ProductCategoryID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ProductCategory records.',
  `Name` varchar(100) NOT NULL COMMENT 'Category description.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductCategoryID`),
  UNIQUE KEY `AK_ProductCategory_Name` (`Name`),
  UNIQUE KEY `AK_ProductCategory_rowguid` (`rowguid`),
  KEY `GUID_ProductCategory` (`rowguid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='High-level product categorization.'
;


CREATE TABLE `ProductCostHistory` (
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID',
  `StartDate` datetime NOT NULL COMMENT 'Product cost start date.',
  `EndDate` datetime DEFAULT NULL COMMENT 'Product cost end date.',
  `StandardCost` decimal(19,4) NOT NULL COMMENT 'Standard cost of the product.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductID`,`StartDate`),
  CONSTRAINT `FK_ProductCostHistory_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Changes in the cost of a product over time.'
;


CREATE TABLE `ProductDescription` (
  `ProductDescriptionID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ProductDescription records.',
  `Description` varchar(400) NOT NULL COMMENT 'Description of the product.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductDescriptionID`),
  UNIQUE KEY `AK_ProductDescription_rowguid` (`rowguid`),
  KEY `GUID_ProductDescription` (`rowguid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product descriptions in several languages.'
;


CREATE TABLE `ProductDocument` (
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `DocumentNode` varchar(255) NOT NULL COMMENT 'Document identification number. Foreign key to Document.DocumentNode.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductID`,`DocumentNode`),
  KEY `FK_ProductDocument_Document_DocumentNode` (`DocumentNode`),
  CONSTRAINT `FK_ProductDocument_Document_DocumentNode` FOREIGN KEY (`DocumentNode`) REFERENCES `Document` (`DocumentNode`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductDocument_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products to related product documents.'
;


CREATE TABLE `ProductInventory` (
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `LocationID` smallint(6) NOT NULL COMMENT 'Inventory location identification number. Foreign key to Location.LocationID. ',
  `Shelf` varchar(10) NOT NULL COMMENT 'Storage compartment within an inventory location.',
  `Bin` tinyint(3) unsigned NOT NULL COMMENT 'Storage container on a shelf in an inventory location.',
  `Quantity` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Quantity of products in the inventory location.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductID`,`LocationID`),
  KEY `FK_ProductInventory_Location_LocationID` (`LocationID`),
  KEY `GUID_ProductInventory` (`rowguid`),
  CONSTRAINT `FK_ProductInventory_Location_LocationID` FOREIGN KEY (`LocationID`) REFERENCES `Location` (`LocationID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductInventory_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product inventory information.'
;


CREATE TABLE `ProductListPriceHistory` (
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID',
  `StartDate` datetime NOT NULL COMMENT 'List price start date.',
  `EndDate` datetime DEFAULT NULL COMMENT 'List price end date',
  `ListPrice` decimal(19,4) NOT NULL COMMENT 'Product list price.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductID`,`StartDate`),
  CONSTRAINT `FK_ProductListPriceHistory_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Changes in the list price of a product over time.'
;


CREATE TABLE `ProductModel` (
  `ProductModelID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ProductModel records.',
  `Name` varchar(100) NOT NULL COMMENT 'Product model description.',
  `CatalogDescription` text DEFAULT NULL COMMENT 'Detailed product catalog information in xml format.',
  `Instructions` text DEFAULT NULL COMMENT 'Manufacturing instructions in xml format.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductModelID`),
  UNIQUE KEY `AK_ProductModel_Name` (`Name`),
  UNIQUE KEY `AK_ProductModel_rowguid` (`rowguid`),
  KEY `PXML_ProductModel_CatalogDescription` (`CatalogDescription`(255)),
  KEY `PXML_ProductModel_Instructions` (`Instructions`(255)),
  KEY `GUID_ProductModel` (`rowguid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product model classification.'
;


CREATE TABLE `ProductModelIllustration` (
  `ProductModelID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductModel.ProductModelID.',
  `IllustrationID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Illustration.IllustrationID.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductModelID`,`IllustrationID`),
  KEY `FK_ProductModelIllustration_Illustration_IllustrationID` (`IllustrationID`),
  CONSTRAINT `FK_ProductModelIllustration_Illustration_IllustrationID` FOREIGN KEY (`IllustrationID`) REFERENCES `Illustration` (`IllustrationID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductModelIllustration_ProductModel_ProductModelID` FOREIGN KEY (`ProductModelID`) REFERENCES `ProductModel` (`ProductModelID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping product models and illustrations.'
;


CREATE TABLE `ProductModelProductDescriptionCulture` (
  `ProductModelID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductModel.ProductModelID.',
  `ProductDescriptionID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductDescription.ProductDescriptionID.',
  `CultureID` char(6) NOT NULL COMMENT 'Culture identification number. Foreign key to Culture.CultureID.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductModelID`,`ProductDescriptionID`,`CultureID`),
  KEY `FK_ProductModelProductDescriptionCulture_ProductDescription_Pr3` (`ProductDescriptionID`),
  KEY `FK_ProductModelProductDescriptionCulture_Culture_CultureID` (`CultureID`),
  CONSTRAINT `FK_ProductModelProductDescriptionCulture_Culture_CultureID` FOREIGN KEY (`CultureID`) REFERENCES `Culture` (`CultureID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductModelProductDescriptionCulture_ProductDescription_Pr3` FOREIGN KEY (`ProductDescriptionID`) REFERENCES `ProductDescription` (`ProductDescriptionID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductModelProductDescriptionCulture_ProductModel_ProductM4` FOREIGN KEY (`ProductModelID`) REFERENCES `ProductModel` (`ProductModelID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping product descriptions and the language the description is written in.'
;


CREATE TABLE `ProductPhoto` (
  `ProductPhotoID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ProductPhoto records.',
  `ThumbNailPhoto` longblob DEFAULT NULL COMMENT 'Small image of the product.',
  `ThumbnailPhotoFileName` varchar(50) DEFAULT NULL COMMENT 'Small image file name.',
  `LargePhoto` longblob DEFAULT NULL COMMENT 'Large image of the product.',
  `LargePhotoFileName` varchar(50) DEFAULT NULL COMMENT 'Large image file name.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductPhotoID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product images.'
;


CREATE TABLE `ProductProductPhoto` (
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `ProductPhotoID` int(11) NOT NULL COMMENT 'Product photo identification number. Foreign key to ProductPhoto.ProductPhotoID.',
  `Primary` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = Photo is not the principal image. 1 = Photo is the principal image.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductID`,`ProductPhotoID`),
  KEY `FK_ProductProductPhoto_ProductPhoto_ProductPhotoID` (`ProductPhotoID`),
  CONSTRAINT `FK_ProductProductPhoto_ProductPhoto_ProductPhotoID` FOREIGN KEY (`ProductPhotoID`) REFERENCES `ProductPhoto` (`ProductPhotoID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductProductPhoto_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products and product photos.'
;


CREATE TABLE `ProductReview` (
  `ProductReviewID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ProductReview records.',
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `ReviewerName` varchar(100) NOT NULL COMMENT 'Name of the reviewer.',
  `ReviewDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date review was submitted.',
  `EmailAddress` varchar(50) NOT NULL COMMENT 'Reviewer''s e-mail address.',
  `Rating` int(11) NOT NULL COMMENT 'Product rating given by the reviewer. Scale is 1 to 5 with 5 as the highest rating.',
  `Comments` varchar(3850) DEFAULT NULL COMMENT 'Reviewer''s comments',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductReviewID`),
  KEY `IX_ProductReview_ProductID_Name` (`ProductID`,`ReviewerName`,`Comments`(255)),
  CONSTRAINT `FK_ProductReview_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customer reviews of products they have purchased.'
;


CREATE TABLE `ProductSubcategory` (
  `ProductSubcategoryID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ProductSubcategory records.',
  `ProductCategoryID` int(11) NOT NULL COMMENT 'Product category identification number. Foreign key to ProductCategory.ProductCategoryID.',
  `Name` varchar(100) NOT NULL COMMENT 'Subcategory description.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductSubcategoryID`),
  UNIQUE KEY `AK_ProductSubcategory_Name` (`Name`),
  UNIQUE KEY `AK_ProductSubcategory_rowguid` (`rowguid`),
  KEY `FK_ProductSubcategory_ProductCategory_ProductCategoryID` (`ProductCategoryID`),
  KEY `GUID_ProductSubcategory` (`rowguid`),
  CONSTRAINT `FK_ProductSubcategory_ProductCategory_ProductCategoryID` FOREIGN KEY (`ProductCategoryID`) REFERENCES `ProductCategory` (`ProductCategoryID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product subcategories. See ProductCategory table.'
;


CREATE TABLE `ProductVendor` (
  `ProductID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Product.ProductID.',
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Vendor.BusinessEntityID.',
  `AverageLeadTime` int(11) NOT NULL COMMENT 'The average span of time (in days) between placing an order with the vendor and receiving the purchased product.',
  `StandardPrice` decimal(19,4) NOT NULL COMMENT 'The vendor''s usual selling price.',
  `LastReceiptCost` decimal(19,4) DEFAULT NULL COMMENT 'The selling price when last purchased.',
  `LastReceiptDate` datetime DEFAULT NULL COMMENT 'Date the product was last received by the vendor.',
  `MinOrderQty` int(11) NOT NULL COMMENT 'The maximum quantity that should be ordered.',
  `MaxOrderQty` int(11) NOT NULL COMMENT 'The minimum quantity that should be ordered.',
  `OnOrderQty` int(11) DEFAULT NULL COMMENT 'The quantity currently on order.',
  `UnitMeasureCode` char(3) NOT NULL COMMENT 'The product''s unit of measure.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ProductID`,`BusinessEntityID`),
  KEY `IX_ProductVendor_UnitMeasureCode` (`UnitMeasureCode`),
  KEY `IX_ProductVendor_BusinessEntityID` (`BusinessEntityID`),
  CONSTRAINT `FK_ProductVendor_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductVendor_UnitMeasure_UnitMeasureCode` FOREIGN KEY (`UnitMeasureCode`) REFERENCES `UnitMeasure` (`UnitMeasureCode`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_ProductVendor_Vendor_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Vendor` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping vendors with the products they supply.'
;


CREATE TABLE `PurchaseOrderDetail` (
  `PurchaseOrderID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to PurchaseOrderHeader.PurchaseOrderID.',
  `PurchaseOrderDetailID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key. One line number per purchased product.',
  `DueDate` datetime NOT NULL COMMENT 'Date the product is expected to be received.',
  `OrderQty` smallint(6) NOT NULL COMMENT 'Quantity ordered.',
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `UnitPrice` decimal(19,4) NOT NULL COMMENT 'Vendor''s selling price of a single product.',
  `LineTotal` decimal(19,4) NOT NULL COMMENT 'Per product subtotal. Computed as OrderQty * UnitPrice.',
  `ReceivedQty` decimal(8,2) NOT NULL COMMENT 'Quantity actually received from the vendor.',
  `RejectedQty` decimal(8,2) NOT NULL COMMENT 'Quantity rejected during inspection.',
  `StockedQty` decimal(9,2) NOT NULL COMMENT 'Quantity accepted into inventory. Computed as ReceivedQty - RejectedQty.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PurchaseOrderDetailID`,`PurchaseOrderID`),
  KEY `IX_PurchaseOrderDetail_ProductID` (`ProductID`),
  KEY `FK_PurchaseOrderDetail_PurchaseOrderHeader_PurchaseOrderID` (`PurchaseOrderID`),
  CONSTRAINT `FK_PurchaseOrderDetail_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_PurchaseOrderDetail_PurchaseOrderHeader_PurchaseOrderID` FOREIGN KEY (`PurchaseOrderID`) REFERENCES `PurchaseOrderHeader` (`PurchaseOrderID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Individual products associated with a specific purchase order. See PurchaseOrderHeader.'
;


CREATE TABLE `PurchaseOrderHeader` (
  `PurchaseOrderID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key.',
  `RevisionNumber` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Incremental number to track changes to the purchase order over time.',
  `Status` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Order current status. 1 = Pending; 2 = Approved; 3 = Rejected; 4 = Complete',
  `EmployeeID` int(11) NOT NULL COMMENT 'Employee who created the purchase order. Foreign key to Employee.BusinessEntityID.',
  `VendorID` int(11) NOT NULL COMMENT 'Vendor with whom the purchase order is placed. Foreign key to Vendor.BusinessEntityID.',
  `ShipMethodID` int(11) NOT NULL COMMENT 'Shipping method. Foreign key to ShipMethod.ShipMethodID.',
  `OrderDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Purchase order creation date.',
  `ShipDate` datetime DEFAULT NULL COMMENT 'Estimated shipment date from the vendor.',
  `SubTotal` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Purchase order subtotal. Computed as SUM(PurchaseOrderDetail.LineTotal)for the appropriate PurchaseOrderID.',
  `TaxAmt` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax amount.',
  `Freight` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping cost.',
  `TotalDue` decimal(19,4) NOT NULL COMMENT 'Total due to vendor. Computed as Subtotal + TaxAmt + Freight.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`PurchaseOrderID`),
  KEY `IX_PurchaseOrderHeader_VendorID` (`VendorID`),
  KEY `IX_PurchaseOrderHeader_EmployeeID` (`EmployeeID`),
  KEY `FK_PurchaseOrderHeader_ShipMethod_ShipMethodID` (`ShipMethodID`),
  CONSTRAINT `FK_PurchaseOrderHeader_Employee_EmployeeID` FOREIGN KEY (`EmployeeID`) REFERENCES `Employee` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_PurchaseOrderHeader_ShipMethod_ShipMethodID` FOREIGN KEY (`ShipMethodID`) REFERENCES `ShipMethod` (`ShipMethodID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_PurchaseOrderHeader_Vendor_VendorID` FOREIGN KEY (`VendorID`) REFERENCES `Vendor` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='General purchase order information. See PurchaseOrderDetail.'
;


CREATE TABLE `RA` (
  `capability` varchar(45) DEFAULT NULL,
  `prof_id` int(11) NOT NULL DEFAULT 0,
  `student_id` int(11) NOT NULL DEFAULT 0,
  `salary` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`prof_id`,`student_id`),
  KEY `RA_capability` (`capability`),
  KEY `RA_salary` (`salary`),
  KEY `RA_student_id` (`student_id`),
  KEY `RA_prof_id` (`prof_id`),
  CONSTRAINT `FK_RA_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_RA_2` FOREIGN KEY (`prof_id`) REFERENCES `prof` (`prof_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `REFERENTIAL_CONSTRAINTS` (
  `CONSTRAINT_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `CONSTRAINT_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `CONSTRAINT_NAME` varchar(64) NOT NULL DEFAULT '',
  `UNIQUE_CONSTRAINT_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `UNIQUE_CONSTRAINT_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `UNIQUE_CONSTRAINT_NAME` varchar(64) DEFAULT NULL,
  `MATCH_OPTION` varchar(64) NOT NULL DEFAULT '',
  `UPDATE_RULE` varchar(64) NOT NULL DEFAULT '',
  `DELETE_RULE` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `REFERENCED_TABLE_NAME` varchar(64) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=446091 ROW_FORMAT=FIXED
;


CREATE TABLE `ROUTINES` (
  `SPECIFIC_NAME` varchar(64) NOT NULL DEFAULT '',
  `ROUTINE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `ROUTINE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `ROUTINE_NAME` varchar(64) NOT NULL DEFAULT '',
  `ROUTINE_TYPE` varchar(9) NOT NULL DEFAULT '',
  `DATA_TYPE` varchar(64) NOT NULL DEFAULT '',
  `CHARACTER_MAXIMUM_LENGTH` int(21) DEFAULT NULL,
  `CHARACTER_OCTET_LENGTH` int(21) DEFAULT NULL,
  `NUMERIC_PRECISION` int(21) DEFAULT NULL,
  `NUMERIC_SCALE` int(21) DEFAULT NULL,
  `DATETIME_PRECISION` bigint(21) unsigned DEFAULT NULL,
  `CHARACTER_SET_NAME` varchar(64) DEFAULT NULL,
  `COLLATION_NAME` varchar(64) DEFAULT NULL,
  `DTD_IDENTIFIER` longtext DEFAULT NULL,
  `ROUTINE_BODY` varchar(8) NOT NULL DEFAULT '',
  `ROUTINE_DEFINITION` longtext DEFAULT NULL,
  `EXTERNAL_NAME` varchar(64) DEFAULT NULL,
  `EXTERNAL_LANGUAGE` varchar(64) DEFAULT NULL,
  `PARAMETER_STYLE` varchar(8) NOT NULL DEFAULT '',
  `IS_DETERMINISTIC` varchar(3) NOT NULL DEFAULT '',
  `SQL_DATA_ACCESS` varchar(64) NOT NULL DEFAULT '',
  `SQL_PATH` varchar(64) DEFAULT NULL,
  `SECURITY_TYPE` varchar(7) NOT NULL DEFAULT '',
  `CREATED` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `LAST_ALTERED` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `SQL_MODE` varchar(8192) NOT NULL DEFAULT '',
  `ROUTINE_COMMENT` longtext NOT NULL,
  `DEFINER` varchar(189) NOT NULL DEFAULT '',
  `CHARACTER_SET_CLIENT` varchar(32) NOT NULL DEFAULT '',
  `COLLATION_CONNECTION` varchar(32) NOT NULL DEFAULT '',
  `DATABASE_COLLATION` varchar(32) NOT NULL DEFAULT ''
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=73811 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `Reviews` (
  `review_id` varchar(30) NOT NULL DEFAULT '',
  `business_id` varchar(30) DEFAULT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `stars` double DEFAULT NULL,
  `review_date` date DEFAULT NULL,
  `votes_funny` int(11) DEFAULT NULL,
  `votes_useful` int(11) DEFAULT NULL,
  `votes_cool` int(11) DEFAULT NULL,
  `review_text` text DEFAULT NULL,
  PRIMARY KEY (`review_id`),
  KEY `business_id` (`business_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `Reviews_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `SALESORDERDETAIL` (
  `SALESORDERID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesOrderHeader.SalesOrderID.',
  `SALESORDERDETAILID` int(11) NOT NULL COMMENT 'Primary key. One incremental unique number per product sold.',
  `CARRIERTRACKINGNUMBER` varchar(25) DEFAULT NULL COMMENT 'Shipment tracking number supplied by the shipper.',
  `ORDERQTY` smallint(6) NOT NULL COMMENT 'Quantity ordered per product.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product sold to customer. Foreign key to Product.ProductID.',
  `SPECIALOFFERID` int(11) NOT NULL COMMENT 'Promotional code. Foreign key to SpecialOffer.SpecialOfferID.',
  `UNITPRICE` decimal(19,4) NOT NULL COMMENT 'Selling price of a single product.',
  `UNITPRICEDISCOUNT` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Discount amount.',
  `LINETOTAL` decimal(38,6) NOT NULL COMMENT 'Per product subtotal. Computed as UnitPrice * (1 - UnitPriceDiscount) * OrderQty.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SALESORDERDETAILID`,`SALESORDERID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Individual products associated with a specific sales order. See SalesOrderHeader.'
;


CREATE TABLE `SALESORDERHEADER` (
  `SALESORDERID` int(11) NOT NULL COMMENT 'Primary key.',
  `REVISIONNUMBER` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Incremental number to track changes to the sales order over time.',
  `ORDERDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Dates the sales order was created.',
  `DUEDATE` datetime NOT NULL COMMENT 'Date the order is due to the customer.',
  `SHIPDATE` datetime DEFAULT NULL COMMENT 'Date the order was shipped to the customer.',
  `STATUS` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Order current status. 1 = In process; 2 = Approved; 3 = Backordered; 4 = Rejected; 5 = Shipped; 6 = Cancelled',
  `ONLINEORDERFLAG` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Order placed by sales person. 1 = Order placed online by customer.',
  `SALESORDERNUMBER` varchar(25) NOT NULL COMMENT 'Unique sales order identification number.',
  `PURCHASEORDERNUMBER` varchar(50) DEFAULT NULL COMMENT 'Customer purchase order number reference. ',
  `ACCOUNTNUMBER` varchar(30) DEFAULT NULL COMMENT 'Financial accounting number reference.',
  `CUSTOMERID` int(11) NOT NULL COMMENT 'Customer identification number. Foreign key to Customer.BusinessEntityID.',
  `SALESPERSONID` int(11) DEFAULT NULL COMMENT 'Sales person who created the sales order. Foreign key to SalesPerson.BusinessEntityID.',
  `TERRITORYID` int(11) DEFAULT NULL COMMENT 'Territory in which the sale was made. Foreign key to SalesTerritory.SalesTerritoryID.',
  `BILLTOADDRESSID` int(11) NOT NULL COMMENT 'Customer billing address. Foreign key to Address.AddressID.',
  `SHIPTOADDRESSID` int(11) NOT NULL COMMENT 'Customer shipping address. Foreign key to Address.AddressID.',
  `SHIPMETHODID` int(11) NOT NULL COMMENT 'Shipping method. Foreign key to ShipMethod.ShipMethodID.',
  `CREDITCARDID` int(11) DEFAULT NULL COMMENT 'Credit card identification number. Foreign key to CreditCard.CreditCardID.',
  `CREDITCARDAPPROVALCODE` varchar(15) DEFAULT NULL COMMENT 'Approval code provided by the credit card company.',
  `CURRENCYRATEID` int(11) DEFAULT NULL COMMENT 'Currency exchange rate used. Foreign key to CurrencyRate.CurrencyRateID.',
  `SUBTOTAL` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales subtotal. Computed as SUM(SalesOrderDetail.LineTotal)for the appropriate SalesOrderID.',
  `TAXAMT` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax amount.',
  `FREIGHT` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping cost.',
  `TOTALDUE` decimal(19,4) NOT NULL COMMENT 'Total due from customer. Computed as Subtotal + TaxAmt + Freight.',
  `COMMENT` varchar(128) DEFAULT NULL COMMENT 'Sales representative comments.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SALESORDERID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='General sales order information.'
;


CREATE TABLE `SALESORDERHEADERSALESREASON` (
  `SALESORDERID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesOrderHeader.SalesOrderID.',
  `SALESREASONID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesReason.SalesReasonID.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SALESORDERID`,`SALESREASONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping sales orders to sales reason codes.'
;


CREATE TABLE `SALESPERSON` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key for SalesPerson records. Foreign key to Employee.BusinessEntityID',
  `TERRITORYID` int(11) DEFAULT NULL COMMENT 'Territory currently assigned to. Foreign key to SalesTerritory.SalesTerritoryID.',
  `SALESQUOTA` decimal(19,4) DEFAULT NULL COMMENT 'Projected yearly sales.',
  `BONUS` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Bonus due if quota is met.',
  `COMMISSIONPCT` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Commision percent received per sale.',
  `SALESYTD` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales total year to date.',
  `SALESLASTYEAR` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales total of previous year.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales representative current information.'
;


CREATE TABLE `SALESPERSONQUOTAHISTORY` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Sales person identification number. Foreign key to SalesPerson.BusinessEntityID.',
  `QUOTADATE` datetime NOT NULL COMMENT 'Sales quota date.',
  `SALESQUOTA` decimal(19,4) NOT NULL COMMENT 'Sales quota amount.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`QUOTADATE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales performance tracking.'
;


CREATE TABLE `SALESREASON` (
  `SALESREASONID` int(11) NOT NULL COMMENT 'Primary key for SalesReason records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Sales reason description.',
  `REASONTYPE` varchar(100) NOT NULL COMMENT 'Category the sales reason belongs to.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SALESREASONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table of customer purchase reasons.'
;


CREATE TABLE `SALESTAXRATE` (
  `SALESTAXRATEID` int(11) NOT NULL COMMENT 'Primary key for SalesTaxRate records.',
  `STATEPROVINCEID` int(11) NOT NULL COMMENT 'State, province, or country/region the sales tax applies to.',
  `TAXTYPE` tinyint(3) unsigned NOT NULL COMMENT '1 = Tax applied to retail transactions, 2 = Tax applied to wholesale transactions, 3 = Tax applied to all sales (retail and wholesale) transactions.',
  `TAXRATE` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax rate amount.',
  `NAME` varchar(100) NOT NULL COMMENT 'Tax rate description.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SALESTAXRATEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Tax rate lookup table.'
;


CREATE TABLE `SALESTERRITORY` (
  `TERRITORYID` int(11) NOT NULL COMMENT 'Primary key for SalesTerritory records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Sales territory description',
  `COUNTRYREGIONCODE` varchar(3) NOT NULL COMMENT 'ISO standard country or region code. Foreign key to CountryRegion.CountryRegionCode. ',
  `GROUP` varchar(50) NOT NULL COMMENT 'Geographic area to which the sales territory belong.',
  `SALESYTD` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales in the territory year to date.',
  `SALESLASTYEAR` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales in the territory the previous year.',
  `COSTYTD` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Business costs in the territory year to date.',
  `COSTLASTYEAR` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Business costs in the territory the previous year.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`TERRITORYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales territory lookup table.'
;


CREATE TABLE `SALESTERRITORYHISTORY` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key. The sales rep.  Foreign key to SalesPerson.BusinessEntityID.',
  `TERRITORYID` int(11) NOT NULL COMMENT 'Primary key. Territory identification number. Foreign key to SalesTerritory.SalesTerritoryID.',
  `STARTDATE` datetime NOT NULL COMMENT 'Primary key. Date the sales representive started work in the territory.',
  `ENDDATE` datetime DEFAULT NULL COMMENT 'Date the sales representative left work in the territory.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`,`STARTDATE`,`TERRITORYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales representative transfers to other sales territories.'
;


CREATE TABLE `SCHEMATA` (
  `CATALOG_NAME` varchar(512) NOT NULL DEFAULT '',
  `SCHEMA_NAME` varchar(64) NOT NULL DEFAULT '',
  `DEFAULT_CHARACTER_SET_NAME` varchar(32) NOT NULL DEFAULT '',
  `DEFAULT_COLLATION_NAME` varchar(32) NOT NULL DEFAULT '',
  `SQL_PATH` varchar(512) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=619943 ROW_FORMAT=FIXED
;


CREATE TABLE `SCHEMA_PRIVILEGES` (
  `GRANTEE` varchar(190) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=856594 ROW_FORMAT=FIXED
;


CREATE TABLE `SCRAPREASON` (
  `SCRAPREASONID` smallint(6) NOT NULL COMMENT 'Primary key for ScrapReason records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Failure description.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SCRAPREASONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Manufacturing failure reasons lookup table.'
;


CREATE TABLE `SESSION_STATUS` (
  `VARIABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `VARIABLE_VALUE` varchar(1024) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=657124 ROW_FORMAT=FIXED
;


CREATE TABLE `SESSION_VARIABLES` (
  `VARIABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `VARIABLE_VALUE` varchar(1024) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=657124 ROW_FORMAT=FIXED
;


CREATE TABLE `SHIFT` (
  `SHIFTID` tinyint(3) unsigned NOT NULL COMMENT 'Primary key for Shift records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Shift description.',
  `STARTTIME` time NOT NULL COMMENT 'Shift start time.',
  `ENDTIME` time NOT NULL COMMENT 'Shift end time.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SHIFTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Work shift lookup table.'
;


CREATE TABLE `SHIPMETHOD` (
  `SHIPMETHODID` int(11) NOT NULL COMMENT 'Primary key for ShipMethod records.',
  `NAME` varchar(100) NOT NULL COMMENT 'Shipping company name.',
  `SHIPBASE` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Minimum shipping charge.',
  `SHIPRATE` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping charge per pound.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SHIPMETHODID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Shipping company lookup table.'
;


CREATE TABLE `SHOPPINGCARTITEM` (
  `SHOPPINGCARTITEMID` int(11) NOT NULL COMMENT 'Primary key for ShoppingCartItem records.',
  `SHOPPINGCARTID` varchar(50) NOT NULL COMMENT 'Shopping cart identification number.',
  `QUANTITY` int(11) NOT NULL DEFAULT 1 COMMENT 'Product quantity ordered.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product ordered. Foreign key to Product.ProductID.',
  `DATECREATED` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date the time the record was created.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SHOPPINGCARTITEMID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Contains online customer orders until the order is submitted or cancelled.'
;


CREATE TABLE `SPECIALOFFER` (
  `SPECIALOFFERID` int(11) NOT NULL COMMENT 'Primary key for SpecialOffer records.',
  `DESCRIPTION` varchar(255) NOT NULL COMMENT 'Discount description.',
  `DISCOUNTPCT` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Discount precentage.',
  `TYPE` varchar(50) NOT NULL COMMENT 'Discount type category.',
  `CATEGORY` varchar(50) NOT NULL COMMENT 'Group the discount applies to such as Reseller or Customer.',
  `STARTDATE` datetime NOT NULL COMMENT 'Discount start date.',
  `ENDDATE` datetime NOT NULL COMMENT 'Discount end date.',
  `MINQTY` int(11) NOT NULL DEFAULT 0 COMMENT 'Minimum discount percent allowed.',
  `MAXQTY` int(11) DEFAULT NULL COMMENT 'Maximum discount percent allowed.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SPECIALOFFERID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sale discounts lookup table.'
;


CREATE TABLE `SPECIALOFFERPRODUCT` (
  `SPECIALOFFERID` int(11) NOT NULL COMMENT 'Primary key for SpecialOfferProduct records.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SPECIALOFFERID`,`PRODUCTID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products to special offer discounts.'
;


CREATE TABLE `STATEPROVINCE` (
  `STATEPROVINCEID` int(11) NOT NULL COMMENT 'Primary key for StateProvince records.',
  `STATEPROVINCECODE` char(3) NOT NULL COMMENT 'ISO standard state or province code.',
  `COUNTRYREGIONCODE` varchar(3) NOT NULL COMMENT 'ISO standard country or region code. Foreign key to CountryRegion.CountryRegionCode. ',
  `ISONLYSTATEPROVINCEFLAG` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = StateProvinceCode exists. 1 = StateProvinceCode unavailable, using CountryRegionCode.',
  `NAME` varchar(100) NOT NULL COMMENT 'State or province description.',
  `TERRITORYID` int(11) NOT NULL COMMENT 'ID of the territory in which the state or province is located. Foreign key to SalesTerritory.SalesTerritoryID.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`STATEPROVINCEID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='State and province lookup table.'
;


CREATE TABLE `STATISTICS` (
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `NON_UNIQUE` bigint(1) NOT NULL DEFAULT 0,
  `INDEX_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `INDEX_NAME` varchar(64) NOT NULL DEFAULT '',
  `SEQ_IN_INDEX` bigint(2) NOT NULL DEFAULT 0,
  `COLUMN_NAME` varchar(64) NOT NULL DEFAULT '',
  `COLLATION` varchar(1) DEFAULT NULL,
  `CARDINALITY` bigint(21) DEFAULT NULL,
  `SUB_PART` bigint(3) DEFAULT NULL,
  `PACKED` varchar(10) DEFAULT NULL,
  `NULLABLE` varchar(3) NOT NULL DEFAULT '',
  `INDEX_TYPE` varchar(16) NOT NULL DEFAULT '',
  `COMMENT` varchar(16) DEFAULT NULL,
  `INDEX_COMMENT` varchar(1024) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=373280 ROW_FORMAT=FIXED
;


CREATE TABLE `STORE` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Customer.BusinessEntityID.',
  `NAME` varchar(100) NOT NULL COMMENT 'Name of the store.',
  `SALESPERSONID` int(11) DEFAULT NULL COMMENT 'ID of the sales person assigned to the customer. Foreign key to SalesPerson.BusinessEntityID.',
  `DEMOGRAPHICS` text DEFAULT NULL COMMENT 'Demographic informationg about the store such as the number of employees, annual sales and store type.',
  `ROWGUID` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customers (resellers) of Adventure Works products.'
;


CREATE TABLE `Sales` (
  `EVENTID` int(11) NOT NULL,
  `REFID` int(11) DEFAULT NULL,
  `EVENT_DATE` datetime DEFAULT NULL,
  `AMOUNT` float DEFAULT NULL,
  PRIMARY KEY (`EVENTID`),
  KEY `Sales_REFID` (`REFID`),
  CONSTRAINT `Sales_ibfk_1` FOREIGN KEY (`REFID`) REFERENCES `Customers` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `SalesOrderDetail` (
  `SalesOrderID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesOrderHeader.SalesOrderID.',
  `SalesOrderDetailID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key. One incremental unique number per product sold.',
  `CarrierTrackingNumber` varchar(25) DEFAULT NULL COMMENT 'Shipment tracking number supplied by the shipper.',
  `OrderQty` smallint(6) NOT NULL COMMENT 'Quantity ordered per product.',
  `ProductID` int(11) NOT NULL COMMENT 'Product sold to customer. Foreign key to Product.ProductID.',
  `SpecialOfferID` int(11) NOT NULL COMMENT 'Promotional code. Foreign key to SpecialOffer.SpecialOfferID.',
  `UnitPrice` decimal(19,4) NOT NULL COMMENT 'Selling price of a single product.',
  `UnitPriceDiscount` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Discount amount.',
  `LineTotal` decimal(38,6) NOT NULL COMMENT 'Per product subtotal. Computed as UnitPrice * (1 - UnitPriceDiscount) * OrderQty.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SalesOrderDetailID`,`SalesOrderID`),
  UNIQUE KEY `AK_SalesOrderDetail_rowguid` (`rowguid`),
  KEY `IX_SalesOrderDetail_ProductID` (`ProductID`),
  KEY `FK_SalesOrderDetail_SalesOrderHeader_SalesOrderID` (`SalesOrderID`),
  KEY `FK_SalesOrderDetail_SpecialOfferProduct_SpecialOfferIDProductID` (`SpecialOfferID`,`ProductID`),
  KEY `GUID_SalesOrderDetail` (`rowguid`),
  CONSTRAINT `FK_SalesOrderDetail_SalesOrderHeader_SalesOrderID` FOREIGN KEY (`SalesOrderID`) REFERENCES `SalesOrderHeader` (`SalesOrderID`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderDetail_SpecialOfferProduct_SpecialOfferIDProductID` FOREIGN KEY (`SpecialOfferID`, `ProductID`) REFERENCES `SpecialOfferProduct` (`SpecialOfferID`, `ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Individual products associated with a specific sales order. See SalesOrderHeader.'
;


CREATE TABLE `SalesOrderHeader` (
  `SalesOrderID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key.',
  `RevisionNumber` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Incremental number to track changes to the sales order over time.',
  `OrderDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Dates the sales order was created.',
  `DueDate` datetime NOT NULL COMMENT 'Date the order is due to the customer.',
  `ShipDate` datetime DEFAULT NULL COMMENT 'Date the order was shipped to the customer.',
  `Status` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Order current status. 1 = In process; 2 = Approved; 3 = Backordered; 4 = Rejected; 5 = Shipped; 6 = Cancelled',
  `OnlineOrderFlag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Order placed by sales person. 1 = Order placed online by customer.',
  `SalesOrderNumber` varchar(25) NOT NULL COMMENT 'Unique sales order identification number.',
  `PurchaseOrderNumber` varchar(50) DEFAULT NULL COMMENT 'Customer purchase order number reference. ',
  `AccountNumber` varchar(30) DEFAULT NULL COMMENT 'Financial accounting number reference.',
  `CustomerID` int(11) NOT NULL COMMENT 'Customer identification number. Foreign key to Customer.BusinessEntityID.',
  `SalesPersonID` int(11) DEFAULT NULL COMMENT 'Sales person who created the sales order. Foreign key to SalesPerson.BusinessEntityID.',
  `TerritoryID` int(11) DEFAULT NULL COMMENT 'Territory in which the sale was made. Foreign key to SalesTerritory.SalesTerritoryID.',
  `BillToAddressID` int(11) NOT NULL COMMENT 'Customer billing address. Foreign key to Address.AddressID.',
  `ShipToAddressID` int(11) NOT NULL COMMENT 'Customer shipping address. Foreign key to Address.AddressID.',
  `ShipMethodID` int(11) NOT NULL COMMENT 'Shipping method. Foreign key to ShipMethod.ShipMethodID.',
  `CreditCardID` int(11) DEFAULT NULL COMMENT 'Credit card identification number. Foreign key to CreditCard.CreditCardID.',
  `CreditCardApprovalCode` varchar(15) DEFAULT NULL COMMENT 'Approval code provided by the credit card company.',
  `CurrencyRateID` int(11) DEFAULT NULL COMMENT 'Currency exchange rate used. Foreign key to CurrencyRate.CurrencyRateID.',
  `SubTotal` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales subtotal. Computed as SUM(SalesOrderDetail.LineTotal)for the appropriate SalesOrderID.',
  `TaxAmt` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax amount.',
  `Freight` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping cost.',
  `TotalDue` decimal(19,4) NOT NULL COMMENT 'Total due from customer. Computed as Subtotal + TaxAmt + Freight.',
  `Comment` varchar(128) DEFAULT NULL COMMENT 'Sales representative comments.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SalesOrderID`),
  UNIQUE KEY `AK_SalesOrderHeader_rowguid` (`rowguid`),
  UNIQUE KEY `AK_SalesOrderHeader_SalesOrderNumber` (`SalesOrderNumber`),
  KEY `IX_SalesOrderHeader_CustomerID` (`CustomerID`),
  KEY `IX_SalesOrderHeader_SalesPersonID` (`SalesPersonID`),
  KEY `FK_SalesOrderHeader_Address_BillToAddressID` (`BillToAddressID`),
  KEY `FK_SalesOrderHeader_Address_ShipToAddressID` (`ShipToAddressID`),
  KEY `FK_SalesOrderHeader_CreditCard_CreditCardID` (`CreditCardID`),
  KEY `FK_SalesOrderHeader_CurrencyRate_CurrencyRateID` (`CurrencyRateID`),
  KEY `FK_SalesOrderHeader_ShipMethod_ShipMethodID` (`ShipMethodID`),
  KEY `FK_SalesOrderHeader_SalesTerritory_TerritoryID` (`TerritoryID`),
  KEY `GUID_SalesOrderHeader` (`rowguid`),
  CONSTRAINT `FK_SalesOrderHeader_Address_BillToAddressID` FOREIGN KEY (`BillToAddressID`) REFERENCES `Address` (`AddressID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeader_Address_ShipToAddressID` FOREIGN KEY (`ShipToAddressID`) REFERENCES `Address` (`AddressID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeader_CreditCard_CreditCardID` FOREIGN KEY (`CreditCardID`) REFERENCES `CreditCard` (`CreditCardID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeader_CurrencyRate_CurrencyRateID` FOREIGN KEY (`CurrencyRateID`) REFERENCES `CurrencyRate` (`CurrencyRateID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeader_Customer_CustomerID` FOREIGN KEY (`CustomerID`) REFERENCES `Customer` (`CustomerID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeader_SalesPerson_SalesPersonID` FOREIGN KEY (`SalesPersonID`) REFERENCES `SalesPerson` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeader_SalesTerritory_TerritoryID` FOREIGN KEY (`TerritoryID`) REFERENCES `SalesTerritory` (`TerritoryID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeader_ShipMethod_ShipMethodID` FOREIGN KEY (`ShipMethodID`) REFERENCES `ShipMethod` (`ShipMethodID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='General sales order information.'
;


CREATE TABLE `SalesOrderHeaderSalesReason` (
  `SalesOrderID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesOrderHeader.SalesOrderID.',
  `SalesReasonID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesReason.SalesReasonID.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SalesOrderID`,`SalesReasonID`),
  KEY `FK_SalesOrderHeaderSalesReason_SalesReason_SalesReasonID` (`SalesReasonID`),
  CONSTRAINT `FK_SalesOrderHeaderSalesReason_SalesOrderHeader_SalesOrderID` FOREIGN KEY (`SalesOrderID`) REFERENCES `SalesOrderHeader` (`SalesOrderID`) ON DELETE CASCADE ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesOrderHeaderSalesReason_SalesReason_SalesReasonID` FOREIGN KEY (`SalesReasonID`) REFERENCES `SalesReason` (`SalesReasonID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping sales orders to sales reason codes.'
;


CREATE TABLE `SalesPerson` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key for SalesPerson records. Foreign key to Employee.BusinessEntityID',
  `TerritoryID` int(11) DEFAULT NULL COMMENT 'Territory currently assigned to. Foreign key to SalesTerritory.SalesTerritoryID.',
  `SalesQuota` decimal(19,4) DEFAULT NULL COMMENT 'Projected yearly sales.',
  `Bonus` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Bonus due if quota is met.',
  `CommissionPct` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Commision percent received per sale.',
  `SalesYTD` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales total year to date.',
  `SalesLastYear` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales total of previous year.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`),
  UNIQUE KEY `AK_SalesPerson_rowguid` (`rowguid`),
  KEY `FK_SalesPerson_SalesTerritory_TerritoryID` (`TerritoryID`),
  KEY `GUID_SalesPerson` (`rowguid`),
  CONSTRAINT `FK_SalesPerson_Employee_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `Employee` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesPerson_SalesTerritory_TerritoryID` FOREIGN KEY (`TerritoryID`) REFERENCES `SalesTerritory` (`TerritoryID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales representative current information.'
;


CREATE TABLE `SalesPersonQuotaHistory` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Sales person identification number. Foreign key to SalesPerson.BusinessEntityID.',
  `QuotaDate` datetime NOT NULL COMMENT 'Sales quota date.',
  `SalesQuota` decimal(19,4) NOT NULL COMMENT 'Sales quota amount.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`QuotaDate`),
  UNIQUE KEY `AK_SalesPersonQuotaHistory_rowguid` (`rowguid`),
  KEY `GUID_SalesPersonQuotaHistory` (`rowguid`),
  CONSTRAINT `FK_SalesPersonQuotaHistory_SalesPerson_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `SalesPerson` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales performance tracking.'
;


CREATE TABLE `SalesReason` (
  `SalesReasonID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for SalesReason records.',
  `Name` varchar(100) NOT NULL COMMENT 'Sales reason description.',
  `ReasonType` varchar(100) NOT NULL COMMENT 'Category the sales reason belongs to.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SalesReasonID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table of customer purchase reasons.'
;


CREATE TABLE `SalesTaxRate` (
  `SalesTaxRateID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for SalesTaxRate records.',
  `StateProvinceID` int(11) NOT NULL COMMENT 'State, province, or country/region the sales tax applies to.',
  `TaxType` tinyint(3) unsigned NOT NULL COMMENT '1 = Tax applied to retail transactions, 2 = Tax applied to wholesale transactions, 3 = Tax applied to all sales (retail and wholesale) transactions.',
  `TaxRate` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax rate amount.',
  `Name` varchar(100) NOT NULL COMMENT 'Tax rate description.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SalesTaxRateID`),
  UNIQUE KEY `AK_SalesTaxRate_StateProvinceID_TaxType` (`StateProvinceID`,`TaxType`),
  UNIQUE KEY `AK_SalesTaxRate_rowguid` (`rowguid`),
  KEY `GUID_SalesTaxRate` (`rowguid`),
  CONSTRAINT `FK_SalesTaxRate_StateProvince_StateProvinceID` FOREIGN KEY (`StateProvinceID`) REFERENCES `StateProvince` (`StateProvinceID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Tax rate lookup table.'
;


CREATE TABLE `SalesTerritory` (
  `TerritoryID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for SalesTerritory records.',
  `Name` varchar(100) NOT NULL COMMENT 'Sales territory description',
  `CountryRegionCode` varchar(3) NOT NULL COMMENT 'ISO standard country or region code. Foreign key to CountryRegion.CountryRegionCode. ',
  `Group` varchar(50) NOT NULL COMMENT 'Geographic area to which the sales territory belong.',
  `SalesYTD` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales in the territory year to date.',
  `SalesLastYear` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales in the territory the previous year.',
  `CostYTD` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Business costs in the territory year to date.',
  `CostLastYear` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Business costs in the territory the previous year.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`TerritoryID`),
  UNIQUE KEY `AK_SalesTerritory_Name` (`Name`),
  UNIQUE KEY `AK_SalesTerritory_rowguid` (`rowguid`),
  KEY `FK_SalesTerritory_CountryRegion_CountryRegionCode` (`CountryRegionCode`),
  KEY `GUID_SalesTerritory` (`rowguid`),
  CONSTRAINT `FK_SalesTerritory_CountryRegion_CountryRegionCode` FOREIGN KEY (`CountryRegionCode`) REFERENCES `CountryRegion` (`CountryRegionCode`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales territory lookup table.'
;


CREATE TABLE `SalesTerritoryHistory` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key. The sales rep.  Foreign key to SalesPerson.BusinessEntityID.',
  `TerritoryID` int(11) NOT NULL COMMENT 'Primary key. Territory identification number. Foreign key to SalesTerritory.SalesTerritoryID.',
  `StartDate` datetime NOT NULL COMMENT 'Primary key. Date the sales representive started work in the territory.',
  `EndDate` datetime DEFAULT NULL COMMENT 'Date the sales representative left work in the territory.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`,`StartDate`,`TerritoryID`),
  UNIQUE KEY `AK_SalesTerritoryHistory_rowguid` (`rowguid`),
  KEY `FK_SalesTerritoryHistory_SalesTerritory_TerritoryID` (`TerritoryID`),
  KEY `GUID_SalesTerritoryHistory` (`rowguid`),
  CONSTRAINT `FK_SalesTerritoryHistory_SalesPerson_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `SalesPerson` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SalesTerritoryHistory_SalesTerritory_TerritoryID` FOREIGN KEY (`TerritoryID`) REFERENCES `SalesTerritory` (`TerritoryID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales representative transfers to other sales territories.'
;


CREATE TABLE `ScrapReason` (
  `ScrapReasonID` smallint(6) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ScrapReason records.',
  `Name` varchar(100) NOT NULL COMMENT 'Failure description.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ScrapReasonID`),
  UNIQUE KEY `AK_ScrapReason_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Manufacturing failure reasons lookup table.'
;


CREATE TABLE `Shift` (
  `ShiftID` tinyint(3) unsigned NOT NULL AUTO_INCREMENT COMMENT 'Primary key for Shift records.',
  `Name` varchar(100) NOT NULL COMMENT 'Shift description.',
  `StartTime` time NOT NULL COMMENT 'Shift start time.',
  `EndTime` time NOT NULL COMMENT 'Shift end time.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ShiftID`),
  UNIQUE KEY `AK_Shift_Name` (`Name`),
  UNIQUE KEY `AK_Shift_StartTime_EndTime` (`StartTime`,`EndTime`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Work shift lookup table.'
;


CREATE TABLE `ShipMethod` (
  `ShipMethodID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ShipMethod records.',
  `Name` varchar(100) NOT NULL COMMENT 'Shipping company name.',
  `ShipBase` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Minimum shipping charge.',
  `ShipRate` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping charge per pound.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ShipMethodID`),
  UNIQUE KEY `AK_ShipMethod_Name` (`Name`),
  UNIQUE KEY `AK_ShipMethod_rowguid` (`rowguid`),
  KEY `GUID_ShipMethod` (`rowguid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Shipping company lookup table.'
;


CREATE TABLE `ShoppingCartItem` (
  `ShoppingCartItemID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for ShoppingCartItem records.',
  `ShoppingCartID` varchar(50) NOT NULL COMMENT 'Shopping cart identification number.',
  `Quantity` int(11) NOT NULL DEFAULT 1 COMMENT 'Product quantity ordered.',
  `ProductID` int(11) NOT NULL COMMENT 'Product ordered. Foreign key to Product.ProductID.',
  `DateCreated` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date the time the record was created.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`ShoppingCartItemID`),
  KEY `IX_ShoppingCartItem_ShoppingCartID_ProductID` (`ShoppingCartID`,`ProductID`),
  KEY `FK_ShoppingCartItem_Product_ProductID` (`ProductID`),
  CONSTRAINT `FK_ShoppingCartItem_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Contains online customer orders until the order is submitted or cancelled.'
;


CREATE TABLE `SpecialOffer` (
  `SpecialOfferID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for SpecialOffer records.',
  `Description` varchar(255) NOT NULL COMMENT 'Discount description.',
  `DiscountPct` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Discount precentage.',
  `Type` varchar(50) NOT NULL COMMENT 'Discount type category.',
  `Category` varchar(50) NOT NULL COMMENT 'Group the discount applies to such as Reseller or Customer.',
  `StartDate` datetime NOT NULL COMMENT 'Discount start date.',
  `EndDate` datetime NOT NULL COMMENT 'Discount end date.',
  `MinQty` int(11) NOT NULL DEFAULT 0 COMMENT 'Minimum discount percent allowed.',
  `MaxQty` int(11) DEFAULT NULL COMMENT 'Maximum discount percent allowed.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SpecialOfferID`),
  UNIQUE KEY `AK_SpecialOffer_rowguid` (`rowguid`),
  KEY `GUID_SpecialOffer` (`rowguid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sale discounts lookup table.'
;


CREATE TABLE `SpecialOfferProduct` (
  `SpecialOfferID` int(11) NOT NULL COMMENT 'Primary key for SpecialOfferProduct records.',
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`SpecialOfferID`,`ProductID`),
  UNIQUE KEY `AK_SpecialOfferProduct_rowguid` (`rowguid`),
  KEY `IX_SpecialOfferProduct_ProductID` (`ProductID`),
  KEY `GUID_SpecialOfferProduct` (`rowguid`),
  CONSTRAINT `FK_SpecialOfferProduct_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_SpecialOfferProduct_SpecialOffer_SpecialOfferID` FOREIGN KEY (`SpecialOfferID`) REFERENCES `SpecialOffer` (`SpecialOfferID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products to special offer discounts.'
;


CREATE TABLE `StateProvince` (
  `StateProvinceID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for StateProvince records.',
  `StateProvinceCode` char(3) NOT NULL COMMENT 'ISO standard state or province code.',
  `CountryRegionCode` varchar(3) NOT NULL COMMENT 'ISO standard country or region code. Foreign key to CountryRegion.CountryRegionCode. ',
  `IsOnlyStateProvinceFlag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = StateProvinceCode exists. 1 = StateProvinceCode unavailable, using CountryRegionCode.',
  `Name` varchar(100) NOT NULL COMMENT 'State or province description.',
  `TerritoryID` int(11) NOT NULL COMMENT 'ID of the territory in which the state or province is located. Foreign key to SalesTerritory.SalesTerritoryID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`StateProvinceID`),
  UNIQUE KEY `AK_StateProvince_Name` (`Name`),
  UNIQUE KEY `AK_StateProvince_StateProvinceCode_CountryRegionCode` (`StateProvinceCode`,`CountryRegionCode`),
  UNIQUE KEY `AK_StateProvince_rowguid` (`rowguid`),
  KEY `FK_StateProvince_CountryRegion_CountryRegionCode` (`CountryRegionCode`),
  KEY `FK_StateProvince_SalesTerritory_TerritoryID` (`TerritoryID`),
  KEY `GUID_StateProvince` (`rowguid`),
  CONSTRAINT `FK_StateProvince_CountryRegion_CountryRegionCode` FOREIGN KEY (`CountryRegionCode`) REFERENCES `CountryRegion` (`CountryRegionCode`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_StateProvince_SalesTerritory_TerritoryID` FOREIGN KEY (`TerritoryID`) REFERENCES `SalesTerritory` (`TerritoryID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='State and province lookup table.'
;


CREATE TABLE `Store` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Customer.BusinessEntityID.',
  `Name` varchar(100) NOT NULL COMMENT 'Name of the store.',
  `SalesPersonID` int(11) DEFAULT NULL COMMENT 'ID of the sales person assigned to the customer. Foreign key to SalesPerson.BusinessEntityID.',
  `Demographics` text DEFAULT NULL COMMENT 'Demographic informationg about the store such as the number of employees, annual sales and store type.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`),
  UNIQUE KEY `AK_Store_rowguid` (`rowguid`),
  KEY `IX_Store_SalesPersonID` (`SalesPersonID`),
  KEY `PXML_Store_Demographics` (`Demographics`(255)),
  KEY `GUID_Store` (`rowguid`),
  CONSTRAINT `FK_Store_BusinessEntity_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `BusinessEntity` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Store_SalesPerson_SalesPersonID` FOREIGN KEY (`SalesPersonID`) REFERENCES `SalesPerson` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customers (resellers) of Adventure Works products.'
;


CREATE TABLE `TABLES` (
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `TABLE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `ENGINE` varchar(64) DEFAULT NULL,
  `VERSION` bigint(21) unsigned DEFAULT NULL,
  `ROW_FORMAT` varchar(10) DEFAULT NULL,
  `TABLE_ROWS` bigint(21) unsigned DEFAULT NULL,
  `AVG_ROW_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `DATA_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `MAX_DATA_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `INDEX_LENGTH` bigint(21) unsigned DEFAULT NULL,
  `DATA_FREE` bigint(21) unsigned DEFAULT NULL,
  `AUTO_INCREMENT` bigint(21) unsigned DEFAULT NULL,
  `CREATE_TIME` datetime DEFAULT NULL,
  `UPDATE_TIME` datetime DEFAULT NULL,
  `CHECK_TIME` datetime DEFAULT NULL,
  `TABLE_COLLATION` varchar(32) DEFAULT NULL,
  `CHECKSUM` bigint(21) unsigned DEFAULT NULL,
  `CREATE_OPTIONS` varchar(255) DEFAULT NULL,
  `TABLE_COMMENT` varchar(2048) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=227246 ROW_FORMAT=FIXED
;


CREATE TABLE `TABLESPACES` (
  `TABLESPACE_NAME` varchar(64) NOT NULL DEFAULT '',
  `ENGINE` varchar(64) NOT NULL DEFAULT '',
  `TABLESPACE_TYPE` varchar(64) DEFAULT NULL,
  `LOGFILE_GROUP_NAME` varchar(64) DEFAULT NULL,
  `EXTENT_SIZE` bigint(21) unsigned DEFAULT NULL,
  `AUTOEXTEND_SIZE` bigint(21) unsigned DEFAULT NULL,
  `MAXIMUM_SIZE` bigint(21) unsigned DEFAULT NULL,
  `NODEGROUP_ID` bigint(21) unsigned DEFAULT NULL,
  `TABLESPACE_COMMENT` varchar(2048) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=308946 ROW_FORMAT=FIXED
;


CREATE TABLE `TABLE_CONSTRAINTS` (
  `CONSTRAINT_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `CONSTRAINT_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `CONSTRAINT_NAME` varchar(64) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `CONSTRAINT_TYPE` varchar(64) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=857621 ROW_FORMAT=FIXED
;


CREATE TABLE `TABLE_PRIVILEGES` (
  `GRANTEE` varchar(190) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=795364 ROW_FORMAT=FIXED
;


CREATE TABLE `TABLE_STATISTICS` (
  `TABLE_SCHEMA` varchar(192) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(192) NOT NULL DEFAULT '',
  `ROWS_READ` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_CHANGED` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_CHANGED_X_INDEXES` bigint(21) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1818360 ROW_FORMAT=FIXED
;


CREATE TABLE `TEAMS` (
  `TID` int(11) NOT NULL,
  `TNAME` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`TID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `TRANSACTIONHISTORY` (
  `TRANSACTIONID` int(11) NOT NULL COMMENT 'Primary key for TransactionHistory records.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `REFERENCEORDERID` int(11) NOT NULL COMMENT 'Purchase order, sales order, or work order identification number.',
  `REFERENCEORDERLINEID` int(11) NOT NULL DEFAULT 0 COMMENT 'Line number associated with the purchase order, sales order, or work order.',
  `TRANSACTIONDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time of the transaction.',
  `TRANSACTIONTYPE` char(1) NOT NULL COMMENT 'W = WorkOrder, S = SalesOrder, P = PurchaseOrder',
  `QUANTITY` int(11) NOT NULL COMMENT 'Product quantity.',
  `ACTUALCOST` decimal(19,4) NOT NULL COMMENT 'Product cost.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`TRANSACTIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Record of each purchase order, sales order, or work order transaction year to date.'
;


CREATE TABLE `TRANSACTIONHISTORYARCHIVE` (
  `TRANSACTIONID` int(11) NOT NULL COMMENT 'Primary key for TransactionHistoryArchive records.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `REFERENCEORDERID` int(11) NOT NULL COMMENT 'Purchase order, sales order, or work order identification number.',
  `REFERENCEORDERLINEID` int(11) NOT NULL DEFAULT 0 COMMENT 'Line number associated with the purchase order, sales order, or work order.',
  `TRANSACTIONDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time of the transaction.',
  `TRANSACTIONTYPE` char(1) NOT NULL COMMENT 'W = Work Order, S = Sales Order, P = Purchase Order',
  `QUANTITY` int(11) NOT NULL COMMENT 'Product quantity.',
  `ACTUALCOST` decimal(19,4) NOT NULL COMMENT 'Product cost.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`TRANSACTIONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Transactions for previous years.'
;


CREATE TABLE `TRIGGERS` (
  `TRIGGER_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TRIGGER_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TRIGGER_NAME` varchar(64) NOT NULL DEFAULT '',
  `EVENT_MANIPULATION` varchar(6) NOT NULL DEFAULT '',
  `EVENT_OBJECT_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `EVENT_OBJECT_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `EVENT_OBJECT_TABLE` varchar(64) NOT NULL DEFAULT '',
  `ACTION_ORDER` bigint(4) NOT NULL DEFAULT 0,
  `ACTION_CONDITION` longtext DEFAULT NULL,
  `ACTION_STATEMENT` longtext NOT NULL,
  `ACTION_ORIENTATION` varchar(9) NOT NULL DEFAULT '',
  `ACTION_TIMING` varchar(6) NOT NULL DEFAULT '',
  `ACTION_REFERENCE_OLD_TABLE` varchar(64) DEFAULT NULL,
  `ACTION_REFERENCE_NEW_TABLE` varchar(64) DEFAULT NULL,
  `ACTION_REFERENCE_OLD_ROW` varchar(3) NOT NULL DEFAULT '',
  `ACTION_REFERENCE_NEW_ROW` varchar(3) NOT NULL DEFAULT '',
  `CREATED` datetime DEFAULT NULL,
  `SQL_MODE` varchar(8192) NOT NULL DEFAULT '',
  `DEFINER` varchar(189) NOT NULL DEFAULT '',
  `CHARACTER_SET_CLIENT` varchar(32) NOT NULL DEFAULT '',
  `COLLATION_CONNECTION` varchar(32) NOT NULL DEFAULT '',
  `DATABASE_COLLATION` varchar(32) NOT NULL DEFAULT ''
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=72065 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `TransactionHistory` (
  `TransactionID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for TransactionHistory records.',
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `ReferenceOrderID` int(11) NOT NULL COMMENT 'Purchase order, sales order, or work order identification number.',
  `ReferenceOrderLineID` int(11) NOT NULL DEFAULT 0 COMMENT 'Line number associated with the purchase order, sales order, or work order.',
  `TransactionDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time of the transaction.',
  `TransactionType` char(1) NOT NULL COMMENT 'W = WorkOrder, S = SalesOrder, P = PurchaseOrder',
  `Quantity` int(11) NOT NULL COMMENT 'Product quantity.',
  `ActualCost` decimal(19,4) NOT NULL COMMENT 'Product cost.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`TransactionID`),
  KEY `IX_TransactionHistory_ProductID` (`ProductID`),
  KEY `IX_TransactionHistory_ReferenceOrderID_ReferenceOrderLineID` (`ReferenceOrderID`,`ReferenceOrderLineID`),
  CONSTRAINT `FK_TransactionHistory_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Record of each purchase order, sales order, or work order transaction year to date.'
;


CREATE TABLE `TransactionHistoryArchive` (
  `TransactionID` int(11) NOT NULL COMMENT 'Primary key for TransactionHistoryArchive records.',
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `ReferenceOrderID` int(11) NOT NULL COMMENT 'Purchase order, sales order, or work order identification number.',
  `ReferenceOrderLineID` int(11) NOT NULL DEFAULT 0 COMMENT 'Line number associated with the purchase order, sales order, or work order.',
  `TransactionDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time of the transaction.',
  `TransactionType` char(1) NOT NULL COMMENT 'W = Work Order, S = Sales Order, P = Purchase Order',
  `Quantity` int(11) NOT NULL COMMENT 'Product quantity.',
  `ActualCost` decimal(19,4) NOT NULL COMMENT 'Product cost.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`TransactionID`),
  KEY `IX_TransactionHistoryArchive_ProductID` (`ProductID`),
  KEY `IX_TransactionHistoryArchive_ReferenceOrderID_ReferenceOrderLi2` (`ReferenceOrderID`,`ReferenceOrderLineID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Transactions for previous years.'
;


CREATE TABLE `UNITMEASURE` (
  `UNITMEASURECODE` char(3) NOT NULL COMMENT 'Primary key.',
  `NAME` varchar(100) NOT NULL COMMENT 'Unit of measure description.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`UNITMEASURECODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Unit of measure lookup table.'
;


CREATE TABLE `UPRAVNA_ENOTA` (
  `ID_UPRAVNA_ENOTA` char(4) NOT NULL,
  `IME_UPRAVNA_ENOTA` varchar(255) NOT NULL,
  `ST_PREBIVALCEV` int(10) unsigned DEFAULT NULL,
  `POVRSINA` smallint(5) unsigned DEFAULT NULL,
  PRIMARY KEY (`ID_UPRAVNA_ENOTA`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `USER_PRIVILEGES` (
  `GRANTEE` varchar(190) NOT NULL DEFAULT '',
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `PRIVILEGE_TYPE` varchar(64) NOT NULL DEFAULT '',
  `IS_GRANTABLE` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=928039 ROW_FORMAT=FIXED
;


CREATE TABLE `USER_STATISTICS` (
  `USER` varchar(128) NOT NULL DEFAULT '',
  `TOTAL_CONNECTIONS` int(11) NOT NULL DEFAULT 0,
  `CONCURRENT_CONNECTIONS` int(11) NOT NULL DEFAULT 0,
  `CONNECTED_TIME` int(11) NOT NULL DEFAULT 0,
  `BUSY_TIME` double NOT NULL DEFAULT 0,
  `CPU_TIME` double NOT NULL DEFAULT 0,
  `BYTES_RECEIVED` bigint(21) NOT NULL DEFAULT 0,
  `BYTES_SENT` bigint(21) NOT NULL DEFAULT 0,
  `BINLOG_BYTES_WRITTEN` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_READ` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_SENT` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_DELETED` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_INSERTED` bigint(21) NOT NULL DEFAULT 0,
  `ROWS_UPDATED` bigint(21) NOT NULL DEFAULT 0,
  `SELECT_COMMANDS` bigint(21) NOT NULL DEFAULT 0,
  `UPDATE_COMMANDS` bigint(21) NOT NULL DEFAULT 0,
  `OTHER_COMMANDS` bigint(21) NOT NULL DEFAULT 0,
  `COMMIT_TRANSACTIONS` bigint(21) NOT NULL DEFAULT 0,
  `ROLLBACK_TRANSACTIONS` bigint(21) NOT NULL DEFAULT 0,
  `DENIED_CONNECTIONS` bigint(21) NOT NULL DEFAULT 0,
  `LOST_CONNECTIONS` bigint(21) NOT NULL DEFAULT 0,
  `ACCESS_DENIED` bigint(21) NOT NULL DEFAULT 0,
  `EMPTY_QUERIES` bigint(21) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=3897429 ROW_FORMAT=FIXED
;


CREATE TABLE `UnitMeasure` (
  `UnitMeasureCode` char(3) NOT NULL COMMENT 'Primary key.',
  `Name` varchar(100) NOT NULL COMMENT 'Unit of measure description.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`UnitMeasureCode`),
  UNIQUE KEY `AK_UnitMeasure_Name` (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Unit of measure lookup table.'
;


CREATE TABLE `Users` (
  `user_id` varchar(30) NOT NULL DEFAULT '',
  `votes_funny` int(11) DEFAULT NULL,
  `votes_useful` int(11) DEFAULT NULL,
  `votes_cool` int(11) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `average_stars` double DEFAULT NULL,
  `review_count` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `VENDOR` (
  `BUSINESSENTITYID` int(11) NOT NULL COMMENT 'Primary key for Vendor records.  Foreign key to BusinessEntity.BusinessEntityID',
  `ACCOUNTNUMBER` varchar(30) NOT NULL COMMENT 'Vendor account (identification) number.',
  `NAME` varchar(100) NOT NULL COMMENT 'Company name.',
  `CREDITRATING` tinyint(3) unsigned NOT NULL COMMENT '1 = Superior, 2 = Excellent, 3 = Above average, 4 = Average, 5 = Below average',
  `PREFERREDVENDORSTATUS` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Do not use if another vendor is available. 1 = Preferred over other vendors supplying the same product.',
  `ACTIVEFLAG` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Vendor no longer used. 1 = Vendor is actively used.',
  `PURCHASINGWEBSERVICEURL` varchar(1024) DEFAULT NULL COMMENT 'Vendor URL.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BUSINESSENTITYID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Companies from whom Adventure Works Cycles purchases parts or other goods.'
;


CREATE TABLE `VIEWS` (
  `TABLE_CATALOG` varchar(512) NOT NULL DEFAULT '',
  `TABLE_SCHEMA` varchar(64) NOT NULL DEFAULT '',
  `TABLE_NAME` varchar(64) NOT NULL DEFAULT '',
  `VIEW_DEFINITION` longtext NOT NULL,
  `CHECK_OPTION` varchar(8) NOT NULL DEFAULT '',
  `IS_UPDATABLE` varchar(3) NOT NULL DEFAULT '',
  `DEFINER` varchar(189) NOT NULL DEFAULT '',
  `SECURITY_TYPE` varchar(7) NOT NULL DEFAULT '',
  `CHARACTER_SET_CLIENT` varchar(32) NOT NULL DEFAULT '',
  `COLLATION_CONNECTION` varchar(32) NOT NULL DEFAULT ''
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=779203 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `Vendor` (
  `BusinessEntityID` int(11) NOT NULL COMMENT 'Primary key for Vendor records.  Foreign key to BusinessEntity.BusinessEntityID',
  `AccountNumber` varchar(30) NOT NULL COMMENT 'Vendor account (identification) number.',
  `Name` varchar(100) NOT NULL COMMENT 'Company name.',
  `CreditRating` tinyint(3) unsigned NOT NULL COMMENT '1 = Superior, 2 = Excellent, 3 = Above average, 4 = Average, 5 = Below average',
  `PreferredVendorStatus` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Do not use if another vendor is available. 1 = Preferred over other vendors supplying the same product.',
  `ActiveFlag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Vendor no longer used. 1 = Vendor is actively used.',
  `PurchasingWebServiceURL` varchar(1024) DEFAULT NULL COMMENT 'Vendor URL.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`BusinessEntityID`),
  UNIQUE KEY `AK_Vendor_AccountNumber` (`AccountNumber`),
  CONSTRAINT `FK_Vendor_BusinessEntity_BusinessEntityID` FOREIGN KEY (`BusinessEntityID`) REFERENCES `BusinessEntity` (`BusinessEntityID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Companies from whom Adventure Works Cycles purchases parts or other goods.'
;


CREATE TABLE `WORKORDER` (
  `WORKORDERID` int(11) NOT NULL COMMENT 'Primary key for WorkOrder records.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `ORDERQTY` int(11) NOT NULL COMMENT 'Product quantity to build.',
  `STOCKEDQTY` int(11) NOT NULL COMMENT 'Quantity built and put in inventory.',
  `SCRAPPEDQTY` smallint(6) NOT NULL COMMENT 'Quantity that failed inspection.',
  `STARTDATE` datetime NOT NULL COMMENT 'Work order start date.',
  `ENDDATE` datetime DEFAULT NULL COMMENT 'Work order end date.',
  `DUEDATE` datetime NOT NULL COMMENT 'Work order due date.',
  `SCRAPREASONID` smallint(6) DEFAULT NULL COMMENT 'Reason for inspection failure.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`WORKORDERID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Manufacturing work orders.'
;


CREATE TABLE `WORKORDERROUTING` (
  `WORKORDERID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to WorkOrder.WorkOrderID.',
  `PRODUCTID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Product.ProductID.',
  `OPERATIONSEQUENCE` smallint(6) NOT NULL COMMENT 'Primary key. Indicates the manufacturing process sequence.',
  `LOCATIONID` smallint(6) NOT NULL COMMENT 'Manufacturing location where the part is processed. Foreign key to Location.LocationID.',
  `SCHEDULEDSTARTDATE` datetime NOT NULL COMMENT 'Planned manufacturing start date.',
  `SCHEDULEDENDDATE` datetime NOT NULL COMMENT 'Planned manufacturing end date.',
  `ACTUALSTARTDATE` datetime DEFAULT NULL COMMENT 'Actual start date.',
  `ACTUALENDDATE` datetime DEFAULT NULL COMMENT 'Actual end date.',
  `ACTUALRESOURCEHRS` decimal(9,4) DEFAULT NULL COMMENT 'Number of manufacturing hours used.',
  `PLANNEDCOST` decimal(19,4) NOT NULL COMMENT 'Estimated manufacturing cost.',
  `ACTUALCOST` decimal(19,4) DEFAULT NULL COMMENT 'Actual manufacturing cost.',
  `MODIFIEDDATE` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`WORKORDERID`,`PRODUCTID`,`OPERATIONSEQUENCE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Work order details.'
;


CREATE TABLE `WorkOrder` (
  `WorkOrderID` int(11) NOT NULL AUTO_INCREMENT COMMENT 'Primary key for WorkOrder records.',
  `ProductID` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `OrderQty` int(11) NOT NULL COMMENT 'Product quantity to build.',
  `StockedQty` int(11) NOT NULL COMMENT 'Quantity built and put in inventory.',
  `ScrappedQty` smallint(6) NOT NULL COMMENT 'Quantity that failed inspection.',
  `StartDate` datetime NOT NULL COMMENT 'Work order start date.',
  `EndDate` datetime DEFAULT NULL COMMENT 'Work order end date.',
  `DueDate` datetime NOT NULL COMMENT 'Work order due date.',
  `ScrapReasonID` smallint(6) DEFAULT NULL COMMENT 'Reason for inspection failure.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`WorkOrderID`),
  KEY `IX_WorkOrder_ScrapReasonID` (`ScrapReasonID`),
  KEY `IX_WorkOrder_ProductID` (`ProductID`),
  CONSTRAINT `FK_WorkOrder_Product_ProductID` FOREIGN KEY (`ProductID`) REFERENCES `Product` (`ProductID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_WorkOrder_ScrapReason_ScrapReasonID` FOREIGN KEY (`ScrapReasonID`) REFERENCES `ScrapReason` (`ScrapReasonID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Manufacturing work orders.'
;


CREATE TABLE `WorkOrderRouting` (
  `WorkOrderID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to WorkOrder.WorkOrderID.',
  `ProductID` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Product.ProductID.',
  `OperationSequence` smallint(6) NOT NULL COMMENT 'Primary key. Indicates the manufacturing process sequence.',
  `LocationID` smallint(6) NOT NULL COMMENT 'Manufacturing location where the part is processed. Foreign key to Location.LocationID.',
  `ScheduledStartDate` datetime NOT NULL COMMENT 'Planned manufacturing start date.',
  `ScheduledEndDate` datetime NOT NULL COMMENT 'Planned manufacturing end date.',
  `ActualStartDate` datetime DEFAULT NULL COMMENT 'Actual start date.',
  `ActualEndDate` datetime DEFAULT NULL COMMENT 'Actual end date.',
  `ActualResourceHrs` decimal(9,4) DEFAULT NULL COMMENT 'Number of manufacturing hours used.',
  `PlannedCost` decimal(19,4) NOT NULL COMMENT 'Estimated manufacturing cost.',
  `ActualCost` decimal(19,4) DEFAULT NULL COMMENT 'Actual manufacturing cost.',
  `ModifiedDate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`WorkOrderID`,`ProductID`,`OperationSequence`),
  KEY `IX_WorkOrderRouting_ProductID` (`ProductID`),
  KEY `FK_WorkOrderRouting_Location_LocationID` (`LocationID`),
  CONSTRAINT `FK_WorkOrderRouting_Location_LocationID` FOREIGN KEY (`LocationID`) REFERENCES `Location` (`LocationID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_WorkOrderRouting_WorkOrder_WorkOrderID` FOREIGN KEY (`WorkOrderID`) REFERENCES `WorkOrder` (`WorkOrderID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Work order details.'
;


CREATE TABLE `XTRADB_INTERNAL_HASH_TABLES` (
  `INTERNAL_HASH_TABLE_NAME` varchar(100) NOT NULL DEFAULT '',
  `TOTAL_MEMORY` bigint(21) unsigned NOT NULL DEFAULT 0,
  `CONSTANT_MEMORY` bigint(21) unsigned NOT NULL DEFAULT 0,
  `VARIABLE_MEMORY` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=6567228 ROW_FORMAT=FIXED
;


CREATE TABLE `XTRADB_READ_VIEW` (
  `READ_VIEW_UNDO_NUMBER` bigint(21) unsigned NOT NULL DEFAULT 0,
  `READ_VIEW_LOW_LIMIT_TRX_NUMBER` varchar(18) NOT NULL DEFAULT '',
  `READ_VIEW_UPPER_LIMIT_TRX_ID` varchar(18) NOT NULL DEFAULT '',
  `READ_VIEW_LOW_LIMIT_TRX_ID` varchar(18) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=12341860 ROW_FORMAT=FIXED
;


CREATE TABLE `XTRADB_RSEG` (
  `rseg_id` bigint(21) unsigned NOT NULL DEFAULT 0,
  `space_id` bigint(21) unsigned NOT NULL DEFAULT 0,
  `zip_size` bigint(21) unsigned NOT NULL DEFAULT 0,
  `page_no` bigint(21) unsigned NOT NULL DEFAULT 0,
  `max_size` bigint(21) unsigned NOT NULL DEFAULT 0,
  `curr_size` bigint(21) unsigned NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=43826196 ROW_FORMAT=FIXED
;


CREATE TABLE `active_follower_real` (
  `user_id` int(11) NOT NULL,
  `follower_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`follower_id`),
  KEY `NewIndex1` (`user_id`),
  KEY `NewIndex2` (`follower_id`),
  CONSTRAINT `active_follower_real_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `distinct_users_from_search_table_real_map` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `active_follower_real_ibfk_2` FOREIGN KEY (`follower_id`) REFERENCES `distinct_users_from_search_table_real_map` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `address` (
  `addressid` int(11) NOT NULL COMMENT 'Primary key for Address records.',
  `addressline1` varchar(60) NOT NULL COMMENT 'First street address line.',
  `addressline2` varchar(60) DEFAULT NULL COMMENT 'Second street address line.',
  `city` varchar(30) NOT NULL COMMENT 'Name of the city.',
  `stateprovinceid` int(11) NOT NULL COMMENT 'Unique identification number for the state or province. Foreign key to StateProvince table.',
  `postalcode` varchar(15) NOT NULL COMMENT 'Postal code for the street address.',
  `spatiallocation` geometry DEFAULT NULL COMMENT 'Latitude and longitude of this address.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`addressid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Street address information for customers, employees, and vendors.'
;


CREATE TABLE `addresstype` (
  `addresstypeid` int(11) NOT NULL COMMENT 'Primary key for AddressType records.',
  `name` varchar(100) NOT NULL COMMENT 'Address type description. For example, Billing, Home, or Shipping.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`addresstypeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Types of addresses stored in the Address table. '
;


CREATE TABLE `algorithm` (
  `name` varchar(128) NOT NULL DEFAULT '',
  `function` text DEFAULT NULL,
  `description` mediumtext DEFAULT NULL,
  `algorithm_class` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `algorithm_quality` (
  `implementation_id` int(16) NOT NULL,
  `quality` varchar(128) NOT NULL DEFAULT '',
  `qualityImplementation` varchar(64) DEFAULT NULL,
  `label` varchar(128) NOT NULL,
  `value` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`implementation_id`,`quality`,`label`),
  KEY `algorithm_quality_quality` (`quality`),
  CONSTRAINT `algorithm_quality_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `algorithm_quality_ibfk_2` FOREIGN KEY (`quality`) REFERENCES `quality` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `algorithm_setup` (
  `sid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `parent` int(10) unsigned NOT NULL,
  `implementation_id` int(16) NOT NULL,
  `algorithm` varchar(128) DEFAULT NULL,
  `role` varchar(64) NOT NULL DEFAULT 'Learner',
  `isDefault` enum('true','false') DEFAULT 'false',
  `algorithm_structure` varchar(64) DEFAULT NULL,
  `setup_string` text DEFAULT NULL,
  PRIMARY KEY (`sid`),
  KEY `algorithm_setup_algorithm_isDefault_sid` (`algorithm`,`isDefault`,`sid`),
  KEY `algorithm_setup_algorithm` (`algorithm`),
  KEY `algorithm_setup_implementation_id` (`implementation_id`),
  KEY `algorithm_setup_isDefault` (`isDefault`),
  KEY `algorithm_setup_parent` (`parent`),
  KEY `algorithm_setup_role` (`role`),
  KEY `algorithm_setup_role_parent` (`role`,`parent`),
  KEY `algorithm_setup_role_sid` (`role`,`sid`),
  CONSTRAINT `algorithm_setup_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `algorithm_setup_ibfk_2` FOREIGN KEY (`algorithm`) REFERENCES `algorithm` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `all_plugins` (
  `plugin_name` varchar(64) NOT NULL DEFAULT '',
  `plugin_version` varchar(20) NOT NULL DEFAULT '',
  `plugin_status` varchar(16) NOT NULL DEFAULT '',
  `plugin_type` varchar(80) NOT NULL DEFAULT '',
  `plugin_type_version` varchar(20) NOT NULL DEFAULT '',
  `plugin_library` varchar(64) DEFAULT NULL,
  `plugin_library_version` varchar(20) DEFAULT NULL,
  `plugin_author` varchar(64) DEFAULT NULL,
  `plugin_description` longtext DEFAULT NULL,
  `plugin_license` varchar(80) NOT NULL DEFAULT '',
  `load_option` varchar(64) NOT NULL DEFAULT '',
  `plugin_maturity` varchar(12) NOT NULL DEFAULT '',
  `plugin_auth_version` varchar(80) DEFAULT NULL
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=1208488 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `app_all` (
  `app_id` bigint(20) NOT NULL,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `app_events` (
  `event_id` int(11) DEFAULT NULL,
  `app_id` bigint(20) DEFAULT NULL,
  `is_installed` tinyint(4) DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT NULL,
  KEY `event_id` (`event_id`),
  CONSTRAINT `app_events_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `app_events_relevant` (
  `event_id` int(11) NOT NULL,
  `app_id` bigint(20) NOT NULL,
  `is_installed` tinyint(4) DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`event_id`,`app_id`),
  KEY `event_id` (`event_id`),
  KEY `app_id` (`app_id`),
  CONSTRAINT `app_events_relevant_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events_relevant` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `app_events_relevant_ibfk_2` FOREIGN KEY (`app_id`) REFERENCES `app_all` (`app_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `app_labels` (
  `app_id` bigint(20) DEFAULT NULL,
  `label_id` int(11) DEFAULT NULL,
  KEY `label_id` (`label_id`),
  KEY `app_id` (`app_id`),
  CONSTRAINT `app_labels_ibfk_1` FOREIGN KEY (`label_id`) REFERENCES `label_categories` (`label_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `app_labels_ibfk_2` FOREIGN KEY (`app_id`) REFERENCES `app_all` (`app_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `applicable_roles` (
  `grantee` varchar(190) NOT NULL DEFAULT '',
  `role_name` varchar(128) NOT NULL DEFAULT '',
  `is_grantable` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=2216185 ROW_FORMAT=FIXED
;


CREATE TABLE `atom` (
  `atom_id` varchar(255) NOT NULL,
  `molecule_id` varchar(255) DEFAULT NULL,
  `element` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`atom_id`),
  KEY `molecule_id` (`molecule_id`),
  KEY `atom_id` (`atom_id`),
  CONSTRAINT `atom_ibfk_1` FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `awbuildversion` (
  `systeminformationid` tinyint(3) unsigned NOT NULL COMMENT 'Primary key for AWBuildVersion records.',
  `database version` varchar(25) NOT NULL COMMENT 'Version number of the database in 9.yy.mm.dd.00 format.',
  `versiondate` datetime NOT NULL COMMENT 'Date and time the record was last updated.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`systeminformationid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Current version number of the AdventureWorks 2014 sample database. '
;


CREATE TABLE `badges` (
  `Id` int(11) NOT NULL,
  `UserId` int(11) DEFAULT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Date` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `badges_UserId_fkey` (`UserId`),
  CONSTRAINT `badges_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `base` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `base_sampled` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  KEY `ix_base_sampled` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bibliographical_reference` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `implementation_id` int(16) NOT NULL,
  `citation` mediumtext NOT NULL,
  `url` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bibliographical_reference_implementation_id` (`implementation_id`),
  CONSTRAINT `bibliographical_reference_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `billofmaterials` (
  `billofmaterialsid` int(11) NOT NULL COMMENT 'Primary key for BillOfMaterials records.',
  `productassemblyid` int(11) DEFAULT NULL COMMENT 'Parent product identification number. Foreign key to Product.ProductID.',
  `componentid` int(11) NOT NULL COMMENT 'Component identification number. Foreign key to Product.ProductID.',
  `startdate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date the component started being used in the assembly item.',
  `enddate` datetime DEFAULT NULL COMMENT 'Date the component stopped being used in the assembly item.',
  `unitmeasurecode` char(3) NOT NULL COMMENT 'Standard code identifying the unit of measure for the quantity.',
  `bomlevel` smallint(6) NOT NULL COMMENT 'Indicates the depth the component is from its parent (AssemblyID).',
  `perassemblyqty` decimal(8,2) NOT NULL DEFAULT 1.00 COMMENT 'Quantity of the component needed to create the assembly.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`billofmaterialsid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Items required to make bicycles and bicycle subassemblies. It identifies the heirarchical relationship between a parent product and its components.'
;


CREATE TABLE `bkp_Walmart_MS` (
  `propagated_id1` int(11) DEFAULT NULL,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `account_date_date_timeDiff_100001` int(7) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_Walmart_j_pattern` (
  `name` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `is_aggregate` int(11) DEFAULT NULL,
  `is_multivariate` int(11) DEFAULT NULL,
  `is_nominal` int(11) DEFAULT NULL,
  `is_numerical` int(11) DEFAULT NULL,
  `is_temporal` int(11) DEFAULT NULL,
  `uses_base_target` int(11) DEFAULT NULL,
  `uses_base_date` int(11) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_Walmart_j_predictor` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_Walmart_j_table` (
  `table_id` int(11) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `original_name` varchar(255) DEFAULT NULL,
  `temporal_constraint` varchar(255) DEFAULT NULL,
  `temporal_constraint_reasoning` varchar(1024) DEFAULT NULL,
  `candidate_temporal_list` varchar(2024) DEFAULT NULL,
  `candidate_temporal_count` int(11) DEFAULT NULL,
  `row_count_optimistic` int(11) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `propagation_id` varchar(1024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `is_id_unique` int(11) DEFAULT NULL,
  `is_target_id_unique` int(11) DEFAULT NULL,
  `qc_successfully_executed` int(11) DEFAULT NULL,
  `qc_row_count` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp__financial_MAINSAMPLE` (
  `propagated_id1` int(11) DEFAULT NULL,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100022` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100027` int(11) DEFAULT NULL,
  `order_account_id_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `order_order_id_aggregate_stddev_samp_100004` double(26,4) DEFAULT NULL,
  `loan_date_directField_timeColumn_100031` date DEFAULT NULL,
  `order_account_to_aggregate_avg_100006` decimal(14,4) DEFAULT NULL,
  `order_amount_aggregate_sum_100019` decimal(28,1) DEFAULT NULL,
  `order_amount_aggregate_avg_100007` decimal(10,5) DEFAULT NULL,
  `order_amount_aggregate_min_100011` decimal(6,1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100026` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp__financial_journal_pattern` (
  `name` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `is_aggregate` int(11) DEFAULT NULL,
  `is_multivariate` int(11) DEFAULT NULL,
  `is_nominal` int(11) DEFAULT NULL,
  `is_numerical` int(11) DEFAULT NULL,
  `is_temporal` int(11) DEFAULT NULL,
  `uses_base_target` int(11) DEFAULT NULL,
  `uses_base_date` int(11) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp__financial_journal_predictor` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp__financial_journal_table` (
  `table_id` int(11) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `original_name` varchar(255) DEFAULT NULL,
  `temporal_constraint` varchar(255) DEFAULT NULL,
  `temporal_constraint_reasoning` varchar(1024) DEFAULT NULL,
  `candidate_temporal_list` varchar(2024) DEFAULT NULL,
  `candidate_temporal_count` int(11) DEFAULT NULL,
  `row_count_optimistic` int(11) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `propagation_id` varchar(1024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `is_id_unique` int(11) DEFAULT NULL,
  `is_target_id_unique` int(11) DEFAULT NULL,
  `qc_successfully_executed` int(11) DEFAULT NULL,
  `qc_row_count` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_MAINSAMPLE` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100015` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100030` int(11) DEFAULT NULL,
  `loan_date_directField_timeColumn_100034` date DEFAULT NULL,
  `order_account_to_aggregate_max_100007` int(11) DEFAULT NULL,
  `order_account_to_aggregate_avg_100003` decimal(14,4) DEFAULT NULL,
  `account_date_directField_timeColumn_100032` date DEFAULT NULL,
  `district_A6_directField_numericalColumn_100025` int(11) DEFAULT NULL,
  `card_issued_directField_timeColumn_100033` date DEFAULT NULL,
  `district_A3_directField_nominalColumn_100014` varchar(15) DEFAULT NULL,
  `district_A11_directField_numericalColumn_100017` int(11) DEFAULT NULL,
  `district_A10_directField_numericalColumn_100016` decimal(4,1) DEFAULT NULL,
  `order_amount_aggregate_sum_100010` decimal(28,1) DEFAULT NULL,
  `order_amount_aggregate_avg_100004` decimal(10,5) DEFAULT NULL,
  `order_amount_aggregate_min_100006` decimal(6,1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100029` int(11) DEFAULT NULL,
  `district_A16_directField_numericalColumn_100022` int(11) DEFAULT NULL,
  `district_A2_directField_nominalColumn_100013` varchar(19) DEFAULT NULL,
  `order_amount_aggregate_max_100008` decimal(6,1) DEFAULT NULL,
  `district_A15_directField_numericalColumn_100021` int(5) DEFAULT NULL,
  `district_A13_directField_numericalColumn_100019` decimal(3,2) DEFAULT NULL,
  `district_A12_directField_numericalColumn_100018` decimal(4,1) DEFAULT NULL,
  `loan_payments_directField_numericalColumn_100031` decimal(6,2) DEFAULT NULL,
  `district_A14_directField_numericalColumn_100020` int(11) DEFAULT NULL,
  `card_type_directField_nominalColumn_100012` varchar(7) DEFAULT NULL,
  `district_A5_directField_numericalColumn_100024` int(11) DEFAULT NULL,
  `district_A7_directField_numericalColumn_100026` int(11) DEFAULT NULL,
  `district_A9_directField_numericalColumn_100028` int(11) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `account_frequency_directField_nominalColumn_100011` varchar(18) DEFAULT '',
  `district_A8_directField_numericalColumn_100027` int(6) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_MS` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100085` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100106` int(11) DEFAULT NULL,
  `order_account_id_aggregate_stddev_samp_100008` double(26,4) DEFAULT NULL,
  `trans_amount_aggregate_min_100046` int(11) DEFAULT NULL,
  `trans_balance_aggregate_min_100047` int(11) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  `order_order_id_aggregate_stddev_samp_100011` double(26,4) DEFAULT NULL,
  `loan_date_directField_timeColumn_100111` date DEFAULT NULL,
  `order_account_to_aggregate_avg_100025` decimal(14,4) DEFAULT NULL,
  `client_client_id_aggregate_sum_100067` decimal(32,0) DEFAULT NULL,
  `loan_account_id_directField_numericalColumn_100104` int(11) DEFAULT NULL,
  `order_amount_aggregate_sum_100074` decimal(28,1) DEFAULT NULL,
  `order_amount_aggregate_avg_100026` decimal(10,5) DEFAULT NULL,
  `order_amount_aggregate_min_100042` decimal(6,1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100105` int(11) DEFAULT NULL,
  `order_amount_aggregate_max_100058` decimal(6,1) DEFAULT NULL,
  `trans_amount_aggregate_max_100062` int(11) DEFAULT NULL,
  `trans_account_aggregate_min_100044` int(11) unsigned DEFAULT NULL,
  `district_A9_directField_numericalColumn_100102` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_j_pattern` (
  `name` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `is_aggregate` int(11) DEFAULT NULL,
  `is_multivariate` int(11) DEFAULT NULL,
  `is_nominal` int(11) DEFAULT NULL,
  `is_numerical` int(11) DEFAULT NULL,
  `is_temporal` int(11) DEFAULT NULL,
  `uses_base_target` int(11) DEFAULT NULL,
  `uses_base_date` int(11) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_j_predictor` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_j_table` (
  `table_id` int(11) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `original_name` varchar(255) DEFAULT NULL,
  `temporal_constraint` varchar(255) DEFAULT NULL,
  `temporal_constraint_reasoning` varchar(1024) DEFAULT NULL,
  `candidate_temporal_list` varchar(2024) DEFAULT NULL,
  `candidate_temporal_count` int(11) DEFAULT NULL,
  `row_count_optimistic` int(11) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `propagation_id` varchar(1024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `is_id_unique` int(11) DEFAULT NULL,
  `is_target_id_unique` int(11) DEFAULT NULL,
  `qc_successfully_executed` int(11) DEFAULT NULL,
  `qc_row_count` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_journal_pattern` (
  `name` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `is_aggregate` int(11) DEFAULT NULL,
  `is_multivariate` int(11) DEFAULT NULL,
  `is_nominal` int(11) DEFAULT NULL,
  `is_numerical` int(11) DEFAULT NULL,
  `is_temporal` int(11) DEFAULT NULL,
  `uses_base_target` int(11) DEFAULT NULL,
  `uses_base_date` int(11) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_journal_predictor` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_financial_journal_table` (
  `table_id` int(11) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `original_name` varchar(255) DEFAULT NULL,
  `temporal_constraint` varchar(255) DEFAULT NULL,
  `temporal_constraint_reasoning` varchar(1024) DEFAULT NULL,
  `candidate_temporal_list` varchar(2024) DEFAULT NULL,
  `candidate_temporal_count` int(11) DEFAULT NULL,
  `row_count_optimistic` int(11) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `propagation_id` varchar(1024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `is_id_unique` int(11) DEFAULT NULL,
  `is_target_id_unique` int(11) DEFAULT NULL,
  `qc_successfully_executed` int(11) DEFAULT NULL,
  `qc_row_count` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_mutagenesis_MAINSAMPLE` (
  `propagated_id1` int(11) DEFAULT NULL,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100022` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100027` int(11) DEFAULT NULL,
  `order_account_id_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `order_order_id_aggregate_stddev_samp_100004` double(26,4) DEFAULT NULL,
  `loan_date_directField_timeColumn_100031` date DEFAULT NULL,
  `order_account_to_aggregate_avg_100006` decimal(14,4) DEFAULT NULL,
  `order_amount_aggregate_sum_100019` decimal(28,1) DEFAULT NULL,
  `order_amount_aggregate_avg_100007` decimal(10,5) DEFAULT NULL,
  `order_amount_aggregate_min_100011` decimal(6,1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100026` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_mutagenesis_journal_pattern` (
  `name` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `is_aggregate` int(11) DEFAULT NULL,
  `is_multivariate` int(11) DEFAULT NULL,
  `is_nominal` int(11) DEFAULT NULL,
  `is_numerical` int(11) DEFAULT NULL,
  `is_temporal` int(11) DEFAULT NULL,
  `uses_base_target` int(11) DEFAULT NULL,
  `uses_base_date` int(11) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_mutagenesis_journal_predictor` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bkp_mutagenesis_journal_table` (
  `table_id` int(11) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `original_name` varchar(255) DEFAULT NULL,
  `temporal_constraint` varchar(255) DEFAULT NULL,
  `temporal_constraint_reasoning` varchar(1024) DEFAULT NULL,
  `candidate_temporal_list` varchar(2024) DEFAULT NULL,
  `candidate_temporal_count` int(11) DEFAULT NULL,
  `row_count_optimistic` int(11) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `propagation_id` varchar(1024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `is_id_unique` int(11) DEFAULT NULL,
  `is_target_id_unique` int(11) DEFAULT NULL,
  `qc_successfully_executed` int(11) DEFAULT NULL,
  `qc_row_count` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bond` (
  `bond_id` varchar(255) NOT NULL,
  `molecule_id` varchar(255) DEFAULT NULL,
  `bond_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`bond_id`),
  KEY `bond_id` (`bond_id`),
  KEY `molecule_id` (`molecule_id`),
  CONSTRAINT `bond_ibfk_1` FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bool` (
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `businessentity` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key for all customers, vendors, and employees.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Source of the ID that connects vendors, customers, and employees with address and contact information.'
;


CREATE TABLE `businessentityaddress` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to BusinessEntity.BusinessEntityID.',
  `addressid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Address.AddressID.',
  `addresstypeid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to AddressType.AddressTypeID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`addressid`,`addresstypeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping customers, vendors, and employees to their addresses.'
;


CREATE TABLE `businessentitycontact` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to BusinessEntity.BusinessEntityID.',
  `personid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Person.BusinessEntityID.',
  `contacttypeid` int(11) NOT NULL COMMENT 'Primary key.  Foreign key to ContactType.ContactTypeID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`personid`,`contacttypeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping stores, vendors, and employees to people'
;


CREATE TABLE `cars` (
  `id` int(11) NOT NULL,
  `train_id` int(11) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `shape` varchar(255) DEFAULT NULL,
  `len` varchar(255) DEFAULT NULL,
  `sides` varchar(255) DEFAULT NULL,
  `roof` varchar(255) DEFAULT NULL,
  `wheels` int(11) DEFAULT NULL,
  `load_shape` varchar(255) DEFAULT NULL,
  `load_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `train_id` (`train_id`),
  CONSTRAINT `cars_ibfk_1` FOREIGN KEY (`train_id`) REFERENCES `trains` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `category` (
  `category_no` int(11) NOT NULL,
  `category_desc` varchar(31) NOT NULL,
  `category_code` char(2) NOT NULL,
  PRIMARY KEY (`category_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `character_sets` (
  `character_set_name` varchar(32) NOT NULL DEFAULT '',
  `default_collate_name` varchar(32) NOT NULL DEFAULT '',
  `description` varchar(60) NOT NULL DEFAULT '',
  `maxlen` bigint(3) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=5592405 ROW_FORMAT=FIXED
;


CREATE TABLE `charge` (
  `charge_no` int(11) NOT NULL,
  `member_no` int(11) NOT NULL,
  `provider_no` int(11) NOT NULL,
  `category_no` int(11) NOT NULL,
  `charge_dt` datetime NOT NULL,
  `charge_amt` decimal(19,4) NOT NULL,
  `statement_no` int(11) NOT NULL,
  `charge_code` char(2) NOT NULL,
  PRIMARY KEY (`charge_no`),
  KEY `charge_category_no` (`category_no`),
  KEY `charge_statement_no` (`statement_no`),
  KEY `charge_statement_no_2` (`statement_no`),
  KEY `charge_statement_no_3` (`statement_no`),
  KEY `charge_member_no` (`member_no`),
  KEY `charge_statement_no_4` (`statement_no`),
  KEY `charge_member_no_2` (`member_no`),
  KEY `charge_statement_no_5` (`statement_no`),
  KEY `charge_member_no_3` (`member_no`),
  KEY `charge_provider_no` (`provider_no`),
  CONSTRAINT `charge_ibfk_1` FOREIGN KEY (`category_no`) REFERENCES `category` (`category_no`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `charge_ibfk_2` FOREIGN KEY (`member_no`) REFERENCES `member` (`member_no`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `charge_ibfk_3` FOREIGN KEY (`member_no`) REFERENCES `member` (`member_no`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `charge_ibfk_4` FOREIGN KEY (`provider_no`) REFERENCES `provider` (`provider_no`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `cites` (
  `cited_paper_id` varchar(255) NOT NULL,
  `citing_paper_id` varchar(255) NOT NULL,
  PRIMARY KEY (`cited_paper_id`,`citing_paper_id`),
  KEY `cited_paper_id` (`cited_paper_id`),
  KEY `citing_paper_id` (`citing_paper_id`),
  CONSTRAINT `cites_ibfk_1` FOREIGN KEY (`cited_paper_id`) REFERENCES `webpage` (`webpage_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `cites_ibfk_2` FOREIGN KEY (`citing_paper_id`) REFERENCES `webpage` (`webpage_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `class` (
  `cls` varchar(8) NOT NULL,
  PRIMARY KEY (`cls`),
  KEY `cls` (`cls`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `client` (
  `client_id` int(11) NOT NULL,
  `kraj` varchar(255) DEFAULT NULL,
  `obor` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `client_statistics` (
  `client` varchar(64) NOT NULL DEFAULT '',
  `total_connections` bigint(21) NOT NULL DEFAULT 0,
  `concurrent_connections` bigint(21) NOT NULL DEFAULT 0,
  `connected_time` bigint(21) NOT NULL DEFAULT 0,
  `busy_time` double NOT NULL DEFAULT 0,
  `cpu_time` double NOT NULL DEFAULT 0,
  `bytes_received` bigint(21) NOT NULL DEFAULT 0,
  `bytes_sent` bigint(21) NOT NULL DEFAULT 0,
  `binlog_bytes_written` bigint(21) NOT NULL DEFAULT 0,
  `rows_read` bigint(21) NOT NULL DEFAULT 0,
  `rows_sent` bigint(21) NOT NULL DEFAULT 0,
  `rows_deleted` bigint(21) NOT NULL DEFAULT 0,
  `rows_inserted` bigint(21) NOT NULL DEFAULT 0,
  `rows_updated` bigint(21) NOT NULL DEFAULT 0,
  `select_commands` bigint(21) NOT NULL DEFAULT 0,
  `update_commands` bigint(21) NOT NULL DEFAULT 0,
  `other_commands` bigint(21) NOT NULL DEFAULT 0,
  `commit_transactions` bigint(21) NOT NULL DEFAULT 0,
  `rollback_transactions` bigint(21) NOT NULL DEFAULT 0,
  `denied_connections` bigint(21) NOT NULL DEFAULT 0,
  `lost_connections` bigint(21) NOT NULL DEFAULT 0,
  `access_denied` bigint(21) NOT NULL DEFAULT 0,
  `empty_queries` bigint(21) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=5804009 ROW_FORMAT=FIXED
;


CREATE TABLE `collation_character_set_applicability` (
  `collation_name` varchar(32) NOT NULL DEFAULT '',
  `character_set_name` varchar(32) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=11012736 ROW_FORMAT=FIXED
;


CREATE TABLE `collations` (
  `collation_name` varchar(32) NOT NULL DEFAULT '',
  `character_set_name` varchar(32) NOT NULL DEFAULT '',
  `id` bigint(11) NOT NULL DEFAULT 0,
  `is_default` varchar(3) NOT NULL DEFAULT '',
  `is_compiled` varchar(3) NOT NULL DEFAULT '',
  `sortlen` bigint(3) NOT NULL DEFAULT 0
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=9296466 ROW_FORMAT=FIXED
;


CREATE TABLE `column_privileges` (
  `grantee` varchar(190) NOT NULL DEFAULT '',
  `table_catalog` varchar(512) NOT NULL DEFAULT '',
  `table_schema` varchar(64) NOT NULL DEFAULT '',
  `table_name` varchar(64) NOT NULL DEFAULT '',
  `column_name` varchar(64) NOT NULL DEFAULT '',
  `privilege_type` varchar(64) NOT NULL DEFAULT '',
  `is_grantable` varchar(3) NOT NULL DEFAULT ''
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=742303 ROW_FORMAT=FIXED
;


CREATE TABLE `columns` (
  `table_catalog` varchar(512) NOT NULL DEFAULT '',
  `table_schema` varchar(64) NOT NULL DEFAULT '',
  `table_name` varchar(64) NOT NULL DEFAULT '',
  `column_name` varchar(64) NOT NULL DEFAULT '',
  `ordinal_position` bigint(21) unsigned NOT NULL DEFAULT 0,
  `column_default` longtext DEFAULT NULL,
  `is_nullable` varchar(3) NOT NULL DEFAULT '',
  `data_type` varchar(64) NOT NULL DEFAULT '',
  `character_maximum_length` bigint(21) unsigned DEFAULT NULL,
  `character_octet_length` bigint(21) unsigned DEFAULT NULL,
  `numeric_precision` bigint(21) unsigned DEFAULT NULL,
  `numeric_scale` bigint(21) unsigned DEFAULT NULL,
  `datetime_precision` bigint(21) unsigned DEFAULT NULL,
  `character_set_name` varchar(32) DEFAULT NULL,
  `collation_name` varchar(32) DEFAULT NULL,
  `column_type` longtext NOT NULL,
  `column_key` varchar(3) NOT NULL DEFAULT '',
  `extra` varchar(27) NOT NULL DEFAULT '',
  `privileges` varchar(80) NOT NULL DEFAULT '',
  `column_comment` varchar(1024) NOT NULL DEFAULT ''
) ENGINE=Aria DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=358272 PAGE_CHECKSUM=0 ROW_FORMAT=PAGE TRANSACTIONAL=0
;


CREATE TABLE `comments` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) DEFAULT NULL,
  `Score` int(11) DEFAULT NULL,
  `Text` longtext DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `UserDisplayName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `comment_staged_UserId_fkey` (`UserId`),
  KEY `comment_PostId_fkey` (`PostId`),
  CONSTRAINT `comment_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comment_staged_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_other` (
  `component_id` varchar(255) DEFAULT NULL,
  `part_ me` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  KEY `comp_other_component_id` (`component_id`),
  CONSTRAINT `comp_other_ibfk_1` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_tee` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `bolt_pattern_long` float DEFAULT NULL,
  `bolt_pattern_wide` float DEFAULT NULL,
  `extension_length` float DEFAULT NULL,
  `overall_length` float DEFAULT NULL,
  `thickness` int(11) DEFAULT NULL,
  `drop_length` float DEFAULT NULL,
  `mj_class_code` varchar(255) DEFAULT NULL,
  `mj_plug_class_code` varchar(255) DEFAULT NULL,
  `groove` varchar(255) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  KEY `comp_tee_component_id` (`component_id`),
  KEY `comp_tee_component_type_id` (`component_type_id`),
  CONSTRAINT `comp_tee_ibfk_1` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `components` (
  `component_id` varchar(255) NOT NULL,
  `me` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`component_id`),
  UNIQUE KEY `components_component_id_key` (`component_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `connected` (
  `atom_id` varchar(255) NOT NULL,
  `atom_id2` varchar(255) NOT NULL,
  `bond_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`atom_id`,`atom_id2`),
  KEY `atom_id` (`atom_id`),
  KEY `atom_id2` (`atom_id2`),
  KEY `bond_id` (`bond_id`),
  CONSTRAINT `connected_ibfk_1` FOREIGN KEY (`atom_id`) REFERENCES `atom` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `connected_ibfk_2` FOREIGN KEY (`atom_id2`) REFERENCES `atom` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `connected_ibfk_3` FOREIGN KEY (`bond_id`) REFERENCES `bond` (`bond_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `contacttype` (
  `contacttypeid` int(11) NOT NULL COMMENT 'Primary key for ContactType records.',
  `name` varchar(100) NOT NULL COMMENT 'Contact type description.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`contacttypeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the types of business entity contacts.'
;


CREATE TABLE `content` (
  `webpage_id` varchar(255) NOT NULL,
  `word_cited_id` varchar(255) NOT NULL,
  PRIMARY KEY (`webpage_id`,`word_cited_id`),
  KEY `webpage_id` (`webpage_id`),
  CONSTRAINT `content_ibfk_1` FOREIGN KEY (`webpage_id`) REFERENCES `webpage` (`webpage_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `corporation` (
  `corp_no` int(11) NOT NULL,
  `corp_name` varchar(31) NOT NULL,
  `street` varchar(15) NOT NULL,
  `city` varchar(15) NOT NULL,
  `state_prov` char(2) NOT NULL,
  `country` char(2) NOT NULL,
  `mail_code` char(10) NOT NULL,
  `phone_no` char(13) NOT NULL,
  `expr_dt` datetime NOT NULL,
  `region_no` int(11) NOT NULL,
  `corp_code` char(2) NOT NULL,
  PRIMARY KEY (`corp_no`),
  KEY `corporation_region_no` (`region_no`),
  CONSTRAINT `corporation_ibfk_1` FOREIGN KEY (`region_no`) REFERENCES `region` (`region_no`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `countryregion` (
  `countryregioncode` varchar(3) NOT NULL COMMENT 'ISO standard code for countries and regions.',
  `name` varchar(100) NOT NULL COMMENT 'Country or region name.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`countryregioncode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the ISO standard codes for countries and regions.'
;


CREATE TABLE `countryregioncurrency` (
  `countryregioncode` varchar(3) NOT NULL COMMENT 'ISO code for countries and regions. Foreign key to CountryRegion.CountryRegionCode.',
  `currencycode` char(3) NOT NULL COMMENT 'ISO standard currency code. Foreign key to Currency.CurrencyCode.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`countryregioncode`,`currencycode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping ISO currency codes to a country or region.'
;


CREATE TABLE `course` (
  `course_id` int(11) NOT NULL,
  `rating` varchar(45) DEFAULT NULL,
  `diff` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `course_rating` (`rating`),
  KEY `course_diff` (`diff`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `courses` (
  `id` int(10) unsigned NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `teacher_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `courses_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `craftsmen` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `craftsmen_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `creditcard` (
  `creditcardid` int(11) NOT NULL COMMENT 'Primary key for CreditCard records.',
  `cardtype` varchar(50) NOT NULL COMMENT 'Credit card name.',
  `cardnumber` varchar(25) NOT NULL COMMENT 'Credit card number.',
  `expmonth` tinyint(3) unsigned NOT NULL COMMENT 'Credit card expiration month.',
  `expyear` smallint(6) NOT NULL COMMENT 'Credit card expiration year.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`creditcardid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customer credit card information.'
;


CREATE TABLE `culture` (
  `cultureid` char(6) NOT NULL COMMENT 'Primary key for Culture records.',
  `name` varchar(100) NOT NULL COMMENT 'Culture description.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`cultureid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the languages in which some AdventureWorks data is stored.'
;


CREATE TABLE `currency` (
  `currencycode` char(3) NOT NULL COMMENT 'The ISO code for the Currency.',
  `name` varchar(100) NOT NULL COMMENT 'Currency name.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`currencycode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing standard ISO currencies.'
;


CREATE TABLE `currencyrate` (
  `currencyrateid` int(11) NOT NULL COMMENT 'Primary key for CurrencyRate records.',
  `currencyratedate` datetime NOT NULL COMMENT 'Date and time the exchange rate was obtained.',
  `fromcurrencycode` char(3) NOT NULL COMMENT 'Exchange rate was converted from this currency code.',
  `tocurrencycode` char(3) NOT NULL COMMENT 'Exchange rate was converted to this currency code.',
  `averagerate` decimal(19,4) NOT NULL COMMENT 'Average exchange rate for the day.',
  `endofdayrate` decimal(19,4) NOT NULL COMMENT 'Final exchange rate for the day.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`currencyrateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Currency exchange rates.'
;


CREATE TABLE `customer` (
  `customerid` int(11) NOT NULL COMMENT 'Primary key.',
  `personid` int(11) DEFAULT NULL COMMENT 'Foreign key to Person.BusinessEntityID',
  `storeid` int(11) DEFAULT NULL COMMENT 'Foreign key to Store.BusinessEntityID',
  `territoryid` int(11) DEFAULT NULL COMMENT 'ID of the territory in which the customer is located. Foreign key to SalesTerritory.SalesTerritoryID.',
  `accountnumber` varchar(10) NOT NULL COMMENT 'Unique number identifying the customer assigned by the accounting system.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`customerid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Current customer information. Also see the Person and Store tables.'
;


CREATE TABLE `customers` (
  `customerid` int(11) NOT NULL,
  `segment` varchar(255) DEFAULT NULL,
  `currency` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`customerid`),
  UNIQUE KEY `customer_staged_customerid_key` (`customerid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `data_feature` (
  `did` int(10) unsigned NOT NULL,
  `index` int(10) NOT NULL DEFAULT 0,
  `name` varchar(64) NOT NULL,
  `data_type` varchar(64) DEFAULT NULL,
  `nominal_values` text DEFAULT NULL,
  `is_target` enum('true','false') NOT NULL DEFAULT 'false',
  `is_row_identifier` enum('true','false') NOT NULL DEFAULT 'false',
  `is_ignore` enum('true','false') NOT NULL DEFAULT 'false',
  `NumberOfDistinctValues` int(11) DEFAULT NULL,
  `NumberOfUniqueValues` int(11) DEFAULT NULL,
  `NumberOfMissingValues` int(11) NOT NULL,
  `NumberOfIntegerValues` int(11) DEFAULT NULL,
  `NumberOfRealValues` int(11) DEFAULT NULL,
  `NumberOfNominalValues` varchar(512) NOT NULL,
  `NumberOfValues` int(11) NOT NULL,
  `MaximumValue` int(11) NOT NULL,
  `MinimumValue` int(11) NOT NULL,
  `MeanValue` int(11) NOT NULL,
  `StandardDeviation` int(11) NOT NULL,
  `ClassDistribution` text DEFAULT NULL,
  PRIMARY KEY (`did`,`index`),
  CONSTRAINT `data_feature_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `data_quality` (
  `data` int(10) unsigned NOT NULL DEFAULT 0,
  `quality` varchar(128) NOT NULL DEFAULT '',
  `implementation_id` int(16) NOT NULL,
  `label` varchar(128) NOT NULL,
  `value` varchar(128) DEFAULT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`data`,`quality`,`label`),
  KEY `data_quality_implementation_id` (`implementation_id`),
  KEY `data_quality_quality` (`quality`),
  CONSTRAINT `data_quality_ibfk_1` FOREIGN KEY (`quality`) REFERENCES `quality` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `data_quality_ibfk_2` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `databaselog` (
  `databaselogid` int(11) NOT NULL COMMENT 'Primary key for DatabaseLog records.',
  `posttime` datetime NOT NULL COMMENT 'The date and time the DDL change occurred.',
  `databaseuser` varchar(160) NOT NULL COMMENT 'The user who implemented the DDL change.',
  `event` varchar(160) NOT NULL COMMENT 'The type of DDL statement that was executed.',
  `schema` varchar(160) DEFAULT NULL COMMENT 'The schema to which the changed object belongs.',
  `object` varchar(160) DEFAULT NULL COMMENT 'The object that was changed by the DDL statment.',
  `tsql` longtext NOT NULL COMMENT 'The exact Transact-SQL statement that was executed.',
  `xmlevent` text NOT NULL COMMENT 'The raw XML data generated by database trigger.',
  PRIMARY KEY (`databaselogid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Audit table tracking all DDL changes made to the AdventureWorks database. Data is captured by the database trigger ddlDatabaseTriggerLog.'
;


CREATE TABLE `dataset` (
  `did` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `uploader` int(10) DEFAULT NULL,
  `source` int(10) unsigned DEFAULT NULL,
  `name` varchar(128) NOT NULL,
  `version` varchar(64) NOT NULL,
  `version_label` varchar(128) DEFAULT NULL,
  `description` text NOT NULL,
  `format` varchar(64) NOT NULL DEFAULT 'arff',
  `creator` text DEFAULT NULL,
  `contributor` text DEFAULT NULL,
  `collection_date` varchar(128) DEFAULT NULL,
  `upload_date` datetime NOT NULL,
  `language` varchar(128) DEFAULT NULL,
  `licence` varchar(64) NOT NULL DEFAULT 'Public',
  `citation` text DEFAULT NULL,
  `collection` varchar(64) DEFAULT NULL,
  `url` mediumtext NOT NULL,
  `isOriginal` enum('true','false') DEFAULT NULL,
  `file_id` int(10) DEFAULT NULL,
  `default_target_attribute` varchar(128) DEFAULT NULL,
  `row_id_attribute` varchar(128) DEFAULT NULL,
  `ignore_attribute` varchar(128) DEFAULT NULL,
  `paper_url` mediumtext DEFAULT NULL,
  `visibility` varchar(128) NOT NULL DEFAULT 'public',
  `original_data_id` int(10) DEFAULT NULL,
  `original_data_url` mediumtext DEFAULT NULL,
  `processed` datetime DEFAULT NULL,
  `error` enum('true','false') NOT NULL DEFAULT 'false',
  `error_message` text DEFAULT NULL,
  `status` enum('in_preparation','active','deactivated') NOT NULL DEFAULT 'in_preparation',
  `update_comment` text DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`did`),
  KEY `dataset_name` (`name`),
  KEY `dataset_name_did_version_version_label` (`name`,`did`,`version`,`version_label`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `department` (
  `departmentid` smallint(6) NOT NULL COMMENT 'Primary key for Department records.',
  `name` varchar(100) NOT NULL COMMENT 'Name of the department.',
  `groupname` varchar(100) NOT NULL COMMENT 'Name of the group to which the department belongs.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`departmentid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table containing the departments within the Adventure Works Cycles company.'
;


CREATE TABLE `distinct_users_from_search_table_real_map` (
  `user_id` int(11) NOT NULL,
  `user_screen_name` varchar(255) DEFAULT NULL,
  `indegree` int(11) DEFAULT NULL,
  `outdegree` int(11) DEFAULT NULL,
  `bad_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `dobito` (
  `client_id` int(11) DEFAULT NULL,
  `month_year_datum_transakce` date NOT NULL,
  `sluzba` varchar(255) NOT NULL,
  `kc_dobito` decimal(10,2) NOT NULL,
  KEY `dobito_client_id` (`client_id`),
  CONSTRAINT `dobito_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `document` (
  `documentnode` varchar(255) NOT NULL COMMENT 'Primary key for Document records.',
  `documentlevel` smallint(6) DEFAULT NULL COMMENT 'Depth in the document hierarchy.',
  `title` varchar(50) NOT NULL COMMENT 'Title of the document.',
  `owner` int(11) NOT NULL COMMENT 'Employee who controls the document.  Foreign key to Employee.BusinessEntityID',
  `folderflag` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = This is a folder, 1 = This is a document.',
  `filename` varchar(400) NOT NULL COMMENT 'File name of the document',
  `fileextension` varchar(8) NOT NULL COMMENT 'File extension indicating the document type. For example, .doc or .txt.',
  `revision` char(5) NOT NULL COMMENT 'Revision number of the document. ',
  `changenumber` int(11) NOT NULL DEFAULT 0 COMMENT 'Engineering change approval number.',
  `status` tinyint(3) unsigned NOT NULL COMMENT '1 = Pending approval, 2 = Approved, 3 = Obsolete',
  `documentsummary` longtext DEFAULT NULL COMMENT 'Document abstract.',
  `document` longblob DEFAULT NULL COMMENT 'Complete document.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Required for FileStream.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`documentnode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product maintenance documents.'
;


CREATE TABLE `downloads` (
  `did` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `knowledge_type` varchar(1) NOT NULL,
  `knowledge_id` int(10) NOT NULL,
  `user_id` mediumint(8) NOT NULL,
  `count` smallint(6) NOT NULL DEFAULT 1,
  `time` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`knowledge_type`,`knowledge_id`,`user_id`),
  KEY `downloads_did` (`did`),
  CONSTRAINT `downloads_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `downvotes` (
  `did` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `knowledge_type` varchar(1) NOT NULL,
  `knowledge_id` int(10) NOT NULL,
  `user_id` mediumint(8) NOT NULL,
  `reason` int(11) NOT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp(),
  `original` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`knowledge_type`,`knowledge_id`,`user_id`),
  KEY `downvotes_did` (`did`),
  CONSTRAINT `downvotes_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_customer` (
  `c_custkey` int(11) NOT NULL,
  `c_name` varchar(25) NOT NULL,
  `c_address` varchar(40) NOT NULL,
  `c_nationkey` int(11) NOT NULL,
  `c_phone` char(15) NOT NULL,
  `c_acctbal` double NOT NULL,
  `c_mktsegment` char(10) NOT NULL,
  `c_comment` varchar(117) DEFAULT NULL,
  PRIMARY KEY (`c_custkey`),
  KEY `c_nationkey` (`c_nationkey`),
  CONSTRAINT `dss_customer_ibfk_1` FOREIGN KEY (`c_nationkey`) REFERENCES `dss_nation` (`n_nationkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_lineitem` (
  `l_orderkey` decimal(18,0) NOT NULL,
  `l_partkey` int(11) NOT NULL,
  `l_suppkey` int(11) NOT NULL,
  `l_linenumber` int(11) NOT NULL,
  `l_quantity` double NOT NULL,
  `l_extendedprice` double NOT NULL,
  `l_discount` double NOT NULL,
  `l_tax` double NOT NULL,
  `l_returnflag` char(1) NOT NULL,
  `l_linestatus` char(1) NOT NULL,
  `l_shipdate` date DEFAULT NULL,
  `l_commitdate` date DEFAULT NULL,
  `l_receiptdate` date DEFAULT NULL,
  `l_shipinstruct` char(25) NOT NULL,
  `l_shipmode` char(10) NOT NULL,
  `l_comment` varchar(44) DEFAULT NULL,
  PRIMARY KEY (`l_orderkey`,`l_linenumber`),
  KEY `lineitem_idx1` (`l_orderkey`,`l_returnflag`,`l_extendedprice`,`l_discount`),
  KEY `lineitem_idx2` (`l_partkey`,`l_quantity`,`l_extendedprice`,`l_suppkey`,`l_orderkey`,`l_discount`),
  KEY `l_suppkey` (`l_suppkey`),
  KEY `l_partkey` (`l_partkey`,`l_suppkey`),
  CONSTRAINT `dss_lineitem_ibfk_1` FOREIGN KEY (`l_orderkey`) REFERENCES `dss_order` (`o_orderkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_nation` (
  `n_nationkey` int(11) NOT NULL,
  `n_name` char(25) NOT NULL,
  `n_regionkey` int(11) NOT NULL,
  `n_comment` varchar(152) DEFAULT NULL,
  PRIMARY KEY (`n_nationkey`),
  KEY `n_regionkey` (`n_regionkey`),
  CONSTRAINT `dss_nation_ibfk_1` FOREIGN KEY (`n_regionkey`) REFERENCES `dss_region` (`r_regionkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_order` (
  `o_orderkey` decimal(18,0) NOT NULL,
  `o_custkey` int(11) NOT NULL,
  `o_orderstatus` char(1) NOT NULL,
  `o_totalprice` double NOT NULL,
  `o_orderdate` date DEFAULT NULL,
  `o_orderpriority` char(15) NOT NULL,
  `o_clerk` char(15) NOT NULL,
  `o_shippriority` int(11) NOT NULL,
  `o_comment` varchar(79) DEFAULT NULL,
  PRIMARY KEY (`o_orderkey`),
  KEY `orders_idx1` (`o_orderkey`),
  KEY `orders_idx2` (`o_clerk`,`o_orderkey`,`o_orderdate`),
  KEY `o_custkey` (`o_custkey`),
  CONSTRAINT `dss_order_ibfk_1` FOREIGN KEY (`o_custkey`) REFERENCES `dss_customer` (`c_custkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_part` (
  `p_partkey` int(11) NOT NULL,
  `p_name` varchar(55) NOT NULL,
  `p_mfgr` char(25) NOT NULL,
  `p_brand` char(10) NOT NULL,
  `p_type` varchar(25) NOT NULL,
  `p_size` int(11) NOT NULL,
  `p_container` char(10) NOT NULL,
  `p_retailprice` double NOT NULL,
  `p_comment` varchar(23) NOT NULL,
  PRIMARY KEY (`p_partkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_partsupp` (
  `ps_partkey` int(11) NOT NULL,
  `ps_suppkey` int(11) NOT NULL,
  `ps_availqty` int(11) NOT NULL,
  `ps_supplycost` double NOT NULL,
  `ps_comment` varchar(199) DEFAULT NULL,
  PRIMARY KEY (`ps_partkey`,`ps_suppkey`),
  KEY `partsupp_idx1` (`ps_partkey`),
  KEY `partsupp_idx2` (`ps_suppkey`,`ps_partkey`),
  KEY `ps_partkey` (`ps_partkey`,`ps_suppkey`),
  CONSTRAINT `dss_partsupp_ibfk_1` FOREIGN KEY (`ps_suppkey`) REFERENCES `dss_supplier` (`s_suppkey`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `dss_partsupp_ibfk_2` FOREIGN KEY (`ps_partkey`) REFERENCES `dss_part` (`p_partkey`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `dss_partsupp_ibfk_3` FOREIGN KEY (`ps_partkey`, `ps_suppkey`) REFERENCES `dss_lineitem` (`l_partkey`, `l_suppkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_region` (
  `r_regionkey` int(11) NOT NULL,
  `r_name` char(25) NOT NULL,
  `r_comment` varchar(152) DEFAULT NULL,
  PRIMARY KEY (`r_regionkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_supplier` (
  `s_suppkey` int(11) NOT NULL,
  `s_name` char(25) NOT NULL,
  `s_address` varchar(40) NOT NULL,
  `s_nationkey` int(11) NOT NULL,
  `s_phone` char(15) NOT NULL,
  `s_acctbal` double NOT NULL,
  `s_comment` varchar(101) NOT NULL,
  PRIMARY KEY (`s_suppkey`),
  UNIQUE KEY `supplier_idx1` (`s_suppkey`),
  KEY `s_nationkey` (`s_nationkey`),
  CONSTRAINT `dss_supplier_ibfk_1` FOREIGN KEY (`s_nationkey`) REFERENCES `dss_nation` (`n_nationkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `emailaddress` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key. Person associated with this email address.  Foreign key to Person.BusinessEntityID',
  `emailaddressid` int(11) NOT NULL COMMENT 'Primary key. ID of this email address.',
  `emailaddress` varchar(50) DEFAULT NULL COMMENT 'E-mail address for the person.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`emailaddressid`,`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Where to send a person email.'
;


CREATE TABLE `employee` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key for Employee records.  Foreign key to BusinessEntity.BusinessEntityID.',
  `nationalidnumber` varchar(15) NOT NULL COMMENT 'Unique national identification number such as a social security number.',
  `loginid` varchar(256) NOT NULL COMMENT 'Network login.',
  `organizationnode` varchar(255) DEFAULT NULL COMMENT 'Where the employee is located in corporate hierarchy.',
  `organizationlevel` smallint(6) DEFAULT NULL COMMENT 'The depth of the employee in the corporate hierarchy.',
  `jobtitle` varchar(50) NOT NULL COMMENT 'Work title such as Buyer or Sales Representative.',
  `birthdate` date NOT NULL COMMENT 'Date of birth.',
  `maritalstatus` char(1) NOT NULL COMMENT 'M = Married, S = Single',
  `gender` char(1) NOT NULL COMMENT 'M = Male, F = Female',
  `hiredate` date NOT NULL COMMENT 'Employee hired on this date.',
  `salariedflag` tinyint(1) NOT NULL DEFAULT 1 COMMENT 'Job classification. 0 = Hourly, not exempt from collective bargaining. 1 = Salaried, exempt from collective bargaining.',
  `vacationhours` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Number of available vacation hours.',
  `sickleavehours` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Number of available sick leave hours.',
  `currentflag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Inactive, 1 = Active',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee information such as salary, department, and title.'
;


CREATE TABLE `employeedepartmenthistory` (
  `businessentityid` int(11) NOT NULL COMMENT 'Employee identification number. Foreign key to Employee.BusinessEntityID.',
  `departmentid` smallint(6) NOT NULL COMMENT 'Department in which the employee worked including currently. Foreign key to Department.DepartmentID.',
  `shiftid` tinyint(3) unsigned NOT NULL COMMENT 'Identifies which 8-hour shift the employee works. Foreign key to Shift.Shift.ID.',
  `startdate` date NOT NULL COMMENT 'Date the employee started work in the department.',
  `enddate` date DEFAULT NULL COMMENT 'Date the employee left the department. NULL = Current department.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`startdate`,`departmentid`,`shiftid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee department transfers.'
;


CREATE TABLE `employeepayhistory` (
  `businessentityid` int(11) NOT NULL COMMENT 'Employee identification number. Foreign key to Employee.BusinessEntityID.',
  `ratechangedate` datetime NOT NULL COMMENT 'Date the change in pay is effective',
  `rate` decimal(19,4) NOT NULL COMMENT 'Salary hourly rate.',
  `payfrequency` tinyint(3) unsigned NOT NULL COMMENT '1 = Salary received monthly, 2 = Salary received biweekly',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`ratechangedate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Employee pay history.'
;


CREATE TABLE `enabled_roles` (
  `role_name` varchar(128) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=5549053 ROW_FORMAT=FIXED
;


CREATE TABLE `engines` (
  `engine` varchar(64) NOT NULL DEFAULT '',
  `support` varchar(8) NOT NULL DEFAULT '',
  `comment` varchar(160) NOT NULL DEFAULT '',
  `transactions` varchar(3) DEFAULT NULL,
  `xa` varchar(3) DEFAULT NULL,
  `savepoints` varchar(3) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci MAX_ROWS=2937734 ROW_FORMAT=FIXED
;


CREATE TABLE `errorlog` (
  `errorlogid` int(11) NOT NULL COMMENT 'Primary key for ErrorLog records.',
  `errortime` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'The date and time at which the error occurred.',
  `username` varchar(160) NOT NULL COMMENT 'The user who executed the batch in which the error occurred.',
  `errornumber` int(11) NOT NULL COMMENT 'The error number of the error that occurred.',
  `errorseverity` int(11) DEFAULT NULL COMMENT 'The severity of the error that occurred.',
  `errorstate` int(11) DEFAULT NULL COMMENT 'The state number of the error that occurred.',
  `errorprocedure` varchar(126) DEFAULT NULL COMMENT 'The name of the stored procedure or trigger where the error occurred.',
  `errorline` int(11) DEFAULT NULL COMMENT 'The line number at which the error occurred.',
  `errormessage` varchar(4000) NOT NULL COMMENT 'The message text of the error that occurred.',
  PRIMARY KEY (`errorlogid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Audit table tracking errors in the the AdventureWorks database that are caught by the CATCH block of a TRY...CATCH construct. Data is inserted by stored procedure dbo.uspLogError when it is executed from inside the CATCH block of a TRY...CATCH construct.'
;


CREATE TABLE `estimateFK_v4` (
  `schema` varchar(255) DEFAULT NULL,
  `pk_table` varchar(255) DEFAULT NULL,
  `pk_column` varchar(255) DEFAULT NULL,
  `pk_dataTypeName` varchar(255) DEFAULT NULL,
  `pk_isUnique` varchar(255) DEFAULT NULL,
  `pk_isUniqueConstraint` varchar(255) DEFAULT NULL,
  `pk_columnSize` int(11) DEFAULT NULL,
  `pk_decimalDigits` int(11) DEFAULT NULL,
  `pk_hasDefault` varchar(255) DEFAULT NULL,
  `pk_ordinalPosition` int(11) DEFAULT NULL,
  `pk_ordinalPositionEnd` int(11) DEFAULT NULL,
  `pk_tableColumnCount` int(11) DEFAULT NULL,
  `pk_isAutoincrement` varchar(255) DEFAULT NULL,
  `pk_isGeneratedColumn` varchar(255) DEFAULT NULL,
  `pk_isNullable` varchar(255) DEFAULT NULL,
  `pk_levenshteinDistance` int(11) DEFAULT NULL,
  `pk_repetitions` int(11) DEFAULT NULL,
  `pk_prefixSchemaCount` int(11) DEFAULT NULL,
  `pk_suffixSchemaCount` int(11) DEFAULT NULL,
  `pk_prefixTableCount` int(11) DEFAULT NULL,
  `pk_suffixTableCount` int(11) DEFAULT NULL,
  `pk_prefixRatio` int(11) DEFAULT NULL,
  `pk_suffixRatio` float DEFAULT NULL,
  `pk_hasNumberedSibling` varchar(255) DEFAULT NULL,
  `pk_containsAux` varchar(255) DEFAULT NULL,
  `pk_containsCode` varchar(255) DEFAULT NULL,
  `pk_containsId` varchar(255) DEFAULT NULL,
  `pk_containsKey` varchar(255) DEFAULT NULL,
  `pk_containsName` varchar(255) DEFAULT NULL,
  `pk_containsNbr` varchar(255) DEFAULT NULL,
  `pk_containsNo` varchar(255) DEFAULT NULL,
  `pk_containsNum` varchar(255) DEFAULT NULL,
  `pk_containsNumber` varchar(255) DEFAULT NULL,
  `pk_containsPk` varchar(255) DEFAULT NULL,
  `pk_containsSk` varchar(255) DEFAULT NULL,
  `pk_containsSymb` varchar(255) DEFAULT NULL,
  `pk_containsType` varchar(255) DEFAULT NULL,
  `pk_contains` varchar(255) DEFAULT NULL,
  `pk_isPrimaryKey` varchar(255) DEFAULT NULL,
  `fk_table` varchar(255) DEFAULT NULL,
  `fk_column` varchar(255) DEFAULT NULL,
  `fk_dataTypeName` varchar(255) DEFAULT NULL,
  `fk_isUnique` varchar(255) DEFAULT NULL,
  `fk_isUniqueConstraint` varchar(255) DEFAULT NULL,
  `fk_columnSize` int(11) DEFAULT NULL,
  `fk_decimalDigits` int(11) DEFAULT NULL,
  `fk_hasDefault` varchar(255) DEFAULT NULL,
  `fk_ordinalPosition` int(11) DEFAULT NULL,
  `fk_ordinalPositionEnd` int(11) DEFAULT NULL,
  `fk_tableColumnCount` int(11) DEFAULT NULL,
  `fk_isAutoincrement` varchar(255) DEFAULT NULL,
  `fk_isGeneratedColumn` varchar(255) DEFAULT NULL,
  `fk_isNullable` varchar(255) DEFAULT NULL,
  `fk_levenshteinDistance` int(11) DEFAULT NULL,
  `fk_repetitions` int(11) DEFAULT NULL,
  `fk_prefixSchemaCount` int(11) DEFAULT NULL,
  `fk_suffixSchemaCount` int(11) DEFAULT NULL,
  `fk_prefixTableCount` int(11) DEFAULT NULL,
  `fk_suffixTableCount` int(11) DEFAULT NULL,
  `fk_prefixRatio` float DEFAULT NULL,
  `fk_suffixRatio` float DEFAULT NULL,
  `fk_hasNumberedSibling` varchar(255) DEFAULT NULL,
  `fk_containsAux` varchar(255) DEFAULT NULL,
  `fk_containsCode` varchar(255) DEFAULT NULL,
  `fk_containsId` varchar(255) DEFAULT NULL,
  `fk_containsKey` varchar(255) DEFAULT NULL,
  `fk_containsName` varchar(255) DEFAULT NULL,
  `fk_containsNbr` varchar(255) DEFAULT NULL,
  `fk_containsNo` varchar(255) DEFAULT NULL,
  `fk_containsNum` varchar(255) DEFAULT NULL,
  `fk_containsNumber` varchar(255) DEFAULT NULL,
  `fk_containsPk` varchar(255) DEFAULT NULL,
  `fk_containsSk` varchar(255) DEFAULT NULL,
  `fk_containsSymb` varchar(255) DEFAULT NULL,
  `fk_containsType` varchar(255) DEFAULT NULL,
  `fk_contains` varchar(255) DEFAULT NULL,
  `fk_isPrimaryKey` varchar(255) DEFAULT NULL,
  `dataTypeAgree` varchar(255) DEFAULT NULL,
  `dataTypeCategoryAgree` varchar(255) DEFAULT NULL,
  `dataLengthAgree` varchar(255) DEFAULT NULL,
  `decimalAgree` varchar(255) DEFAULT NULL,
  `levenshteinColumns` int(11) DEFAULT NULL,
  `containsFk` varchar(255) DEFAULT NULL,
  `containsType` varchar(255) DEFAULT NULL,
  `containsEid` varchar(255) DEFAULT NULL,
  `contains` varchar(255) DEFAULT NULL,
  `isForeignKey` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `estimation_procedure` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `ttid` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `type` varchar(64) NOT NULL,
  `repeats` int(8) DEFAULT NULL,
  `folds` int(8) DEFAULT NULL,
  `percentage` int(8) DEFAULT NULL,
  `stratified_sampling` enum('true','false') DEFAULT NULL,
  `custom_testset` enum('true','false') NOT NULL DEFAULT 'false',
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `estimation_procedure_ttid` (`ttid`),
  KEY `estimation_procedure__type` (`type`),
  CONSTRAINT `estimation_procedure_ibfk_1` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `estimation_procedure_ibfk_2` FOREIGN KEY (`type`) REFERENCES `estimation_procedure_type` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `estimation_procedure_type` (
  `name` varchar(64) NOT NULL,
  `description` mediumtext NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `evaluation` (
  `did` int(10) unsigned NOT NULL DEFAULT 0,
  `source` int(10) unsigned NOT NULL,
  `implementation_id` int(16) NOT NULL,
  `function` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `label` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `value` double NOT NULL,
  `stdev` double DEFAULT NULL,
  UNIQUE KEY `did` (`did`,`function`,`label`),
  KEY `function` (`function`,`source`,`label`(32)),
  KEY `func` (`function`),
  KEY `implementation_id` (`implementation_id`),
  CONSTRAINT `evaluation_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`),
  CONSTRAINT `evaluation_ibfk_2` FOREIGN KEY (`function`) REFERENCES `math_function` (`name`),
  CONSTRAINT `evaluation_ibfk_3` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
;


CREATE TABLE `event_type` (
  `id` int(11) NOT NULL,
  `event_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`,`event_type`),
  CONSTRAINT `event_type_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `events` (
  `event_id` int(11) NOT NULL,
  `device_id` bigint(20) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `longitude` decimal(10,0) DEFAULT NULL,
  `latitude` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `events_relevant` (
  `event_id` int(11) NOT NULL,
  `device_id` bigint(20) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `longitude` decimal(10,0) DEFAULT NULL,
  `latitude` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `device_id` (`device_id`),
  CONSTRAINT `events_relevant_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `gender_age` (`device_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `fault` (
  `tm` int(11) NOT NULL,
  `tf` varchar(1) NOT NULL,
  PRIMARY KEY (`tm`,`tf`),
  KEY `tm` (`tm`),
  KEY `tf` (`tf`),
  CONSTRAINT `fault_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fault_ibfk_2` FOREIGN KEY (`tf`) REFERENCES `trfl` (`tf`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `fault_test` (
  `tm` int(11) NOT NULL,
  `tf` varchar(1) NOT NULL,
  PRIMARY KEY (`tm`,`tf`),
  KEY `tf` (`tf`),
  KEY `tm` (`tm`),
  CONSTRAINT `fault_test_ibfk_1` FOREIGN KEY (`tf`) REFERENCES `trfl` (`tf`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fault_test_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `fault_test_Neg` (
  `tm` int(11) NOT NULL,
  `tf` varchar(1) NOT NULL,
  PRIMARY KEY (`tm`,`tf`),
  KEY `tm` (`tm`),
  KEY `tf` (`tf`),
  CONSTRAINT `fault_test_Neg_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fault_test_Neg_ibfk_2` FOREIGN KEY (`tf`) REFERENCES `trfl` (`tf`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `features` (
  `Store` int(11) NOT NULL,
  `Date` date NOT NULL,
  `Temperature` float DEFAULT NULL,
  `Fuel_Price` float DEFAULT NULL,
  `MarkDown1` float DEFAULT NULL,
  `MarkDown2` float DEFAULT NULL,
  `MarkDown3` float DEFAULT NULL,
  `MarkDown4` float DEFAULT NULL,
  `MarkDown5` float DEFAULT NULL,
  `CPI` float DEFAULT NULL,
  `Unemployment` float DEFAULT NULL,
  `IsHoliday` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Store`,`Date`),
  KEY `Store` (`Store`),
  CONSTRAINT `features_ibfk_1` FOREIGN KEY (`Store`) REFERENCES `stores` (`Store`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gasstations` (
  `gasstationid` int(11) NOT NULL,
  `chainid` int(11) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `segment` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`gasstationid`),
  UNIQUE KEY `gasstations_gasstationid_key` (`gasstationid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gender_age` (
  `device_id` bigint(20) NOT NULL,
  `gender` varchar(255) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `group` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`device_id`),
  CONSTRAINT `gender_age_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `phone_brand_device_model2` (`device_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gender_age_test` (
  `device_id` bigint(20) NOT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gender_age_train` (
  `device_id` bigint(20) NOT NULL,
  `gender` varchar(255) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `group` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gmt_mission_phase` (
  `state` varchar(50) NOT NULL,
  `tm` int(11) NOT NULL,
  PRIMARY KEY (`state`,`tm`),
  KEY `tm` (`tm`),
  CONSTRAINT `gmt_mission_phase_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `grades` (
  `student_id` int(10) unsigned NOT NULL,
  `course_id` int(10) unsigned NOT NULL,
  `grade` varchar(2) DEFAULT NULL,
  PRIMARY KEY (`student_id`,`course_id`),
  KEY `student_id` (`student_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `grades_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `students` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `grades_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `courses` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `illustration` (
  `illustrationid` int(11) NOT NULL COMMENT 'Primary key for Illustration records.',
  `diagram` text DEFAULT NULL COMMENT 'Illustrations used in manufacturing instructions. Stored as XML.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`illustrationid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Bicycle assembly diagrams.'
;


CREATE TABLE `implementation` (
  `id` int(16) NOT NULL AUTO_INCREMENT,
  `fullName` varchar(1024) NOT NULL,
  `uploader` int(10) DEFAULT NULL,
  `name` varchar(1024) NOT NULL,
  `version` int(16) NOT NULL,
  `external_version` varchar(128) NOT NULL,
  `creator` varchar(128) DEFAULT NULL,
  `contributor` text DEFAULT NULL,
  `uploadDate` datetime NOT NULL,
  `licence` varchar(64) DEFAULT NULL,
  `language` varchar(128) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `fullDescription` text DEFAULT NULL,
  `installationNotes` text DEFAULT NULL,
  `dependencies` text DEFAULT NULL,
  `implements` varchar(128) DEFAULT NULL,
  `binary_file_id` int(10) DEFAULT NULL,
  `source_file_id` int(10) DEFAULT NULL,
  `visibility` varchar(128) NOT NULL DEFAULT 'public',
  `citation` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `implementation_uploader` (`uploader`),
  KEY `implementation_id_external_version` (`id`,`external_version`),
  KEY `implementation_name` (`name`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=DYNAMIC
;


CREATE TABLE `implementation_component` (
  `parent` int(16) NOT NULL,
  `child` int(16) NOT NULL,
  `identifier` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`parent`,`child`),
  KEY `implementation_component_child` (`child`),
  CONSTRAINT `implementation_component_ibfk_1` FOREIGN KEY (`parent`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `implementation_component_ibfk_2` FOREIGN KEY (`child`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `impotenten` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `impotenten_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `input` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `fullName` varchar(128) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `implementation_id` int(16) NOT NULL,
  `name` varchar(128) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `dataType` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `defaultValue` varchar(256) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `recommendedRange` varchar(256) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `input_implementation_id` (`implementation_id`),
  CONSTRAINT `input_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `invoices` (
  `number` int(11) DEFAULT NULL,
  `number_sup` char(1) DEFAULT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `invoice` int(11) DEFAULT NULL,
  `chamber` char(1) DEFAULT NULL,
  KEY `invoices_number_fkey` (`number`,`number_sup`),
  CONSTRAINT `invoices_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `j_Carcinogenesis` (
  `predictor_id` int(11) NOT NULL DEFAULT 0,
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(2024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT 0,
  `qc_nullCount` int(11) DEFAULT 0,
  `is_ok` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `j_SAP` (
  `predictor_id` int(11) NOT NULL DEFAULT 0,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(2024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `j_Toxicology` (
  `predictor_id` int(11) NOT NULL DEFAULT 0,
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(2024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT 0,
  `qc_nullCount` int(11) DEFAULT 0,
  `is_ok` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `j_financial` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `j_mutagenesis` (
  `predictor_id` int(11) NOT NULL DEFAULT 0,
  `start_time` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(1024) DEFAULT NULL,
  `sql_code` varchar(1024) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT 0,
  `qc_nullCount` int(11) DEFAULT 0,
  `is_ok` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `j_tpcc` (
  `predictor_id` int(11) NOT NULL DEFAULT 0,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(2024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `j_voc` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `jobcandidate` (
  `jobcandidateid` int(11) NOT NULL COMMENT 'Primary key for JobCandidate records.',
  `businessentityid` int(11) DEFAULT NULL COMMENT 'Employee identification number if applicant was hired. Foreign key to Employee.BusinessEntityID.',
  `resume` text DEFAULT NULL COMMENT 'Résumé in XML format.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`jobcandidateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Résumés submitted to Human Resources by job applicants.'
;


CREATE TABLE `journal` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`predictor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_financial_exhaustive` (
  `predictor_id` int(11) NOT NULL DEFAULT 0,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(2024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  PRIMARY KEY (`predictor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_pattern2` (
  `name` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `is_aggregate` int(11) DEFAULT NULL,
  `is_multivariate` int(11) DEFAULT NULL,
  `is_nominal` int(11) DEFAULT NULL,
  `is_numerical` int(11) DEFAULT NULL,
  `is_temporal` int(11) DEFAULT NULL,
  `uses_base_target` int(11) DEFAULT NULL,
  `uses_base_date` int(11) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_pattern3` (
  `name` varchar(255) NOT NULL,
  `author` varchar(255) DEFAULT NULL,
  `is_aggregate` int(11) DEFAULT NULL,
  `is_multivariate` int(11) DEFAULT NULL,
  `is_nominal` int(11) DEFAULT NULL,
  `is_numerical` int(11) DEFAULT NULL,
  `is_temporal` int(11) DEFAULT NULL,
  `uses_base_target` int(11) DEFAULT NULL,
  `uses_base_date` int(11) DEFAULT NULL,
  `description` varchar(4000) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_predictor` (
  `predictor_id` int(11) NOT NULL,
  `group_id` int(11) DEFAULT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `predictor_name` varchar(255) DEFAULT NULL,
  `predictor_long_name` varchar(512) DEFAULT NULL,
  `table_name` varchar(1024) DEFAULT NULL,
  `column_list` varchar(1024) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `date_constrain` varchar(255) DEFAULT NULL,
  `parameter_list` varchar(1024) DEFAULT NULL,
  `pattern_name` varchar(255) DEFAULT NULL,
  `pattern_author` varchar(255) DEFAULT NULL,
  `pattern_code` varchar(3600) DEFAULT NULL,
  `sql_code` varchar(3600) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL,
  `relevance` decimal(18,3) DEFAULT NULL,
  `concept_drift` decimal(7,6) DEFAULT NULL,
  `qc_rowCount` int(11) DEFAULT NULL,
  `qc_nullCount` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  `is_duplicate` int(11) DEFAULT NULL,
  `duplicate_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`predictor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_run` (
  `finish_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `schema_name` varchar(255) DEFAULT NULL,
  `run_time` decimal(18,3) DEFAULT NULL,
  `memory` decimal(18,3) DEFAULT NULL,
  `warn_count` int(11) DEFAULT NULL,
  `error_count` int(11) DEFAULT NULL,
  `predictor_count` int(11) DEFAULT NULL,
  `predictor_output_count` int(11) DEFAULT NULL,
  `propagated_table_count` int(11) DEFAULT NULL,
  `setting` varchar(2024) DEFAULT NULL,
  `accuracy_avg` decimal(8,3) DEFAULT NULL,
  `accuracy_std` decimal(8,3) DEFAULT NULL,
  `auc_avg` decimal(8,3) DEFAULT NULL,
  `auc_std` decimal(8,3) DEFAULT NULL,
  `fscore_avg` decimal(8,3) DEFAULT NULL,
  `fscore_std` decimal(8,3) DEFAULT NULL,
  `precision_avg` decimal(8,3) DEFAULT NULL,
  `precision_std` decimal(8,3) DEFAULT NULL,
  `recall_avg` decimal(8,3) DEFAULT NULL,
  `recall_std` decimal(8,3) DEFAULT NULL,
  `auc_optimistic_avg` decimal(8,3) DEFAULT NULL,
  `auc_optimistic_std` decimal(8,3) DEFAULT NULL,
  `auc_average_avg` decimal(8,3) DEFAULT NULL,
  `auc_average_std` decimal(8,3) DEFAULT NULL,
  `auc_pessimistic_avg` decimal(8,3) DEFAULT NULL,
  `auc_pessimistic_std` decimal(8,3) DEFAULT NULL,
  `correlation_avg` decimal(8,3) DEFAULT NULL,
  `correlation_std` decimal(8,3) DEFAULT NULL,
  `rmse_avg` decimal(8,3) DEFAULT NULL,
  `rmse_std` decimal(8,3) DEFAULT NULL,
  `relative_error_avg` decimal(8,3) DEFAULT NULL,
  `relative_error_std` decimal(8,3) DEFAULT NULL,
  PRIMARY KEY (`finish_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_run2` (
  `finish_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `schema_name` varchar(255) DEFAULT NULL,
  `relative_error_std` decimal(8,3) DEFAULT NULL,
  PRIMARY KEY (`finish_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_run3` (
  `finish_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `schema_name` varchar(255) DEFAULT NULL,
  `run_time` decimal(18,3) DEFAULT NULL,
  `memory` decimal(18,3) DEFAULT NULL,
  `warn_count` int(11) DEFAULT NULL,
  `error_count` int(11) DEFAULT NULL,
  `predictor_count` int(11) DEFAULT NULL,
  `predictor_output_count` int(11) DEFAULT NULL,
  `propagated_table_count` int(11) DEFAULT NULL,
  `recall` decimal(8,3) DEFAULT NULL,
  `recall_std` decimal(8,3) DEFAULT NULL,
  `auc_optimistic` decimal(8,3) DEFAULT NULL,
  `auc_optimistic_std` decimal(8,3) DEFAULT NULL,
  `auc_average` decimal(8,3) DEFAULT NULL,
  `auc_average_std` decimal(8,3) DEFAULT NULL,
  `auc_pessimistic` decimal(8,3) DEFAULT NULL,
  `auc_pessimistic_std` decimal(8,3) DEFAULT NULL,
  `correlation` decimal(8,3) DEFAULT NULL,
  `correlation_std` decimal(8,3) DEFAULT NULL,
  `rmse` decimal(8,3) DEFAULT NULL,
  `rmse_std` decimal(8,3) DEFAULT NULL,
  `relative_error` decimal(8,3) DEFAULT NULL,
  `relative_error_std` decimal(8,3) DEFAULT NULL,
  PRIMARY KEY (`finish_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_run4` (
  `finish_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `schema_name` varchar(255) DEFAULT NULL,
  `run_time` decimal(18,3) DEFAULT NULL,
  `memory` decimal(18,3) DEFAULT NULL,
  `warn_count` int(11) DEFAULT NULL,
  `error_count` int(11) DEFAULT NULL,
  `predictor_count` int(11) DEFAULT NULL,
  `predictor_output_count` int(11) DEFAULT NULL,
  `propagated_table_count` int(11) DEFAULT NULL,
  `setting` varchar(2024) DEFAULT NULL,
  `accuracy` decimal(8,3) DEFAULT NULL,
  `accuracy_std` decimal(8,3) DEFAULT NULL,
  `auc` decimal(8,3) DEFAULT NULL,
  `auc_std` decimal(8,3) DEFAULT NULL,
  `fscore` decimal(8,3) DEFAULT NULL,
  `fscore_std` decimal(8,3) DEFAULT NULL,
  `precision_std` decimal(8,3) DEFAULT NULL,
  `recall` decimal(8,3) DEFAULT NULL,
  `recall_std` decimal(8,3) DEFAULT NULL,
  `auc_optimistic` decimal(8,3) DEFAULT NULL,
  `auc_optimistic_std` decimal(8,3) DEFAULT NULL,
  `auc_average` decimal(8,3) DEFAULT NULL,
  `auc_average_std` decimal(8,3) DEFAULT NULL,
  `auc_pessimistic` decimal(8,3) DEFAULT NULL,
  `auc_pessimistic_std` decimal(8,3) DEFAULT NULL,
  `correlation` decimal(8,3) DEFAULT NULL,
  `correlation_std` decimal(8,3) DEFAULT NULL,
  `rmse` decimal(8,3) DEFAULT NULL,
  `rmse_std` decimal(8,3) DEFAULT NULL,
  `relative_error` decimal(8,3) DEFAULT NULL,
  `relative_error_std` decimal(8,3) DEFAULT NULL,
  PRIMARY KEY (`finish_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `journal_table` (
  `table_id` int(11) NOT NULL,
  `start_time` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `run_time` decimal(18,3) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `original_name` varchar(255) DEFAULT NULL,
  `temporal_constraint` varchar(255) DEFAULT NULL,
  `temporal_constraint_reasoning` varchar(1024) DEFAULT NULL,
  `candidate_temporal_list` varchar(2024) DEFAULT NULL,
  `candidate_temporal_count` int(11) DEFAULT NULL,
  `row_count_optimistic` int(11) DEFAULT NULL,
  `propagation_path` varchar(1024) DEFAULT NULL,
  `propagation_depth` int(11) DEFAULT NULL,
  `propagation_id` varchar(1024) DEFAULT NULL,
  `sql_code` varchar(2024) DEFAULT NULL,
  `is_id_unique` int(11) DEFAULT NULL,
  `is_target_id_unique` int(11) DEFAULT NULL,
  `qc_successfully_executed` int(11) DEFAULT NULL,
  `qc_row_count` int(11) DEFAULT NULL,
  `is_ok` int(11) DEFAULT NULL,
  PRIMARY KEY (`table_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `key` (
  `store_nbr` int(11) NOT NULL,
  `station_nbr` int(11) DEFAULT NULL,
  PRIMARY KEY (`store_nbr`),
  UNIQUE KEY `key_store_nbr_key` (`store_nbr`),
  KEY `key_station_nbr_fkey` (`station_nbr`),
  CONSTRAINT `key_station_nbr_fkey` FOREIGN KEY (`station_nbr`) REFERENCES `station` (`station_nbr`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `label_categories` (
  `label_id` int(11) NOT NULL,
  `category` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`label_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `location` (
  `locationid` smallint(6) NOT NULL COMMENT 'Primary key for Location records.',
  `name` varchar(100) NOT NULL COMMENT 'Location description.',
  `costrate` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Standard hourly cost of the manufacturing location.',
  `availability` decimal(8,2) NOT NULL DEFAULT 0.00 COMMENT 'Work capacity (in hours) of the manufacturing location.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`locationid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product inventory and manufacturing locations.'
;


CREATE TABLE `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `schema_name` varchar(255) NOT NULL,
  `runtime` int(11) DEFAULT NULL,
  `accuracy` float DEFAULT NULL,
  `timestamp` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `predictor_count` int(11) DEFAULT NULL,
  `propagated_table_count` int(11) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `log_copy` (
  `id` int(11) NOT NULL,
  `schema_name` varchar(255) NOT NULL,
  `runtime` int(11) DEFAULT NULL,
  `accuracy` decimal(8,5) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `predictor_count` int(11) DEFAULT NULL,
  `propagated_table_count` int(11) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `accuracy_std` decimal(8,5) DEFAULT NULL,
  `auc` decimal(8,5) DEFAULT NULL,
  `auc_std` decimal(8,5) DEFAULT NULL,
  `fscore` decimal(8,5) DEFAULT NULL,
  `fscore_std` decimal(8,5) DEFAULT NULL,
  `precision` decimal(8,5) DEFAULT NULL,
  `precision_std` decimal(8,5) DEFAULT NULL,
  `recall` decimal(8,5) DEFAULT NULL,
  `recall_std` decimal(8,5) DEFAULT NULL,
  `correlation` decimal(8,5) DEFAULT NULL,
  `correlation_std` decimal(8,5) DEFAULT NULL,
  `auc_optimistic` decimal(8,5) DEFAULT NULL,
  `auc_optimistic_std` decimal(8,5) DEFAULT NULL,
  `auc_pessimistic` decimal(8,5) DEFAULT NULL,
  `auc_pessimistic_std` decimal(8,5) DEFAULT NULL,
  `auc_average` decimal(8,5) DEFAULT NULL,
  `auc_average_std` decimal(8,5) DEFAULT NULL,
  `rmse` decimal(20,5) DEFAULT NULL,
  `rmse_std` decimal(20,5) DEFAULT NULL,
  `relative_error` decimal(20,5) DEFAULT NULL,
  `relative_error_std` decimal(20,5) DEFAULT NULL,
  `setting` text DEFAULT NULL,
  `memory` decimal(8,3) DEFAULT NULL,
  `warn_count` int(11) DEFAULT NULL,
  `error_count` int(11) DEFAULT NULL,
  `runtime_s` decimal(8,3) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `log_feature` (
  `id` int(11) NOT NULL,
  `log_feature` varchar(255) NOT NULL,
  `volume` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`,`log_feature`),
  CONSTRAINT `log_feature_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mailings3` (
  `REFID` int(11) NOT NULL,
  `REF_DATE` datetime DEFAULT NULL,
  `RESPONSE` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`REFID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mainsample` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directfield_nominalcolumn_100030` varchar(1) DEFAULT NULL,
  `loan_duration_directfield_numericalcolumn_100045` int(11) DEFAULT NULL,
  `trans_balance_aggregate_min_100015` int(11) DEFAULT NULL,
  `trans_amount_aggregate_min_100014` int(11) DEFAULT NULL,
  `district_a9_directfield_numericalcolumn_100043` int(11) DEFAULT NULL,
  `district_a12_directfield_numericalcolumn_100033` decimal(4,1) DEFAULT NULL,
  `account_frequency_directfield_nominalcolumn_100026` varchar(18) DEFAULT '',
  `district_a14_directfield_numericalcolumn_100035` int(11) DEFAULT NULL,
  `district_a11_directfield_numericalcolumn_100032` int(11) DEFAULT NULL,
  `district_a10_directfield_numericalcolumn_100031` decimal(4,1) DEFAULT NULL,
  `trans_account_aggregate_min_100013` int(11) DEFAULT NULL,
  `district_a16_directfield_numericalcolumn_100037` int(11) DEFAULT NULL,
  `district_a2_directfield_nominalcolumn_100028` varchar(19) DEFAULT NULL,
  `district_a15_directfield_numericalcolumn_100036` int(5) DEFAULT NULL,
  `district_a3_directfield_nominalcolumn_100029` varchar(15) DEFAULT NULL,
  `district_a13_directfield_numericalcolumn_100034` decimal(3,2) DEFAULT NULL,
  `loan_date_directfield_timecolumn_100049` date DEFAULT NULL,
  `account_date_directfield_timecolumn_100047` date DEFAULT NULL,
  `order_amount_aggregate_min_100012` decimal(6,1) DEFAULT NULL,
  `order_account_to_aggregate_max_100016` int(11) DEFAULT NULL,
  `district_a6_directfield_numericalcolumn_100040` int(11) DEFAULT NULL,
  `order_account_to_aggregate_avg_100006` decimal(14,4) DEFAULT NULL,
  `order_amount_aggregate_avg_100007` decimal(10,5) DEFAULT NULL,
  `trans_balance_aggregate_max_100020` int(11) DEFAULT NULL,
  `order_amount_aggregate_max_100017` decimal(6,1) DEFAULT NULL,
  `trans_amount_aggregate_max_100019` int(11) DEFAULT NULL,
  `trans_amount_aggregate_stddev_samp_100004` double(26,4) DEFAULT NULL,
  `loan_amount_directfield_numericalcolumn_100044` int(11) DEFAULT NULL,
  `district_a5_directfield_numericalcolumn_100039` int(11) DEFAULT NULL,
  `loan_payments_directfield_numericalcolumn_100046` decimal(6,2) DEFAULT NULL,
  `trans_account_aggregate_max_100018` int(11) DEFAULT NULL,
  `trans_account_aggregate_sum_100023` decimal(32,0) DEFAULT NULL,
  `trans_account_aggregate_avg_100008` decimal(14,4) DEFAULT NULL,
  `district_a8_directfield_numericalcolumn_100042` int(6) DEFAULT NULL,
  `district_a7_directfield_numericalcolumn_100041` int(11) DEFAULT NULL,
  `trans_account_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  `order_amount_aggregate_stddev_samp_100002` double(18,5) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `card_issued_directfield_timecolumn_100048` date DEFAULT NULL,
  `card_type_directfield_nominalcolumn_100027` varchar(7) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mainsample_temp100` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directfield_nominalcolumn_100030` varchar(1) DEFAULT NULL,
  `loan_duration_directfield_numericalcolumn_100045` int(11) DEFAULT NULL,
  `trans_balance_aggregate_min_100015` int(11) DEFAULT NULL,
  `trans_amount_aggregate_min_100014` int(11) DEFAULT NULL,
  `district_a9_directfield_numericalcolumn_100043` int(11) DEFAULT NULL,
  `district_a12_directfield_numericalcolumn_100033` decimal(4,1) DEFAULT NULL,
  `account_frequency_directfield_nominalcolumn_100026` varchar(18) DEFAULT '',
  `district_a14_directfield_numericalcolumn_100035` int(11) DEFAULT NULL,
  `district_a11_directfield_numericalcolumn_100032` int(11) DEFAULT NULL,
  `district_a10_directfield_numericalcolumn_100031` decimal(4,1) DEFAULT NULL,
  `trans_account_aggregate_min_100013` int(11) DEFAULT NULL,
  `district_a16_directfield_numericalcolumn_100037` int(11) DEFAULT NULL,
  `district_a2_directfield_nominalcolumn_100028` varchar(19) DEFAULT NULL,
  `district_a15_directfield_numericalcolumn_100036` int(5) DEFAULT NULL,
  `district_a3_directfield_nominalcolumn_100029` varchar(15) DEFAULT NULL,
  `district_a13_directfield_numericalcolumn_100034` decimal(3,2) DEFAULT NULL,
  `loan_date_directfield_timecolumn_100049` date DEFAULT NULL,
  `account_date_directfield_timecolumn_100047` date DEFAULT NULL,
  `order_amount_aggregate_min_100012` decimal(6,1) DEFAULT NULL,
  `order_account_to_aggregate_max_100016` int(11) DEFAULT NULL,
  `district_a6_directfield_numericalcolumn_100040` int(11) DEFAULT NULL,
  `order_account_to_aggregate_avg_100006` decimal(14,4) DEFAULT NULL,
  `order_amount_aggregate_avg_100007` decimal(10,5) DEFAULT NULL,
  `trans_balance_aggregate_max_100020` int(11) DEFAULT NULL,
  `order_amount_aggregate_max_100017` decimal(6,1) DEFAULT NULL,
  `trans_amount_aggregate_max_100019` int(11) DEFAULT NULL,
  `trans_amount_aggregate_stddev_samp_100004` double(26,4) DEFAULT NULL,
  `loan_amount_directfield_numericalcolumn_100044` int(11) DEFAULT NULL,
  `district_a5_directfield_numericalcolumn_100039` int(11) DEFAULT NULL,
  `loan_payments_directfield_numericalcolumn_100046` decimal(6,2) DEFAULT NULL,
  `trans_account_aggregate_max_100018` int(11) DEFAULT NULL,
  `trans_account_aggregate_sum_100023` decimal(32,0) DEFAULT NULL,
  `trans_account_aggregate_avg_100008` decimal(14,4) DEFAULT NULL,
  `district_a8_directfield_numericalcolumn_100042` int(6) DEFAULT NULL,
  `district_a7_directfield_numericalcolumn_100041` int(11) DEFAULT NULL,
  `trans_account_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  `order_amount_aggregate_stddev_samp_100002` double(18,5) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `card_issued_directfield_timecolumn_100048` date DEFAULT NULL,
  `card_type_directfield_nominalcolumn_100027` varchar(7) DEFAULT NULL,
  KEY `ix_temp100` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `math_function` (
  `name` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `functionType` varchar(128) NOT NULL DEFAULT 'EvaluationFunction',
  `min` varchar(64) NOT NULL,
  `max` varchar(64) NOT NULL,
  `unit` varchar(64) NOT NULL,
  `higherIsBetter` varchar(16) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `source_code` text NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `member` (
  `member_no` int(11) NOT NULL,
  `lastname` varchar(15) NOT NULL,
  `firstname` varchar(15) NOT NULL,
  `middleinitial` char(1) DEFAULT NULL,
  `street` varchar(15) NOT NULL,
  `city` varchar(15) NOT NULL,
  `state_prov` char(2) NOT NULL,
  `country` char(2) NOT NULL,
  `mail_code` char(10) NOT NULL,
  `phone_no` char(13) DEFAULT NULL,
  `photograph` longblob DEFAULT NULL,
  `issue_dt` datetime NOT NULL,
  `expr_dt` datetime NOT NULL,
  `region_no` int(11) NOT NULL,
  `corp_no` int(11) DEFAULT NULL,
  `prev_balance` decimal(19,4) DEFAULT NULL,
  `curr_balance` decimal(19,4) DEFAULT NULL,
  `member_code` char(2) NOT NULL,
  PRIMARY KEY (`member_no`),
  KEY `member_region_no` (`region_no`),
  KEY `member_corp_no` (`corp_no`),
  CONSTRAINT `member_ibfk_1` FOREIGN KEY (`region_no`) REFERENCES `region` (`region_no`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `member_ibfk_2` FOREIGN KEY (`corp_no`) REFERENCES `corporation` (`corp_no`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `molecule` (
  `molecule_id` varchar(255) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`molecule_id`),
  KEY `molecule_id` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ms_Carcinogenesis` (
  `propagated_id` char(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '',
  `propagated_date` char(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '',
  `propagated_target` char(1) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `atom_name_existencionalCount_o_100034` decimal(23,0) DEFAULT NULL,
  `atom_name_textLength_stddev_samp_100068` double(24,4) DEFAULT NULL,
  `atom_charge_existencionalCount_a00_0615x0_1375_100027` decimal(23,0) DEFAULT NULL,
  `atom_numberOfChildren_100058` bigint(21) DEFAULT 0,
  `atom_atomtype_numberOfChildTypes_100063` bigint(21) DEFAULT 0,
  `atom_name_textLength_avg_100071` decimal(13,4) DEFAULT NULL,
  `atom_name_existencionalCount_h_100032` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_3_100007` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_10_100009` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_s_100037` decimal(23,0) DEFAULT NULL,
  `atom_charge_existencionalCount_a0infx0_1355_100031` decimal(23,0) DEFAULT NULL,
  `sbond_1_numberOfChildren_100059` bigint(21) DEFAULT 0,
  `atom_atomtype_existencionalCount_22_100008` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_36_100022` decimal(23,0) DEFAULT NULL,
  `sbond_2_numberOfChildren_100060` bigint(21) DEFAULT 0,
  `atom_name_numberOfChildTypes_100065` bigint(21) DEFAULT 0,
  `atom_atomtype_textLength_avg_100069` decimal(13,4) DEFAULT NULL,
  `atom_charge_existencionalCount_a00_1355x0_0175_100029` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_textLength_stddev_samp_100066` double(24,4) DEFAULT NULL,
  `atom_name_existencionalCount_c_100033` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_8_100018` decimal(23,0) DEFAULT NULL,
  `sbond_7_numberOfChildren_100062` bigint(21) DEFAULT 0,
  `atom_atomtype_existencionalCount_45_100015` decimal(23,0) DEFAULT NULL,
  `atom_charge_existencionalCount_a00_1375xinf_100028` decimal(23,0) DEFAULT NULL,
  `atom_charge_numberOfChildTypes_100064` bigint(21) DEFAULT 0,
  `atom_atomtype_existencionalCount_1_100010` decimal(23,0) DEFAULT NULL,
  `atom_charge_textLength_avg_100070` decimal(13,4) DEFAULT NULL,
  `atom_charge_textLength_stddev_samp_100067` double(24,4) DEFAULT NULL,
  `atom_charge_duplicationRatio_nominalColumn_100005` decimal(46,4) DEFAULT NULL,
  `atom_atomtype_existencionalCount_14_100014` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_40_100012` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_93_100011` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_cl_100036` decimal(23,0) DEFAULT NULL,
  `atom_charge_existencionalCount_a00_0175x0_0615_100030` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_50_100016` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_29_100026` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_51_100020` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_94_100024` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_br_100038` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_n_100035` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_49_100019` decimal(23,0) DEFAULT NULL,
  `atom_charge_textLength_min_100073` bigint(10) DEFAULT NULL,
  `atom_name_existencionalCount_na_100040` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_textLength_min_100072` bigint(10) DEFAULT NULL,
  `atom_atomtype_existencionalCount_32_100013` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_21_100025` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_27_100021` decimal(23,0) DEFAULT NULL,
  `atom_charge_textLength_max_100076` bigint(10) DEFAULT NULL,
  `atom_atomtype_duplicationRatio_nominalColumn_100004` decimal(46,4) DEFAULT NULL,
  `atom_name_existencionalCount_p_100039` decimal(23,0) DEFAULT NULL,
  `atom_name_textLength_max_100077` bigint(10) DEFAULT NULL,
  `atom_name_duplicationRatio_nominalColumn_100006` decimal(46,4) DEFAULT NULL,
  `atom_atomtype_existencionalCount_16_100017` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_i_100042` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_sn_100044` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_ti_100045` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_pb_100046` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_as_100051` decimal(23,0) DEFAULT NULL,
  `atom_atomtype_existencionalCount_38_100023` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_cu_100043` decimal(23,0) DEFAULT NULL,
  `atom_name_existencionalCount_ba_100050` decimal(23,0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ms_SAP` (
  `propagated_id1` int(11) DEFAULT NULL,
  `propagated_date` datetime DEFAULT NULL,
  `propagated_target` varchar(255) DEFAULT NULL,
  `Mailings1_2_KxIndex_directField_numericalColumn_100037` int(11) DEFAULT NULL,
  `Sales_AMOUNT_aggregate_sum_100005` double DEFAULT NULL,
  `Sales_AMOUNT_aggregate_max_100004` float DEFAULT NULL,
  `Demog_A_VAR16_directField_numericalColumn_100024` float DEFAULT NULL,
  `Demog_A_VAR10_directField_numericalColumn_100018` float DEFAULT NULL,
  `Customers_DATA3_directField_numericalColumn_100014` float DEFAULT NULL,
  `Customers_age_directField_numericalColumn_100016` int(11) DEFAULT NULL,
  `Sales_AMOUNT_aggregate_avg_100002` double DEFAULT NULL,
  `Sales_AMOUNT_aggregate_stddev_samp_100001` double DEFAULT NULL,
  `Customers_OCCUPATION_directField_nominalColumn_100010` varchar(255) DEFAULT NULL,
  `Sales_AMOUNT_aggregate_min_100003` float DEFAULT NULL,
  `Demog_A_VAR12_directField_numericalColumn_100020` float DEFAULT NULL,
  `Demog_A_VAR4_directField_numericalColumn_100029` float DEFAULT NULL,
  `Customers_DATA2_directField_numericalColumn_100013` float DEFAULT NULL,
  `Customers_NOM1_directField_nominalColumn_100007` varchar(255) DEFAULT NULL,
  `Demog_A_VAR6_directField_numericalColumn_100031` float DEFAULT NULL,
  `Demog_A_VAR9_directField_numericalColumn_100034` float DEFAULT NULL,
  `Sales_EVENT_DATE_timeFrequency_100039` decimal(26,5) DEFAULT NULL,
  `Demog_INHABITANTS_K_directField_numericalColumn_100036` float DEFAULT NULL,
  `Demog_A_VAR7_directField_numericalColumn_100032` float DEFAULT NULL,
  `Customers_DATA1_directField_numericalColumn_100012` float DEFAULT NULL,
  `Demog_A_VAR3_directField_numericalColumn_100028` float DEFAULT NULL,
  `Demog_A_VAR8_directField_numericalColumn_100033` float DEFAULT NULL,
  `Demog_A_VAR2_directField_numericalColumn_100027` float DEFAULT NULL,
  `Demog_A_VAR17_directField_numericalColumn_100025` float DEFAULT NULL,
  `Customers_NOM2_directField_nominalColumn_100008` varchar(255) DEFAULT NULL,
  `Demog_A_VAR14_directField_numericalColumn_100022` float DEFAULT NULL,
  `Demog_A_VAR13_directField_numericalColumn_100021` float DEFAULT NULL,
  `Demog_A_VAR1_directField_numericalColumn_100017` float DEFAULT NULL,
  `Customers_NOM3_directField_nominalColumn_100009` varchar(255) DEFAULT NULL,
  `Customers_EDUCATIONNUM_directField_numericalColumn_100015` int(11) DEFAULT NULL,
  `Customers_SEX_directField_nominalColumn_100011` varchar(255) DEFAULT NULL,
  `Demog_INCOME_K_directField_numericalColumn_100035` decimal(10,2) DEFAULT NULL,
  `Demog_A_VAR11_directField_numericalColumn_100019` float DEFAULT NULL,
  `Demog_A_VAR15_directField_numericalColumn_100023` float DEFAULT NULL,
  `Demog_A_VAR5_directField_numericalColumn_100030` float DEFAULT NULL,
  `Customers_MARITAL_STATUS_directField_nominalColumn_100006` varchar(255) DEFAULT NULL,
  `Demog_A_VAR18_directField_numericalColumn_100026` float DEFAULT NULL,
  `Mailings1_2_REF_DATE_directField_timeColumn_100038` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ms_Toxicology` (
  `propagated_id` varchar(255) NOT NULL DEFAULT '',
  `propagated_date` varchar(255) NOT NULL DEFAULT '',
  `propagated_target` varchar(255) DEFAULT NULL,
  `atom_numberOfChildren_100032` bigint(21) DEFAULT 0,
  `bond_numberOfChildren_100033` bigint(21) DEFAULT 0,
  `connected_numberOfChildren_100034` bigint(21) DEFAULT 0,
  `connected_numberOfChildren_100035` bigint(21) DEFAULT 0,
  `atom_element_existencionalCount_c_100006` decimal(23,0) DEFAULT NULL,
  `bond_bond_type_existencionalCount__100026` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_o_100007` decimal(23,0) DEFAULT NULL,
  `atom_element_numberOfChildTypes_100036` bigint(21) DEFAULT 0,
  `atom_element_textLength_stddev_samp_100038` double(24,4) DEFAULT NULL,
  `atom_element_existencionalCount_s_100010` decimal(23,0) DEFAULT NULL,
  `atom_element_textLength_avg_100040` decimal(13,4) DEFAULT NULL,
  `bond_bond_type_existencionalCount__100025` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_h_100005` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_br_100011` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_cl_100009` decimal(23,0) DEFAULT NULL,
  `atom_element_duplicationRatio_nominalColumn_100003` decimal(46,4) DEFAULT NULL,
  `bond_bond_type_numberOfChildTypes_100037` bigint(21) DEFAULT 0,
  `atom_element_existencionalCount_na_100012` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_n_100008` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_f_100014` decimal(23,0) DEFAULT NULL,
  `bond_bond_type_duplicationRatio_nominalColumn_100004` decimal(46,4) DEFAULT NULL,
  `atom_element_textLength_max_100044` bigint(10) DEFAULT NULL,
  `bond_bond_type_existencionalCount__100027` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_sn_100018` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_cu_100017` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_y_100021` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_p_100013` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_i_100015` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_k_100020` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_pb_100022` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_ca_100024` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_si_100016` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_b_100019` decimal(23,0) DEFAULT NULL,
  `atom_element_existencionalCount_te_100023` decimal(23,0) DEFAULT NULL,
  `atom_element_ratioOfMissingValues_nominalColumn_100030` decimal(25,4) DEFAULT NULL,
  `bond_bond_type_ratioOfMissingValues_nominalColumn_100031` decimal(25,4) DEFAULT NULL,
  `bond_bond_type_textLength_stddev_samp_100039` double(24,4) DEFAULT NULL,
  `bond_bond_type_textLength_avg_100041` decimal(13,4) DEFAULT NULL,
  `atom_element_textLength_min_100042` bigint(10) DEFAULT NULL,
  `bond_bond_type_textLength_min_100043` bigint(10) DEFAULT NULL,
  `bond_bond_type_textLength_max_100045` bigint(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ms_financial` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directField_nominalColumn_100060` varchar(1) DEFAULT NULL,
  `loan_duration_directField_numericalColumn_100081` int(11) DEFAULT NULL,
  `order_account_id_aggregate_stddev_samp_100008` double(26,4) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  `order_order_id_aggregate_stddev_samp_100011` double(26,4) DEFAULT NULL,
  `loan_date_directField_timeColumn_100086` date DEFAULT NULL,
  `client_district_id_aggregate_avg_100015` decimal(14,4) DEFAULT NULL,
  `order_account_to_aggregate_max_100042` int(11) DEFAULT NULL,
  `order_account_to_aggregate_avg_100020` decimal(14,4) DEFAULT NULL,
  `account_date_directField_timeColumn_100084` date DEFAULT NULL,
  `district_A6_directField_numericalColumn_100074` int(11) DEFAULT NULL,
  `order_account_id_aggregate_sum_100052` decimal(32,0) DEFAULT NULL,
  `district_A3_directField_nominalColumn_100059` varchar(15) DEFAULT NULL,
  `disp_account_id_aggregate_sum_100049` decimal(32,0) DEFAULT NULL,
  `client_client_id_aggregate_sum_100047` decimal(32,0) DEFAULT NULL,
  `order_order_id_aggregate_sum_100055` decimal(32,0) DEFAULT NULL,
  `client_client_id_aggregate_avg_100014` decimal(14,4) DEFAULT NULL,
  `disp_disp_id_aggregate_sum_100051` decimal(32,0) DEFAULT NULL,
  `district_A11_directField_numericalColumn_100066` int(11) DEFAULT NULL,
  `district_A10_directField_numericalColumn_100065` decimal(4,1) DEFAULT NULL,
  `order_amount_aggregate_sum_100054` decimal(28,1) DEFAULT NULL,
  `client_district_id_aggregate_sum_100046` decimal(32,0) DEFAULT NULL,
  `order_amount_aggregate_avg_100021` decimal(10,5) DEFAULT NULL,
  `order_amount_aggregate_min_100032` decimal(6,1) DEFAULT NULL,
  `loan_amount_directField_numericalColumn_100080` int(11) DEFAULT NULL,
  `district_A16_directField_numericalColumn_100071` int(11) DEFAULT NULL,
  `client_client_id_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `order_amount_aggregate_max_100043` decimal(6,1) DEFAULT NULL,
  `district_A15_directField_numericalColumn_100070` int(5) DEFAULT NULL,
  `district_A13_directField_numericalColumn_100068` decimal(3,2) DEFAULT NULL,
  `district_A12_directField_numericalColumn_100067` decimal(4,1) DEFAULT NULL,
  `loan_payments_directField_numericalColumn_100083` decimal(6,2) DEFAULT NULL,
  `district_A14_directField_numericalColumn_100069` int(11) DEFAULT NULL,
  `district_A5_directField_numericalColumn_100073` int(11) DEFAULT NULL,
  `client_district_id_aggregate_sum_100048` decimal(32,0) DEFAULT NULL,
  `district_A7_directField_numericalColumn_100075` int(11) DEFAULT NULL,
  `district_A9_directField_numericalColumn_100077` int(11) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100009` double(26,4) DEFAULT NULL,
  `account_frequency_directField_nominalColumn_100056` varchar(18) DEFAULT '',
  `district_A8_directField_numericalColumn_100076` int(6) DEFAULT NULL,
  `card_card_id_directField_numericalColumn_100063` int(11) DEFAULT 0,
  `card_type_directField_nominalColumn_100057` varchar(7) DEFAULT NULL,
  `client_district_id_aggregate_stddev_samp_100002` double(26,4) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ms_mutagenesis` (
  `propagated_id` char(4) NOT NULL DEFAULT '',
  `propagated_date` char(4) NOT NULL DEFAULT '',
  `propagated_target` char(3) DEFAULT NULL,
  `molecule_logp_ind1_ratio_100141` double DEFAULT NULL,
  `molecule_logp_inda_ratio_100142` double DEFAULT NULL,
  `atom_charge_aggregate_stddev_samp_100001` double DEFAULT NULL,
  `atom_type_aggregate_stddev_samp_100002` double(26,4) DEFAULT NULL,
  `atom_charge_aggregate_avg_100003` double DEFAULT NULL,
  `atom_type_aggregate_avg_100004` decimal(14,4) DEFAULT NULL,
  `atom_charge_aggregate_min_100005` double DEFAULT NULL,
  `atom_type_aggregate_min_100006` int(11) DEFAULT NULL,
  `atom_charge_aggregate_max_100007` double DEFAULT NULL,
  `atom_type_aggregate_max_100008` int(11) DEFAULT NULL,
  `atom_charge_aggregate_sum_100009` double DEFAULT NULL,
  `atom_type_aggregate_sum_100010` decimal(32,0) DEFAULT NULL,
  `bond_type_aggregate_stddev_samp_100011` double(26,4) DEFAULT NULL,
  `bond_type_aggregate_avg_100012` decimal(14,4) DEFAULT NULL,
  `bond_type_aggregate_min_100013` int(11) DEFAULT NULL,
  `bond_type_aggregate_max_100014` int(11) DEFAULT NULL,
  `bond_type_aggregate_sum_100015` decimal(32,0) DEFAULT NULL,
  `atom_charge_aggregateDistinct_avg_100018` double DEFAULT NULL,
  `atom_type_aggregateDistinct_avg_100019` decimal(14,4) DEFAULT NULL,
  `atom_charge_aggregateDistinct_sum_100020` double DEFAULT NULL,
  `atom_type_aggregateDistinct_sum_100021` decimal(32,0) DEFAULT NULL,
  `bond_type_aggregateDistinct_avg_100023` decimal(14,4) DEFAULT NULL,
  `bond_type_aggregateDistinct_sum_100024` decimal(32,0) DEFAULT NULL,
  `atom_charge_aggregateRange_100025` double DEFAULT NULL,
  `atom_type_aggregateRange_100026` bigint(12) DEFAULT NULL,
  `bond_type_aggregateRange_100027` bigint(12) DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_stddev_samp_c_100040` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_stddev_samp_h_100041` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_stddev_samp_o_100042` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_stddev_samp_n_100043` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_stddev_samp_f_100044` double DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_stddev_samp_c_100045` double(26,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_stddev_samp_h_100046` double(26,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_stddev_samp_o_100047` double(26,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_stddev_samp_n_100048` double(26,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_stddev_samp_f_100049` double(26,4) DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_avg_c_100050` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_avg_h_100051` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_avg_o_100052` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_avg_n_100053` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_avg_f_100054` double DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_avg_c_100055` decimal(14,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_avg_h_100056` decimal(14,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_avg_o_100057` decimal(14,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_avg_n_100058` decimal(14,4) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_avg_f_100059` decimal(14,4) DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_min_c_100060` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_min_h_100061` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_min_o_100062` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_min_n_100063` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_min_f_100064` double DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_min_c_100065` int(11) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_min_h_100066` int(11) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_min_o_100067` int(11) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_min_n_100068` int(11) DEFAULT NULL,
  `atom_element_type_aggregateSubgroup_min_f_100069` int(11) DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_max_c_100070` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_max_h_100071` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_max_o_100072` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_max_n_100073` double DEFAULT NULL,
  `atom_element_charge_aggregateSubgroup_max_f_100074` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ms_voc` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_id2` char(1) NOT NULL DEFAULT '',
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(30) DEFAULT NULL,
  `voyages_arrival_harbour_directField_nominalColumn_100028` varchar(30) DEFAULT NULL,
  `voyages_number_directField_numericalColumn_100092` int(11) DEFAULT NULL,
  `voyages_next_voyage_directField_numericalColumn_100091` int(11) DEFAULT NULL,
  `voyages_chamber_directField_nominalColumn_100034` char(1) DEFAULT NULL,
  `total_number_directField_numericalColumn_100086` int(11) DEFAULT NULL,
  `voyages_departure_harbour_directField_nominalColumn_100035` varchar(30) DEFAULT NULL,
  `seafarers_number_directField_numericalColumn_100070` int(11) DEFAULT NULL,
  `soldiers_number_directField_numericalColumn_100078` int(11) DEFAULT NULL,
  `soldiers_onboard_at_departure_directField_numericalColum_100081` int(11) DEFAULT NULL,
  `voyages_number_sup_directField_nominalColumn_100038` char(1) DEFAULT NULL,
  `voyages_type_of_boat_directField_nominalColumn_100041` varchar(30) DEFAULT NULL,
  `voyages_yard_directField_nominalColumn_100042` char(1) DEFAULT NULL,
  `voyages_tonnage_directField_numericalColumn_100093` int(11) DEFAULT NULL,
  `passengers_number_directField_numericalColumn_100062` int(11) DEFAULT NULL,
  `seafarers_onboard_at_departure_directField_numericalColu_100073` int(11) DEFAULT NULL,
  `invoices_number_aggregate_avg_100005` decimal(14,4) DEFAULT NULL,
  `craftsmen_number_directField_numericalColumn_100046` int(11) DEFAULT NULL,
  `total_onboard_at_departure_directField_numericalColumn_100089` int(11) DEFAULT NULL,
  `voyages_built_directField_nominalColumn_100032` varchar(15) DEFAULT NULL,
  `soldiers_left_at_cape_directField_numericalColumn_100077` int(11) DEFAULT NULL,
  `voyages_bought_directField_nominalColumn_100031` varchar(15) DEFAULT NULL,
  `voyages_master_directField_nominalColumn_100037` varchar(50) DEFAULT NULL,
  `voyages_boatname_directField_nominalColumn_100030` varchar(50) DEFAULT NULL,
  `seafarers_onboard_at_arrival_directField_numericalColumn_100071` int(11) DEFAULT NULL,
  `voyages_artificial_id_directField_nominalColumn_100029` char(12) DEFAULT NULL,
  `voyages_particulars_directField_nominalColumn_100039` text DEFAULT NULL,
  `total_left_at_cape_directField_numericalColumn_100085` int(11) DEFAULT NULL,
  `voyages_hired_directField_nominalColumn_100036` varchar(15) DEFAULT NULL,
  `soldiers_onboard_at_arrival_directField_numericalColumn_100079` int(11) DEFAULT NULL,
  `total_death_during_voyage_directField_numericalColumn_100084` int(11) DEFAULT NULL,
  `seafarers_death_during_voyage_directField_numericalColum_100068` int(11) DEFAULT NULL,
  `invoices_number_aggregate_sum_100014` decimal(32,0) DEFAULT NULL,
  `total_death_at_cape_directField_numericalColumn_100083` int(11) DEFAULT NULL,
  `total_trip_directField_numericalColumn_100090` int(11) DEFAULT NULL,
  `craftsmen_onboard_at_arrival_directField_numericalColumn_100047` int(11) DEFAULT NULL,
  `voyages_trip_directField_numericalColumn_100094` int(11) DEFAULT NULL,
  `passengers_onboard_at_arrival_directField_numericalColum_100063` int(11) DEFAULT NULL,
  `seafarers_onboard_at_cape_directField_numericalColumn_100072` int(11) DEFAULT NULL,
  `soldiers_death_during_voyage_directField_numericalColumn_100076` int(11) DEFAULT NULL,
  `impotenten_number_directField_numericalColumn_100054` int(11) DEFAULT NULL,
  `soldiers_onboard_at_cape_directField_numericalColumn_100080` int(11) DEFAULT NULL,
  `voyages_cape_call_directField_nominalColumn_100033` varchar(5) DEFAULT NULL,
  `invoices_invoice_aggregate_avg_100004` decimal(14,4) DEFAULT NULL,
  `invoices_invoice_aggregate_sum_100013` decimal(32,0) DEFAULT NULL,
  `passengers_death_at_cape_directField_numericalColumn_100059` int(11) DEFAULT NULL,
  `invoices_invoice_aggregate_min_100007` int(11) DEFAULT NULL,
  `impotenten_onboard_at_departure_directField_numericalCol_100057` int(11) DEFAULT NULL,
  `invoices_invoice_aggregate_max_100010` int(11) DEFAULT NULL,
  `invoices_trip_aggregate_max_100012` int(11) DEFAULT NULL,
  `invoices_trip_aggregate_min_100009` int(11) DEFAULT NULL,
  `invoices_trip_aggregate_avg_100006` decimal(14,4) DEFAULT NULL,
  `total_onboard_at_arrival_directField_numericalColumn_100087` int(11) DEFAULT NULL,
  `craftsmen_death_during_voyage_directField_numericalColum_100044` int(11) DEFAULT NULL,
  `seafarers_death_at_cape_directField_numericalColumn_100067` int(11) DEFAULT NULL,
  `invoices_invoice_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  `passengers_left_at_cape_directField_numericalColumn_100061` int(11) DEFAULT NULL,
  `seafarers_left_at_cape_directField_numericalColumn_100069` int(11) DEFAULT NULL,
  `craftsmen_left_at_cape_directField_numericalColumn_100045` int(11) DEFAULT NULL,
  `invoices_trip_aggregate_sum_100015` decimal(32,0) DEFAULT NULL,
  `passengers_onboard_at_cape_directField_numericalColumn_100064` int(11) DEFAULT NULL,
  `passengers_trip_directField_numericalColumn_100066` int(11) DEFAULT NULL,
  `soldiers_death_at_cape_directField_numericalColumn_100075` int(11) DEFAULT NULL,
  `passengers_onboard_at_departure_directField_numericalCol_100065` int(11) DEFAULT NULL,
  `craftsmen_onboard_at_cape_directField_numericalColumn_100048` int(11) DEFAULT NULL,
  `seafarers_trip_directField_numericalColumn_100074` int(11) DEFAULT NULL,
  `soldiers_trip_directField_numericalColumn_100082` int(11) DEFAULT NULL,
  `invoices_trip_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  `invoices_number_aggregate_stddev_samp_100002` double(26,4) DEFAULT NULL,
  `total_onboard_at_cape_directField_numericalColumn_100088` int(11) DEFAULT NULL,
  `craftsmen_trip_directField_numericalColumn_100050` int(11) DEFAULT NULL,
  `passengers_death_during_voyage_directField_numericalColu_100060` int(11) DEFAULT NULL,
  `impotenten_trip_directField_numericalColumn_100058` int(11) DEFAULT NULL,
  `craftsmen_death_at_cape_directField_numericalColumn_100043` int(11) DEFAULT NULL,
  `soldiers_number_sup_directField_nominalColumn_100024` char(1) DEFAULT NULL,
  `seafarers_number_sup_directField_nominalColumn_100022` char(1) DEFAULT NULL,
  `craftsmen_onboard_at_departure_directField_numericalColu_100049` int(11) DEFAULT NULL,
  `craftsmen_number_sup_directField_nominalColumn_100016` char(1) DEFAULT NULL,
  `total_trip_sup_directField_nominalColumn_100027` char(1) DEFAULT NULL,
  `voyages_trip_sup_directField_nominalColumn_100040` char(1) DEFAULT NULL,
  `impotenten_number_sup_directField_nominalColumn_100018` char(1) DEFAULT NULL,
  `seafarers_trip_sup_directField_nominalColumn_100023` char(1) DEFAULT NULL,
  `soldiers_trip_sup_directField_nominalColumn_100025` char(1) DEFAULT NULL,
  `voyages_cape_departure_directField_timeColumn_100097` date DEFAULT NULL,
  `voyages_cape_arrival_directField_timeColumn_100096` date DEFAULT NULL,
  `total_number_sup_directField_nominalColumn_100026` char(1) DEFAULT NULL,
  `passengers_number_sup_directField_nominalColumn_100020` char(1) DEFAULT NULL,
  `craftsmen_trip_sup_directField_nominalColumn_100017` char(1) DEFAULT NULL,
  `impotenten_trip_sup_directField_nominalColumn_100019` char(1) DEFAULT NULL,
  `impotenten_death_at_cape_directField_numericalColumn_100051` int(11) DEFAULT NULL,
  `voyages_arrival_date_directField_timeColumn_100095` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `passengers` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `passengers_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `password` (
  `businessentityid` int(11) NOT NULL,
  `passwordhash` varchar(128) NOT NULL COMMENT 'Password for the e-mail account.',
  `passwordsalt` varchar(10) NOT NULL COMMENT 'Random value concatenated with the password string before the password is hashed.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='One way hashed authentication information'
;


CREATE TABLE `payment` (
  `payment_no` int(11) NOT NULL,
  `member_no` int(11) NOT NULL,
  `payment_dt` datetime NOT NULL,
  `payment_amt` decimal(19,4) NOT NULL,
  `statement_no` int(11) DEFAULT NULL,
  `payment_code` char(2) NOT NULL,
  PRIMARY KEY (`payment_no`),
  KEY `payment_statement_no` (`statement_no`),
  KEY `payment_member_no` (`member_no`),
  CONSTRAINT `payment_ibfk_1` FOREIGN KEY (`member_no`) REFERENCES `member` (`member_no`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `person` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key for Person records.',
  `persontype` char(2) NOT NULL COMMENT 'Primary type of person: SC = Store Contact, IN = Individual (retail) customer, SP = Sales person, EM = Employee (non-sales), VC = Vendor contact, GC = General contact',
  `namestyle` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = The data in FirstName and LastName are stored in western style (first name, last name) order.  1 = Eastern style (last name, first name) order.',
  `title` varchar(8) DEFAULT NULL COMMENT 'A courtesy title. For example, Mr. or Ms.',
  `firstname` varchar(100) NOT NULL COMMENT 'First name of the person.',
  `middlename` varchar(100) DEFAULT NULL COMMENT 'Middle name or middle initial of the person.',
  `lastname` varchar(100) NOT NULL COMMENT 'Last name of the person.',
  `suffix` varchar(10) DEFAULT NULL COMMENT 'Surname suffix. For example, Sr. or Jr.',
  `emailpromotion` int(11) NOT NULL DEFAULT 0 COMMENT '0 = Contact does not wish to receive e-mail promotions, 1 = Contact does wish to receive e-mail promotions from AdventureWorks, 2 = Contact does wish to receive e-mail promotions from AdventureWorks and selected partners. ',
  `additionalcontactinfo` text DEFAULT NULL COMMENT 'Additional contact information about the person stored in xml format. ',
  `demographics` text DEFAULT NULL COMMENT 'Personal information such as hobbies, and income collected from online shoppers. Used for sales analysis.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Human beings involved with AdventureWorks: employees, customer contacts, and vendor contacts.'
;


CREATE TABLE `personcreditcard` (
  `businessentityid` int(11) NOT NULL COMMENT 'Business entity identification number. Foreign key to Person.BusinessEntityID.',
  `creditcardid` int(11) NOT NULL COMMENT 'Credit card identification number. Foreign key to CreditCard.CreditCardID.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`creditcardid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping people to their credit card information in the CreditCard table. '
;


CREATE TABLE `personphone` (
  `businessentityid` int(11) NOT NULL COMMENT 'Business entity identification number. Foreign key to Person.BusinessEntityID.',
  `phonenumber` varchar(50) NOT NULL COMMENT 'Telephone number identification number.',
  `phonenumbertypeid` int(11) NOT NULL COMMENT 'Kind of phone number. Foreign key to PhoneNumberType.PhoneNumberTypeID.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`phonenumber`,`phonenumbertypeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Telephone number and type of a person.'
;


CREATE TABLE `phone_brand_device_model2` (
  `device_id` bigint(20) NOT NULL,
  `phone_brand` varchar(255) NOT NULL,
  `device_model` varchar(255) NOT NULL,
  PRIMARY KEY (`device_id`,`phone_brand`,`device_model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `phonenumbertype` (
  `phonenumbertypeid` int(11) NOT NULL COMMENT 'Primary key for telephone number type records.',
  `name` varchar(100) NOT NULL COMMENT 'Name of the telephone number type',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`phonenumbertypeid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Type of phone number of a person.'
;


CREATE TABLE `postHistory` (
  `Id` int(11) NOT NULL,
  `PostHistoryTypeId` int(11) DEFAULT NULL,
  `PostId` int(11) DEFAULT NULL,
  `RevisionGUID` varchar(255) DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `Text` longtext DEFAULT NULL,
  `Comment` text DEFAULT NULL,
  `UserDisplayName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `postHistory_Id_key` (`Id`),
  KEY `postHistory_UserId_fkey` (`UserId`),
  KEY `postHistory_PostId_fkey` (`PostId`),
  CONSTRAINT `postHistory_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `postHistory_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `postLinks` (
  `Id` int(11) NOT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `PostId` int(11) DEFAULT NULL,
  `RelatedPostId` int(11) DEFAULT NULL,
  `LinkTypeId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `postlinks_stripped_PostId_fkey` (`PostId`),
  KEY `postlinks_stripped_RelatedPostId_fkey` (`RelatedPostId`),
  CONSTRAINT `postlinks_stripped_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `postlinks_stripped_RelatedPostId_fkey` FOREIGN KEY (`RelatedPostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `posts` (
  `Id` int(11) NOT NULL,
  `PostTypeId` int(11) DEFAULT NULL,
  `AcceptedAnswerId` int(11) DEFAULT NULL,
  `CreaionDate` datetime DEFAULT NULL,
  `Score` int(11) DEFAULT NULL,
  `ViewCount` int(11) DEFAULT NULL,
  `Body` longtext DEFAULT NULL,
  `OwnerUserId` int(11) DEFAULT NULL,
  `LasActivityDate` datetime DEFAULT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `Tags` varchar(255) DEFAULT NULL,
  `AnswerCount` int(11) DEFAULT NULL,
  `CommentCount` int(11) DEFAULT NULL,
  `FavoriteCount` int(11) DEFAULT NULL,
  `LastEditorUserId` int(11) DEFAULT NULL,
  `LastEditDate` datetime DEFAULT NULL,
  `CommunityOwnedDate` datetime DEFAULT NULL,
  `ParentId` int(11) DEFAULT NULL,
  `ClosedDate` datetime DEFAULT NULL,
  `OwnerDisplayName` varchar(255) DEFAULT NULL,
  `LastEditorDisplayName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `posts_Id_key` (`Id`),
  KEY `posts_ParentId_fkey` (`ParentId`),
  KEY `posts_OwnerUserId_fkey` (`OwnerUserId`),
  KEY `posts_LastEditorUserId_fkey` (`LastEditorUserId`),
  CONSTRAINT `posts_LastEditorUserId_fkey` FOREIGN KEY (`LastEditorUserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `posts_OwnerUserId_fkey` FOREIGN KEY (`OwnerUserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `posts_ParentId_fkey` FOREIGN KEY (`ParentId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100001` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_account_to_aggregate_stddev_samp_100001` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100002` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_stddev_samp_100002` double(18,5) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100003` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_stddev_samp_100003` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100004` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_amount_aggregate_stddev_samp_100004` double(26,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100006` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_account_to_aggregate_avg_100006` decimal(14,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100007` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_avg_100007` decimal(10,5) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100008` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_avg_100008` decimal(14,4) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100012` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_min_100012` decimal(6,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100013` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_min_100013` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100014` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_amount_aggregate_min_100014` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100015` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_balance_aggregate_min_100015` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100016` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_account_to_aggregate_max_100016` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100017` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `order_amount_aggregate_max_100017` decimal(6,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100018` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_max_100018` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100019` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_amount_aggregate_max_100019` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100020` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_balance_aggregate_max_100020` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100023` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `trans_account_aggregate_sum_100023` decimal(32,0) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100026` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `account_frequency_directfield_nominalcolumn_100026` varchar(18) DEFAULT '',
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100027` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `card_type_directfield_nominalcolumn_100027` varchar(7) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100028` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a2_directfield_nominalcolumn_100028` varchar(19) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100029` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a3_directfield_nominalcolumn_100029` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100030` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_status_directfield_nominalcolumn_100030` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100031` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a10_directfield_numericalcolumn_100031` decimal(4,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100032` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a11_directfield_numericalcolumn_100032` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100033` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a12_directfield_numericalcolumn_100033` decimal(4,1) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100034` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a13_directfield_numericalcolumn_100034` decimal(3,2) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100035` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a14_directfield_numericalcolumn_100035` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100036` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a15_directfield_numericalcolumn_100036` int(5) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100037` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a16_directfield_numericalcolumn_100037` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100039` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a5_directfield_numericalcolumn_100039` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100040` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a6_directfield_numericalcolumn_100040` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100041` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a7_directfield_numericalcolumn_100041` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100042` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a8_directfield_numericalcolumn_100042` int(6) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100043` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `district_a9_directfield_numericalcolumn_100043` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100044` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_amount_directfield_numericalcolumn_100044` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100045` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_duration_directfield_numericalcolumn_100045` int(11) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100046` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_payments_directfield_numericalcolumn_100046` decimal(6,2) DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100047` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `account_date_directfield_timecolumn_100047` date DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100048` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `card_issued_directfield_timecolumn_100048` date DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `predictor100049` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date NOT NULL DEFAULT '0000-00-00',
  `propagated_target` varchar(1) DEFAULT NULL,
  `loan_date_directfield_timecolumn_100049` date DEFAULT NULL,
  PRIMARY KEY (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `probehnuto` (
  `client_id` int(11) DEFAULT NULL,
  `month_year_datum_transakce` date NOT NULL,
  `sluzba` varchar(255) DEFAULT NULL,
  `kc_proklikano` decimal(10,2) NOT NULL,
  KEY `probehnuto_client_id` (`client_id`),
  CONSTRAINT `probehnuto_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `probehnuto_mimo_penezenku` (
  `client_id` int(11) NOT NULL,
  `Month/Year` date NOT NULL,
  `probehla_inzerce_mimo_penezenku` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`client_id`,`Month/Year`),
  KEY `probehnuto_mimo_penezenku_client_id` (`client_id`),
  CONSTRAINT `probehnuto_mimo_penezenku_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `product` (
  `productid` int(11) NOT NULL COMMENT 'Primary key for Product records.',
  `name` varchar(100) NOT NULL COMMENT 'Name of the product.',
  `productnumber` varchar(25) NOT NULL COMMENT 'Unique product identification number.',
  `makeflag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Product is purchased, 1 = Product is manufactured in-house.',
  `finishedgoodsflag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Product is not a salable item. 1 = Product is salable.',
  `color` varchar(15) DEFAULT NULL COMMENT 'Product color.',
  `safetystocklevel` smallint(6) NOT NULL COMMENT 'Minimum inventory quantity. ',
  `reorderpoint` smallint(6) NOT NULL COMMENT 'Inventory level that triggers a purchase order or work order. ',
  `standardcost` decimal(19,4) NOT NULL COMMENT 'Standard cost of the product.',
  `listprice` decimal(19,4) NOT NULL COMMENT 'Selling price.',
  `size` varchar(5) DEFAULT NULL COMMENT 'Product size.',
  `sizeunitmeasurecode` char(3) DEFAULT NULL COMMENT 'Unit of measure for Size column.',
  `weightunitmeasurecode` char(3) DEFAULT NULL COMMENT 'Unit of measure for Weight column.',
  `weight` decimal(8,2) DEFAULT NULL COMMENT 'Product weight.',
  `daystomanufacture` int(11) NOT NULL COMMENT 'Number of days required to manufacture the product.',
  `productline` char(2) DEFAULT NULL COMMENT 'R = Road, M = Mountain, T = Touring, S = Standard',
  `class` char(2) DEFAULT NULL COMMENT 'H = High, M = Medium, L = Low',
  `style` char(2) DEFAULT NULL COMMENT 'W = Womens, M = Mens, U = Universal',
  `productsubcategoryid` int(11) DEFAULT NULL COMMENT 'Product is a member of this product subcategory. Foreign key to ProductSubCategory.ProductSubCategoryID. ',
  `productmodelid` int(11) DEFAULT NULL COMMENT 'Product is a member of this product model. Foreign key to ProductModel.ProductModelID.',
  `sellstartdate` datetime NOT NULL COMMENT 'Date the product was available for sale.',
  `sellenddate` datetime DEFAULT NULL COMMENT 'Date the product was no longer available for sale.',
  `discontinueddate` datetime DEFAULT NULL COMMENT 'Date the product was discontinued.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Products sold or used in the manfacturing of sold products.'
;


CREATE TABLE `productcategory` (
  `productcategoryid` int(11) NOT NULL COMMENT 'Primary key for ProductCategory records.',
  `name` varchar(100) NOT NULL COMMENT 'Category description.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productcategoryid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='High-level product categorization.'
;


CREATE TABLE `productcosthistory` (
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID',
  `startdate` datetime NOT NULL COMMENT 'Product cost start date.',
  `enddate` datetime DEFAULT NULL COMMENT 'Product cost end date.',
  `standardcost` decimal(19,4) NOT NULL COMMENT 'Standard cost of the product.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productid`,`startdate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Changes in the cost of a product over time.'
;


CREATE TABLE `productdescription` (
  `productdescriptionid` int(11) NOT NULL COMMENT 'Primary key for ProductDescription records.',
  `description` varchar(400) NOT NULL COMMENT 'Description of the product.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productdescriptionid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product descriptions in several languages.'
;


CREATE TABLE `productdocument` (
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `documentnode` varchar(255) NOT NULL COMMENT 'Document identification number. Foreign key to Document.DocumentNode.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productid`,`documentnode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products to related product documents.'
;


CREATE TABLE `productinventory` (
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `locationid` smallint(6) NOT NULL COMMENT 'Inventory location identification number. Foreign key to Location.LocationID. ',
  `shelf` varchar(10) NOT NULL COMMENT 'Storage compartment within an inventory location.',
  `bin` tinyint(3) unsigned NOT NULL COMMENT 'Storage container on a shelf in an inventory location.',
  `quantity` smallint(6) NOT NULL DEFAULT 0 COMMENT 'Quantity of products in the inventory location.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productid`,`locationid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product inventory information.'
;


CREATE TABLE `productlistpricehistory` (
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID',
  `startdate` datetime NOT NULL COMMENT 'List price start date.',
  `enddate` datetime DEFAULT NULL COMMENT 'List price end date',
  `listprice` decimal(19,4) NOT NULL COMMENT 'Product list price.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productid`,`startdate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Changes in the list price of a product over time.'
;


CREATE TABLE `productmodel` (
  `productmodelid` int(11) NOT NULL COMMENT 'Primary key for ProductModel records.',
  `name` varchar(100) NOT NULL COMMENT 'Product model description.',
  `catalogdescription` text DEFAULT NULL COMMENT 'Detailed product catalog information in xml format.',
  `instructions` text DEFAULT NULL COMMENT 'Manufacturing instructions in xml format.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productmodelid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product model classification.'
;


CREATE TABLE `productmodelillustration` (
  `productmodelid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductModel.ProductModelID.',
  `illustrationid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Illustration.IllustrationID.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productmodelid`,`illustrationid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping product models and illustrations.'
;


CREATE TABLE `productmodelproductdescriptionculture` (
  `productmodelid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductModel.ProductModelID.',
  `productdescriptionid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to ProductDescription.ProductDescriptionID.',
  `cultureid` char(6) NOT NULL COMMENT 'Culture identification number. Foreign key to Culture.CultureID.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productmodelid`,`productdescriptionid`,`cultureid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping product descriptions and the language the description is written in.'
;


CREATE TABLE `productphoto` (
  `productphotoid` int(11) NOT NULL COMMENT 'Primary key for ProductPhoto records.',
  `thumbnailphoto` longblob DEFAULT NULL COMMENT 'Small image of the product.',
  `thumbnailphotofilename` varchar(50) DEFAULT NULL COMMENT 'Small image file name.',
  `largephoto` longblob DEFAULT NULL COMMENT 'Large image of the product.',
  `largephotofilename` varchar(50) DEFAULT NULL COMMENT 'Large image file name.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productphotoid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product images.'
;


CREATE TABLE `productproductphoto` (
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `productphotoid` int(11) NOT NULL COMMENT 'Product photo identification number. Foreign key to ProductPhoto.ProductPhotoID.',
  `primary` tinyint(1) NOT NULL DEFAULT 0 COMMENT '0 = Photo is not the principal image. 1 = Photo is the principal image.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productid`,`productphotoid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products and product photos.'
;


CREATE TABLE `productreview` (
  `productreviewid` int(11) NOT NULL COMMENT 'Primary key for ProductReview records.',
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `reviewername` varchar(100) NOT NULL COMMENT 'Name of the reviewer.',
  `reviewdate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date review was submitted.',
  `emailaddress` varchar(50) NOT NULL COMMENT 'Reviewer''s e-mail address.',
  `rating` int(11) NOT NULL COMMENT 'Product rating given by the reviewer. Scale is 1 to 5 with 5 as the highest rating.',
  `comments` varchar(3850) DEFAULT NULL COMMENT 'Reviewer''s comments',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productreviewid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customer reviews of products they have purchased.'
;


CREATE TABLE `products` (
  `productid` int(11) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`productid`),
  UNIQUE KEY `products_productid_key` (`productid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `productsubcategory` (
  `productsubcategoryid` int(11) NOT NULL COMMENT 'Primary key for ProductSubcategory records.',
  `productcategoryid` int(11) NOT NULL COMMENT 'Product category identification number. Foreign key to ProductCategory.ProductCategoryID.',
  `name` varchar(100) NOT NULL COMMENT 'Subcategory description.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productsubcategoryid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Product subcategories. See ProductCategory table.'
;


CREATE TABLE `productvendor` (
  `productid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Product.ProductID.',
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Vendor.BusinessEntityID.',
  `averageleadtime` int(11) NOT NULL COMMENT 'The average span of time (in days) between placing an order with the vendor and receiving the purchased product.',
  `standardprice` decimal(19,4) NOT NULL COMMENT 'The vendor''s usual selling price.',
  `lastreceiptcost` decimal(19,4) DEFAULT NULL COMMENT 'The selling price when last purchased.',
  `lastreceiptdate` datetime DEFAULT NULL COMMENT 'Date the product was last received by the vendor.',
  `minorderqty` int(11) NOT NULL COMMENT 'The maximum quantity that should be ordered.',
  `maxorderqty` int(11) NOT NULL COMMENT 'The minimum quantity that should be ordered.',
  `onorderqty` int(11) DEFAULT NULL COMMENT 'The quantity currently on order.',
  `unitmeasurecode` char(3) NOT NULL COMMENT 'The product''s unit of measure.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`productid`,`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping vendors with the products they supply.'
;


CREATE TABLE `prof` (
  `prof_id` int(11) NOT NULL DEFAULT 0,
  `popularity` varchar(45) DEFAULT NULL,
  `teachingability` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`prof_id`),
  KEY `prof_popularity` (`popularity`),
  KEY `prof_teachingability` (`teachingability`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `propagated_account_002` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `account_id` int(11) NOT NULL DEFAULT 0,
  `district_id` int(11) DEFAULT 0,
  `frequency` varchar(18) DEFAULT '',
  `date` date DEFAULT NULL,
  KEY `ix_account_002` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_card_009` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `card_id` int(11) NOT NULL DEFAULT 0,
  `disp_id` int(11) DEFAULT NULL,
  `type` varchar(7) DEFAULT NULL,
  `issued` date DEFAULT NULL,
  KEY `ix_card_009` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_client_007` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `client_id` int(11) NOT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `district_id` int(11) DEFAULT NULL,
  KEY `ix_client_007` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_client_008` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `client_id` int(11) NOT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `district_id` int(11) DEFAULT NULL,
  KEY `ix_client_008` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_disp_004` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `disp_id` int(11) NOT NULL,
  `client_id` int(11) DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  `type` varchar(9) DEFAULT NULL,
  KEY `ix_disp_004` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_district_003` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `district_id` int(11) NOT NULL DEFAULT 0,
  `A2` varchar(19) DEFAULT NULL,
  `A3` varchar(15) DEFAULT NULL,
  `A4` int(20) DEFAULT NULL,
  `A5` int(11) DEFAULT NULL,
  `A6` int(11) DEFAULT NULL,
  `A7` int(11) DEFAULT NULL,
  `A8` int(6) DEFAULT NULL,
  `A9` int(11) DEFAULT NULL,
  `A10` decimal(4,1) DEFAULT NULL,
  `A11` int(11) DEFAULT NULL,
  `A12` decimal(4,1) DEFAULT NULL,
  `A13` decimal(3,2) DEFAULT NULL,
  `A14` int(11) DEFAULT NULL,
  `A15` int(5) DEFAULT NULL,
  `A16` int(11) DEFAULT NULL,
  KEY `ix_district_003` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_loan_001` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `loan_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `payments` decimal(6,2) DEFAULT NULL,
  `status` varchar(1) DEFAULT NULL,
  KEY `ix_loan_001` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_order_005` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `order_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) DEFAULT NULL,
  `bank_to` varchar(2) DEFAULT NULL,
  `account_to` int(11) DEFAULT NULL,
  `amount` decimal(6,1) DEFAULT NULL,
  `k_symbol` varchar(8) DEFAULT NULL,
  KEY `ix_order_005` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `propagated_trans_006` (
  `propagated_id1` int(11) NOT NULL DEFAULT 0,
  `propagated_date` date DEFAULT NULL,
  `propagated_target` varchar(1) DEFAULT NULL,
  `propagated_fold` double(17,0) NOT NULL DEFAULT 0,
  `trans_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) DEFAULT 0,
  `date` date DEFAULT NULL,
  `type` varchar(6) DEFAULT NULL,
  `operation` varchar(14) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `balance` int(11) DEFAULT NULL,
  `k_symbol` varchar(11) DEFAULT NULL,
  `bank` varchar(2) DEFAULT NULL,
  `account` int(11) unsigned DEFAULT NULL,
  KEY `ix_trans_006` (`propagated_id1`,`propagated_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `provider` (
  `provider_no` int(11) NOT NULL,
  `provider_name` varchar(15) NOT NULL,
  `street` varchar(15) NOT NULL,
  `city` varchar(15) NOT NULL,
  `state_prov` char(2) NOT NULL,
  `mail_code` char(10) NOT NULL,
  `country` char(2) NOT NULL,
  `phone_no` char(13) NOT NULL,
  `issue_dt` datetime NOT NULL,
  `expr_dt` datetime NOT NULL,
  `region_no` int(11) NOT NULL,
  `provider_code` char(2) NOT NULL,
  PRIMARY KEY (`provider_no`),
  KEY `provider_region_no` (`region_no`),
  CONSTRAINT `provider_ibfk_1` FOREIGN KEY (`region_no`) REFERENCES `region` (`region_no`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `purchaseorderdetail` (
  `purchaseorderid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to PurchaseOrderHeader.PurchaseOrderID.',
  `purchaseorderdetailid` int(11) NOT NULL COMMENT 'Primary key. One line number per purchased product.',
  `duedate` datetime NOT NULL COMMENT 'Date the product is expected to be received.',
  `orderqty` smallint(6) NOT NULL COMMENT 'Quantity ordered.',
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `unitprice` decimal(19,4) NOT NULL COMMENT 'Vendor''s selling price of a single product.',
  `linetotal` decimal(19,4) NOT NULL COMMENT 'Per product subtotal. Computed as OrderQty * UnitPrice.',
  `receivedqty` decimal(8,2) NOT NULL COMMENT 'Quantity actually received from the vendor.',
  `rejectedqty` decimal(8,2) NOT NULL COMMENT 'Quantity rejected during inspection.',
  `stockedqty` decimal(9,2) NOT NULL COMMENT 'Quantity accepted into inventory. Computed as ReceivedQty - RejectedQty.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`purchaseorderdetailid`,`purchaseorderid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Individual products associated with a specific purchase order. See PurchaseOrderHeader.'
;


CREATE TABLE `purchaseorderheader` (
  `purchaseorderid` int(11) NOT NULL COMMENT 'Primary key.',
  `revisionnumber` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Incremental number to track changes to the purchase order over time.',
  `status` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Order current status. 1 = Pending; 2 = Approved; 3 = Rejected; 4 = Complete',
  `employeeid` int(11) NOT NULL COMMENT 'Employee who created the purchase order. Foreign key to Employee.BusinessEntityID.',
  `vendorid` int(11) NOT NULL COMMENT 'Vendor with whom the purchase order is placed. Foreign key to Vendor.BusinessEntityID.',
  `shipmethodid` int(11) NOT NULL COMMENT 'Shipping method. Foreign key to ShipMethod.ShipMethodID.',
  `orderdate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Purchase order creation date.',
  `shipdate` datetime DEFAULT NULL COMMENT 'Estimated shipment date from the vendor.',
  `subtotal` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Purchase order subtotal. Computed as SUM(PurchaseOrderDetail.LineTotal)for the appropriate PurchaseOrderID.',
  `taxamt` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax amount.',
  `freight` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping cost.',
  `totaldue` decimal(19,4) NOT NULL COMMENT 'Total due to vendor. Computed as Subtotal + TaxAmt + Freight.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`purchaseorderid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='General purchase order information. See PurchaseOrderDetail.'
;


CREATE TABLE `quality` (
  `name` varchar(128) NOT NULL,
  `type` varchar(128) NOT NULL DEFAULT 'DataProperty',
  `formula` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `datatype` varchar(128) NOT NULL DEFAULT 'undefined',
  `min` float DEFAULT NULL,
  `max` float DEFAULT NULL,
  `unit` varchar(32) DEFAULT NULL,
  `priority` int(11) NOT NULL DEFAULT 9999,
  `showonline` enum('true','false') NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `region` (
  `region_no` int(11) NOT NULL,
  `region_name` varchar(15) NOT NULL,
  `street` varchar(15) NOT NULL,
  `city` varchar(15) NOT NULL,
  `state_prov` char(2) NOT NULL,
  `country` char(2) NOT NULL,
  `mail_code` char(10) NOT NULL,
  `phone_no` char(13) NOT NULL,
  `region_code` char(2) NOT NULL,
  PRIMARY KEY (`region_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `registration` (
  `course_id` int(11) NOT NULL DEFAULT 0,
  `student_id` int(11) NOT NULL DEFAULT 0,
  `grade` varchar(45) NOT NULL,
  `sat` varchar(45) NOT NULL,
  PRIMARY KEY (`course_id`,`student_id`),
  KEY `registration_sat` (`sat`),
  KEY `registration_grade` (`grade`),
  KEY `registration_student_id` (`student_id`),
  KEY `registration_course_id` (`course_id`),
  CONSTRAINT `FK_registration_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_registration_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `resource_type` (
  `id` int(11) NOT NULL,
  `resource_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`,`resource_type`),
  CONSTRAINT `resource_type_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `run` (
  `rid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `uploader` int(10) DEFAULT NULL,
  `parent` int(10) unsigned DEFAULT NULL,
  `setup` int(10) unsigned NOT NULL DEFAULT 0,
  `task_id` int(10) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `status` varchar(64) NOT NULL,
  `priority` tinyint(8) NOT NULL DEFAULT 10,
  `error` varchar(512) DEFAULT NULL,
  `warning` varchar(512) DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `processed` datetime DEFAULT NULL,
  `experiment` int(10) unsigned DEFAULT NULL,
  `runner` varchar(16) DEFAULT NULL,
  `machine` varchar(64) DEFAULT NULL,
  `visibility` varchar(128) NOT NULL DEFAULT 'public',
  PRIMARY KEY (`rid`),
  KEY `run_setup_task_id` (`setup`,`task_id`),
  KEY `run_setup_uploader` (`setup`,`uploader`),
  KEY `run_task_id_uploader` (`task_id`,`uploader`),
  KEY `run_task_id_uploader_start_time` (`task_id`,`uploader`,`start_time`),
  CONSTRAINT `run_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `runfile` (
  `did` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `source` int(16) NOT NULL,
  `field` varchar(128) NOT NULL,
  `name` varchar(128) NOT NULL,
  `format` varchar(128) NOT NULL,
  `file_id` int(16) NOT NULL,
  PRIMARY KEY (`did`),
  KEY `runfile_source_field` (`source`,`field`),
  CONSTRAINT `runfile_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `salesorderdetail` (
  `salesorderid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesOrderHeader.SalesOrderID.',
  `salesorderdetailid` int(11) NOT NULL COMMENT 'Primary key. One incremental unique number per product sold.',
  `carriertrackingnumber` varchar(25) DEFAULT NULL COMMENT 'Shipment tracking number supplied by the shipper.',
  `orderqty` smallint(6) NOT NULL COMMENT 'Quantity ordered per product.',
  `productid` int(11) NOT NULL COMMENT 'Product sold to customer. Foreign key to Product.ProductID.',
  `specialofferid` int(11) NOT NULL COMMENT 'Promotional code. Foreign key to SpecialOffer.SpecialOfferID.',
  `unitprice` decimal(19,4) NOT NULL COMMENT 'Selling price of a single product.',
  `unitpricediscount` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Discount amount.',
  `linetotal` decimal(38,6) NOT NULL COMMENT 'Per product subtotal. Computed as UnitPrice * (1 - UnitPriceDiscount) * OrderQty.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`salesorderdetailid`,`salesorderid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Individual products associated with a specific sales order. See SalesOrderHeader.'
;


CREATE TABLE `salesorderheader` (
  `salesorderid` int(11) NOT NULL COMMENT 'Primary key.',
  `revisionnumber` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT 'Incremental number to track changes to the sales order over time.',
  `orderdate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Dates the sales order was created.',
  `duedate` datetime NOT NULL COMMENT 'Date the order is due to the customer.',
  `shipdate` datetime DEFAULT NULL COMMENT 'Date the order was shipped to the customer.',
  `status` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT 'Order current status. 1 = In process; 2 = Approved; 3 = Backordered; 4 = Rejected; 5 = Shipped; 6 = Cancelled',
  `onlineorderflag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Order placed by sales person. 1 = Order placed online by customer.',
  `salesordernumber` varchar(25) NOT NULL COMMENT 'Unique sales order identification number.',
  `purchaseordernumber` varchar(50) DEFAULT NULL COMMENT 'Customer purchase order number reference. ',
  `accountnumber` varchar(30) DEFAULT NULL COMMENT 'Financial accounting number reference.',
  `customerid` int(11) NOT NULL COMMENT 'Customer identification number. Foreign key to Customer.BusinessEntityID.',
  `salespersonid` int(11) DEFAULT NULL COMMENT 'Sales person who created the sales order. Foreign key to SalesPerson.BusinessEntityID.',
  `territoryid` int(11) DEFAULT NULL COMMENT 'Territory in which the sale was made. Foreign key to SalesTerritory.SalesTerritoryID.',
  `billtoaddressid` int(11) NOT NULL COMMENT 'Customer billing address. Foreign key to Address.AddressID.',
  `shiptoaddressid` int(11) NOT NULL COMMENT 'Customer shipping address. Foreign key to Address.AddressID.',
  `shipmethodid` int(11) NOT NULL COMMENT 'Shipping method. Foreign key to ShipMethod.ShipMethodID.',
  `creditcardid` int(11) DEFAULT NULL COMMENT 'Credit card identification number. Foreign key to CreditCard.CreditCardID.',
  `creditcardapprovalcode` varchar(15) DEFAULT NULL COMMENT 'Approval code provided by the credit card company.',
  `currencyrateid` int(11) DEFAULT NULL COMMENT 'Currency exchange rate used. Foreign key to CurrencyRate.CurrencyRateID.',
  `subtotal` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales subtotal. Computed as SUM(SalesOrderDetail.LineTotal)for the appropriate SalesOrderID.',
  `taxamt` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax amount.',
  `freight` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping cost.',
  `totaldue` decimal(19,4) NOT NULL COMMENT 'Total due from customer. Computed as Subtotal + TaxAmt + Freight.',
  `comment` varchar(128) DEFAULT NULL COMMENT 'Sales representative comments.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`salesorderid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='General sales order information.'
;


CREATE TABLE `salesorderheadersalesreason` (
  `salesorderid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesOrderHeader.SalesOrderID.',
  `salesreasonid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to SalesReason.SalesReasonID.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`salesorderid`,`salesreasonid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping sales orders to sales reason codes.'
;


CREATE TABLE `salesperson` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key for SalesPerson records. Foreign key to Employee.BusinessEntityID',
  `territoryid` int(11) DEFAULT NULL COMMENT 'Territory currently assigned to. Foreign key to SalesTerritory.SalesTerritoryID.',
  `salesquota` decimal(19,4) DEFAULT NULL COMMENT 'Projected yearly sales.',
  `bonus` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Bonus due if quota is met.',
  `commissionpct` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Commision percent received per sale.',
  `salesytd` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales total year to date.',
  `saleslastyear` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales total of previous year.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales representative current information.'
;


CREATE TABLE `salespersonquotahistory` (
  `businessentityid` int(11) NOT NULL COMMENT 'Sales person identification number. Foreign key to SalesPerson.BusinessEntityID.',
  `quotadate` datetime NOT NULL COMMENT 'Sales quota date.',
  `salesquota` decimal(19,4) NOT NULL COMMENT 'Sales quota amount.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`quotadate`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales performance tracking.'
;


CREATE TABLE `salesreason` (
  `salesreasonid` int(11) NOT NULL COMMENT 'Primary key for SalesReason records.',
  `name` varchar(100) NOT NULL COMMENT 'Sales reason description.',
  `reasontype` varchar(100) NOT NULL COMMENT 'Category the sales reason belongs to.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`salesreasonid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Lookup table of customer purchase reasons.'
;


CREATE TABLE `salestaxrate` (
  `salestaxrateid` int(11) NOT NULL COMMENT 'Primary key for SalesTaxRate records.',
  `stateprovinceid` int(11) NOT NULL COMMENT 'State, province, or country/region the sales tax applies to.',
  `taxtype` tinyint(3) unsigned NOT NULL COMMENT '1 = Tax applied to retail transactions, 2 = Tax applied to wholesale transactions, 3 = Tax applied to all sales (retail and wholesale) transactions.',
  `taxrate` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Tax rate amount.',
  `name` varchar(100) NOT NULL COMMENT 'Tax rate description.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`salestaxrateid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Tax rate lookup table.'
;


CREATE TABLE `salesterritory` (
  `territoryid` int(11) NOT NULL COMMENT 'Primary key for SalesTerritory records.',
  `name` varchar(100) NOT NULL COMMENT 'Sales territory description',
  `countryregioncode` varchar(3) NOT NULL COMMENT 'ISO standard country or region code. Foreign key to CountryRegion.CountryRegionCode. ',
  `group` varchar(50) NOT NULL COMMENT 'Geographic area to which the sales territory belong.',
  `salesytd` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales in the territory year to date.',
  `saleslastyear` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Sales in the territory the previous year.',
  `costytd` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Business costs in the territory year to date.',
  `costlastyear` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Business costs in the territory the previous year.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`territoryid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales territory lookup table.'
;


CREATE TABLE `salesterritoryhistory` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key. The sales rep.  Foreign key to SalesPerson.BusinessEntityID.',
  `territoryid` int(11) NOT NULL COMMENT 'Primary key. Territory identification number. Foreign key to SalesTerritory.SalesTerritoryID.',
  `startdate` datetime NOT NULL COMMENT 'Primary key. Date the sales representive started work in the territory.',
  `enddate` datetime DEFAULT NULL COMMENT 'Date the sales representative left work in the territory.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`,`startdate`,`territoryid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sales representative transfers to other sales territories.'
;


CREATE TABLE `sample_submission` (
  `device_id` bigint(20) NOT NULL,
  `F23-` float DEFAULT NULL,
  `F24-26` float DEFAULT NULL,
  `F27-28` float DEFAULT NULL,
  `F29-32` float DEFAULT NULL,
  `F33-42` float DEFAULT NULL,
  `F43+` float DEFAULT NULL,
  `M22-` float DEFAULT NULL,
  `M23-26` float DEFAULT NULL,
  `M27-28` float DEFAULT NULL,
  `M29-31` float DEFAULT NULL,
  `M32-38` float DEFAULT NULL,
  `M39+` float DEFAULT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sandbox` (
  `propagated_target` int(11) NOT NULL,
  `feature` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `schedule` (
  `sid` int(8) NOT NULL,
  `task_id` int(8) NOT NULL,
  `experiment` varchar(128) NOT NULL DEFAULT '',
  `active` enum('true','false') NOT NULL DEFAULT 'true',
  `last_assigned` datetime DEFAULT NULL,
  `ttid` int(11) NOT NULL,
  `dependencies` varchar(128) NOT NULL,
  `setup_string` mediumtext NOT NULL,
  PRIMARY KEY (`sid`,`task_id`),
  KEY `schedule_dependencies_active_ttid_last_assigned` (`dependencies`,`active`,`ttid`,`last_assigned`),
  KEY `schedule_sid_task_id_active` (`sid`,`task_id`,`active`),
  KEY `schedule_sid_task_id_active_last_assigned` (`sid`,`task_id`,`active`,`last_assigned`),
  KEY `schedule_task_id` (`task_id`),
  KEY `schedule_ttid` (`ttid`),
  CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `schedule_ibfk_2` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `scrapreason` (
  `scrapreasonid` smallint(6) NOT NULL COMMENT 'Primary key for ScrapReason records.',
  `name` varchar(100) NOT NULL COMMENT 'Failure description.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`scrapreasonid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Manufacturing failure reasons lookup table.'
;


CREATE TABLE `seafarers` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `seafarers_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `setup_differences` (
  `sidA` int(10) unsigned NOT NULL,
  `sidB` int(10) unsigned NOT NULL,
  `task_id` int(10) NOT NULL,
  `task_size` int(10) NOT NULL,
  `differences` int(10) NOT NULL,
  PRIMARY KEY (`sidA`,`sidB`,`task_id`),
  KEY `setup_differences_sidB` (`sidB`),
  KEY `setup_differences_task_id` (`task_id`),
  CONSTRAINT `setup_differences_ibfk_1` FOREIGN KEY (`sidA`) REFERENCES `algorithm_setup` (`sid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `setup_differences_ibfk_2` FOREIGN KEY (`sidB`) REFERENCES `algorithm_setup` (`sid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `setup_differences_ibfk_3` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `severity_type` (
  `id` int(11) NOT NULL,
  `severity_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `severity_type_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `shift` (
  `shiftid` tinyint(3) unsigned NOT NULL COMMENT 'Primary key for Shift records.',
  `name` varchar(100) NOT NULL COMMENT 'Shift description.',
  `starttime` time NOT NULL COMMENT 'Shift start time.',
  `endtime` time NOT NULL COMMENT 'Shift end time.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`shiftid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Work shift lookup table.'
;


CREATE TABLE `shipmethod` (
  `shipmethodid` int(11) NOT NULL COMMENT 'Primary key for ShipMethod records.',
  `name` varchar(100) NOT NULL COMMENT 'Shipping company name.',
  `shipbase` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Minimum shipping charge.',
  `shiprate` decimal(19,4) NOT NULL DEFAULT 0.0000 COMMENT 'Shipping charge per pound.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`shipmethodid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Shipping company lookup table.'
;


CREATE TABLE `shoppingcartitem` (
  `shoppingcartitemid` int(11) NOT NULL COMMENT 'Primary key for ShoppingCartItem records.',
  `shoppingcartid` varchar(50) NOT NULL COMMENT 'Shopping cart identification number.',
  `quantity` int(11) NOT NULL DEFAULT 1 COMMENT 'Product quantity ordered.',
  `productid` int(11) NOT NULL COMMENT 'Product ordered. Foreign key to Product.ProductID.',
  `datecreated` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date the time the record was created.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`shoppingcartitemid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Contains online customer orders until the order is submitted or cancelled.'
;


CREATE TABLE `soldiers` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `soldiers_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `specialoffer` (
  `specialofferid` int(11) NOT NULL COMMENT 'Primary key for SpecialOffer records.',
  `description` varchar(255) NOT NULL COMMENT 'Discount description.',
  `discountpct` decimal(10,4) NOT NULL DEFAULT 0.0000 COMMENT 'Discount precentage.',
  `type` varchar(50) NOT NULL COMMENT 'Discount type category.',
  `category` varchar(50) NOT NULL COMMENT 'Group the discount applies to such as Reseller or Customer.',
  `startdate` datetime NOT NULL COMMENT 'Discount start date.',
  `enddate` datetime NOT NULL COMMENT 'Discount end date.',
  `minqty` int(11) NOT NULL DEFAULT 0 COMMENT 'Minimum discount percent allowed.',
  `maxqty` int(11) DEFAULT NULL COMMENT 'Maximum discount percent allowed.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`specialofferid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Sale discounts lookup table.'
;


CREATE TABLE `specialofferproduct` (
  `specialofferid` int(11) NOT NULL COMMENT 'Primary key for SpecialOfferProduct records.',
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`specialofferid`,`productid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Cross-reference table mapping products to special offer discounts.'
;


CREATE TABLE `statement` (
  `statement_no` int(11) NOT NULL,
  `member_no` int(11) NOT NULL,
  `statement_dt` datetime NOT NULL,
  `due_dt` datetime NOT NULL,
  `statement_amt` decimal(19,4) NOT NULL,
  `statement_code` char(2) NOT NULL,
  PRIMARY KEY (`statement_no`),
  KEY `statement_member_no` (`member_no`),
  CONSTRAINT `statement_ibfk_1` FOREIGN KEY (`member_no`) REFERENCES `member` (`member_no`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `stateprovince` (
  `stateprovinceid` int(11) NOT NULL COMMENT 'Primary key for StateProvince records.',
  `stateprovincecode` char(3) NOT NULL COMMENT 'ISO standard state or province code.',
  `countryregioncode` varchar(3) NOT NULL COMMENT 'ISO standard country or region code. Foreign key to CountryRegion.CountryRegionCode. ',
  `isonlystateprovinceflag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = StateProvinceCode exists. 1 = StateProvinceCode unavailable, using CountryRegionCode.',
  `name` varchar(100) NOT NULL COMMENT 'State or province description.',
  `territoryid` int(11) NOT NULL COMMENT 'ID of the territory in which the state or province is located. Foreign key to SalesTerritory.SalesTerritoryID.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`stateprovinceid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='State and province lookup table.'
;


CREATE TABLE `station` (
  `station_nbr` int(11) NOT NULL,
  PRIMARY KEY (`station_nbr`),
  UNIQUE KEY `station_station_nbr_key` (`station_nbr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `status` (
  `status_code` char(2) NOT NULL,
  `status_desc` varchar(31) NOT NULL,
  PRIMARY KEY (`status_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `store` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Customer.BusinessEntityID.',
  `name` varchar(100) NOT NULL COMMENT 'Name of the store.',
  `salespersonid` int(11) DEFAULT NULL COMMENT 'ID of the sales person assigned to the customer. Foreign key to SalesPerson.BusinessEntityID.',
  `demographics` text DEFAULT NULL COMMENT 'Demographic informationg about the store such as the number of employees, annual sales and store type.',
  `rowguid` varchar(64) NOT NULL COMMENT 'ROWGUIDCOL number uniquely identifying the record. Used to support a merge replication sample.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Customers (resellers) of Adventure Works products.'
;


CREATE TABLE `stores` (
  `Store` int(11) NOT NULL,
  `Type` varchar(255) DEFAULT NULL,
  `Size` int(11) DEFAULT NULL,
  PRIMARY KEY (`Store`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `student` (
  `student_id` int(11) NOT NULL DEFAULT 0,
  `intelligence` varchar(45) DEFAULT NULL,
  `ranking` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  KEY `student_intelligence` (`intelligence`),
  KEY `student_ranking` (`ranking`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `students` (
  `id` int(10) unsigned NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  `email` varchar(32) DEFAULT NULL,
  `password` varchar(16) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `succ` (
  `tm1` int(11) NOT NULL,
  `tm2` int(11) NOT NULL,
  PRIMARY KEY (`tm1`,`tm2`),
  KEY `tm1` (`tm1`),
  KEY `tm2` (`tm2`),
  CONSTRAINT `succ_ibfk_1` FOREIGN KEY (`tm1`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `succ_ibfk_2` FOREIGN KEY (`tm2`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `tags` (
  `Id` int(11) NOT NULL,
  `TagName` varchar(255) DEFAULT NULL,
  `Count` int(11) DEFAULT NULL,
  `ExcerptPostId` int(11) DEFAULT NULL,
  `WikiPostId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `tags_ExcerptPostId_fkey` (`ExcerptPostId`),
  CONSTRAINT `tags_ExcerptPostId_fkey` FOREIGN KEY (`ExcerptPostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `id` int(11) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `fault_severity` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `target_id_key` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task` (
  `task_id` int(10) NOT NULL AUTO_INCREMENT,
  `ttid` int(10) NOT NULL,
  `creator` int(10) DEFAULT NULL,
  `creation_date` datetime DEFAULT NULL,
  PRIMARY KEY (`task_id`),
  KEY `task_ttid` (`ttid`),
  CONSTRAINT `task_ibfk_1` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_inputs` (
  `task_id` int(10) NOT NULL,
  `input` varchar(64) NOT NULL,
  `value` mediumtext NOT NULL,
  PRIMARY KEY (`task_id`,`input`),
  UNIQUE KEY `task_inputs_task_id_input_value` (`task_id`,`input`,`value`(16)),
  CONSTRAINT `task_inputs_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_io_types` (
  `name` varchar(64) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_type` (
  `ttid` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `description` mediumtext NOT NULL,
  `creator` varchar(128) NOT NULL,
  `contributors` mediumtext DEFAULT NULL,
  `creationDate` datetime NOT NULL,
  PRIMARY KEY (`ttid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_type_inout` (
  `ttid` int(10) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(64) NOT NULL,
  `io` enum('input','output') NOT NULL,
  `requirement` enum('required','optional','hidden') NOT NULL,
  `description` varchar(256) NOT NULL,
  `order` int(8) NOT NULL,
  `template_api` text DEFAULT NULL,
  `template_search` text DEFAULT NULL,
  PRIMARY KEY (`ttid`,`name`,`type`),
  KEY `task_type_inout_type` (`type`),
  CONSTRAINT `task_type_inout_ibfk_1` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `task_type_inout_ibfk_2` FOREIGN KEY (`type`) REFERENCES `task_io_types` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `teachers` (
  `id` int(10) unsigned NOT NULL,
  `name` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `time` (
  `tm` int(11) NOT NULL,
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `tm001_eod_relay` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm001_eod_relay_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm001_eod_relay_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm002_battov_temp` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm002_battov_temp_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm002_battov_temp_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm004_eoc_signaled` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm004_eoc_signaled_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm004_eoc_signaled_ibfk_2` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm007_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm007_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm007_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm009_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm009_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm009_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm011_eod_override` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm011_eod_override_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm011_eod_override_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm013_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm013_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm013_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm015_eod_signaled` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm015_eod_signaled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm015_eod_signaled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm017_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm017_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm017_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm018_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm018_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm018_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm021_eoc_disabled` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm021_eoc_disabled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm021_eoc_disabled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm022_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm022_switch_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm022_switch_ibfk_2` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm029_ovt_disabled` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm029_ovt_disabled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm029_ovt_disabled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm031_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm031_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm031_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm038_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm038_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm038_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm039_eod_disabled` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm039_eod_disabled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm039_eod_disabled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm040_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm040_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm040_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm042_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm042_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm042_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm043_switch` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm043_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm043_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm054_supply_1a` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm054_supply_1a_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm054_supply_1a_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm055_supply_1b` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm055_supply_1b_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm055_supply_1b_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm057_supply_2c` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm057_supply_2c_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm057_supply_2c_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm058_asr_or_switch_10` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm058_asr_or_switch_10_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm058_asr_or_switch_10_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm070_supply_3c` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm070_supply_3c_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm070_supply_3c_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm071_asr_or_switch_20` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm071_asr_or_switch_20_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm071_asr_or_switch_20_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm211_bus_voltage` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm211_bus_voltage_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm211_bus_voltage_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm220_supply_1c` (
  `class` varchar(8) NOT NULL,
  `tm` int(11) NOT NULL,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm220_supply_1c_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm220_supply_1c_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm222_charging` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm222_charging_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm222_charging_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm257_battery_voltage` (
  `class` varchar(8) NOT NULL DEFAULT '',
  `tm` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`class`,`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm257_battery_voltage_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm257_battery_voltage_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `total` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `total_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `trace` (
  `run_id` int(10) unsigned NOT NULL,
  `repeat` int(11) NOT NULL,
  `fold` int(11) NOT NULL,
  `iteration` int(11) NOT NULL,
  `setup_string` mediumtext NOT NULL,
  `evaluation` varchar(265) NOT NULL,
  `selected` enum('true','false') NOT NULL,
  PRIMARY KEY (`run_id`,`repeat`,`fold`,`iteration`),
  CONSTRAINT `trace_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `run` (`rid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `train` (
  `date` date NOT NULL,
  `store_nbr` int(11) NOT NULL,
  `item_nbr` int(11) NOT NULL,
  `units` int(11) DEFAULT NULL,
  PRIMARY KEY (`store_nbr`,`date`,`item_nbr`),
  CONSTRAINT `train_store_nbr_fkey` FOREIGN KEY (`store_nbr`) REFERENCES `key` (`store_nbr`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `trains` (
  `id` int(11) NOT NULL,
  `direction` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `transactionhistory` (
  `transactionid` int(11) NOT NULL COMMENT 'Primary key for TransactionHistory records.',
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `referenceorderid` int(11) NOT NULL COMMENT 'Purchase order, sales order, or work order identification number.',
  `referenceorderlineid` int(11) NOT NULL DEFAULT 0 COMMENT 'Line number associated with the purchase order, sales order, or work order.',
  `transactiondate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time of the transaction.',
  `transactiontype` char(1) NOT NULL COMMENT 'W = WorkOrder, S = SalesOrder, P = PurchaseOrder',
  `quantity` int(11) NOT NULL COMMENT 'Product quantity.',
  `actualcost` decimal(19,4) NOT NULL COMMENT 'Product cost.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`transactionid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Record of each purchase order, sales order, or work order transaction year to date.'
;


CREATE TABLE `transactionhistoryarchive` (
  `transactionid` int(11) NOT NULL COMMENT 'Primary key for TransactionHistoryArchive records.',
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `referenceorderid` int(11) NOT NULL COMMENT 'Purchase order, sales order, or work order identification number.',
  `referenceorderlineid` int(11) NOT NULL DEFAULT 0 COMMENT 'Line number associated with the purchase order, sales order, or work order.',
  `transactiondate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time of the transaction.',
  `transactiontype` char(1) NOT NULL COMMENT 'W = Work Order, S = Sales Order, P = Purchase Order',
  `quantity` int(11) NOT NULL COMMENT 'Product quantity.',
  `actualcost` decimal(19,4) NOT NULL COMMENT 'Product cost.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`transactionid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Transactions for previous years.'
;


CREATE TABLE `transactions` (
  `date` date DEFAULT NULL,
  `time` time DEFAULT NULL,
  `customerid` int(11) DEFAULT NULL,
  `cardid` int(11) DEFAULT NULL,
  `gasstationid` int(11) DEFAULT NULL,
  `productid` int(11) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  KEY `transactions_large_staged_customerid_fkey` (`customerid`),
  KEY `transactions_large_staged_gasstationid_fkey` (`gasstationid`),
  KEY `transactions_large_staged_productid_fkey` (`productid`),
  CONSTRAINT `transactions_large_staged_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`customerid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transactions_large_staged_gasstationid_fkey` FOREIGN KEY (`gasstationid`) REFERENCES `gasstations` (`gasstationid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `transactions_large_staged_productid_fkey` FOREIGN KEY (`productid`) REFERENCES `products` (`productid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `transactions_1k` (
  `transactionid` int(11) NOT NULL AUTO_INCREMENT,
  `date` date DEFAULT NULL,
  `time` time DEFAULT NULL,
  `customerid` int(11) DEFAULT NULL,
  `cardid` int(11) DEFAULT NULL,
  `gasstationid` int(11) DEFAULT NULL,
  `productid` int(11) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `price` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`transactionid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `trfl` (
  `tf` varchar(1) NOT NULL,
  PRIMARY KEY (`tf`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `unitmeasure` (
  `unitmeasurecode` char(3) NOT NULL COMMENT 'Primary key.',
  `name` varchar(100) NOT NULL COMMENT 'Unit of measure description.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`unitmeasurecode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Unit of measure lookup table.'
;


CREATE TABLE `users` (
  `Id` int(11) NOT NULL,
  `Reputation` int(11) DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `DisplayName` varchar(255) DEFAULT NULL,
  `LastAccessDate` datetime DEFAULT NULL,
  `WebsiteUrl` varchar(255) DEFAULT NULL,
  `Location` varchar(255) DEFAULT NULL,
  `AboutMe` longtext DEFAULT NULL,
  `Views` int(11) DEFAULT NULL,
  `UpVotes` int(11) DEFAULT NULL,
  `DownVotes` int(11) DEFAULT NULL,
  `AccountId` int(11) DEFAULT NULL,
  `Age` int(11) DEFAULT NULL,
  `ProfileImageUrl` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `users_staged_Id_key` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `utube_attributes` (
  `id_states` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `value1` varchar(255) DEFAULT NULL,
  `value2` varchar(255) DEFAULT NULL,
  `direction` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_states`,`name`),
  KEY `id_states` (`id_states`),
  CONSTRAINT `utube_attributes_ibfk_1` FOREIGN KEY (`id_states`) REFERENCES `utube_states` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `utube_states` (
  `id` int(11) NOT NULL,
  `class` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `vendor` (
  `businessentityid` int(11) NOT NULL COMMENT 'Primary key for Vendor records.  Foreign key to BusinessEntity.BusinessEntityID',
  `accountnumber` varchar(30) NOT NULL COMMENT 'Vendor account (identification) number.',
  `name` varchar(100) NOT NULL COMMENT 'Company name.',
  `creditrating` tinyint(3) unsigned NOT NULL COMMENT '1 = Superior, 2 = Excellent, 3 = Above average, 4 = Average, 5 = Below average',
  `preferredvendorstatus` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Do not use if another vendor is available. 1 = Preferred over other vendors supplying the same product.',
  `activeflag` tinyint(1) NOT NULL DEFAULT 1 COMMENT '0 = Vendor no longer used. 1 = Vendor is actively used.',
  `purchasingwebserviceurl` varchar(1024) DEFAULT NULL COMMENT 'Vendor URL.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`businessentityid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Companies from whom Adventure Works Cycles purchases parts or other goods.'
;


CREATE TABLE `votes` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) DEFAULT NULL,
  `VoteTypeId` int(11) DEFAULT NULL,
  `CreationDate` date DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `BountyAmount` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `votes_stripped_UserId_fkey` (`UserId`),
  KEY `votes_stripped_PostId_fkey` (`PostId`),
  CONSTRAINT `votes_stripped_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `votes_stripped_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `voyages` (
  `artificial_id` char(12) DEFAULT NULL,
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) DEFAULT NULL,
  `boatname` varchar(50) DEFAULT NULL,
  `master` varchar(50) DEFAULT NULL,
  `tonnage` int(11) DEFAULT NULL,
  `type_of_boat` varchar(30) DEFAULT NULL,
  `built` varchar(15) DEFAULT NULL,
  `bought` varchar(15) DEFAULT NULL,
  `hired` varchar(15) DEFAULT NULL,
  `yard` char(1) DEFAULT NULL,
  `chamber` char(1) DEFAULT NULL,
  `departure_date` date DEFAULT NULL,
  `departure_harbour` varchar(30) DEFAULT NULL,
  `cape_arrival` date DEFAULT NULL,
  `cape_departure` date DEFAULT NULL,
  `cape_call` varchar(5) DEFAULT NULL,
  `arrival_date` date DEFAULT NULL,
  `arrival_harbour` varchar(30) DEFAULT NULL,
  `next_voyage` int(11) DEFAULT NULL,
  `particulars` text DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `weather` (
  `station_nbr` int(11) NOT NULL,
  `date` date NOT NULL,
  `tmax` int(11) DEFAULT NULL,
  `tmin` int(11) DEFAULT NULL,
  `tavg` int(11) DEFAULT NULL,
  `depart` int(11) DEFAULT NULL,
  `dewpoint` int(11) DEFAULT NULL,
  `wetbulb` int(11) DEFAULT NULL,
  `heat` int(11) DEFAULT NULL,
  `cool` int(11) DEFAULT NULL,
  `sunrise` time DEFAULT NULL,
  `sunset` time DEFAULT NULL,
  `codesum` varchar(255) DEFAULT NULL,
  `snowfall` float DEFAULT NULL,
  `preciptotal` float DEFAULT NULL,
  `stnpressure` float DEFAULT NULL,
  `sealevel` float DEFAULT NULL,
  `resultspeed` float DEFAULT NULL,
  `resultdir` int(11) DEFAULT NULL,
  `avgspeed` float DEFAULT NULL,
  PRIMARY KEY (`station_nbr`,`date`),
  CONSTRAINT `weather_station_nbr_fkey` FOREIGN KEY (`station_nbr`) REFERENCES `station` (`station_nbr`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `webpage` (
  `webpage_id` varchar(255) NOT NULL,
  `class_label` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`webpage_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `workorder` (
  `workorderid` int(11) NOT NULL COMMENT 'Primary key for WorkOrder records.',
  `productid` int(11) NOT NULL COMMENT 'Product identification number. Foreign key to Product.ProductID.',
  `orderqty` int(11) NOT NULL COMMENT 'Product quantity to build.',
  `stockedqty` int(11) NOT NULL COMMENT 'Quantity built and put in inventory.',
  `scrappedqty` smallint(6) NOT NULL COMMENT 'Quantity that failed inspection.',
  `startdate` datetime NOT NULL COMMENT 'Work order start date.',
  `enddate` datetime DEFAULT NULL COMMENT 'Work order end date.',
  `duedate` datetime NOT NULL COMMENT 'Work order due date.',
  `scrapreasonid` smallint(6) DEFAULT NULL COMMENT 'Reason for inspection failure.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`workorderid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Manufacturing work orders.'
;


CREATE TABLE `workorderrouting` (
  `workorderid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to WorkOrder.WorkOrderID.',
  `productid` int(11) NOT NULL COMMENT 'Primary key. Foreign key to Product.ProductID.',
  `operationsequence` smallint(6) NOT NULL COMMENT 'Primary key. Indicates the manufacturing process sequence.',
  `locationid` smallint(6) NOT NULL COMMENT 'Manufacturing location where the part is processed. Foreign key to Location.LocationID.',
  `scheduledstartdate` datetime NOT NULL COMMENT 'Planned manufacturing start date.',
  `scheduledenddate` datetime NOT NULL COMMENT 'Planned manufacturing end date.',
  `actualstartdate` datetime DEFAULT NULL COMMENT 'Actual start date.',
  `actualenddate` datetime DEFAULT NULL COMMENT 'Actual end date.',
  `actualresourcehrs` decimal(9,4) DEFAULT NULL COMMENT 'Number of manufacturing hours used.',
  `plannedcost` decimal(19,4) NOT NULL COMMENT 'Estimated manufacturing cost.',
  `actualcost` decimal(19,4) DEFAULT NULL COMMENT 'Actual manufacturing cost.',
  `modifieddate` timestamp NOT NULL DEFAULT current_timestamp() COMMENT 'Date and time the record was last updated.',
  PRIMARY KEY (`workorderid`,`productid`,`operationsequence`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Work order details.'
;


CREATE TABLE `yearmonth` (
  `customerid` int(11) NOT NULL,
  `date` int(11) NOT NULL,
  `consumption` decimal(12,2) DEFAULT NULL,
  PRIMARY KEY (`customerid`,`date`),
  CONSTRAINT `yearmonth_staged_customerid_fkey` FOREIGN KEY (`customerid`) REFERENCES `customers` (`customerid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

