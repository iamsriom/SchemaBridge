-- Schema for database: WebKP

CREATE TABLE `cites` (
  `cited_paper_id` varchar(255) NOT NULL,
  `citing_paper_id` varchar(255) NOT NULL,
  PRIMARY KEY (`cited_paper_id`,`citing_paper_id`),
  KEY `cited_paper_id` (`cited_paper_id`),
  KEY `citing_paper_id` (`citing_paper_id`),
  CONSTRAINT `cites_ibfk_1` FOREIGN KEY (`cited_paper_id`) REFERENCES `webpage` (`webpage_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `cites_ibfk_2` FOREIGN KEY (`citing_paper_id`) REFERENCES `webpage` (`webpage_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `content` (
  `webpage_id` varchar(255) NOT NULL,
  `word_cited_id` varchar(255) NOT NULL,
  PRIMARY KEY (`webpage_id`,`word_cited_id`),
  KEY `webpage_id` (`webpage_id`),
  CONSTRAINT `content_ibfk_1` FOREIGN KEY (`webpage_id`) REFERENCES `webpage` (`webpage_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `webpage` (
  `webpage_id` varchar(255) NOT NULL,
  `class_label` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`webpage_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

