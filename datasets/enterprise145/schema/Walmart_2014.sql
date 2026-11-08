-- Schema for database: Walmart_2014

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


CREATE TABLE `stores` (
  `Store` int(11) NOT NULL,
  `Type` varchar(255) DEFAULT NULL,
  `Size` int(11) DEFAULT NULL,
  PRIMARY KEY (`Store`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `train` (
  `Store` int(11) NOT NULL,
  `Dept` int(11) NOT NULL,
  `Date` date NOT NULL,
  `Weekly_Sales` float DEFAULT NULL,
  `IsHoliday` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Store`,`Dept`,`Date`),
  CONSTRAINT `train_ibfk_1` FOREIGN KEY (`Store`) REFERENCES `stores` (`Store`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

