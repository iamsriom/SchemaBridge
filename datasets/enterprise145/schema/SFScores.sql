-- Schema for database: SFScores

CREATE TABLE `businesses` (
  `business_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `postal_code` varchar(255) DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `phone_number` bigint(20) DEFAULT NULL,
  `tax_code` varchar(255) DEFAULT NULL,
  `business_certificate` int(11) NOT NULL,
  `application_date` date DEFAULT NULL,
  `owner_name` varchar(255) NOT NULL,
  `owner_address` varchar(255) DEFAULT NULL,
  `owner_city` varchar(255) DEFAULT NULL,
  `owner_state` varchar(255) DEFAULT NULL,
  `owner_zip` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `inspections` (
  `business_id` int(11) NOT NULL,
  `score` int(11) DEFAULT NULL,
  `date` date NOT NULL,
  `type` varchar(255) NOT NULL,
  KEY `inspections__business_id` (`business_id`) USING BTREE,
  CONSTRAINT `inspections_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `violations` (
  `business_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `violation_type_id` varchar(255) NOT NULL,
  `risk_category` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  KEY `violations__business_id` (`business_id`) USING BTREE,
  CONSTRAINT `violations_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `businesses` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

