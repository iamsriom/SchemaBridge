-- Schema for database: Mondial_Tutorial

CREATE TABLE `Borders` (
  `Name1` varchar(35) NOT NULL DEFAULT '',
  `Name2` varchar(35) NOT NULL DEFAULT '',
  PRIMARY KEY (`Name1`,`Name2`),
  KEY `country1_idx` (`Name1`),
  KEY `countr2_idx` (`Name2`),
  CONSTRAINT `countr2` FOREIGN KEY (`Name2`) REFERENCES `Country` (`Name`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `country1` FOREIGN KEY (`Name1`) REFERENCES `Country` (`Name`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Country` (
  `Name` varchar(35) NOT NULL,
  `Continent` varchar(20) NOT NULL,
  `DiscreteArea` varchar(35) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `DiscretePopulation` varchar(35) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  PRIMARY KEY (`Name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

