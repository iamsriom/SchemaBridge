-- Schema for database: tpcc

CREATE TABLE `C_Customer` (
  `c_id` int(11) NOT NULL,
  `c_d_id` int(11) NOT NULL,
  `c_w_id` int(11) NOT NULL,
  `c_first` char(16) DEFAULT NULL,
  `c_middle` char(2) DEFAULT NULL,
  `c_last` char(16) DEFAULT NULL,
  `c_street_1` char(20) DEFAULT NULL,
  `c_street_2` char(20) DEFAULT NULL,
  `c_city` char(20) DEFAULT NULL,
  `c_state` char(2) DEFAULT NULL,
  `c_zip` char(9) DEFAULT NULL,
  `c_phone` char(16) DEFAULT NULL,
  `c_since` datetime DEFAULT NULL,
  `c_credit` char(2) DEFAULT NULL,
  `c_credit_lim` float DEFAULT NULL,
  `c_discount` float DEFAULT NULL,
  `c_balance` float DEFAULT NULL,
  `c_ytd_payment` float DEFAULT NULL,
  `c_payment_cnt` int(11) DEFAULT NULL,
  `c_delivery_cnt` int(11) DEFAULT NULL,
  `c_data1` char(250) DEFAULT NULL,
  `c_data2` char(250) DEFAULT NULL,
  PRIMARY KEY (`c_id`,`c_d_id`,`c_w_id`),
  UNIQUE KEY `C_Customer_I1` (`c_w_id`,`c_d_id`,`c_id`),
  UNIQUE KEY `C_Customer_I2` (`c_w_id`,`c_d_id`,`c_last`,`c_first`,`c_id`),
  KEY `c_d_id` (`c_d_id`),
  KEY `c_d_id_2` (`c_d_id`,`c_id`,`c_w_id`),
  CONSTRAINT `C_Customer_ibfk_1` FOREIGN KEY (`c_d_id`) REFERENCES `C_District` (`d_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_District` (
  `d_id` int(11) NOT NULL,
  `d_w_id` int(11) NOT NULL,
  `d_name` char(10) DEFAULT NULL,
  `d_street_1` char(20) DEFAULT NULL,
  `d_street_2` char(20) DEFAULT NULL,
  `d_city` char(20) DEFAULT NULL,
  `d_state` char(2) DEFAULT NULL,
  `d_zip` char(9) DEFAULT NULL,
  `d_tax` float DEFAULT NULL,
  `d_ytd` float DEFAULT NULL,
  `d_next_o_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`d_id`,`d_w_id`),
  UNIQUE KEY `C_District_I1` (`d_w_id`,`d_id`),
  CONSTRAINT `C_District_ibfk_1` FOREIGN KEY (`d_w_id`) REFERENCES `C_Warehouse` (`w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_History` (
  `h_c_id` int(11) DEFAULT NULL,
  `h_c_d_id` int(11) DEFAULT NULL,
  `h_c_w_id` int(11) DEFAULT NULL,
  `h_d_id` int(11) DEFAULT NULL,
  `h_w_id` int(11) DEFAULT NULL,
  `h_date` datetime DEFAULT NULL,
  `h_amount` float DEFAULT NULL,
  `h_data` char(24) DEFAULT NULL,
  KEY `h_c_w_id` (`h_c_w_id`),
  KEY `h_d_id` (`h_d_id`),
  KEY `h_c_id` (`h_c_id`,`h_c_d_id`,`h_c_w_id`),
  KEY `h_d_id_2` (`h_d_id`,`h_w_id`),
  CONSTRAINT `C_History_ibfk_3` FOREIGN KEY (`h_c_id`, `h_c_d_id`, `h_c_w_id`) REFERENCES `C_Customer` (`c_id`, `c_d_id`, `c_w_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `C_History_ibfk_4` FOREIGN KEY (`h_d_id`, `h_w_id`) REFERENCES `C_District` (`d_id`, `d_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Item` (
  `i_id` int(11) NOT NULL,
  `i_im_id` int(11) DEFAULT NULL,
  `i_name` char(24) DEFAULT NULL,
  `i_price` float DEFAULT NULL,
  `i_data` char(50) DEFAULT NULL,
  PRIMARY KEY (`i_id`),
  UNIQUE KEY `C_Item_I1` (`i_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_New_Order` (
  `no_o_id` int(11) NOT NULL,
  `no_d_id` int(11) NOT NULL,
  `no_w_id` int(11) NOT NULL,
  PRIMARY KEY (`no_o_id`,`no_d_id`,`no_w_id`),
  UNIQUE KEY `C_New_Order_I1` (`no_w_id`,`no_d_id`,`no_o_id`),
  CONSTRAINT `C_New_Order_ibfk_1` FOREIGN KEY (`no_o_id`, `no_d_id`, `no_w_id`) REFERENCES `C_Order` (`o_id`, `o_d_id`, `o_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Order` (
  `o_id` int(11) NOT NULL,
  `o_d_id` int(11) NOT NULL,
  `o_w_id` int(11) NOT NULL,
  `o_c_id` int(11) DEFAULT NULL,
  `o_entry_d` datetime DEFAULT NULL,
  `o_carrier_id` int(11) DEFAULT NULL,
  `o_ol_cnt` int(11) DEFAULT NULL,
  `o_all_local` int(11) DEFAULT NULL,
  PRIMARY KEY (`o_id`,`o_d_id`,`o_w_id`),
  UNIQUE KEY `C_Order_I1` (`o_w_id`,`o_d_id`,`o_id`),
  KEY `o_d_id` (`o_d_id`,`o_c_id`,`o_w_id`),
  CONSTRAINT `C_Order_ibfk_1` FOREIGN KEY (`o_d_id`, `o_c_id`, `o_w_id`) REFERENCES `C_Customer` (`c_d_id`, `c_id`, `c_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Order_Line` (
  `ol_o_id` int(11) NOT NULL,
  `ol_d_id` int(11) NOT NULL,
  `ol_w_id` int(11) NOT NULL,
  `ol_number` int(11) NOT NULL,
  `ol_i_id` int(11) DEFAULT NULL,
  `ol_supply_w_id` int(11) DEFAULT NULL,
  `ol_delivery_d` datetime DEFAULT NULL,
  `ol_quantity` int(11) DEFAULT NULL,
  `ol_amount` float DEFAULT NULL,
  `ol_dist_info` char(24) DEFAULT NULL,
  PRIMARY KEY (`ol_o_id`,`ol_d_id`,`ol_w_id`,`ol_number`),
  UNIQUE KEY `C_Order_Line_I1` (`ol_w_id`,`ol_d_id`,`ol_o_id`,`ol_number`),
  KEY `ol_o_id` (`ol_o_id`,`ol_d_id`,`ol_w_id`),
  KEY `ol_i_id` (`ol_i_id`),
  KEY `ol_i_id_2` (`ol_i_id`,`ol_supply_w_id`),
  CONSTRAINT `C_Order_Line_ibfk_1` FOREIGN KEY (`ol_o_id`, `ol_d_id`, `ol_w_id`) REFERENCES `C_Order` (`o_id`, `o_d_id`, `o_w_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `C_Order_Line_ibfk_2` FOREIGN KEY (`ol_i_id`, `ol_supply_w_id`) REFERENCES `C_Stock` (`s_i_id`, `s_w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Stock` (
  `s_i_id` int(11) NOT NULL,
  `s_w_id` int(11) NOT NULL,
  `s_quantity` int(11) DEFAULT NULL,
  `s_dist_01` char(24) DEFAULT NULL,
  `s_dist_02` char(24) DEFAULT NULL,
  `s_dist_03` char(24) DEFAULT NULL,
  `s_dist_04` char(24) DEFAULT NULL,
  `s_dist_05` char(24) DEFAULT NULL,
  `s_dist_06` char(24) DEFAULT NULL,
  `s_dist_07` char(24) DEFAULT NULL,
  `s_dist_08` char(24) DEFAULT NULL,
  `s_dist_09` char(24) DEFAULT NULL,
  `s_dist_10` char(24) DEFAULT NULL,
  `s_ytd` int(11) DEFAULT NULL,
  `s_order_cnt` int(11) DEFAULT NULL,
  `s_remote_cnt` int(11) DEFAULT NULL,
  `s_data` char(50) DEFAULT NULL,
  PRIMARY KEY (`s_i_id`,`s_w_id`),
  UNIQUE KEY `C_Stock_I1` (`s_i_id`,`s_w_id`),
  KEY `s_w_id` (`s_w_id`),
  CONSTRAINT `C_Stock_ibfk_1` FOREIGN KEY (`s_i_id`) REFERENCES `C_Item` (`i_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `C_Stock_ibfk_2` FOREIGN KEY (`s_w_id`) REFERENCES `C_Warehouse` (`w_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `C_Warehouse` (
  `w_id` int(11) NOT NULL,
  `w_name` char(10) DEFAULT NULL,
  `w_street_1` char(20) DEFAULT NULL,
  `w_street_2` char(20) DEFAULT NULL,
  `w_city` char(20) DEFAULT NULL,
  `w_state` char(2) DEFAULT NULL,
  `w_zip` char(9) DEFAULT NULL,
  `w_tax` float DEFAULT NULL,
  `w_ytd` float DEFAULT NULL,
  PRIMARY KEY (`w_id`),
  UNIQUE KEY `C_Warehouse_I1` (`w_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

