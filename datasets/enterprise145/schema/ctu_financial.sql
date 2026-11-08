-- Schema for database: ctu_financial

CREATE TABLE `account` (
  `account_id` int(11) NOT NULL DEFAULT 0,
  `district_id` int(11) NOT NULL DEFAULT 0,
  `frequency` varchar(18) NOT NULL,
  `date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `card` (
  `card_id` int(11) NOT NULL DEFAULT 0,
  `disp_id` int(11) NOT NULL,
  `type` varchar(7) NOT NULL,
  `issued` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `client` (
  `client_id` int(11) NOT NULL,
  `gender` varchar(1) NOT NULL,
  `birth_date` date NOT NULL,
  `district_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `disp` (
  `disp_id` int(11) NOT NULL,
  `client_id` int(11) NOT NULL,
  `account_id` int(11) NOT NULL,
  `type` varchar(9) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `district` (
  `district_id` int(11) NOT NULL DEFAULT 0,
  `A2` varchar(19) DEFAULT NULL,
  `A3` varchar(15) DEFAULT NULL,
  `A4` int(20) DEFAULT NULL,
  `A5` int(11) DEFAULT NULL,
  `A6` int(11) DEFAULT NULL,
  `A7` int(11) DEFAULT NULL,
  `A8` int(6) DEFAULT NULL,
  `A9` int(11) DEFAULT NULL,
  `A10` decimal(4,1) DEFAULT NULL,
  `A11` int(11) DEFAULT NULL,
  `A12` decimal(4,1) DEFAULT NULL,
  `A13` decimal(3,2) DEFAULT NULL,
  `A14` int(11) DEFAULT NULL,
  `A15` int(5) DEFAULT NULL,
  `A16` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `loan` (
  `loan_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `amount` int(11) NOT NULL,
  `duration` int(11) NOT NULL,
  `payments` decimal(6,2) NOT NULL,
  `status` varchar(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `order` (
  `order_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) NOT NULL,
  `bank_to` varchar(2) NOT NULL,
  `account_to` int(11) NOT NULL,
  `amount` decimal(6,1) NOT NULL,
  `k_symbol` varchar(8) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `trans` (
  `trans_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) NOT NULL DEFAULT 0,
  `date` date NOT NULL,
  `type` varchar(6) NOT NULL,
  `operation` varchar(14) DEFAULT NULL,
  `amount` int(11) NOT NULL,
  `balance` int(11) NOT NULL,
  `k_symbol` varchar(11) DEFAULT NULL,
  `bank` varchar(2) DEFAULT NULL,
  `account` int(11) unsigned DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

