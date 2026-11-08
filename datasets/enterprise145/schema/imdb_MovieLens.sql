-- Schema for database: imdb_MovieLens

CREATE TABLE `actors` (
  `actorid` mediumint(8) unsigned NOT NULL,
  `a_gender` enum('M','F') NOT NULL,
  `a_quality` int(2) NOT NULL,
  PRIMARY KEY (`actorid`),
  KEY `a_gender` (`a_gender`),
  KEY `a_quality` (`a_quality`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `directors` (
  `directorid` mediumint(8) unsigned NOT NULL,
  `d_quality` int(2) NOT NULL,
  `avg_revenue` int(11) NOT NULL,
  PRIMARY KEY (`directorid`),
  KEY `d_quality` (`d_quality`),
  KEY `avg_revenue` (`avg_revenue`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci COMMENT='version without Gender information of Directors.'
;


CREATE TABLE `movies` (
  `movieid` mediumint(8) unsigned NOT NULL DEFAULT 0,
  `year` int(11) NOT NULL,
  `isEnglish` enum('T','F') NOT NULL,
  `country` varchar(50) NOT NULL,
  `runningtime` int(11) NOT NULL,
  PRIMARY KEY (`movieid`),
  KEY `year` (`year`),
  KEY `isEnglish` (`isEnglish`),
  KEY `country` (`country`),
  KEY `runningtime` (`runningtime`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `movies2actors` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `actorid` mediumint(8) unsigned NOT NULL,
  `cast_num` int(11) NOT NULL,
  PRIMARY KEY (`movieid`,`actorid`),
  KEY `fk_m2a_mid_idx` (`movieid`),
  KEY `fk_m2a_aid_idx` (`actorid`),
  KEY `cast_num` (`cast_num`),
  CONSTRAINT `fk_m2a_aid` FOREIGN KEY (`actorid`) REFERENCES `actors` (`actorid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_m2a_mid` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `movies2directors` (
  `movieid` mediumint(8) unsigned NOT NULL,
  `directorid` mediumint(8) unsigned NOT NULL,
  `genre` varchar(15) NOT NULL,
  PRIMARY KEY (`movieid`,`directorid`),
  KEY `fk_m2d_mid_idx` (`movieid`),
  KEY `fk_m2d_did_idx` (`directorid`),
  KEY `genre` (`genre`),
  CONSTRAINT `fk_m2d_did` FOREIGN KEY (`directorid`) REFERENCES `directors` (`directorid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_m2d_mid` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `u2base` (
  `userid` int(11) NOT NULL DEFAULT 0,
  `movieid` mediumint(8) unsigned NOT NULL,
  `rating` varchar(45) NOT NULL,
  PRIMARY KEY (`userid`,`movieid`),
  KEY `fk_u2base_uid_idx` (`userid`),
  KEY `fk_u2base_mid_idx` (`movieid`),
  KEY `rating` (`rating`),
  CONSTRAINT `fk_u2base_mid` FOREIGN KEY (`movieid`) REFERENCES `movies` (`movieid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_u2base_uid` FOREIGN KEY (`userid`) REFERENCES `users` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `users` (
  `userid` int(11) NOT NULL DEFAULT 0,
  `age` varchar(5) NOT NULL,
  `u_gender` varchar(5) NOT NULL,
  `occupation` varchar(45) NOT NULL,
  PRIMARY KEY (`userid`),
  KEY `index` (`age`,`u_gender`,`occupation`),
  KEY `age` (`age`),
  KEY `u_gender` (`u_gender`),
  KEY `occupation` (`occupation`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

