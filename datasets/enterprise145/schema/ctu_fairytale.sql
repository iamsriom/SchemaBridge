-- Schema for database: ctu_fairytale

CREATE TABLE `JuanManuel Tales` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tale` varchar(80) DEFAULT NULL,
  `book` varchar(50) DEFAULT NULL,
  `author` varchar(50) DEFAULT NULL,
  `date` int(4) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `source` varchar(100) DEFAULT NULL,
  `text` longtext DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=152 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `authors_gutenberg` (
  `Surname` varchar(255) DEFAULT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Born` int(11) DEFAULT NULL,
  `Died` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `authors_wikipedia` (
  `author` varchar(255) DEFAULT NULL,
  `date_birth` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `baldwin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `book` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `content` mediumtext NOT NULL,
  `url` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=581 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `feedbooks` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` longtext DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `globalgrey` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` longtext DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `google` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content` longtext DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `gutenberg` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `book` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `country` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `content` longtext DEFAULT NULL,
  `url` text DEFAULT NULL,
  `id_gutenberg` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=509 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `gutenberg_cleared` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `book` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `country` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  `content` longtext DEFAULT NULL,
  `url` text DEFAULT NULL,
  `id_gutenberg` int(11) DEFAULT NULL,
  `clear_success` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=211 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `old_truncated` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` tinytext DEFAULT NULL,
  `content` longtext DEFAULT NULL,
  `url` tinytext DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `book` varchar(255) DEFAULT NULL,
  `date` int(11) DEFAULT NULL,
  `continent` varchar(255) DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4320 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin ROW_FORMAT=COMPACT
;


CREATE TABLE `tales_template` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(255) DEFAULT NULL,
  `book` varchar(255) DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `date` date DEFAULT NULL,
  `country` varchar(255) DEFAULT NULL,
  `url` text DEFAULT NULL,
  `content` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

