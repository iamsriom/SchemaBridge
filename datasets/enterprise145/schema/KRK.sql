-- Schema for database: KRK

CREATE TABLE `krk` (
  `id` int(11) NOT NULL,
  `white_king_file` int(11) DEFAULT NULL,
  `white_king_rank` int(11) DEFAULT NULL,
  `white_rook_file` int(11) DEFAULT NULL,
  `white_rook_rank` int(11) DEFAULT NULL,
  `black_king_file` int(11) DEFAULT NULL,
  `black_king_rank` int(11) DEFAULT NULL,
  `class` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

