-- Schema for database: pubs

CREATE TABLE `authors` (
  `au_id` varchar(11) NOT NULL,
  `au_lname` varchar(40) NOT NULL,
  `au_fname` varchar(20) NOT NULL,
  `phone` char(12) NOT NULL,
  `address` varchar(40) DEFAULT NULL,
  `city` varchar(20) DEFAULT NULL,
  `state` char(2) DEFAULT NULL,
  `zip` char(5) DEFAULT NULL,
  `contract` tinyint(4) NOT NULL,
  PRIMARY KEY (`au_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `discounts` (
  `discounttype` varchar(40) NOT NULL,
  `stor_id` char(4) DEFAULT NULL,
  `lowqty` smallint(6) DEFAULT NULL,
  `highqty` smallint(6) DEFAULT NULL,
  `discount` decimal(4,2) NOT NULL,
  KEY `discounts_stor_id` (`stor_id`),
  CONSTRAINT `discounts_ibfk_1` FOREIGN KEY (`stor_id`) REFERENCES `stores` (`stor_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `employee` (
  `emp_id` char(9) NOT NULL,
  `fname` varchar(20) NOT NULL,
  `minit` char(1) DEFAULT NULL,
  `lname` varchar(30) NOT NULL,
  `job_id` smallint(6) NOT NULL,
  `job_lvl` smallint(6) DEFAULT NULL,
  `pub_id` char(4) NOT NULL,
  `hire_date` datetime NOT NULL,
  PRIMARY KEY (`emp_id`),
  KEY `employee_job_id` (`job_id`),
  KEY `employee_pub_id` (`pub_id`),
  CONSTRAINT `employee_ibfk_1` FOREIGN KEY (`job_id`) REFERENCES `jobs` (`job_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `employee_ibfk_2` FOREIGN KEY (`pub_id`) REFERENCES `publishers` (`pub_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `jobs` (
  `job_id` smallint(6) NOT NULL,
  `job_desc` varchar(50) NOT NULL,
  `min_lvl` smallint(6) NOT NULL,
  `max_lvl` smallint(6) NOT NULL,
  PRIMARY KEY (`job_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pub_info` (
  `pub_id` char(4) NOT NULL,
  `logo` longblob DEFAULT NULL,
  `pr_info` longtext DEFAULT NULL,
  PRIMARY KEY (`pub_id`),
  CONSTRAINT `pub_info_ibfk_1` FOREIGN KEY (`pub_id`) REFERENCES `publishers` (`pub_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `publishers` (
  `pub_id` char(4) NOT NULL,
  `pub_name` varchar(40) DEFAULT NULL,
  `city` varchar(20) DEFAULT NULL,
  `state` char(2) DEFAULT NULL,
  `country` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`pub_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `roysched` (
  `title_id` varchar(6) NOT NULL,
  `lorange` int(11) DEFAULT NULL,
  `hirange` int(11) DEFAULT NULL,
  `royalty` int(11) DEFAULT NULL,
  KEY `roysched_title_id` (`title_id`),
  CONSTRAINT `roysched_ibfk_1` FOREIGN KEY (`title_id`) REFERENCES `titles` (`title_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sales` (
  `stor_id` char(4) NOT NULL,
  `ord_num` varchar(20) NOT NULL,
  `ord_date` datetime NOT NULL,
  `qty` smallint(6) NOT NULL,
  `payterms` varchar(12) NOT NULL,
  `title_id` varchar(6) NOT NULL,
  PRIMARY KEY (`stor_id`,`ord_num`,`title_id`),
  KEY `sales_title_id` (`title_id`),
  CONSTRAINT `sales_ibfk_1` FOREIGN KEY (`stor_id`) REFERENCES `stores` (`stor_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sales_ibfk_2` FOREIGN KEY (`title_id`) REFERENCES `titles` (`title_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `stores` (
  `stor_id` char(4) NOT NULL,
  `stor_name` varchar(40) DEFAULT NULL,
  `stor_address` varchar(40) DEFAULT NULL,
  `city` varchar(20) DEFAULT NULL,
  `state` char(2) DEFAULT NULL,
  `zip` char(5) DEFAULT NULL,
  PRIMARY KEY (`stor_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `titleauthor` (
  `au_id` varchar(11) NOT NULL,
  `title_id` varchar(6) NOT NULL,
  `au_ord` tinyint(4) DEFAULT NULL,
  `royaltyper` int(11) DEFAULT NULL,
  PRIMARY KEY (`au_id`,`title_id`),
  KEY `titleauthor_title_id` (`title_id`),
  CONSTRAINT `titleauthor_ibfk_1` FOREIGN KEY (`title_id`) REFERENCES `titles` (`title_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `titleauthor_ibfk_2` FOREIGN KEY (`au_id`) REFERENCES `authors` (`au_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `titles` (
  `title_id` varchar(6) NOT NULL,
  `title` varchar(80) NOT NULL,
  `type` char(12) NOT NULL,
  `pub_id` char(4) DEFAULT NULL,
  `price` decimal(19,4) DEFAULT NULL,
  `advance` decimal(19,4) DEFAULT NULL,
  `royalty` int(11) DEFAULT NULL,
  `ytd_sales` int(11) DEFAULT NULL,
  `notes` varchar(200) DEFAULT NULL,
  `pubdate` datetime NOT NULL,
  PRIMARY KEY (`title_id`),
  KEY `titles_pub_id` (`pub_id`),
  CONSTRAINT `titles_ibfk_1` FOREIGN KEY (`pub_id`) REFERENCES `publishers` (`pub_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

