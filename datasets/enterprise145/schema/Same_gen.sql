-- Schema for database: Same_gen

CREATE TABLE `parent` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `parent_name1` (`name1`) USING BTREE,
  KEY `parent_name2` (`name2`) USING BTREE,
  CONSTRAINT `parent_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `parent_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `person` (
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `person_name` (`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `same_gen` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  PRIMARY KEY (`name1`,`name2`),
  KEY `same_gen_name1` (`name1`) USING BTREE,
  KEY `same_gen_name2` (`name2`) USING BTREE,
  CONSTRAINT `same_gen_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `same_gen_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `name1` varchar(50) NOT NULL,
  `name2` varchar(50) NOT NULL,
  `target` int(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`name1`,`name2`),
  KEY `target_name1` (`name1`) USING BTREE,
  KEY `target_name2` (`name2`) USING BTREE,
  CONSTRAINT `target_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `target_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

