-- Schema for database: ftp

CREATE TABLE `product` (
  `session_id` char(6) NOT NULL,
  `sequence_order` int(11) NOT NULL,
  `category_a` char(6) DEFAULT NULL,
  `category_b` char(6) DEFAULT NULL,
  `category_c` char(6) DEFAULT NULL,
  `category_d` char(6) DEFAULT NULL,
  PRIMARY KEY (`session_id`,`sequence_order`),
  KEY `session_id` (`session_id`),
  CONSTRAINT `product_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `session` (`session_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `session` (
  `session_id` char(6) NOT NULL,
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `gender` char(6) DEFAULT NULL,
  PRIMARY KEY (`session_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

