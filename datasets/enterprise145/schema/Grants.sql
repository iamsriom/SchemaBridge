-- Schema for database: Grants

CREATE TABLE `awards` (
  `award_title` varchar(300) DEFAULT NULL,
  `award_effective_date` varchar(20) DEFAULT NULL,
  `award_expiration_date` varchar(20) DEFAULT NULL,
  `award_amount` int(11) DEFAULT NULL,
  `award_instrument` varchar(50) DEFAULT NULL,
  `organisation_code` int(11) DEFAULT NULL,
  `program_officer` varchar(50) DEFAULT NULL,
  `abstract_narration` varchar(3000) DEFAULT NULL,
  `min_amd_letter_date` varchar(20) DEFAULT NULL,
  `max_amd_letter_date` varchar(20) DEFAULT NULL,
  `arra_amount` int(11) DEFAULT NULL,
  `award_id` int(11) NOT NULL,
  PRIMARY KEY (`award_id`) USING BTREE,
  KEY `organisation_code` (`organisation_code`) USING BTREE,
  CONSTRAINT `awards_ibfk_1` FOREIGN KEY (`organisation_code`) REFERENCES `organization` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `foa_info` (
  `code` int(11) NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `foa_info_awards` (
  `award_id` int(11) NOT NULL,
  `code` int(11) NOT NULL,
  PRIMARY KEY (`award_id`,`code`) USING BTREE,
  KEY `code` (`code`) USING BTREE,
  CONSTRAINT `foa_info_awards_ibfk_1` FOREIGN KEY (`code`) REFERENCES `foa_info` (`code`),
  CONSTRAINT `foa_info_awards_ibfk_2` FOREIGN KEY (`award_id`) REFERENCES `awards` (`award_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `institution` (
  `name` varchar(100) NOT NULL,
  `city_name` varchar(50) DEFAULT NULL,
  `zipcode` varchar(50) NOT NULL,
  `contact` int(11) DEFAULT NULL,
  `address` varchar(100) DEFAULT NULL,
  `country_name` varchar(30) DEFAULT NULL,
  `state_name` varchar(30) DEFAULT NULL,
  `state_code` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`name`,`zipcode`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `institution_awards` (
  `award_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `zipcode` varchar(50) NOT NULL,
  PRIMARY KEY (`award_id`,`name`,`zipcode`) USING BTREE,
  KEY `name` (`name`,`zipcode`) USING BTREE,
  CONSTRAINT `institution_awards_ibfk_1` FOREIGN KEY (`award_id`) REFERENCES `awards` (`award_id`),
  CONSTRAINT `institution_awards_ibfk_2` FOREIGN KEY (`name`, `zipcode`) REFERENCES `institution` (`name`, `zipcode`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `investigator` (
  `email_id` varchar(50) NOT NULL,
  `first_name` varchar(30) DEFAULT NULL,
  `last_name` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`email_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `investigator_awards` (
  `award_id` int(11) NOT NULL,
  `email_id` varchar(50) NOT NULL,
  `start_date` varchar(20) DEFAULT NULL,
  `end_date` varchar(20) DEFAULT NULL,
  `role_code` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`award_id`,`email_id`) USING BTREE,
  KEY `email_id` (`email_id`) USING BTREE,
  CONSTRAINT `investigator_awards_ibfk_1` FOREIGN KEY (`award_id`) REFERENCES `awards` (`award_id`),
  CONSTRAINT `investigator_awards_ibfk_2` FOREIGN KEY (`email_id`) REFERENCES `investigator` (`email_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `organization` (
  `code` int(11) NOT NULL,
  `division` varchar(100) DEFAULT NULL,
  `directorate` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `program_element` (
  `code` varchar(20) NOT NULL,
  `text` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `program_element_awards` (
  `award_id` int(11) NOT NULL,
  `code` varchar(20) NOT NULL,
  PRIMARY KEY (`award_id`,`code`) USING BTREE,
  KEY `code` (`code`) USING BTREE,
  CONSTRAINT `program_element_awards_ibfk_1` FOREIGN KEY (`code`) REFERENCES `program_element` (`code`),
  CONSTRAINT `program_element_awards_ibfk_2` FOREIGN KEY (`award_id`) REFERENCES `awards` (`award_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `program_reference` (
  `code` varchar(20) NOT NULL,
  `text` varchar(150) DEFAULT NULL,
  PRIMARY KEY (`code`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `program_reference_awards` (
  `award_id` int(11) NOT NULL,
  `code` varchar(20) NOT NULL,
  PRIMARY KEY (`award_id`,`code`) USING BTREE,
  KEY `code` (`code`) USING BTREE,
  CONSTRAINT `program_reference_awards_ibfk_1` FOREIGN KEY (`code`) REFERENCES `program_reference` (`code`),
  CONSTRAINT `program_reference_awards_ibfk_2` FOREIGN KEY (`award_id`) REFERENCES `awards` (`award_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

