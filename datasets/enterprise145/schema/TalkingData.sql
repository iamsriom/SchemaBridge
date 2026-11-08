-- Schema for database: TalkingData

CREATE TABLE `app_all` (
  `app_id` bigint(20) NOT NULL,
  PRIMARY KEY (`app_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `app_events` (
  `event_id` int(11) NOT NULL,
  `app_id` bigint(20) NOT NULL,
  `is_installed` tinyint(4) NOT NULL,
  `is_active` tinyint(4) NOT NULL,
  PRIMARY KEY (`event_id`,`app_id`),
  KEY `event_id` (`event_id`),
  CONSTRAINT `app_events_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `app_events_relevant` (
  `event_id` int(11) NOT NULL,
  `app_id` bigint(20) NOT NULL,
  `is_installed` tinyint(4) DEFAULT NULL,
  `is_active` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`event_id`,`app_id`),
  KEY `event_id` (`event_id`),
  KEY `app_id` (`app_id`),
  CONSTRAINT `app_events_relevant_ibfk_1` FOREIGN KEY (`event_id`) REFERENCES `events_relevant` (`event_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `app_events_relevant_ibfk_2` FOREIGN KEY (`app_id`) REFERENCES `app_all` (`app_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `app_labels` (
  `app_id` bigint(20) NOT NULL,
  `label_id` int(11) NOT NULL,
  KEY `label_id` (`label_id`),
  KEY `app_id` (`app_id`),
  CONSTRAINT `app_labels_ibfk_1` FOREIGN KEY (`label_id`) REFERENCES `label_categories` (`label_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `app_labels_ibfk_2` FOREIGN KEY (`app_id`) REFERENCES `app_all` (`app_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `events` (
  `event_id` int(11) NOT NULL,
  `device_id` bigint(20) DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `longitude` decimal(10,0) DEFAULT NULL,
  `latitude` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `device_id` (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `events_relevant` (
  `event_id` int(11) NOT NULL,
  `device_id` bigint(20) DEFAULT NULL,
  `timestamp` datetime NOT NULL,
  `longitude` decimal(10,0) NOT NULL,
  `latitude` decimal(10,0) NOT NULL,
  PRIMARY KEY (`event_id`),
  KEY `device_id` (`device_id`),
  CONSTRAINT `events_relevant_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `gender_age` (`device_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gender_age` (
  `device_id` bigint(20) NOT NULL,
  `gender` varchar(255) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `group` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`device_id`),
  CONSTRAINT `gender_age_ibfk_1` FOREIGN KEY (`device_id`) REFERENCES `phone_brand_device_model2` (`device_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gender_age_test` (
  `device_id` bigint(20) NOT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gender_age_train` (
  `device_id` bigint(20) NOT NULL,
  `gender` varchar(255) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `group` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `label_categories` (
  `label_id` int(11) NOT NULL,
  `category` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`label_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `phone_brand_device_model2` (
  `device_id` bigint(20) NOT NULL,
  `phone_brand` varchar(255) NOT NULL,
  `device_model` varchar(255) NOT NULL,
  PRIMARY KEY (`device_id`,`phone_brand`,`device_model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sample_submission` (
  `device_id` bigint(20) NOT NULL,
  `F23-` float DEFAULT NULL,
  `F24-26` float DEFAULT NULL,
  `F27-28` float DEFAULT NULL,
  `F29-32` float DEFAULT NULL,
  `F33-42` float DEFAULT NULL,
  `F43+` float DEFAULT NULL,
  `M22-` float DEFAULT NULL,
  `M23-26` float DEFAULT NULL,
  `M27-28` float DEFAULT NULL,
  `M29-31` float DEFAULT NULL,
  `M32-38` float DEFAULT NULL,
  `M39+` float DEFAULT NULL,
  PRIMARY KEY (`device_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

