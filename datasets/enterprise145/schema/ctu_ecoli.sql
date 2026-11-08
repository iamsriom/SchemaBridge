-- Schema for database: ctu_ecoli

CREATE TABLE `data` (
  `sequence_name` varchar(10) NOT NULL,
  `mcg` double DEFAULT NULL,
  `gvh` double DEFAULT NULL,
  `lip` double DEFAULT NULL,
  `chg` double DEFAULT NULL,
  `aac` double DEFAULT NULL,
  `alm1` double DEFAULT NULL,
  `alm2` double DEFAULT NULL,
  `class` varchar(3) DEFAULT NULL,
  PRIMARY KEY (`sequence_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

