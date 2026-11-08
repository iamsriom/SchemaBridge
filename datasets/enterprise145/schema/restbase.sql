-- Schema for database: restbase

CREATE TABLE `generalinfo` (
  `id_restaurant` int(11) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  `food_type` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `review` decimal(2,1) DEFAULT NULL,
  PRIMARY KEY (`id_restaurant`),
  KEY `field4` (`city`),
  CONSTRAINT `generalinfo_ibfk_1` FOREIGN KEY (`city`) REFERENCES `geographic` (`city`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `geographic` (
  `city` varchar(255) NOT NULL,
  `county` varchar(255) DEFAULT NULL,
  `region` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `location` (
  `id_restaurant` int(11) NOT NULL,
  `street_num` int(11) DEFAULT NULL,
  `street_name` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_restaurant`),
  KEY `city` (`city`),
  KEY `city_2` (`city`),
  KEY `id_restaurant` (`id_restaurant`),
  CONSTRAINT `location_ibfk_1` FOREIGN KEY (`city`) REFERENCES `geographic` (`city`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `location_ibfk_2` FOREIGN KEY (`id_restaurant`) REFERENCES `generalinfo` (`id_restaurant`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

