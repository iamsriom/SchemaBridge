-- Schema for database: ErgastF1

CREATE TABLE `circuits` (
  `circuitId` int(11) NOT NULL AUTO_INCREMENT,
  `circuitRef` varchar(255) NOT NULL DEFAULT '',
  `name` varchar(255) NOT NULL DEFAULT '',
  `location` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `lat` float DEFAULT NULL,
  `lng` float DEFAULT NULL,
  `alt` int(11) DEFAULT NULL,
  `url` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`circuitId`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=74 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `constructorResults` (
  `constructorResultsId` int(11) NOT NULL AUTO_INCREMENT,
  `raceId` int(11) NOT NULL DEFAULT 0,
  `constructorId` int(11) NOT NULL DEFAULT 0,
  `points` float DEFAULT NULL,
  `status` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`constructorResultsId`),
  KEY `raceId` (`raceId`),
  KEY `constructorId` (`constructorId`),
  CONSTRAINT `constructorResults_ibfk_1` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`),
  CONSTRAINT `constructorResults_ibfk_2` FOREIGN KEY (`constructorId`) REFERENCES `constructors` (`constructorId`)
) ENGINE=InnoDB AUTO_INCREMENT=15580 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `constructorStandings` (
  `constructorStandingsId` int(11) NOT NULL AUTO_INCREMENT,
  `raceId` int(11) NOT NULL DEFAULT 0,
  `constructorId` int(11) NOT NULL DEFAULT 0,
  `points` float NOT NULL DEFAULT 0,
  `position` int(11) DEFAULT NULL,
  `positionText` varchar(255) DEFAULT NULL,
  `wins` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`constructorStandingsId`),
  KEY `raceId` (`raceId`),
  KEY `constructorId` (`constructorId`),
  CONSTRAINT `constructorStandings_ibfk_1` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`),
  CONSTRAINT `constructorStandings_ibfk_2` FOREIGN KEY (`constructorId`) REFERENCES `constructors` (`constructorId`)
) ENGINE=InnoDB AUTO_INCREMENT=26873 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `constructors` (
  `constructorId` int(11) NOT NULL AUTO_INCREMENT,
  `constructorRef` varchar(255) NOT NULL DEFAULT '',
  `name` varchar(255) NOT NULL DEFAULT '',
  `nationality` varchar(255) DEFAULT NULL,
  `url` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`constructorId`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=211 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `driverStandings` (
  `driverStandingsId` int(11) NOT NULL AUTO_INCREMENT,
  `raceId` int(11) NOT NULL DEFAULT 0,
  `driverId` int(11) NOT NULL DEFAULT 0,
  `points` float NOT NULL DEFAULT 0,
  `position` int(11) DEFAULT NULL,
  `positionText` varchar(255) DEFAULT NULL,
  `wins` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`driverStandingsId`),
  KEY `raceId` (`raceId`),
  KEY `driverId` (`driverId`),
  CONSTRAINT `driverStandings_ibfk_1` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`),
  CONSTRAINT `driverStandings_ibfk_2` FOREIGN KEY (`driverId`) REFERENCES `drivers` (`driverId`)
) ENGINE=InnoDB AUTO_INCREMENT=68461 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `drivers` (
  `driverId` int(11) NOT NULL AUTO_INCREMENT,
  `driverRef` varchar(255) NOT NULL DEFAULT '',
  `number` int(11) DEFAULT NULL,
  `code` varchar(3) DEFAULT NULL,
  `forename` varchar(255) NOT NULL DEFAULT '',
  `surname` varchar(255) NOT NULL DEFAULT '',
  `dob` date DEFAULT NULL,
  `nationality` varchar(255) DEFAULT NULL,
  `url` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`driverId`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=842 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `lapTimes` (
  `raceId` int(11) NOT NULL,
  `driverId` int(11) NOT NULL,
  `lap` int(11) NOT NULL,
  `position` int(11) DEFAULT NULL,
  `time` varchar(255) DEFAULT NULL,
  `milliseconds` int(11) DEFAULT NULL,
  PRIMARY KEY (`raceId`,`driverId`,`lap`),
  KEY `raceId` (`raceId`),
  KEY `driverId` (`driverId`),
  CONSTRAINT `lapTimes_ibfk_1` FOREIGN KEY (`driverId`) REFERENCES `drivers` (`driverId`),
  CONSTRAINT `lapTimes_ibfk_2` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pitStops` (
  `raceId` int(11) NOT NULL,
  `driverId` int(11) NOT NULL,
  `stop` int(11) NOT NULL,
  `lap` int(11) NOT NULL,
  `time` time NOT NULL,
  `duration` varchar(255) DEFAULT NULL,
  `milliseconds` int(11) DEFAULT NULL,
  PRIMARY KEY (`raceId`,`driverId`,`stop`),
  KEY `raceId` (`raceId`),
  KEY `driverId` (`driverId`),
  CONSTRAINT `pitStops_ibfk_1` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`),
  CONSTRAINT `pitStops_ibfk_2` FOREIGN KEY (`driverId`) REFERENCES `drivers` (`driverId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `qualifying` (
  `qualifyId` int(11) NOT NULL AUTO_INCREMENT,
  `raceId` int(11) NOT NULL DEFAULT 0,
  `driverId` int(11) NOT NULL DEFAULT 0,
  `constructorId` int(11) NOT NULL DEFAULT 0,
  `number` int(11) NOT NULL DEFAULT 0,
  `position` int(11) DEFAULT NULL,
  `q1` varchar(255) DEFAULT NULL,
  `q2` varchar(255) DEFAULT NULL,
  `q3` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`qualifyId`),
  KEY `constructorId` (`constructorId`),
  KEY `driverId` (`driverId`),
  KEY `raceId` (`raceId`),
  CONSTRAINT `qualifying_ibfk_1` FOREIGN KEY (`constructorId`) REFERENCES `constructors` (`constructorId`),
  CONSTRAINT `qualifying_ibfk_2` FOREIGN KEY (`driverId`) REFERENCES `drivers` (`driverId`),
  CONSTRAINT `qualifying_ibfk_3` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`)
) ENGINE=InnoDB AUTO_INCREMENT=7420 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `races` (
  `raceId` int(11) NOT NULL AUTO_INCREMENT,
  `year` int(11) NOT NULL DEFAULT 0,
  `round` int(11) NOT NULL DEFAULT 0,
  `circuitId` int(11) NOT NULL DEFAULT 0,
  `name` varchar(255) NOT NULL DEFAULT '',
  `date` date NOT NULL DEFAULT '0000-00-00',
  `time` time DEFAULT NULL,
  `url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`raceId`),
  UNIQUE KEY `url` (`url`),
  KEY `circuitId` (`circuitId`),
  KEY `year` (`year`),
  CONSTRAINT `races_ibfk_1` FOREIGN KEY (`circuitId`) REFERENCES `circuits` (`circuitId`),
  CONSTRAINT `races_ibfk_2` FOREIGN KEY (`year`) REFERENCES `seasons` (`year`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=989 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `results` (
  `resultId` int(11) NOT NULL AUTO_INCREMENT,
  `raceId` int(11) NOT NULL DEFAULT 0,
  `driverId` int(11) NOT NULL DEFAULT 0,
  `constructorId` int(11) NOT NULL DEFAULT 0,
  `number` int(11) DEFAULT NULL,
  `grid` int(11) NOT NULL DEFAULT 0,
  `position` int(11) DEFAULT NULL,
  `positionText` varchar(255) NOT NULL DEFAULT '',
  `positionOrder` int(11) NOT NULL DEFAULT 0,
  `points` float NOT NULL DEFAULT 0,
  `laps` int(11) NOT NULL DEFAULT 0,
  `time` varchar(255) DEFAULT NULL,
  `milliseconds` int(11) DEFAULT NULL,
  `fastestLap` int(11) DEFAULT NULL,
  `rank` int(11) DEFAULT 0,
  `fastestLapTime` varchar(255) DEFAULT NULL,
  `fastestLapSpeed` varchar(255) DEFAULT NULL,
  `statusId` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`resultId`),
  KEY `constructorId` (`constructorId`),
  KEY `driverId` (`driverId`),
  KEY `statusId` (`statusId`),
  KEY `raceId` (`raceId`),
  CONSTRAINT `results_ibfk_1` FOREIGN KEY (`constructorId`) REFERENCES `constructors` (`constructorId`),
  CONSTRAINT `results_ibfk_2` FOREIGN KEY (`driverId`) REFERENCES `drivers` (`driverId`),
  CONSTRAINT `results_ibfk_3` FOREIGN KEY (`statusId`) REFERENCES `status` (`statusId`),
  CONSTRAINT `results_ibfk_4` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`)
) ENGINE=InnoDB AUTO_INCREMENT=23662 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `seasons` (
  `year` int(11) NOT NULL DEFAULT 0,
  `url` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`year`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `status` (
  `statusId` int(11) NOT NULL AUTO_INCREMENT,
  `status` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`statusId`)
) ENGINE=InnoDB AUTO_INCREMENT=137 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `targetId` int(11) NOT NULL,
  `raceId` int(11) NOT NULL,
  `driverId` int(11) NOT NULL,
  `win` int(11) NOT NULL,
  PRIMARY KEY (`targetId`) USING BTREE,
  KEY `raceId` (`raceId`),
  KEY `driverId` (`driverId`),
  CONSTRAINT `target_ibfk_1` FOREIGN KEY (`raceId`) REFERENCES `races` (`raceId`),
  CONSTRAINT `target_ibfk_2` FOREIGN KEY (`driverId`) REFERENCES `drivers` (`driverId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

