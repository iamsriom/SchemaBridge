-- Schema for database: Financial_ijs

CREATE TABLE `accounts` (
  `id` int(11) NOT NULL,
  `district_id` int(11) DEFAULT NULL,
  `frequency` char(30) DEFAULT NULL,
  `date` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `district_id` (`district_id`),
  CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `districts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `cards` (
  `id` int(11) NOT NULL,
  `disp_id` int(11) DEFAULT NULL,
  `type` char(20) DEFAULT NULL,
  `issued` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `disp_id` (`disp_id`),
  CONSTRAINT `cards_ibfk_1` FOREIGN KEY (`disp_id`) REFERENCES `disps` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `clients` (
  `id` int(11) NOT NULL,
  `birth_number` char(10) DEFAULT NULL,
  `district_id` int(11) DEFAULT NULL,
  `tkey_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `district_id` (`district_id`),
  CONSTRAINT `clients_ibfk_1` FOREIGN KEY (`district_id`) REFERENCES `districts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `disps` (
  `id` int(11) NOT NULL,
  `client_id` int(11) DEFAULT NULL,
  `account_id` int(11) DEFAULT NULL,
  `type` char(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `client_id` (`client_id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `disps_ibfk_1` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `disps_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `districts` (
  `id` int(11) NOT NULL,
  `A2` char(30) DEFAULT NULL,
  `A3` char(30) DEFAULT NULL,
  `A4` int(11) DEFAULT NULL,
  `A5` int(11) DEFAULT NULL,
  `A6` int(11) DEFAULT NULL,
  `A7` int(11) DEFAULT NULL,
  `A8` int(11) DEFAULT NULL,
  `A9` int(11) DEFAULT NULL,
  `A10` decimal(10,0) DEFAULT NULL,
  `A11` int(11) DEFAULT NULL,
  `A12` decimal(10,0) DEFAULT NULL,
  `A13` decimal(10,0) DEFAULT NULL,
  `A14` int(11) DEFAULT NULL,
  `A15` int(11) DEFAULT NULL,
  `A16` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `loans` (
  `id` int(11) NOT NULL,
  `account_id` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `amount` decimal(10,0) DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `payments` decimal(10,0) DEFAULT NULL,
  `status` char(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `loans_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `orders` (
  `id` int(11) NOT NULL,
  `account_id` int(11) DEFAULT NULL,
  `bank_to` char(20) DEFAULT NULL,
  `account_to` char(20) DEFAULT NULL,
  `amount` decimal(10,0) DEFAULT NULL,
  `k_symbol` char(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `orders_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `tkeys` (
  `id` int(11) NOT NULL,
  `goodClient` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `trans` (
  `id` int(11) NOT NULL,
  `account_id` int(11) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `type` char(20) DEFAULT NULL,
  `operation` char(20) DEFAULT NULL,
  `amount` decimal(10,0) DEFAULT NULL,
  `balance` decimal(10,0) DEFAULT NULL,
  `k_symbol` char(20) DEFAULT NULL,
  `bank` char(20) DEFAULT NULL,
  `account` char(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `trans_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

