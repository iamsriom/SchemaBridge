-- Schema for database: Dunur

CREATE TABLE `aunt` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `aunt_name1` (`name1`) USING BTREE,
  KEY `aunt_name2` (`name2`) USING BTREE,
  CONSTRAINT `aunt_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `aunt_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `brother` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother_name1` (`name1`) USING BTREE,
  KEY `brother_name2` (`name2`) USING BTREE,
  CONSTRAINT `brother_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `brother_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter_name1` (`name1`) USING BTREE,
  KEY `daughter_name2` (`name2`) USING BTREE,
  CONSTRAINT `daughter_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `daughter_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dunur` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `dunur_name1` (`name1`) USING BTREE,
  KEY `dunur_name2` (`name2`) USING BTREE,
  CONSTRAINT `dunur_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `dunur_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `father_name1` (`name1`) USING BTREE,
  KEY `father_name2` (`name2`) USING BTREE,
  CONSTRAINT `father_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `father_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband_name1` (`name1`) USING BTREE,
  KEY `husband_name2` (`name2`) USING BTREE,
  CONSTRAINT `husband_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `husband_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband2` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband2_name1` (`name1`) USING BTREE,
  KEY `husband2_name2` (`name2`) USING BTREE,
  CONSTRAINT `husband2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `husband2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother_name1` (`name1`) USING BTREE,
  KEY `mother_name2` (`name2`) USING BTREE,
  CONSTRAINT `mother_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `mother_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nephew` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `nephew_name1` (`name1`) USING BTREE,
  KEY `nephew_name2` (`name2`) USING BTREE,
  CONSTRAINT `nephew_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `nephew_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `niece` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `niece_name1` (`name1`) USING BTREE,
  KEY `niece_name2` (`name2`) USING BTREE,
  CONSTRAINT `niece_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `niece_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `person` (
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `person_name` (`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister_name1` (`name1`) USING BTREE,
  KEY `sister_name2` (`name2`) USING BTREE,
  CONSTRAINT `sister_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `sister_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `son_name1` (`name1`) USING BTREE,
  KEY `son_name2` (`name2`) USING BTREE,
  CONSTRAINT `son_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `son_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  `is_dunur` bigint(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`name1`,`name2`),
  KEY `target_name1` (`name1`) USING BTREE,
  KEY `target_name2` (`name2`) USING BTREE,
  CONSTRAINT `target_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `target_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `uncle` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `uncle_name1` (`name1`) USING BTREE,
  KEY `uncle_name2` (`name2`) USING BTREE,
  CONSTRAINT `uncle_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `uncle_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `wife` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `wife_name1` (`name1`) USING BTREE,
  KEY `wife_name2` (`name2`) USING BTREE,
  CONSTRAINT `wife_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `wife_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `wife2` (
  `name1` varchar(50) NOT NULL DEFAULT '',
  `name2` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `wife2_name1` (`name1`) USING BTREE,
  KEY `wife2_name2` (`name2`) USING BTREE,
  CONSTRAINT `wife2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `wife2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

