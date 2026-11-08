-- Schema for database: Countries

CREATE TABLE `Data` (
  `Country Name` varchar(255) DEFAULT NULL,
  `Country Code` varchar(255) NOT NULL,
  `Indicator Name` varchar(255) DEFAULT NULL,
  `Indicator Code` varchar(255) NOT NULL,
  `1960` double DEFAULT NULL,
  `1961` double DEFAULT NULL,
  `1962` double DEFAULT NULL,
  `1963` double DEFAULT NULL,
  `1964` double DEFAULT NULL,
  `1965` double DEFAULT NULL,
  `1966` double DEFAULT NULL,
  `1967` double DEFAULT NULL,
  `1968` double DEFAULT NULL,
  `1969` double DEFAULT NULL,
  `1970` double DEFAULT NULL,
  `1971` double DEFAULT NULL,
  `1972` double DEFAULT NULL,
  `1973` double DEFAULT NULL,
  `1974` double DEFAULT NULL,
  `1975` double DEFAULT NULL,
  `1976` double DEFAULT NULL,
  `1977` double DEFAULT NULL,
  `1978` double DEFAULT NULL,
  `1979` double DEFAULT NULL,
  `1980` double DEFAULT NULL,
  `1981` double DEFAULT NULL,
  `1982` double DEFAULT NULL,
  `1983` double DEFAULT NULL,
  `1984` double DEFAULT NULL,
  `1985` double DEFAULT NULL,
  `1986` double DEFAULT NULL,
  `1987` double DEFAULT NULL,
  `1988` double DEFAULT NULL,
  `1989` double DEFAULT NULL,
  `1990` double DEFAULT NULL,
  `1991` double DEFAULT NULL,
  `1992` double DEFAULT NULL,
  `1993` double DEFAULT NULL,
  `1994` double DEFAULT NULL,
  `1995` double DEFAULT NULL,
  `1996` double DEFAULT NULL,
  `1997` double DEFAULT NULL,
  `1998` double DEFAULT NULL,
  `1999` double DEFAULT NULL,
  `2000` double DEFAULT NULL,
  `2001` double DEFAULT NULL,
  `2002` double DEFAULT NULL,
  `2003` double DEFAULT NULL,
  `2004` double DEFAULT NULL,
  `2005` double DEFAULT NULL,
  `2006` double DEFAULT NULL,
  `2007` double DEFAULT NULL,
  `2008` double DEFAULT NULL,
  `2009` double DEFAULT NULL,
  `2010` double DEFAULT NULL,
  `2011` double DEFAULT NULL,
  PRIMARY KEY (`Country Code`,`Indicator Code`),
  KEY `Indicator Code` (`Indicator Code`),
  KEY `Country Code` (`Country Code`),
  CONSTRAINT `Data_ibfk_1` FOREIGN KEY (`Indicator Code`) REFERENCES `Metadata - Indicators` (`INDICATOR_CODE`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Data_ibfk_2` FOREIGN KEY (`Country Code`) REFERENCES `Metadata - Countries` (`Country Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `Metadata - Countries` (
  `Country Code` varchar(255) NOT NULL,
  `Country Name` varchar(255) DEFAULT NULL,
  `Region` varchar(255) DEFAULT NULL,
  `IncomeGroup` varchar(255) DEFAULT NULL,
  `SpecialNotes` text DEFAULT NULL,
  PRIMARY KEY (`Country Code`),
  KEY `Country Name` (`Country Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `Metadata - Indicators` (
  `INDICATOR_CODE` varchar(255) NOT NULL,
  `INDICATOR_NAME` varchar(255) DEFAULT NULL,
  `SOURCE_NOTE` text DEFAULT NULL,
  `SOURCE_ORGANIZATION` text DEFAULT NULL,
  PRIMARY KEY (`INDICATOR_CODE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `target` (
  `Country Code` varchar(255) NOT NULL,
  `2012` double DEFAULT NULL,
  PRIMARY KEY (`Country Code`),
  KEY `Country Code` (`Country Code`),
  CONSTRAINT `target_ibfk_1` FOREIGN KEY (`Country Code`) REFERENCES `Metadata - Countries` (`Country Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

