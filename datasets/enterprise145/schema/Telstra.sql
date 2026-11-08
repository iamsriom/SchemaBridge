-- Schema for database: Telstra

CREATE TABLE `event_type` (
  `id` int(11) NOT NULL,
  `event_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`,`event_type`),
  CONSTRAINT `event_type_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `log_feature` (
  `id` int(11) NOT NULL,
  `log_feature` varchar(255) NOT NULL,
  `volume` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`,`log_feature`),
  CONSTRAINT `log_feature_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `resource_type` (
  `id` int(11) NOT NULL,
  `resource_type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`,`resource_type`),
  CONSTRAINT `resource_type_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `severity_type` (
  `id` int(11) NOT NULL,
  `severity_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `severity_type_id_fkey` FOREIGN KEY (`id`) REFERENCES `target` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `id` int(11) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `fault_severity` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `target_id_key` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

