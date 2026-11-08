-- Schema for database: imdb_full

CREATE TABLE `actors` (
  `actorid` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  `sex` enum('M','F') DEFAULT NULL,
  PRIMARY KEY (`actorid`),
  KEY `name` (`name`(10)),
  FULLTEXT KEY `actors_name_fulltext` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2749387 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `business` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `businesstext` mediumtext DEFAULT NULL,
  PRIMARY KEY (`movieid`),
  CONSTRAINT `business_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `countries` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `country` varchar(50) NOT NULL,
  PRIMARY KEY (`movieid`,`country`),
  CONSTRAINT `countries_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `directors` (
  `directorid` mediumint(8) unsigned NOT NULL DEFAULT 0,
  `name` varchar(250) NOT NULL,
  `rate` double(18,1) DEFAULT NULL,
  `gross` decimal(32,0) DEFAULT NULL,
  `num` bigint(21) NOT NULL DEFAULT 0,
  PRIMARY KEY (`directorid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `distributors` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `name` varchar(250) NOT NULL,
  PRIMARY KEY (`movieid`,`name`),
  CONSTRAINT `distributors_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `editors` (
  `editorid` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  PRIMARY KEY (`editorid`),
  KEY `name` (`name`(10))
) ENGINE=InnoDB AUTO_INCREMENT=202790 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `genres` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `genre` varchar(50) NOT NULL,
  PRIMARY KEY (`movieid`,`genre`),
  KEY `movieid` (`movieid`),
  KEY `genre` (`genre`(15)),
  CONSTRAINT `genres_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `language` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `language` varchar(100) NOT NULL,
  PRIMARY KEY (`movieid`,`language`),
  KEY `index1` (`movieid`),
  CONSTRAINT `language_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `movies` (
  `movieid` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `title` varchar(400) NOT NULL,
  `year` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`movieid`),
  KEY `title` (`title`(15)),
  FULLTEXT KEY `movies_title_fulltext` (`title`)
) ENGINE=InnoDB AUTO_INCREMENT=2593314 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `movies2actors` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `actorid` mediumint(8) unsigned NOT NULL,
  `as_character` varchar(1000) DEFAULT NULL,
  `leading` int(11) DEFAULT NULL,
  PRIMARY KEY (`movieid`,`actorid`),
  KEY `a` (`actorid`),
  KEY `movieid` (`movieid`),
  CONSTRAINT `movies2actors_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `movies2actors_ibfk_2` FOREIGN KEY (`actorid`) REFERENCES `actors` (`actorid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `movies2directors` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `directorid` mediumint(8) unsigned NOT NULL,
  `genre` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`movieid`,`directorid`),
  KEY `movieid` (`movieid`),
  KEY `directorid` (`directorid`),
  CONSTRAINT `movies2directors_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `movies2directors_ibfk_2` FOREIGN KEY (`directorid`) REFERENCES `directors` (`directorid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `movies2editors` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `editorid` mediumint(8) unsigned NOT NULL,
  `addition` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`movieid`,`editorid`),
  KEY `movieid` (`movieid`),
  KEY `editorid` (`editorid`),
  CONSTRAINT `movies2editors_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `movies2editors_ibfk_2` FOREIGN KEY (`editorid`) REFERENCES `editors` (`editorid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `movies2producers` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `producerid` mediumint(8) unsigned NOT NULL,
  `addition` varchar(100) NOT NULL,
  PRIMARY KEY (`movieid`,`producerid`,`addition`),
  KEY `movieid` (`movieid`),
  KEY `producerid` (`producerid`),
  CONSTRAINT `movies2producers_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `movies2producers_ibfk_2` FOREIGN KEY (`producerid`) REFERENCES `producers` (`producerid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `movies2writers` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `writerid` mediumint(8) unsigned NOT NULL,
  `addition` varchar(250) NOT NULL,
  PRIMARY KEY (`movieid`,`writerid`,`addition`),
  KEY `movieid` (`movieid`),
  KEY `writerid` (`writerid`),
  CONSTRAINT `movies2writers_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `movies2writers_ibfk_2` FOREIGN KEY (`writerid`) REFERENCES `writers` (`writerid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `prodcompanies` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `name` varchar(250) NOT NULL,
  PRIMARY KEY (`movieid`,`name`),
  KEY `movieid` (`movieid`),
  KEY `name` (`name`(15)),
  CONSTRAINT `prodcompanies_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `producers` (
  `producerid` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  PRIMARY KEY (`producerid`),
  KEY `name` (`name`(10)),
  FULLTEXT KEY `producers_name_fulltext` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=532348 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `ratings` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `rank` char(4) NOT NULL,
  `votes` mediumint(8) unsigned DEFAULT NULL,
  `distribution` char(10) NOT NULL,
  PRIMARY KEY (`movieid`),
  CONSTRAINT `ratings_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `runningtimes` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `time` varchar(50) NOT NULL,
  `addition` varchar(100) NOT NULL,
  `time1` int(11) DEFAULT NULL,
  PRIMARY KEY (`movieid`,`time`,`addition`),
  KEY `movieid` (`movieid`),
  CONSTRAINT `runningtimes_ibfk_1` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `writers` (
  `writerid` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(250) NOT NULL,
  PRIMARY KEY (`writerid`),
  KEY `name` (`name`(10))
) ENGINE=InnoDB AUTO_INCREMENT=407171 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

