-- Schema for database: ctu_outliers

CREATE TABLE `dataset1` (
  `X` varchar(255) DEFAULT NULL,
  `Y` varchar(255) DEFAULT NULL,
  `Artificial` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dataset2` (
  `X` double DEFAULT NULL,
  `Y` double DEFAULT NULL,
  `Stranger` varchar(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

