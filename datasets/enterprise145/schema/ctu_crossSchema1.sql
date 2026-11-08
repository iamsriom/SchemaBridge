-- Schema for database: ctu_crossSchema1

CREATE TABLE `account` (
  `account_id` int(11) NOT NULL,
  `district_id` int(11) DEFAULT NULL,
  `frequency` varchar(18) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`account_id`),
  UNIQUE KEY `account_account_id_key` (`account_id`),
  KEY `account_ibfk_1` (`district_id`),
  CONSTRAINT `account_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `ctu_crossSchema2`.`district` (`district_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `loan` (
  `loan_id` int(11) NOT NULL,
  `account_id` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `amount` bigint(20) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `payments` decimal(6,2) DEFAULT NULL,
  `status` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`loan_id`),
  KEY `loan_ibfk_1` (`account_id`),
  CONSTRAINT `loan_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `account` (`account_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `order` (
  `order_id` int(11) NOT NULL,
  `account_id` int(11) DEFAULT NULL,
  `bank_to` varchar(2) DEFAULT NULL,
  `account_to` bigint(20) DEFAULT NULL,
  `amount` decimal(6,1) DEFAULT NULL,
  `k_symbol` varchar(8) DEFAULT NULL,
  PRIMARY KEY (`order_id`),
  KEY `order_ibfk_1` (`account_id`),
  CONSTRAINT `order_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `account` (`account_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `trans` (
  `trans_id` int(11) NOT NULL,
  `account_id` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `operation` varchar(255) DEFAULT NULL,
  `amount` decimal(30,0) DEFAULT NULL,
  `balance` decimal(30,0) DEFAULT NULL,
  `k_symbol` varchar(255) DEFAULT NULL,
  `bank` varchar(255) DEFAULT NULL,
  `account` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`trans_id`),
  KEY `trans_ibfk_1` (`account_id`),
  CONSTRAINT `trans_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `account` (`account_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

