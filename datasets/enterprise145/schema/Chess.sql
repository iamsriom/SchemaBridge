-- Schema for database: Chess

CREATE TABLE `game` (
  `game_id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `opening_id` int(10) DEFAULT NULL,
  `event` text DEFAULT NULL,
  `site` text DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `round` text DEFAULT NULL,
  `white` text DEFAULT NULL,
  `black` text DEFAULT NULL,
  `game_result` text DEFAULT NULL,
  `ECO` text DEFAULT NULL,
  `whiteElo` int(10) DEFAULT NULL,
  `BlackElo` int(10) DEFAULT NULL,
  `opening` text DEFAULT NULL,
  `w1` text DEFAULT NULL,
  `b1` text DEFAULT NULL,
  `w2` text DEFAULT NULL,
  `b2` text DEFAULT NULL,
  `w3` text DEFAULT NULL,
  `b3` text DEFAULT NULL,
  `w4` text DEFAULT NULL,
  `b4` text DEFAULT NULL,
  `w5` text DEFAULT NULL,
  `b5` text DEFAULT NULL,
  `w6` text DEFAULT NULL,
  `b6` text DEFAULT NULL,
  `w7` text DEFAULT NULL,
  `b7` text DEFAULT NULL,
  `w8` text DEFAULT NULL,
  `b8` text DEFAULT NULL,
  `w9` text DEFAULT NULL,
  `b9` text DEFAULT NULL,
  `w10` text DEFAULT NULL,
  `b10` text DEFAULT NULL,
  PRIMARY KEY (`game_id`),
  KEY `opening_id` (`opening_id`),
  CONSTRAINT `game_ibfk_1` FOREIGN KEY (`opening_id`) REFERENCES `opening` (`opening_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=296 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;


CREATE TABLE `opening` (
  `opening_id` int(10) NOT NULL AUTO_INCREMENT,
  `name` text DEFAULT NULL,
  `code` text DEFAULT NULL,
  `w1` text DEFAULT NULL,
  `b1` text DEFAULT NULL,
  `w2` text DEFAULT NULL,
  `b2` text DEFAULT NULL,
  `w3` text DEFAULT NULL,
  `b3` text DEFAULT NULL,
  `w4` text DEFAULT NULL,
  `b4` text DEFAULT NULL,
  `variation` text DEFAULT NULL,
  PRIMARY KEY (`opening_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1766 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin
;

