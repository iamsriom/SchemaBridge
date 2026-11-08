-- Schema for database: Mondial

Country2Continent
;


Country_Full
;


Independent_Borders
;


Independent_Countries
;


Named_Borders
;


Symmetric_Borders
;


CREATE TABLE `borders` (
  `Country1` varchar(4) NOT NULL DEFAULT '',
  `Country2` varchar(4) NOT NULL DEFAULT '',
  `Length` float DEFAULT NULL,
  PRIMARY KEY (`Country1`,`Country2`),
  KEY `ix_city_Country2` (`Country2`) USING BTREE,
  KEY `ix_city_Country1` (`Country1`) USING BTREE,
  CONSTRAINT `borders_ibfk_1` FOREIGN KEY (`Country1`) REFERENCES `country` (`Code`),
  CONSTRAINT `borders_ibfk_2` FOREIGN KEY (`Country2`) REFERENCES `country` (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `city` (
  `Name` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  `Population` int(11) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  PRIMARY KEY (`Name`,`Province`),
  KEY `ix_city_Country` (`Country`) USING BTREE,
  KEY `ix_city_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `city_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `city_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `continent` (
  `Name` varchar(20) NOT NULL DEFAULT '',
  `Area` float DEFAULT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `country` (
  `Name` varchar(35) NOT NULL,
  `Code` varchar(4) NOT NULL DEFAULT '',
  `Capital` varchar(35) DEFAULT NULL,
  `Province` varchar(35) DEFAULT NULL,
  `Area` float DEFAULT NULL,
  `Population` int(11) DEFAULT NULL,
  PRIMARY KEY (`Code`),
  UNIQUE KEY `ix_county_Name` (`Name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `desert` (
  `Name` varchar(35) NOT NULL DEFAULT '',
  `Area` float DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `economy` (
  `Country` varchar(4) NOT NULL DEFAULT '',
  `GDP` float DEFAULT NULL,
  `Agriculture` float DEFAULT NULL,
  `Service` float DEFAULT NULL,
  `Industry` float DEFAULT NULL,
  `Inflation` float DEFAULT NULL,
  PRIMARY KEY (`Country`),
  CONSTRAINT `economy_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `encompasses` (
  `Country` varchar(4) NOT NULL,
  `Continent` varchar(20) NOT NULL,
  `Percentage` float DEFAULT NULL,
  PRIMARY KEY (`Country`,`Continent`),
  KEY `ix_encompasses_Continent` (`Continent`) USING BTREE,
  CONSTRAINT `encompasses_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `encompasses_ibfk_2` FOREIGN KEY (`Continent`) REFERENCES `continent` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ethnicGroup` (
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Name` varchar(50) NOT NULL DEFAULT '',
  `Percentage` float DEFAULT NULL,
  PRIMARY KEY (`Name`,`Country`),
  KEY `ix_ethnicGroup_Country` (`Country`) USING BTREE,
  CONSTRAINT `ethnicGroup_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_desert` (
  `Desert` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`Desert`),
  KEY `ix_geo_desert_Country` (`Country`) USING BTREE,
  KEY `ix_geo_desert_Desert` (`Desert`) USING BTREE,
  KEY `ix_geo_desert_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_desert_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_desert_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_desert_ibfk_3` FOREIGN KEY (`Desert`) REFERENCES `desert` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_estuary` (
  `River` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`River`),
  KEY `ix_geo_estuary_Country` (`Country`) USING BTREE,
  KEY `ix_geo_estuary_River` (`River`) USING BTREE,
  KEY `ix_geo_estuary_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_estuary_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_estuary_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_estuary_ibfk_3` FOREIGN KEY (`River`) REFERENCES `river` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_island` (
  `Island` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`Island`),
  KEY `ix_geo_island_Country` (`Country`) USING BTREE,
  KEY `ix_geo_island_Island` (`Island`) USING BTREE,
  KEY `ix_geo_island_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_island_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_island_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_island_ibfk_3` FOREIGN KEY (`Island`) REFERENCES `island` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_lake` (
  `Lake` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`Lake`),
  KEY `ix_geo_lake_Country` (`Country`) USING BTREE,
  KEY `ix_geo_lake_Lake` (`Lake`) USING BTREE,
  KEY `ix_geo_lake_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_lake_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_lake_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_lake_ibfk_3` FOREIGN KEY (`Lake`) REFERENCES `lake` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_mountain` (
  `Mountain` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`Mountain`),
  KEY `ix_geo_mountain_Country` (`Country`) USING BTREE,
  KEY `ix_geo_mountain_Mountain` (`Mountain`) USING BTREE,
  KEY `ix_geo_mountain_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_mountain_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_mountain_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_mountain_ibfk_3` FOREIGN KEY (`Mountain`) REFERENCES `mountain` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_river` (
  `River` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`River`),
  KEY `ix_geo_river_Country` (`Country`) USING BTREE,
  KEY `ix_geo_river_River` (`River`) USING BTREE,
  KEY `ix_geo_river_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_river_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_river_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_river_ibfk_3` FOREIGN KEY (`River`) REFERENCES `river` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_sea` (
  `Sea` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`Sea`),
  KEY `ix_geo_sea_Country` (`Country`) USING BTREE,
  KEY `ix_geo_sea_Sea` (`Sea`) USING BTREE,
  KEY `ix_geo_sea_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_sea_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_sea_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_sea_ibfk_3` FOREIGN KEY (`Sea`) REFERENCES `sea` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `geo_source` (
  `River` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Province`,`Country`,`River`),
  KEY `ix_geo_source_Country` (`Country`) USING BTREE,
  KEY `ix_geo_source_River` (`River`) USING BTREE,
  KEY `ix_geo_source_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `geo_source_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_source_ibfk_2` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `geo_source_ibfk_3` FOREIGN KEY (`River`) REFERENCES `river` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `isMember` (
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Organization` varchar(12) NOT NULL DEFAULT '',
  `Type` varchar(35) DEFAULT 'member',
  PRIMARY KEY (`Country`,`Organization`),
  KEY `ix_isMember_Organization` (`Organization`) USING BTREE,
  CONSTRAINT `isMember_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `isMember_ibfk_2` FOREIGN KEY (`Organization`) REFERENCES `organization` (`Abbreviation`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `island` (
  `Name` varchar(35) NOT NULL DEFAULT '',
  `Islands` varchar(35) DEFAULT NULL,
  `Area` float DEFAULT NULL,
  `Height` float DEFAULT NULL,
  `Type` varchar(10) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  PRIMARY KEY (`Name`),
  KEY `ix_island_Islands` (`Islands`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `islandIn` (
  `Island` varchar(35) DEFAULT NULL,
  `Sea` varchar(35) DEFAULT NULL,
  `Lake` varchar(35) DEFAULT NULL,
  `River` varchar(35) DEFAULT NULL,
  KEY `ix_islandIn_Lake` (`Lake`) USING BTREE,
  KEY `ix_islandIn_River` (`River`) USING BTREE,
  KEY `ix_islandIn_Sea` (`Sea`) USING BTREE,
  KEY `ix_islandIn_Island` (`Island`) USING BTREE,
  CONSTRAINT `islandIn_ibfk_1` FOREIGN KEY (`Lake`) REFERENCES `lake` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `islandIn_ibfk_2` FOREIGN KEY (`River`) REFERENCES `river` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `islandIn_ibfk_3` FOREIGN KEY (`Sea`) REFERENCES `sea` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `islandIn_ibfk_4` FOREIGN KEY (`Island`) REFERENCES `island` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `lake` (
  `Name` varchar(35) NOT NULL DEFAULT '',
  `Area` float DEFAULT NULL,
  `Depth` float DEFAULT NULL,
  `Altitude` float DEFAULT NULL,
  `Type` varchar(10) DEFAULT NULL,
  `River` varchar(35) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `language` (
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Name` varchar(50) NOT NULL DEFAULT '',
  `Percentage` float DEFAULT NULL,
  PRIMARY KEY (`Name`,`Country`),
  KEY `ix_language_Country` (`Country`) USING BTREE,
  CONSTRAINT `language_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `located` (
  `City` varchar(35) DEFAULT NULL,
  `Province` varchar(35) DEFAULT NULL,
  `Country` varchar(4) DEFAULT NULL,
  `River` varchar(35) DEFAULT NULL,
  `Lake` varchar(35) DEFAULT NULL,
  `Sea` varchar(35) DEFAULT NULL,
  KEY `ix_located_Country` (`Country`) USING BTREE,
  KEY `ix_located_River` (`River`) USING BTREE,
  KEY `ix_located_Lake` (`Lake`) USING BTREE,
  KEY `ix_located_Sea` (`Sea`) USING BTREE,
  KEY `ix_located_City` (`City`,`Province`) USING BTREE,
  KEY `ix_located_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `located_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `located_ibfk_2` FOREIGN KEY (`City`, `Province`) REFERENCES `city` (`Name`, `Province`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `located_ibfk_3` FOREIGN KEY (`River`) REFERENCES `river` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `located_ibfk_4` FOREIGN KEY (`Lake`) REFERENCES `lake` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `located_ibfk_5` FOREIGN KEY (`Sea`) REFERENCES `sea` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `located_ibfk_6` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `locatedOn` (
  `City` varchar(35) NOT NULL DEFAULT '',
  `Province` varchar(35) NOT NULL DEFAULT '',
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Island` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`City`,`Province`,`Country`,`Island`),
  KEY `ix_locatedOn_Country` (`Country`) USING BTREE,
  KEY `ix_locatedOn_Island` (`Island`) USING BTREE,
  KEY `ix_locatedOn_Province` (`Province`) USING BTREE,
  KEY `Province` (`Province`,`Country`),
  CONSTRAINT `locatedOn_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `locatedOn_ibfk_2` FOREIGN KEY (`Island`) REFERENCES `island` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `locatedOn_ibfk_3` FOREIGN KEY (`City`, `Province`) REFERENCES `city` (`Name`, `Province`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `locatedOn_ibfk_4` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mergesWith` (
  `Sea1` varchar(35) NOT NULL DEFAULT '',
  `Sea2` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Sea1`,`Sea2`),
  KEY `ix_mergeWith_Sea2` (`Sea2`) USING BTREE,
  CONSTRAINT `mergesWith_ibfk_1` FOREIGN KEY (`Sea1`) REFERENCES `sea` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `mergesWith_ibfk_2` FOREIGN KEY (`Sea2`) REFERENCES `sea` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mountain` (
  `Name` varchar(35) NOT NULL DEFAULT '',
  `Mountains` varchar(35) DEFAULT NULL,
  `Height` float DEFAULT NULL,
  `Type` varchar(10) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  PRIMARY KEY (`Name`),
  KEY `ix_mountain_Mountains` (`Mountains`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mountainOnIsland` (
  `Mountain` varchar(35) NOT NULL DEFAULT '',
  `Island` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Mountain`,`Island`),
  KEY `ix_mountainOnIsland_Island` (`Island`) USING BTREE,
  CONSTRAINT `mountainOnIsland_ibfk_1` FOREIGN KEY (`Island`) REFERENCES `island` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `mountainOnIsland_ibfk_2` FOREIGN KEY (`Mountain`) REFERENCES `mountain` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `organization` (
  `Abbreviation` varchar(12) NOT NULL,
  `Name` varchar(80) NOT NULL,
  `City` varchar(35) DEFAULT NULL,
  `Country` varchar(4) DEFAULT NULL,
  `Province` varchar(35) DEFAULT NULL,
  `Established` date DEFAULT NULL,
  PRIMARY KEY (`Abbreviation`),
  UNIQUE KEY `ix_organization_OrgNameUnique` (`Name`) USING BTREE,
  KEY `ix_organization_Country` (`Country`) USING BTREE,
  KEY `ix_organization_City` (`City`,`Province`) USING BTREE,
  KEY `ix_organization_Province` (`Province`,`Country`) USING BTREE,
  CONSTRAINT `organization_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `organization_ibfk_2` FOREIGN KEY (`City`, `Province`) REFERENCES `city` (`Name`, `Province`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `organization_ibfk_3` FOREIGN KEY (`Province`, `Country`) REFERENCES `province` (`Name`, `Country`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `politics` (
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Independence` date DEFAULT NULL,
  `Dependent` varchar(4) DEFAULT NULL,
  `Government` varchar(120) DEFAULT NULL,
  PRIMARY KEY (`Country`),
  KEY `ix_politics_Dependent` (`Dependent`) USING BTREE,
  CONSTRAINT `politics_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `politics_ibfk_2` FOREIGN KEY (`Dependent`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `population` (
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Population_Growth` float DEFAULT NULL,
  `Infant_Mortality` float DEFAULT NULL,
  PRIMARY KEY (`Country`),
  CONSTRAINT `population_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `province` (
  `Name` varchar(35) NOT NULL,
  `Country` varchar(4) NOT NULL,
  `Population` int(11) DEFAULT NULL,
  `Area` float DEFAULT NULL,
  `Capital` varchar(35) DEFAULT NULL,
  `CapProv` varchar(35) DEFAULT NULL,
  PRIMARY KEY (`Name`,`Country`),
  KEY `ix_province_Country` (`Country`) USING BTREE,
  CONSTRAINT `province_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `religion` (
  `Country` varchar(4) NOT NULL DEFAULT '',
  `Name` varchar(50) NOT NULL DEFAULT '',
  `Percentage` float DEFAULT NULL,
  PRIMARY KEY (`Name`,`Country`),
  KEY `ix_religion_Country` (`Country`) USING BTREE,
  CONSTRAINT `religion_ibfk_1` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `river` (
  `Name` varchar(35) NOT NULL DEFAULT '',
  `River` varchar(35) DEFAULT NULL,
  `Lake` varchar(35) DEFAULT NULL,
  `Sea` varchar(35) DEFAULT NULL,
  `Length` float DEFAULT NULL,
  `SourceLongitude` float DEFAULT NULL,
  `SourceLatitude` float DEFAULT NULL,
  `Mountains` varchar(35) DEFAULT NULL,
  `SourceAltitude` float DEFAULT NULL,
  `EstuaryLongitude` float DEFAULT NULL,
  `EstuaryLatitude` float DEFAULT NULL,
  PRIMARY KEY (`Name`),
  KEY `ix_river_Lake` (`Lake`) USING BTREE,
  KEY `ix_river_River` (`River`) USING BTREE,
  KEY `ix_river_Sea` (`Sea`) USING BTREE,
  KEY `ix_river_Mountains` (`Mountains`) USING BTREE,
  CONSTRAINT `river_ibfk_1` FOREIGN KEY (`Lake`) REFERENCES `lake` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sea` (
  `Name` varchar(35) NOT NULL DEFAULT '',
  `Depth` float DEFAULT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `Country` varchar(4) NOT NULL,
  `Target` varchar(13) DEFAULT NULL,
  PRIMARY KEY (`Country`),
  CONSTRAINT `target_Country_fkey` FOREIGN KEY (`Country`) REFERENCES `country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

