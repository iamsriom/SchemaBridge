-- Schema for database: arnaud_citeseer

CREATE TABLE `cites` (
  `cited_paper_id` varchar(255) DEFAULT NULL,
  `citing_paper_id` varchar(255) DEFAULT NULL,
  KEY `cited_paper_id` (`cited_paper_id`),
  KEY `citing_paper_id` (`citing_paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `content` (
  `paper_id` varchar(255) DEFAULT NULL,
  `word_cited_id` varchar(255) DEFAULT NULL,
  `class_label` varchar(255) DEFAULT NULL,
  KEY `paper_id` (`paper_id`),
  CONSTRAINT `content_ibfk_1` FOREIGN KEY (`paper_id`) REFERENCES `paper` (`paper_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `paper` (
  `paper_id` varchar(255) NOT NULL,
  `class_label` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

