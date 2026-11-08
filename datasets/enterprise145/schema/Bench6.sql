-- Schema for database: Bench6

CREATE TABLE `ATOMS` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `DRUG_ID` int(11) DEFAULT NULL,
  `ELEMENT` varchar(2) DEFAULT NULL,
  `ATOM_TYPE` int(11) DEFAULT NULL,
  `CHARGE` float DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `ATOMS_DRUG_ID` (`DRUG_ID`),
  CONSTRAINT `ATOMS_IBFK_1` FOREIGN KEY (`DRUG_ID`) REFERENCES `DRUGS` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `BONDS` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `DRUG_ID` int(11) DEFAULT NULL,
  `ATOM1_ID` int(11) DEFAULT NULL,
  `ATOM2_ID` int(11) DEFAULT NULL,
  `BOND_TYPE` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `BONDS_DRUG_ID` (`DRUG_ID`),
  KEY `BONDS_ATOM1_ID` (`ATOM1_ID`),
  KEY `BONDS_ATOM2_ID` (`ATOM2_ID`),
  CONSTRAINT `BONDS_IBFK_1` FOREIGN KEY (`DRUG_ID`) REFERENCES `DRUGS` (`ID`),
  CONSTRAINT `BONDS_IBFK_2` FOREIGN KEY (`ATOM1_ID`) REFERENCES `ATOMS` (`ID`),
  CONSTRAINT `BONDS_IBFK_3` FOREIGN KEY (`ATOM2_ID`) REFERENCES `ATOMS` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `DRUGS` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `IND1` float DEFAULT NULL,
  `INDA` float DEFAULT NULL,
  `ACT` float DEFAULT NULL,
  `LOGP` float DEFAULT NULL,
  `LUMO` float DEFAULT NULL,
  `ACTIVE` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `LEGALACTS` (
  `ID` int(11) NOT NULL,
  `HASH` char(32) NOT NULL,
  `UPDATE` timestamp NOT NULL DEFAULT current_timestamp(),
  `COURT` varchar(100) DEFAULT NULL,
  `CASEKIND` varchar(50) DEFAULT NULL,
  `CASENUMBER` smallint(6) DEFAULT NULL,
  `ACTYEAR` smallint(6) DEFAULT NULL,
  `JUDGE` varchar(255) DEFAULT NULL,
  `ACTKIND` varchar(20) DEFAULT NULL,
  `ACTNUMBER` smallint(6) DEFAULT NULL,
  `STARTDATE` date DEFAULT NULL,
  `LEGALDATE` date DEFAULT NULL,
  `STATUS` varchar(20) DEFAULT NULL,
  `ACTLINK` tinyint(1) NOT NULL DEFAULT 0,
  `MOTIVEDATE` date DEFAULT NULL,
  `MOTIVELINK` tinyint(1) NOT NULL DEFAULT 0,
  `HIGHCOURT` varchar(100) DEFAULT NULL,
  `OUTNUMBER` smallint(6) DEFAULT NULL,
  `YEARHIGHERCOURT` smallint(6) DEFAULT NULL,
  `TYPEOFDOCUMENT` varchar(100) DEFAULT NULL,
  `SENDDATE` date DEFAULT NULL,
  `RESULTOFAPPEAL` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `LEGALACT_LINK` (
  `ACTID1` int(11) NOT NULL,
  `ACTID2` int(11) NOT NULL,
  PRIMARY KEY (`ACTID1`,`ACTID2`),
  KEY `ACTID2` (`ACTID2`),
  CONSTRAINT `LEGALACT_LINK_IBFK_1` FOREIGN KEY (`ACTID1`) REFERENCES `LEGALACTS` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `LEGALACT_LINK_IBFK_2` FOREIGN KEY (`ACTID2`) REFERENCES `LEGALACTS` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `LEGALACT_PEOPLE` (
  `PEOPLEID` int(11) NOT NULL,
  `ACTID` int(11) NOT NULL,
  PRIMARY KEY (`PEOPLEID`,`ACTID`),
  KEY `ACTID` (`ACTID`),
  CONSTRAINT `LEGALACT_PEOPLE_IBFK_1` FOREIGN KEY (`PEOPLEID`) REFERENCES `PEOPLE` (`PERSONID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `LEGALACT_PEOPLE_IBFK_2` FOREIGN KEY (`ACTID`) REFERENCES `LEGALACTS` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `PEOPLE` (
  `PERSONID` int(11) NOT NULL AUTO_INCREMENT,
  `NAME` varchar(255) NOT NULL,
  `JURY` tinyint(1) NOT NULL DEFAULT 0,
  `COURT` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`PERSONID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `RINGS` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `RING_STRUC_ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `RINGS_RING_STRUC_ID` (`RING_STRUC_ID`),
  CONSTRAINT `RINGS_IBFK_1` FOREIGN KEY (`RING_STRUC_ID`) REFERENCES `RING_STRUCS` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `RING_ATOM` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `RING_ID` int(11) DEFAULT NULL,
  `ATOM_ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `RING_ATOM_RING_ID` (`RING_ID`),
  KEY `RING_ATOM_ATOM_ID` (`ATOM_ID`),
  CONSTRAINT `RING_ATOM_IBFK_1` FOREIGN KEY (`RING_ID`) REFERENCES `RINGS` (`ID`),
  CONSTRAINT `RING_ATOM_IBFK_2` FOREIGN KEY (`ATOM_ID`) REFERENCES `ATOMS` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `RING_STRUCS` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `DRUG_ID` int(11) DEFAULT NULL,
  `NAME` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `RING_STRUCTS_DRUG_ID` (`DRUG_ID`),
  CONSTRAINT `RING_STRUCS_IBFK_1` FOREIGN KEY (`DRUG_ID`) REFERENCES `DRUGS` (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `SCRAPEFIX` (
  `ACTID` int(11) NOT NULL,
  `FIX_DESCRIPTION` text NOT NULL,
  `CONTRIBUTOR` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`ACTID`),
  CONSTRAINT `SCRAPEFIX_IBFK_1` FOREIGN KEY (`ACTID`) REFERENCES `LEGALACTS` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `course` (
  `course_id` int(11) NOT NULL,
  `rating` varchar(45) DEFAULT NULL,
  `diff` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `course_rating` (`rating`),
  KEY `course_diff` (`diff`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `key` (
  `store_nbr` int(11) NOT NULL,
  `station_nbr` int(11) DEFAULT NULL,
  PRIMARY KEY (`store_nbr`),
  UNIQUE KEY `key_store_nbr_key` (`store_nbr`),
  KEY `key_station_nbr_fkey` (`station_nbr`),
  CONSTRAINT `key_station_nbr_fkey` FOREIGN KEY (`station_nbr`) REFERENCES `station` (`station_nbr`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `prof` (
  `prof_id` int(11) NOT NULL DEFAULT 0,
  `popularity` varchar(45) DEFAULT NULL,
  `teachingability` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`prof_id`),
  KEY `prof_popularity` (`popularity`),
  KEY `prof_teachingability` (`teachingability`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `ra` (
  `capability` varchar(45) DEFAULT NULL,
  `prof_id` int(11) NOT NULL DEFAULT 0,
  `student_id` int(11) NOT NULL DEFAULT 0,
  `salary` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`prof_id`,`student_id`),
  KEY `ra_capability` (`capability`),
  KEY `ra_salary` (`salary`),
  KEY `ra_student_id` (`student_id`),
  KEY `ra_prof_id` (`prof_id`),
  CONSTRAINT `fk_ra_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_ra_2` FOREIGN KEY (`prof_id`) REFERENCES `prof` (`prof_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `registration` (
  `course_id` int(11) NOT NULL DEFAULT 0,
  `student_id` int(11) NOT NULL DEFAULT 0,
  `grade` varchar(45) NOT NULL,
  `sat` varchar(45) NOT NULL,
  PRIMARY KEY (`course_id`,`student_id`),
  KEY `registration_sat` (`sat`),
  KEY `registration_grade` (`grade`),
  KEY `registration_student_id` (`student_id`),
  KEY `registration_course_id` (`course_id`),
  CONSTRAINT `fk_registration_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_registration_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `station` (
  `station_nbr` int(11) NOT NULL,
  PRIMARY KEY (`station_nbr`),
  UNIQUE KEY `station_station_nbr_key` (`station_nbr`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `student` (
  `student_id` int(11) NOT NULL DEFAULT 0,
  `intelligence` varchar(45) DEFAULT NULL,
  `ranking` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  KEY `student_intelligence` (`intelligence`),
  KEY `student_ranking` (`ranking`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `train` (
  `date` date NOT NULL,
  `store_nbr` int(11) NOT NULL,
  `item_nbr` int(11) NOT NULL,
  `units` int(11) DEFAULT NULL,
  PRIMARY KEY (`store_nbr`,`date`,`item_nbr`),
  CONSTRAINT `train_store_nbr_fkey` FOREIGN KEY (`store_nbr`) REFERENCES `key` (`store_nbr`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `weather` (
  `station_nbr` int(11) NOT NULL,
  `date` date NOT NULL,
  `tmax` int(11) DEFAULT NULL,
  `tmin` int(11) DEFAULT NULL,
  `tavg` int(11) DEFAULT NULL,
  `depart` int(11) DEFAULT NULL,
  `dewpoint` int(11) DEFAULT NULL,
  `wetbulb` int(11) DEFAULT NULL,
  `heat` int(11) DEFAULT NULL,
  `cool` int(11) DEFAULT NULL,
  `sunrise` time DEFAULT NULL,
  `sunset` time DEFAULT NULL,
  `codesum` varchar(255) DEFAULT NULL,
  `snowfall` float DEFAULT NULL,
  `preciptotal` float DEFAULT NULL,
  `stnpressure` float DEFAULT NULL,
  `sealevel` float DEFAULT NULL,
  `resultspeed` float DEFAULT NULL,
  `resultdir` int(11) DEFAULT NULL,
  `avgspeed` float DEFAULT NULL,
  PRIMARY KEY (`station_nbr`,`date`),
  CONSTRAINT `weather_station_nbr_fkey` FOREIGN KEY (`station_nbr`) REFERENCES `station` (`station_nbr`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

