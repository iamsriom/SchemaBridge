-- Schema for database: PubMed_Diabetes

CREATE TABLE `cites` (
  `citing_paper_id` int(11) NOT NULL,
  `cites_paper_id` int(11) NOT NULL,
  PRIMARY KEY (`citing_paper_id`,`cites_paper_id`),
  KEY `cites_paper_id` (`cites_paper_id`),
  CONSTRAINT `cites_ibfk_1` FOREIGN KEY (`cites_paper_id`) REFERENCES `paper` (`paper_id`),
  CONSTRAINT `cites_ibfk_2` FOREIGN KEY (`cites_paper_id`) REFERENCES `paper` (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `content` (
  `paper_id` int(11) NOT NULL,
  `word` varchar(255) NOT NULL,
  `tf_idf` double NOT NULL,
  PRIMARY KEY (`paper_id`,`word`),
  CONSTRAINT `content_ibfk_1` FOREIGN KEY (`paper_id`) REFERENCES `paper` (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `paper` (
  `paper_id` int(11) NOT NULL,
  `class_label` int(11) NOT NULL,
  PRIMARY KEY (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

