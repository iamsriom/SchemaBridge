-- Schema for database: IMDB_1R

CREATE TABLE `HasRated` (
  `user_id` int(11) NOT NULL DEFAULT 0,
  `item_id` int(11) NOT NULL DEFAULT 0,
  `rating` varchar(45) NOT NULL,
  PRIMARY KEY (`user_id`,`item_id`),
  KEY `fk_u2base_1` (`item_id`),
  CONSTRAINT `fk_u2base_1` FOREIGN KEY (`item_id`) REFERENCES `Movie` (`item_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_u2base_2` FOREIGN KEY (`user_id`) REFERENCES `User` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Movie` (
  `item_id` int(11) NOT NULL,
  `Action` varchar(5) NOT NULL,
  `Drama` varchar(5) NOT NULL,
  `Horror` varchar(5) NOT NULL,
  PRIMARY KEY (`item_id`),
  KEY `Action_in` (`Action`),
  KEY `Drama_in` (`Drama`),
  KEY `Horror_in` (`Horror`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `User` (
  `user_id` int(11) NOT NULL DEFAULT 0,
  `Age` varchar(5) DEFAULT NULL,
  `Gender` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  KEY `index` (`Age`,`Gender`),
  KEY `gender_in` (`Gender`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

