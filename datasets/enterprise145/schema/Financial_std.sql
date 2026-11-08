-- Schema for database: Financial_std

CREATE TABLE `Loan_Acc` (
  `loan_id` int(11) NOT NULL,
  `account_id` int(10) unsigned NOT NULL,
  PRIMARY KEY (`loan_id`,`account_id`),
  KEY `FK_rel1_1` (`account_id`),
  KEY `FK_rel1_2` (`loan_id`),
  CONSTRAINT `FK_rel1_1` FOREIGN KEY (`account_id`) REFERENCES `acc` (`account_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_rel1_2` FOREIGN KEY (`loan_id`) REFERENCES `loan` (`loan_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Loan_Order` (
  `order_id` int(10) unsigned NOT NULL,
  `loan_id` int(11) NOT NULL,
  PRIMARY KEY (`order_id`,`loan_id`),
  KEY `FK_rel2_2` (`order_id`),
  KEY `FK_rel2_1` (`loan_id`),
  CONSTRAINT `FK_rel2_1` FOREIGN KEY (`order_id`) REFERENCES `order` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_rel2_2` FOREIGN KEY (`loan_id`) REFERENCES `loan` (`loan_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Loan_Trans` (
  `transaction_id` int(10) unsigned NOT NULL DEFAULT 0,
  `loan_id` int(11) NOT NULL,
  PRIMARY KEY (`transaction_id`,`loan_id`),
  KEY `FK_rel5_1` (`transaction_id`),
  KEY `FK_rel5_2` (`loan_id`),
  CONSTRAINT `FK_rel5_1` FOREIGN KEY (`transaction_id`) REFERENCES `trans` (`transaction_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_rel5_2` FOREIGN KEY (`loan_id`) REFERENCES `loan` (`loan_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `acc` (
  `account_id` int(10) unsigned NOT NULL,
  `frequency` varchar(255) DEFAULT NULL COMMENT 'Type: Ordinal; Aggr: AVG, MAX, MIN, SUM, STDDEV, MEDIAN',
  PRIMARY KEY (`account_id`),
  KEY `freq` (`frequency`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `loan` (
  `loan_id` int(10) NOT NULL,
  `amount` int(10) DEFAULT NULL COMMENT 'Type: Numeric; Aggr: AVG, MAX, MIN, COUNT, SUM, MEDIAN',
  `duration` int(10) DEFAULT NULL COMMENT 'Type: Numeric; Aggr: AVG, MAX, MIN, STDDEV, MEDIAN',
  `payments` int(10) unsigned DEFAULT NULL COMMENT 'Type: Numeric; Aggr: AVG, MAX, MIN, SUM, STDDEV, MEDIAN',
  `status` varchar(5) DEFAULT NULL COMMENT 'Type: Ordinal; Aggr: A, B, C, D',
  PRIMARY KEY (`loan_id`),
  KEY `amount_in` (`amount`) USING BTREE,
  KEY `duration_in` (`duration`) USING BTREE,
  KEY `payments_in` (`payments`) USING BTREE,
  KEY `status_in` (`status`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `order` (
  `order_id` int(10) unsigned NOT NULL,
  `bank_to` varchar(255) DEFAULT NULL COMMENT 'Type: Categorical; Aggr: MIN, MAX',
  `amount3` int(10) unsigned DEFAULT NULL COMMENT 'Type: Numeric; Aggr: AVG, MAX, MIN, SUM, STDDEV, MEDIAN',
  `k_symbol` varchar(255) DEFAULT 'Household' COMMENT 'Type: Categorical; Aggr: MIN, MAX',
  PRIMARY KEY (`order_id`),
  KEY `bank_to_in` (`bank_to`) USING BTREE,
  KEY `amount3_in` (`amount3`) USING BTREE,
  KEY `k_symbol_in` (`k_symbol`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `trans` (
  `transaction_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `type` varchar(45) NOT NULL,
  `operation` varchar(45) NOT NULL,
  `amount2` int(10) unsigned NOT NULL,
  `balance` int(10) unsigned NOT NULL,
  PRIMARY KEY (`transaction_id`),
  KEY `type_in` (`type`) USING BTREE,
  KEY `operation_in` (`operation`) USING BTREE,
  KEY `amount2_in` (`amount2`) USING BTREE,
  KEY `balance_in` (`balance`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=3682968 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

