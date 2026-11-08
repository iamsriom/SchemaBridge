-- Schema for database: meta

CREATE TABLE `algorithm` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `algorithm` varchar(255) NOT NULL COMMENT 'Algorithm name',
  `type` varchar(255) DEFAULT NULL COMMENT 'Rough category',
  `released` int(4) DEFAULT NULL COMMENT 'Publication date',
  `reference_count` int(11) DEFAULT NULL COMMENT 'Reference count on Google Scholar',
  `ranking` decimal(10,5) DEFAULT NULL COMMENT 'Ranking based on accuracy. Higher value is better',
  `propagation` varchar(255) DEFAULT NULL COMMENT 'Used information propagation',
  `feature_function` varchar(255) DEFAULT NULL COMMENT 'Used feature function',
  `use_in_ranking` int(11) DEFAULT 1,
  `rank_confidence` float DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL COMMENT 'Free text',
  PRIMARY KEY (`id`),
  KEY `algorithm` (`algorithm`)
) ENGINE=InnoDB AUTO_INCREMENT=92 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Hand entered data about relational algorithms/implementations.'
;


CREATE TABLE `author` (
  `author_text` varchar(255) NOT NULL COMMENT 'Reference name',
  `author_url` varchar(2550) NOT NULL COMMENT 'Reference URL',
  `has_confidence_interval` int(1) DEFAULT 0,
  PRIMARY KEY (`author_text`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `database` (
  `database_name` varchar(255) NOT NULL COMMENT 'Name of the dataset in the database.\n',
  `dataset_name` varchar(255) NOT NULL COMMENT 'The name used in the web page.',
  `is_primary_version` int(1) DEFAULT 0 COMMENT 'A dataset can have multiple versions, show this version as the default?',
  `is_hidden` int(1) DEFAULT 0 COMMENT 'Hide it from the web page.',
  `uploader_name` varchar(255) DEFAULT NULL COMMENT 'Name of the person who uploaded the dataset.',
  `uploader_url` varchar(500) DEFAULT NULL COMMENT 'URL to the uploader.',
  `upload_date` datetime DEFAULT NULL COMMENT 'Date when the dataset was uploaded.',
  `download_url` varchar(255) DEFAULT NULL COMMENT 'URL to web site, where the dataset can be downloaded.',
  `modifications` varchar(2550) DEFAULT NULL COMMENT 'Description of the changes performed on the dataset.',
  `has_loop` int(1) DEFAULT NULL COMMENT 'Does there exist a loop over more than a single table if we treat foreign keys as an undirected graph?',
  `null_count` int(11) DEFAULT NULL COMMENT 'Count of missing values in the database.',
  `target_table` varchar(255) DEFAULT NULL COMMENT 'The column to predict.',
  `target_column` varchar(255) DEFAULT NULL COMMENT 'Identifier of the target column.',
  `target_id` varchar(255) DEFAULT NULL COMMENT 'The target table - the place where the target column resides.',
  `target_timestamp` varchar(255) DEFAULT NULL COMMENT 'When to perform the prediction?',
  `task` varchar(255) DEFAULT NULL COMMENT 'The task that is performed on the target column. Generally either classification or regression.',
  `img_path` varchar(255) DEFAULT NULL COMMENT 'Filename of the schema image on the server.',
  PRIMARY KEY (`database_name`),
  KEY `dataset_name` (`dataset_name`),
  CONSTRAINT `database_ibfk_1` FOREIGN KEY (`dataset_name`) REFERENCES `dataset` (`dataset_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Hand entered data about individual versions of the datasets.'
;


CREATE TABLE `dataset` (
  `dataset_name` varchar(255) NOT NULL COMMENT 'Name of the database on the server.',
  `domain` varchar(255) NOT NULL COMMENT 'An approximate categorization of the dataset into industries. ',
  `description` text DEFAULT NULL COMMENT 'A brief description of the dataset.',
  `alternative_names` varchar(255) DEFAULT NULL COMMENT 'Sometimes the dataset can be known under several names. List the alternatives.',
  `publication_count` int(11) DEFAULT NULL COMMENT 'Offline hand entered value that is used to identify the most popular datasets.',
  `original_row_count` int(11) DEFAULT NULL COMMENT 'Count of the rows over all the tables in the database as reported by the author of the dataset.',
  `bibtex_filename` varchar(255) DEFAULT NULL COMMENT 'Filename of the BibTex file on the server.',
  `is_artificial` int(1) DEFAULT NULL COMMENT 'The dataset can be either synthetic or a measurement of the real world.',
  `has_single_entity` int(1) DEFAULT NULL,
  `is_graph_friendly` int(1) NOT NULL COMMENT 'Subjective. If transitive relationships have to be modeled or label propagation have to be employed, we say that graph aproach is desirable.',
  `thing_taxonomy` varchar(255) DEFAULT NULL COMMENT 'Categorization of the target table into 8 categories based on http://schema.org/Thing',
  `graph_taxonomy` varchar(255) DEFAULT NULL COMMENT 'Is the target table an Entity or a Relationship? Heuristic: Does the target table reference the same table twice?',
  `license` varchar(255) DEFAULT NULL,
  `license_url` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`dataset_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Hand entered data about the datasets.'
;


CREATE TABLE `information` (
  `database_name` varchar(64) NOT NULL COMMENT 'Name of database on MySQL server.',
  `dataset_name` varchar(255) DEFAULT NULL COMMENT 'The name used in the web page.',
  `is_primary_version` int(1) DEFAULT 0 COMMENT 'A dataset can have multiple versions, show this version as the default?',
  `is_hidden` int(1) DEFAULT 0 COMMENT 'Hide it from the web page.',
  `is_artificial` int(1) DEFAULT NULL COMMENT 'The dataset can be either synthetic or a measurement of the real world.',
  `domain` varchar(255) DEFAULT NULL COMMENT 'An approximate categorization of the dataset into industries. ',
  `description` text DEFAULT NULL COMMENT 'A brief description of the dataset.',
  `alternative_names` varchar(255) DEFAULT NULL COMMENT 'Sometimes the dataset can be known under several names. List the alternatives.',
  `publication_count` int(11) DEFAULT NULL COMMENT 'Offline hand entered value that is used to identify the most popular datasets.',
  `database_size` decimal(46,1) DEFAULT NULL COMMENT 'Database size in MB as reported by MariaDB. The size includes indexes.',
  `table_count` bigint(21) DEFAULT 0 COMMENT 'Count of the tables in the database.',
  `row_count` decimal(43,0) DEFAULT NULL COMMENT 'Count of rows over all the tables in the database.',
  `row_max` bigint(21) unsigned DEFAULT NULL COMMENT 'Count of rows in the tallest table in the database.',
  `null_count` int(11) DEFAULT NULL COMMENT 'Count of missing values in the database.',
  `column_count` bigint(21) DEFAULT 0 COMMENT 'Count of columns over all the tables in the database.',
  `geo_count` bigint(21) DEFAULT NULL COMMENT 'Count of geography related data types in the database.',
  `date_count` bigint(21) DEFAULT NULL COMMENT 'Count of time, date, datetime and timestamp columns in the database.',
  `lob_count` bigint(21) DEFAULT NULL COMMENT 'Count of large objects in the database like images or text attributes.',
  `string_count` bigint(21) DEFAULT NULL COMMENT 'Count of string columns in the database.',
  `numeric_count` bigint(21) DEFAULT NULL COMMENT 'Count of numerical attributes in the database. Includes integers, floats,...',
  `primary_key_count` bigint(21) DEFAULT NULL COMMENT 'Count of indexes in the database.',
  `foreign_key_count` bigint(21) DEFAULT NULL COMMENT 'Count of foreign keys.',
  `composite_foreign_key_count` bigint(21) DEFAULT NULL COMMENT 'Count of primary keys that are composed of two or more columns.',
  `self_referencing_table_count` bigint(21) DEFAULT NULL COMMENT 'Count of tables, whose foreign key references the primary key of the table.',
  `has_loop` int(1) DEFAULT NULL COMMENT 'Does there exist a loop over more than a single table if we treat foreign keys as an undirected graph?',
  `target_table` varchar(255) DEFAULT NULL COMMENT 'The column to predict.',
  `target_column` varchar(255) DEFAULT NULL COMMENT 'Identifier of the target column.',
  `target_id` varchar(255) DEFAULT NULL COMMENT 'The target table - the place where the target column resides.',
  `target_timestamp` varchar(255) DEFAULT NULL COMMENT 'When to perform the prediction?',
  `task` varchar(255) DEFAULT NULL COMMENT 'The task that is performed on the target column. Generally either classification or regression.',
  `instance_count` bigint(21) unsigned DEFAULT NULL COMMENT 'Count of rows in the target table.',
  `duplicate_target_id` int(1) DEFAULT NULL COMMENT 'Does the target table contain duplicate target_id?',
  `has_target_table_loop` int(1) DEFAULT NULL COMMENT 'Does the target table and some other table create a loop?',
  `class_count` bigint(21) DEFAULT NULL,
  `majority_class_ratio` decimal(24,4) DEFAULT NULL COMMENT 'Proportion of majority class in the target column.',
  `uploader_name` varchar(255) DEFAULT NULL COMMENT 'Name of the person who uploaded the dataset.',
  `uploader_url` varchar(500) DEFAULT NULL COMMENT 'URL to the uploader.',
  `upload_date` datetime DEFAULT NULL COMMENT 'Date when the dataset was uploaded.',
  `download_url` varchar(255) DEFAULT NULL COMMENT 'URL to web site, where the dataset can be downloaded.',
  `modifications` varchar(2550) DEFAULT NULL COMMENT 'Description of the changes performed on the dataset.',
  `bibtex_filename` varchar(255) DEFAULT NULL COMMENT 'Filename of the BibTex file on the server.',
  `img_filename` binary(0) DEFAULT NULL,
  `mwb_filename` binary(0) DEFAULT NULL,
  PRIMARY KEY (`database_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Automatically generated meta data about the datasets.'
;


CREATE TABLE `information_bkp` (
  `database_name` varchar(64) NOT NULL COMMENT 'Name of database on MySQL server.',
  `dataset_name` varchar(255) DEFAULT NULL COMMENT 'The name used in the web page.',
  `is_primary_version` int(1) DEFAULT 0 COMMENT 'A dataset can have multiple versions, show this version as the default?',
  `is_hidden` int(1) DEFAULT 0 COMMENT 'Hide it from the web page.',
  `is_artificial` int(1) DEFAULT NULL COMMENT 'The dataset can be either synthetic or a measurement of the real world.',
  `domain` varchar(255) DEFAULT NULL COMMENT 'An approximate categorization of the dataset into industries. ',
  `description` text DEFAULT NULL COMMENT 'A brief description of the dataset.',
  `alternative_names` varchar(255) DEFAULT NULL COMMENT 'Sometimes the dataset can be known under several names. List the alternatives.',
  `publication_count` int(11) DEFAULT NULL COMMENT 'Offline hand entered value that is used to identify the most popular datasets.',
  `database_size` decimal(46,1) DEFAULT NULL COMMENT 'Database size in MB as reported by MariaDB. The size includes indexes.',
  `table_count` bigint(21) DEFAULT 0 COMMENT 'Count of the tables in the database.',
  `row_count` decimal(43,0) DEFAULT NULL COMMENT 'Count of rows over all the tables in the database.',
  `row_max` bigint(21) unsigned DEFAULT NULL COMMENT 'Count of rows in the tallest table in the database.',
  `null_count` int(11) DEFAULT NULL COMMENT 'Count of missing values in the database.',
  `column_count` bigint(21) DEFAULT 0 COMMENT 'Count of columns over all the tables in the database.',
  `geo_count` bigint(21) DEFAULT NULL COMMENT 'Count of geography related data types in the database.',
  `date_count` bigint(21) DEFAULT NULL COMMENT 'Count of time, date, datetime and timestamp columns in the database.',
  `lob_count` bigint(21) DEFAULT NULL COMMENT 'Count of large objects in the database like images or text attributes.',
  `string_count` bigint(21) DEFAULT NULL COMMENT 'Count of string columns in the database.',
  `numeric_count` bigint(21) DEFAULT NULL COMMENT 'Count of numerical attributes in the database. Includes integers, floats,...',
  `primary_key_count` bigint(21) DEFAULT NULL COMMENT 'Count of indexes in the database.',
  `foreign_key_count` bigint(21) DEFAULT NULL COMMENT 'Count of foreign keys.',
  `composite_foreign_key_count` bigint(21) DEFAULT NULL COMMENT 'Count of primary keys that are composed of two or more columns.',
  `self_referencing_table_count` bigint(21) DEFAULT NULL COMMENT 'Count of tables, whose foreign key references the primary key of the table.',
  `has_loop` int(1) DEFAULT NULL COMMENT 'Does there exist a loop over more than a single table if we treat foreign keys as an undirected graph?',
  `target_table` varchar(255) DEFAULT NULL COMMENT 'The column to predict.',
  `target_column` varchar(255) DEFAULT NULL COMMENT 'Identifier of the target column.',
  `target_id` varchar(255) DEFAULT NULL COMMENT 'The target table - the place where the target column resides.',
  `target_timestamp` varchar(255) DEFAULT NULL COMMENT 'When to perform the prediction?',
  `task` varchar(255) DEFAULT NULL COMMENT 'The task that is performed on the target column. Generally either classification or regression.',
  `instance_count` bigint(21) unsigned DEFAULT NULL COMMENT 'Count of rows in the target table.',
  `duplicate_target_id` int(1) DEFAULT NULL COMMENT 'Does the target table contain duplicate target_id?',
  `has_target_table_loop` int(1) DEFAULT NULL COMMENT 'Does the target table and some other table create a loop?',
  `class_count` bigint(21) DEFAULT NULL,
  `majority_class_ratio` decimal(24,4) DEFAULT NULL COMMENT 'Proportion of majority class in the target column.',
  `uploader_name` varchar(255) DEFAULT NULL COMMENT 'Name of the person who uploaded the dataset.',
  `uploader_url` varchar(500) DEFAULT NULL COMMENT 'URL to the uploader.',
  `upload_date` datetime DEFAULT NULL COMMENT 'Date when the dataset was uploaded.',
  `download_url` varchar(255) DEFAULT NULL COMMENT 'URL to web site, where the dataset can be downloaded.',
  `modifications` varchar(2550) DEFAULT NULL COMMENT 'Description of the changes performed on the dataset.',
  `bibtex_filename` varchar(255) DEFAULT NULL COMMENT 'Filename of the BibTex file on the server.',
  `img_filename` binary(0) DEFAULT NULL,
  `mwb_filename` binary(0) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `measure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `dataset` varchar(255) NOT NULL COMMENT 'Dataset name',
  `dataset_version` varchar(255) DEFAULT NULL,
  `target` varchar(255) DEFAULT NULL COMMENT 'Target column',
  `algorithm` varchar(255) NOT NULL COMMENT 'Algorithm name',
  `author_text` varchar(255) DEFAULT NULL COMMENT 'Reference name',
  `measure` varchar(255) NOT NULL COMMENT 'Measure name',
  `value` decimal(24,4) NOT NULL COMMENT 'Measure value',
  `timestamp` timestamp NULL DEFAULT current_timestamp() COMMENT 'Timestamp of the record',
  `has_confidence_interval` int(11) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL COMMENT 'Free text',
  PRIMARY KEY (`id`),
  KEY `algorithm` (`algorithm`),
  KEY `dataset_version` (`dataset_version`),
  KEY `author_text` (`author_text`),
  CONSTRAINT `measure_ibfk_2` FOREIGN KEY (`author_text`) REFERENCES `author` (`author_text`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `measure_ibfk_3` FOREIGN KEY (`algorithm`) REFERENCES `algorithm` (`algorithm`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=755 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Hand entered model accuracie''s on the datasets.'
;


CREATE TABLE `performance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `database_name` varchar(50) NOT NULL,
  `algorithm` varchar(50) NOT NULL,
  `error_message` text DEFAULT NULL,
  `error_message_corrected_target_in_Aleph` text DEFAULT NULL,
  `accuracy` decimal(10,4) DEFAULT NULL,
  `auc` decimal(10,3) DEFAULT NULL,
  `fbeta` decimal(10,3) DEFAULT NULL,
  `fscore` decimal(10,3) DEFAULT NULL,
  `precision` decimal(10,3) DEFAULT NULL,
  `recall` decimal(10,3) DEFAULT NULL,
  `runtime` decimal(10,3) DEFAULT NULL,
  `comment` text DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `qc` (
  `database_name` varchar(64) NOT NULL DEFAULT '',
  `has_tables` int(1) NOT NULL,
  `has_records` int(1) DEFAULT NULL,
  `matches_expected_row_count` int(1) DEFAULT NULL,
  `has_primary_keys` int(1) DEFAULT NULL,
  `has_normal_column` int(1) DEFAULT NULL,
  `has_target_table` int(1) NOT NULL,
  `has_description` int(1) NOT NULL,
  `has_task` int(1) NOT NULL,
  `has_bibtex` int(1) NOT NULL,
  `qc` bigint(10) DEFAULT NULL,
  PRIMARY KEY (`database_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Automatically generated quality control overview.'
;


CREATE TABLE `reference` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `database_name` varchar(255) NOT NULL,
  `text` varchar(255) NOT NULL,
  `url` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `database_name` (`database_name`),
  CONSTRAINT `reference_ibfk_1` FOREIGN KEY (`database_name`) REFERENCES `database` (`database_name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci COMMENT='Hand entered refereces to datasets (beyond origin url).'
;

