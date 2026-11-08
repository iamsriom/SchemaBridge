-- Schema for database: ctu_adult

CREATE TABLE `data` (
  `age` int(11) DEFAULT NULL,
  `workclass` varchar(16) DEFAULT NULL,
  `fnlwgt` int(11) DEFAULT NULL,
  `education` varchar(12) DEFAULT NULL,
  `education-num` int(11) DEFAULT NULL,
  `marital-status` varchar(21) DEFAULT NULL,
  `occupation` varchar(17) DEFAULT NULL,
  `relationship` varchar(14) DEFAULT NULL,
  `race` varchar(18) DEFAULT NULL,
  `sex` varchar(6) DEFAULT NULL,
  `capital-gain` int(11) DEFAULT NULL,
  `capital-loss` int(11) DEFAULT NULL,
  `hours-per-week` int(11) DEFAULT NULL,
  `native-country` varchar(26) DEFAULT NULL,
  `income` varchar(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

