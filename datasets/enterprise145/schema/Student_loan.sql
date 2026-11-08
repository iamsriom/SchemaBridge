-- Schema for database: Student_loan

CREATE TABLE `bool` (
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `disabled` (
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `disabled_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `enlist` (
  `name` varchar(50) NOT NULL,
  `organ` varchar(50) NOT NULL,
  KEY `name` (`name`),
  KEY `organ` (`organ`),
  CONSTRAINT `enlist_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `enrolled` (
  `name` varchar(50) NOT NULL,
  `school` varchar(50) NOT NULL,
  `month` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`name`,`school`),
  KEY `month` (`month`),
  KEY `name` (`name`),
  KEY `school` (`school`),
  CONSTRAINT `enrolled_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `filed_for_bankrupcy` (
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `filed_for_bankrupcy_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `longest_absense_from_school` (
  `name` varchar(50) NOT NULL DEFAULT '',
  `month` int(11) DEFAULT 0,
  PRIMARY KEY (`name`),
  KEY `month` (`month`),
  KEY `name` (`name`),
  CONSTRAINT `longest_absense_from_school_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `male` (
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `male_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `no_payment_due` (
  `name` varchar(50) NOT NULL DEFAULT '',
  `bool` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `bool` (`bool`),
  KEY `name` (`name`),
  CONSTRAINT `no_payment_due_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `no_payment_due_ibfk_2` FOREIGN KEY (`bool`) REFERENCES `bool` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `person` (
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `unemployed` (
  `name` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `unemployed_ibfk_1` FOREIGN KEY (`name`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

