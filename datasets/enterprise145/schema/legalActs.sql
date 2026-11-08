-- Schema for database: legalActs

CREATE TABLE `legalact_link` (
  `actId1` int(11) NOT NULL,
  `actId2` int(11) NOT NULL,
  PRIMARY KEY (`actId1`,`actId2`),
  KEY `actId2` (`actId2`),
  CONSTRAINT `legalact_link_ibfk_1` FOREIGN KEY (`actId1`) REFERENCES `legalacts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `legalact_link_ibfk_2` FOREIGN KEY (`actId2`) REFERENCES `legalacts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `legalact_people` (
  `peopleId` int(11) NOT NULL,
  `actId` int(11) NOT NULL,
  PRIMARY KEY (`peopleId`,`actId`),
  KEY `actId` (`actId`),
  CONSTRAINT `legalact_people_ibfk_1` FOREIGN KEY (`peopleId`) REFERENCES `people` (`personId`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `legalact_people_ibfk_2` FOREIGN KEY (`actId`) REFERENCES `legalacts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `legalacts` (
  `id` int(11) NOT NULL,
  `hash` char(32) NOT NULL,
  `update` timestamp NOT NULL DEFAULT current_timestamp(),
  `Court` varchar(100) DEFAULT NULL,
  `CaseKind` varchar(50) DEFAULT NULL,
  `CaseNumber` smallint(6) DEFAULT NULL,
  `ActYear` smallint(6) DEFAULT NULL,
  `Judge` varchar(255) DEFAULT NULL,
  `ActKind` varchar(20) DEFAULT NULL,
  `ActNumber` smallint(6) DEFAULT NULL,
  `StartDate` date DEFAULT NULL,
  `LegalDate` date DEFAULT NULL,
  `Status` varchar(20) DEFAULT NULL,
  `ActLink` tinyint(1) NOT NULL DEFAULT 0,
  `MotiveDate` date DEFAULT NULL,
  `MotiveLink` tinyint(1) NOT NULL DEFAULT 0,
  `HighCourt` varchar(100) DEFAULT NULL,
  `OutNumber` smallint(6) DEFAULT NULL,
  `YearHigherCourt` smallint(6) DEFAULT NULL,
  `TypeOfDocument` varchar(100) DEFAULT NULL,
  `SendDate` date DEFAULT NULL,
  `ResultOfAppeal` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `people` (
  `personId` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `jury` tinyint(1) NOT NULL DEFAULT 0,
  `court` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`personId`)
) ENGINE=InnoDB AUTO_INCREMENT=3790 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `scrapefix` (
  `actId` int(11) NOT NULL,
  `fix_description` text NOT NULL,
  `contributor` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`actId`),
  CONSTRAINT `scrapefix_ibfk_1` FOREIGN KEY (`actId`) REFERENCES `legalacts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

