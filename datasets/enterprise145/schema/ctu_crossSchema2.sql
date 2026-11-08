-- Schema for database: ctu_crossSchema2

CREATE TABLE `card` (
  `card_id` int(11) NOT NULL,
  `disp_id` int(11) DEFAULT NULL,
  `type` varchar(7) DEFAULT NULL,
  `issued` date DEFAULT NULL,
  PRIMARY KEY (`card_id`),
  KEY `card_disp_id_fkey` (`disp_id`),
  CONSTRAINT `card_disp_id_fkey` FOREIGN KEY (`disp_id`) REFERENCES `disp` (`disp_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `client` (
  `client_id` int(11) NOT NULL,
  `gender` varchar(1) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `district_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`client_id`),
  UNIQUE KEY `client_client_id_key` (`client_id`),
  KEY `client_district_id_fkey` (`district_id`),
  CONSTRAINT `client_district_id_fkey` FOREIGN KEY (`district_id`) REFERENCES `district` (`district_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `disp` (
  `disp_id` int(11) NOT NULL,
  `client_id` int(11) DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  `type` varchar(9) DEFAULT NULL,
  PRIMARY KEY (`disp_id`),
  KEY `disp_ibfk_1` (`account_id`),
  KEY `disp_ibfk_2` (`client_id`),
  CONSTRAINT `disp_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `ctu_crossSchema1`.`account` (`account_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `disp_ibfk_2` FOREIGN KEY (`client_id`) REFERENCES `client` (`client_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `district` (
  `district_id` int(11) NOT NULL,
  `A2` varchar(19) NOT NULL,
  `A3` varchar(15) NOT NULL,
  `A4` int(11) NOT NULL,
  `A5` int(11) NOT NULL,
  `A6` int(11) NOT NULL,
  `A7` int(11) NOT NULL,
  `A8` int(11) NOT NULL,
  `A9` int(11) NOT NULL,
  `A10` decimal(4,1) NOT NULL,
  `A11` int(11) NOT NULL,
  `A12` decimal(4,1) DEFAULT NULL,
  `A13` decimal(3,2) NOT NULL,
  `A14` int(11) NOT NULL,
  `A15` int(11) DEFAULT NULL,
  `A16` int(11) NOT NULL,
  PRIMARY KEY (`district_id`),
  UNIQUE KEY `district_district_id_key` (`district_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

