-- Schema for database: ctu_auta

CREATE TABLE `auta` (
  `mpg` int(11) DEFAULT NULL,
  `cylinders` int(11) DEFAULT NULL,
  `displacement` int(11) DEFAULT NULL,
  `horsepower` int(11) DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `acceleration` float DEFAULT NULL,
  `model year` int(11) DEFAULT NULL,
  `origin` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

