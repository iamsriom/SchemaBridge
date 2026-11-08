-- Schema for database: Pima

CREATE TABLE `age` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `age_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `age_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `bmi` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `bmi_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `bmi_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `diastolic` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `diastolic_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `diastolic_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `numPreg` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `numPreg_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `numPreg_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `pedigree` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `pedigree_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `pedigree_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `pima` (
  `arg1` varchar(4) NOT NULL,
  `arg2` varchar(1) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `pima_arg1` (`arg1`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `plasma` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `plasma_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `plasma_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `serum` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `serum_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `serum_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `tricepts` (
  `arg1` varchar(4) NOT NULL,
  `arg2` decimal(18,3) DEFAULT NULL,
  PRIMARY KEY (`arg1`),
  KEY `tricepts_arg1` (`arg1`) USING BTREE,
  CONSTRAINT `tricepts_ibfk_1` FOREIGN KEY (`arg1`) REFERENCES `pima` (`arg1`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

