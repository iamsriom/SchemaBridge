-- Schema for database: Triazine

CREATE TABLE `molecule` (
  `molecule_id` int(11) NOT NULL DEFAULT 0,
  `activity` float DEFAULT NULL,
  PRIMARY KEY (`molecule_id`),
  KEY `molecule_id` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `position` (
  `molecule_id` int(11) NOT NULL DEFAULT 0,
  `position` int(11) NOT NULL DEFAULT 0,
  `branch` float DEFAULT NULL,
  `flex` float DEFAULT NULL,
  `h_acceptor` float DEFAULT NULL,
  `h_doner` float DEFAULT NULL,
  `pi_acceptor` float DEFAULT NULL,
  `pi_doner` float DEFAULT NULL,
  `polar` float DEFAULT NULL,
  `polarisable` float DEFAULT NULL,
  `sigma` float DEFAULT NULL,
  `size` float DEFAULT NULL,
  PRIMARY KEY (`molecule_id`,`position`),
  KEY `molecule_id` (`molecule_id`),
  CONSTRAINT `position_ibfk_1` FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

