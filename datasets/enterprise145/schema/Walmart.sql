-- Schema for database: Walmart

CREATE TABLE `key` (
  `store_nbr` int(11) NOT NULL,
  `station_nbr` int(11) DEFAULT NULL,
  PRIMARY KEY (`store_nbr`),
  UNIQUE KEY `key_store_nbr_key` (`store_nbr`),
  KEY `key_station_nbr_fkey` (`station_nbr`),
  CONSTRAINT `key_station_nbr_fkey` FOREIGN KEY (`station_nbr`) REFERENCES `station` (`station_nbr`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `station` (
  `station_nbr` int(11) NOT NULL,
  PRIMARY KEY (`station_nbr`),
  UNIQUE KEY `station_station_nbr_key` (`station_nbr`)
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

