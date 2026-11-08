-- Schema for database: ctu_feature_data

CREATE TABLE `financial_order` (
  `id` int(11) DEFAULT NULL,
  `target` varchar(1) DEFAULT NULL,
  `timestamp` date DEFAULT NULL,
  `order_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) DEFAULT NULL,
  `bank_to` varchar(2) DEFAULT NULL,
  `account_to` int(11) DEFAULT NULL,
  `amount` decimal(6,1) DEFAULT NULL,
  `k_symbol` varchar(8) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `financial_trans` (
  `id` int(11) DEFAULT NULL,
  `target` varchar(1) DEFAULT NULL,
  `timestamp` date DEFAULT NULL,
  `trans_id` int(11) NOT NULL DEFAULT 0,
  `account_id` int(11) DEFAULT 0,
  `date` date DEFAULT NULL,
  `type` varchar(6) DEFAULT NULL,
  `operation` varchar(14) DEFAULT NULL,
  `amount` int(11) DEFAULT NULL,
  `balance` int(11) DEFAULT NULL,
  `k_symbol` varchar(11) DEFAULT NULL,
  `bank` varchar(2) DEFAULT NULL,
  `account` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `trains_cars` (
  `id` int(11) DEFAULT NULL,
  `target` varchar(4) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `car_id` int(11) NOT NULL,
  `position` int(11) DEFAULT NULL,
  `shape` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `len` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `sides` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `roof` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `wheels` int(11) DEFAULT NULL,
  `load_shape` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `load_num` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

