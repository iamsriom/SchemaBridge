-- Schema for database: UTube

CREATE TABLE `utube_attributes` (
  `id_states` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `value1` varchar(255) DEFAULT NULL,
  `value2` varchar(255) DEFAULT NULL,
  `direction` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_states`,`name`),
  KEY `id_states` (`id_states`),
  CONSTRAINT `utube_attributes_ibfk_1` FOREIGN KEY (`id_states`) REFERENCES `utube_states` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `utube_states` (
  `id` int(11) NOT NULL,
  `class` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

