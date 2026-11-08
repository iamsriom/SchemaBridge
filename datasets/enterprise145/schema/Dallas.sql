-- Schema for database: Dallas

CREATE TABLE `incidents` (
  `case_number` varchar(255) NOT NULL,
  `date` date NOT NULL,
  `location` varchar(255) NOT NULL,
  `subject_statuses` varchar(255) NOT NULL,
  `subject_weapon` varchar(255) NOT NULL,
  `subjects` varchar(255) NOT NULL,
  `subject_count` int(11) NOT NULL,
  `officers` varchar(2550) NOT NULL,
  `officer_count` int(11) NOT NULL,
  `grand_jury_disposition` varchar(255) DEFAULT NULL,
  `attorney_general_forms_url` varchar(255) DEFAULT NULL,
  `summary_url` varchar(255) DEFAULT NULL,
  `summary_text` varchar(2550) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  PRIMARY KEY (`case_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `officers` (
  `case_number` varchar(255) NOT NULL,
  `race` char(1) DEFAULT NULL,
  `gender` char(1) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `full_name` varchar(255) NOT NULL,
  KEY `case_number` (`case_number`),
  CONSTRAINT `officers_ibfk_1` FOREIGN KEY (`case_number`) REFERENCES `incidents` (`case_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `subjects` (
  `case_number` varchar(255) NOT NULL,
  `race` char(1) NOT NULL,
  `gender` char(1) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `full_name` varchar(255) NOT NULL,
  KEY `case_number` (`case_number`),
  CONSTRAINT `subjects_ibfk_1` FOREIGN KEY (`case_number`) REFERENCES `incidents` (`case_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

