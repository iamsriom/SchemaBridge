-- Schema for database: Shakespeare

CREATE TABLE `chapters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Act` int(11) NOT NULL,
  `Scene` int(11) NOT NULL,
  `Description` text NOT NULL,
  `work_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `work_id` (`work_id`),
  CONSTRAINT `chapters_ibfk_1` FOREIGN KEY (`work_id`) REFERENCES `works` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19649 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
;


CREATE TABLE `characters` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `CharName` varchar(128) NOT NULL,
  `Abbrev` varchar(32) NOT NULL,
  `Description` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1267 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
;


CREATE TABLE `paragraphs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ParagraphNum` int(11) NOT NULL,
  `PlainText` text NOT NULL,
  `character_id` int(11) NOT NULL,
  `chapter_id` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `character_id` (`character_id`),
  KEY `chapter_id` (`chapter_id`),
  CONSTRAINT `paragraphs_ibfk_1` FOREIGN KEY (`character_id`) REFERENCES `characters` (`id`),
  CONSTRAINT `paragraphs_ibfk_2` FOREIGN KEY (`chapter_id`) REFERENCES `chapters` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=666328 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
;


CREATE TABLE `works` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Title` varchar(128) NOT NULL,
  `LongTitle` text NOT NULL,
  `Date` int(11) NOT NULL,
  `GenreType` varchar(32) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
;

