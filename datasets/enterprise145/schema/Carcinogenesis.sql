-- Schema for database: Carcinogenesis

CREATE TABLE `atom` (
  `atomid` char(100) NOT NULL,
  `drug` char(100) DEFAULT NULL,
  `atomtype` char(100) DEFAULT NULL,
  `charge` char(100) DEFAULT NULL,
  `name` char(2) DEFAULT NULL,
  PRIMARY KEY (`atomid`),
  KEY `atom_drug` (`drug`) USING BTREE,
  CONSTRAINT `atom_ibfk_1` FOREIGN KEY (`drug`) REFERENCES `canc` (`drug_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `canc` (
  `drug_id` char(100) NOT NULL,
  `class` char(1) DEFAULT NULL,
  PRIMARY KEY (`drug_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `sbond_1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `drug` char(100) DEFAULT NULL,
  `atomid` char(100) DEFAULT NULL,
  `atomid_2` char(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sbond_1_drug` (`drug`) USING BTREE,
  KEY `sbond_1_atomid` (`atomid`) USING BTREE,
  KEY `sbond_1_atomid_2` (`atomid_2`) USING BTREE,
  CONSTRAINT `sbond_1_ibfk_1` FOREIGN KEY (`drug`) REFERENCES `canc` (`drug_id`),
  CONSTRAINT `sbond_1_ibfk_2` FOREIGN KEY (`atomid`) REFERENCES `atom` (`atomid`),
  CONSTRAINT `sbond_1_ibfk_3` FOREIGN KEY (`atomid_2`) REFERENCES `atom` (`atomid`)
) ENGINE=InnoDB AUTO_INCREMENT=13563 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `sbond_2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `drug` char(100) DEFAULT NULL,
  `atomid` char(100) DEFAULT NULL,
  `atomid_2` char(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sbond_2_drug` (`drug`) USING BTREE,
  KEY `sbond_2_atomid` (`atomid`) USING BTREE,
  KEY `sbond_2_atomid_2` (`atomid_2`) USING BTREE,
  CONSTRAINT `sbond_2_ibfk_1` FOREIGN KEY (`drug`) REFERENCES `canc` (`drug_id`),
  CONSTRAINT `sbond_2_ibfk_2` FOREIGN KEY (`atomid`) REFERENCES `atom` (`atomid`),
  CONSTRAINT `sbond_2_ibfk_3` FOREIGN KEY (`atomid_2`) REFERENCES `atom` (`atomid`)
) ENGINE=InnoDB AUTO_INCREMENT=927 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `sbond_3` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `drug` char(100) DEFAULT NULL,
  `atomid` char(100) DEFAULT NULL,
  `atomid_2` char(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sbond_3_drug` (`drug`) USING BTREE,
  KEY `sbond_3_atomid` (`atomid`) USING BTREE,
  KEY `sbond_3_atomid_2` (`atomid_2`) USING BTREE,
  CONSTRAINT `sbond_3_ibfk_1` FOREIGN KEY (`drug`) REFERENCES `canc` (`drug_id`),
  CONSTRAINT `sbond_3_ibfk_2` FOREIGN KEY (`atomid`) REFERENCES `atom` (`atomid`),
  CONSTRAINT `sbond_3_ibfk_3` FOREIGN KEY (`atomid_2`) REFERENCES `atom` (`atomid`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `sbond_7` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `drug` char(100) DEFAULT NULL,
  `atomid` char(100) DEFAULT NULL,
  `atomid_2` char(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `sbond_7_drug` (`drug`) USING BTREE,
  KEY `sbond_7_atomid` (`atomid`) USING BTREE,
  KEY `sbond_7_atomid_2` (`atomid_2`) USING BTREE,
  CONSTRAINT `sbond_7_ibfk_1` FOREIGN KEY (`drug`) REFERENCES `canc` (`drug_id`),
  CONSTRAINT `sbond_7_ibfk_2` FOREIGN KEY (`atomid`) REFERENCES `atom` (`atomid`),
  CONSTRAINT `sbond_7_ibfk_3` FOREIGN KEY (`atomid_2`) REFERENCES `atom` (`atomid`)
) ENGINE=InnoDB AUTO_INCREMENT=4135 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

