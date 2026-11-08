-- Schema for database: Elti

CREATE TABLE `brother` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother_name1` (`name1`),
  KEY `brother_name2` (`name2`),
  CONSTRAINT `brother_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `brother_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter_name1` (`name1`),
  KEY `daughter_name2` (`name2`),
  CONSTRAINT `daughter_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `daughter_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `elti` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `elti_name1` (`name1`),
  KEY `elti_name2` (`name2`),
  CONSTRAINT `elti_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `elti_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `father_name1` (`name1`),
  KEY `father_name2` (`name2`),
  CONSTRAINT `father_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `father_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband_name1` (`name1`),
  KEY `husband_name2` (`name2`),
  CONSTRAINT `husband_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `husband_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother_name1` (`name1`),
  KEY `mother_name2` (`name2`),
  CONSTRAINT `mother_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `mother_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `person` (
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `person_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister_name1` (`name1`),
  KEY `sister_name2` (`name2`),
  CONSTRAINT `sister_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sister_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `son_name1` (`name1`),
  KEY `son_name2` (`name2`),
  CONSTRAINT `son_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `son_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  `is_elti` bigint(20) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `target_name1` (`name1`),
  KEY `target_name2` (`name2`),
  CONSTRAINT `target_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `target_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `wife` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `wife_name1` (`name1`),
  KEY `wife_name2` (`name2`),
  CONSTRAINT `wife_name1_fkey` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `wife_name2_fkey` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

