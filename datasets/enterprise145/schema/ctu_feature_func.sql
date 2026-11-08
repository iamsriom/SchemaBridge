-- Schema for database: ctu_feature_func

CREATE TABLE `result_list` (
  `feature_id` int(11) NOT NULL,
  `query_id` int(11) NOT NULL,
  `timestamp` datetime DEFAULT NULL,
  `author` varchar(255) DEFAULT NULL,
  `feature_name` varchar(255) DEFAULT NULL,
  `feature_description` varchar(2550) DEFAULT NULL,
  `example_usage` varchar(2550) DEFAULT NULL,
  `sql_original` varchar(2550) DEFAULT NULL,
  `table_name` varchar(255) DEFAULT NULL,
  `col1` varchar(255) DEFAULT NULL,
  `col2` varchar(255) DEFAULT NULL,
  `sql` varchar(2550) DEFAULT NULL,
  `error_message` varchar(2550) DEFAULT NULL,
  `chi2` decimal(10,3) DEFAULT NULL,
  `run_time` decimal(10,3) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

