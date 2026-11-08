-- Schema for database: CiteSeer

CREATE TABLE `cites` (
  `cited_paper_id` varchar(40) NOT NULL,
  `citing_paper_id` varchar(40) NOT NULL,
  PRIMARY KEY (`cited_paper_id`,`citing_paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `content` (
  `paper_id` varchar(40) NOT NULL,
  `word_cited_id` varchar(40) NOT NULL,
  PRIMARY KEY (`paper_id`,`word_cited_id`),
  CONSTRAINT `content_ibfk_1` FOREIGN KEY (`paper_id`) REFERENCES `paper` (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `paper` (
  `paper_id` varchar(40) NOT NULL,
  `class_label` varchar(255) NOT NULL,
  PRIMARY KEY (`paper_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

