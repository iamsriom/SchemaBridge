-- Schema for database: Seznam

CREATE TABLE `client` (
  `client_id` int(11) NOT NULL,
  `kraj` varchar(255) DEFAULT NULL,
  `obor` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`client_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dobito` (
  `client_id` int(11) DEFAULT NULL,
  `month_year_datum_transakce` date NOT NULL,
  `sluzba` varchar(255) NOT NULL,
  `kc_dobito` decimal(10,2) NOT NULL,
  KEY `dobito_client_id` (`client_id`) USING BTREE,
  CONSTRAINT `dobito_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `probehnuto` (
  `client_id` int(11) DEFAULT NULL,
  `month_year_datum_transakce` date NOT NULL,
  `sluzba` varchar(255) DEFAULT NULL,
  `kc_proklikano` decimal(10,2) NOT NULL,
  KEY `probehnuto_client_id` (`client_id`) USING BTREE,
  CONSTRAINT `probehnuto_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `probehnuto_mimo_penezenku` (
  `client_id` int(11) NOT NULL,
  `Month/Year` date NOT NULL,
  `probehla_inzerce_mimo_penezenku` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`client_id`,`Month/Year`),
  KEY `probehnuto_mimo_penezenku_client_id` (`client_id`) USING BTREE,
  CONSTRAINT `probehnuto_mimo_penezenku_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

