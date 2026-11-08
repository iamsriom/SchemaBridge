-- Schema for database: AustralianFootball

CREATE TABLE `match_stats` (
  `mid` varchar(255) NOT NULL,
  `pid` int(11) NOT NULL,
  `tid` int(11) DEFAULT NULL,
  `loc` varchar(255) DEFAULT NULL,
  `KI` int(11) DEFAULT NULL,
  `MK` int(11) DEFAULT NULL,
  `HB` int(11) DEFAULT NULL,
  `DI` int(11) DEFAULT NULL,
  `GL` int(11) DEFAULT NULL,
  `BH` int(11) DEFAULT NULL,
  `HO` int(11) DEFAULT NULL,
  `TK` int(11) DEFAULT NULL,
  `RB` int(11) DEFAULT NULL,
  `IF` int(11) DEFAULT NULL,
  `CL` int(11) DEFAULT NULL,
  `CG` int(11) DEFAULT NULL,
  `FF` int(11) DEFAULT NULL,
  `FA` int(11) DEFAULT NULL,
  `BR` int(11) DEFAULT NULL,
  `CP` int(11) DEFAULT NULL,
  `UP` int(11) DEFAULT NULL,
  `CM` int(11) DEFAULT NULL,
  `MI` int(11) DEFAULT NULL,
  `1P` float DEFAULT NULL,
  `BO` int(11) DEFAULT NULL,
  `GA` int(11) DEFAULT NULL,
  `PP` float DEFAULT NULL,
  PRIMARY KEY (`mid`,`pid`),
  KEY `mid` (`mid`),
  KEY `pid` (`pid`),
  KEY `tid` (`tid`),
  CONSTRAINT `match_stats_ibfk_1` FOREIGN KEY (`pid`) REFERENCES `players` (`pid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `match_stats_ibfk_2` FOREIGN KEY (`tid`) REFERENCES `teams` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `match_stats_ibfk_3` FOREIGN KEY (`mid`) REFERENCES `matches` (`mid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `matches` (
  `mid` varchar(255) NOT NULL DEFAULT '',
  `season` int(11) DEFAULT NULL,
  `round` varchar(255) DEFAULT NULL,
  `tid1` int(11) DEFAULT NULL,
  `tid2` int(11) DEFAULT NULL,
  `tid1_loc` varchar(255) DEFAULT NULL,
  `tid2_loc` varchar(255) DEFAULT NULL,
  `start_dt` datetime DEFAULT NULL,
  `venue` varchar(255) DEFAULT NULL,
  `att` int(11) DEFAULT NULL,
  `margin` int(11) DEFAULT NULL,
  `win_score` int(11) DEFAULT NULL,
  `win_tid` int(11) DEFAULT NULL,
  `win_loc` varchar(255) DEFAULT NULL,
  `lose_score` int(11) DEFAULT NULL,
  `lose_loc` varchar(255) DEFAULT NULL,
  `lose_tid` int(11) DEFAULT NULL,
  `h_tid` int(11) DEFAULT NULL,
  `h_score` int(11) DEFAULT NULL,
  `h_q1g` int(11) DEFAULT NULL,
  `h_q2g` int(11) DEFAULT NULL,
  `h_q3g` int(11) DEFAULT NULL,
  `h_q4g` int(11) DEFAULT NULL,
  `h_etg` int(11) DEFAULT NULL,
  `h_q1b` int(11) DEFAULT NULL,
  `h_q2b` int(11) DEFAULT NULL,
  `h_q3b` int(11) DEFAULT NULL,
  `h_q4b` int(11) DEFAULT NULL,
  `h_etb` int(11) DEFAULT NULL,
  `a_tid` int(11) DEFAULT NULL,
  `a_score` int(11) DEFAULT NULL,
  `a_q1g` int(11) DEFAULT NULL,
  `a_q2g` int(11) DEFAULT NULL,
  `a_q3g` int(11) DEFAULT NULL,
  `a_q4g` int(11) DEFAULT NULL,
  `a_etg` int(11) DEFAULT NULL,
  `a_q1b` int(11) DEFAULT NULL,
  `a_q2b` int(11) DEFAULT NULL,
  `a_q3b` int(11) DEFAULT NULL,
  `a_q4b` int(11) DEFAULT NULL,
  `a_etb` int(11) DEFAULT NULL,
  `target` int(1) DEFAULT NULL,
  PRIMARY KEY (`mid`),
  KEY `tid1` (`tid1`),
  KEY `tid2` (`tid2`),
  CONSTRAINT `matches_ibfk_1` FOREIGN KEY (`tid1`) REFERENCES `teams` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `matches_ibfk_2` FOREIGN KEY (`tid2`) REFERENCES `teams` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `players` (
  `pid` int(11) NOT NULL,
  `dob` datetime DEFAULT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `teams` (
  `tid` int(11) NOT NULL,
  `tname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`tid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;

