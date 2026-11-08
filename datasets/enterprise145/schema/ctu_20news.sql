-- Schema for database: ctu_20news

CREATE TABLE `20news` (
  `id` int(11) NOT NULL,
  `text` mediumtext DEFAULT NULL,
  `label` varchar(24) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `2news` (
  `id` int(11) NOT NULL,
  `text` mediumtext DEFAULT NULL,
  `label` varchar(24) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

