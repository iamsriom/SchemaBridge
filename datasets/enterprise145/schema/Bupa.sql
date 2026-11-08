-- Schema for database: Bupa

CREATE TABLE `alkphos` (
  `arg1` varchar(4) NOT NULL,
  `arg2` int(11) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `alkphos_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `alkphos_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `bupa_name` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `bupa` (
  `arg1` varchar(4) NOT NULL,
  `arg2` varchar(1) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `bupa_arg1` (`arg1`) USING BTREE,
  KEY `bupa_arg2` (`arg2`) USING BTREE,
  CONSTRAINT `bupa_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `bupa_name` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `bupa_ibfk_2` FOREIGN KEY (`arg2`) REFERENCES `bupa_type` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `bupa_name` (
  `arg1` varchar(4) NOT NULL,
  PRIMARY KEY (`arg1`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `bupa_type` (
  `arg1` varchar(1) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `bupa_type_arg1` (`arg1`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `drinks` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `drinks_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `drinks_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `bupa_name` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `gammagt` (
  `arg1` varchar(4) NOT NULL,
  `arg2` int(11) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `gammagt_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `gammagt_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `bupa_name` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `mcv` (
  `arg1` varchar(4) NOT NULL,
  `arg2` int(11) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `mcv_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `mcv_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `bupa_name` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `sgot` (
  `arg1` varchar(4) NOT NULL,
  `arg2` int(11) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `sgot_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `sgot_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `bupa_name` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `sgpt` (
  `arg1` varchar(4) NOT NULL,
  `arg2` int(11) NOT NULL,
  PRIMARY KEY (`arg1`),
  KEY `sgpt_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `sgpt_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `bupa_name` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

