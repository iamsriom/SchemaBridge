-- Schema for database: Mondial_geo

CREATE TABLE `City` (
  `City_id` varchar(64) NOT NULL DEFAULT '',
  `Population` int(11) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  PRIMARY KEY (`City_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Continent` (
  `Name` varchar(20) NOT NULL DEFAULT '',
  `Area` varchar(35) DEFAULT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Country` (
  `Code` varchar(4) NOT NULL DEFAULT '',
  `Area` varchar(35) DEFAULT NULL,
  `Population` varchar(35) DEFAULT NULL,
  PRIMARY KEY (`Code`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CountryDiscrete
;


CountryFull
;


CREATE TABLE `Province` (
  `Prov_id` varchar(64) NOT NULL DEFAULT '',
  `Population` varchar(35) DEFAULT NULL,
  `Area` varchar(35) DEFAULT NULL,
  PRIMARY KEY (`Prov_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `borders` (
  `Country1` varchar(4) NOT NULL DEFAULT '',
  `Country2` varchar(4) NOT NULL DEFAULT '',
  `Length` varchar(35) DEFAULT NULL,
  PRIMARY KEY (`Country1`,`Country2`),
  KEY `fk_borders_c1_idx` (`Country1`),
  KEY `fk_borders_c2_idx` (`Country2`),
  CONSTRAINT `fk_borders_c1` FOREIGN KEY (`Country1`) REFERENCES `Country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_borders_c2` FOREIGN KEY (`Country2`) REFERENCES `Country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `capt_Country` (
  `Country` varchar(4) NOT NULL,
  `Capital` varchar(64) NOT NULL,
  PRIMARY KEY (`Country`,`Capital`),
  KEY `fk_capt_Country_Coun_idx` (`Country`),
  KEY `fk_capt_Country_Capt_idx` (`Capital`),
  CONSTRAINT `fk_capt_Country_Capt` FOREIGN KEY (`Capital`) REFERENCES `City` (`City_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_capt_Country_Coun` FOREIGN KEY (`Country`) REFERENCES `Country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `capt_Prov` (
  `Province` varchar(64) NOT NULL,
  `Capital` varchar(64) NOT NULL,
  PRIMARY KEY (`Province`,`Capital`),
  KEY `fk_capt_Prov_prov_idx` (`Province`),
  KEY `fk_capt_Prov_capt_idx` (`Capital`),
  CONSTRAINT `fk_capt_Prov_capt` FOREIGN KEY (`Capital`) REFERENCES `City` (`City_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_capt_Prov_prov` FOREIGN KEY (`Province`) REFERENCES `Province` (`Prov_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `cityInProv` (
  `City` varchar(64) NOT NULL,
  `Province` varchar(64) NOT NULL,
  PRIMARY KEY (`City`,`Province`),
  KEY `fk_cityInProv_city_idx` (`City`),
  KEY `fk_cityInProv_prov_idx` (`Province`),
  CONSTRAINT `fk_cityInProv_city` FOREIGN KEY (`City`) REFERENCES `City` (`City_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cityInProv_prov` FOREIGN KEY (`Province`) REFERENCES `Province` (`Prov_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `countryOfProv` (
  `Province` varchar(64) NOT NULL,
  `Country` varchar(4) NOT NULL,
  PRIMARY KEY (`Province`,`Country`),
  KEY `fk_countryOfProv_prov_idx` (`Province`),
  KEY `fk_countryOfProv_coun_idx` (`Country`),
  CONSTRAINT `fk_countryOfProv_coun` FOREIGN KEY (`Country`) REFERENCES `Country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_countryOfProv_prov` FOREIGN KEY (`Province`) REFERENCES `Province` (`Prov_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `encompasses` (
  `Country` varchar(4) NOT NULL,
  `Continent` varchar(20) NOT NULL,
  `Percentage` varchar(35) DEFAULT NULL,
  PRIMARY KEY (`Continent`,`Country`),
  KEY `fk_encompasses_coun_idx` (`Country`),
  KEY `fk_encompasses_cont_idx` (`Continent`),
  CONSTRAINT `fk_encompasses_cont` FOREIGN KEY (`Continent`) REFERENCES `Continent` (`Name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_encompasses_coun` FOREIGN KEY (`Country`) REFERENCES `Country` (`Code`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

