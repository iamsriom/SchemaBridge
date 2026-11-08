-- Schema for database: trains

CREATE TABLE `cars` (
  `id` int(11) NOT NULL,
  `train_id` int(11) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `shape` varchar(255) DEFAULT NULL,
  `len` varchar(255) DEFAULT NULL,
  `sides` varchar(255) DEFAULT NULL,
  `roof` varchar(255) DEFAULT NULL,
  `wheels` int(11) DEFAULT NULL,
  `load_shape` varchar(255) DEFAULT NULL,
  `load_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `train_id` (`train_id`),
  CONSTRAINT `cars_ibfk_1` FOREIGN KEY (`train_id`) REFERENCES `trains` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `trains` (
  `id` int(11) NOT NULL,
  `direction` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

