-- Schema for database: Hepatitis_std

CREATE TABLE `Bio` (
  `fibros` varchar(45) NOT NULL,
  `activity` varchar(45) NOT NULL,
  `b_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`b_id`),
  KEY `Hepatitis_fibros` (`fibros`),
  KEY `Hepatitis_activity` (`activity`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci AVG_ROW_LENGTH=512
;


CREATE TABLE `dispat` (
  `m_id` int(10) unsigned NOT NULL DEFAULT 0,
  `sex` varchar(45) DEFAULT NULL COMMENT 'Type: Categorical; Aggr: COUNT',
  `age` varchar(45) DEFAULT NULL,
  `Type` varchar(45) DEFAULT NULL COMMENT 'Type: Categorical; Aggr: B, C',
  PRIMARY KEY (`m_id`),
  KEY `dispat_sex` (`sex`),
  KEY `dispat_age` (`age`),
  KEY `dispat_Type` (`Type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci AVG_ROW_LENGTH=85
;


CREATE TABLE `indis` (
  `got` varchar(10) DEFAULT NULL,
  `gpt` varchar(10) DEFAULT NULL,
  `alb` varchar(45) DEFAULT NULL,
  `tbil` varchar(45) DEFAULT NULL,
  `dbil` varchar(45) DEFAULT NULL,
  `che` varchar(45) DEFAULT NULL,
  `ttt` varchar(45) DEFAULT NULL,
  `ztt` varchar(45) DEFAULT NULL,
  `tcho` varchar(45) DEFAULT NULL,
  `tp` varchar(45) DEFAULT NULL,
  `in_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`in_id`),
  KEY `indis_got` (`got`),
  KEY `indis_gpt` (`gpt`),
  KEY `indis_alb` (`alb`),
  KEY `indis_tbil` (`tbil`),
  KEY `indis_dbil` (`dbil`),
  KEY `indis_che` (`che`),
  KEY `indis_ttt` (`ttt`),
  KEY `indis_ztt` (`ztt`),
  KEY `indis_tcho` (`tcho`),
  KEY `indis_tp` (`tp`)
) ENGINE=InnoDB AUTO_INCREMENT=5692 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci AVG_ROW_LENGTH=50
;


CREATE TABLE `inf` (
  `dur` varchar(45) DEFAULT NULL,
  `a_id` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`a_id`),
  KEY `inf_dur` (`dur`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci AVG_ROW_LENGTH=83
;


CREATE TABLE `rel11` (
  `b_id` int(10) unsigned NOT NULL DEFAULT 0,
  `m_id` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`b_id`,`m_id`),
  KEY `FK_rel11_2` (`m_id`),
  CONSTRAINT `FK_rel11_1` FOREIGN KEY (`b_id`) REFERENCES `Bio` (`b_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_rel11_2` FOREIGN KEY (`m_id`) REFERENCES `dispat` (`m_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci AVG_ROW_LENGTH=63
;


CREATE TABLE `rel12` (
  `in_id` int(10) unsigned NOT NULL DEFAULT 0,
  `m_id` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`in_id`,`m_id`),
  KEY `FK_rel12_1` (`m_id`),
  CONSTRAINT `FK_rel12_1` FOREIGN KEY (`m_id`) REFERENCES `dispat` (`m_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_rel12_2` FOREIGN KEY (`in_id`) REFERENCES `indis` (`in_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci AVG_ROW_LENGTH=42
;


CREATE TABLE `rel13` (
  `a_id` int(10) unsigned NOT NULL DEFAULT 0,
  `m_id` int(10) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`a_id`,`m_id`),
  KEY `FK_rel13_1` (`m_id`),
  CONSTRAINT `FK_rel13_1` FOREIGN KEY (`m_id`) REFERENCES `dispat` (`m_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_rel13_2` FOREIGN KEY (`a_id`) REFERENCES `inf` (`a_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci AVG_ROW_LENGTH=83
;

