-- Schema for database: OpenML_2016

CREATE TABLE `algorithm` (
  `name` varchar(128) NOT NULL DEFAULT '',
  `function` text DEFAULT NULL,
  `description` mediumtext DEFAULT NULL,
  `algorithm_class` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `algorithm_quality` (
  `implementation_id` int(16) NOT NULL,
  `quality` varchar(128) NOT NULL DEFAULT '',
  `qualityImplementation` varchar(64) DEFAULT NULL,
  `label` varchar(128) NOT NULL,
  `value` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`implementation_id`,`quality`,`label`),
  KEY `algorithm_quality_quality` (`quality`),
  CONSTRAINT `algorithm_quality_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `algorithm_quality_ibfk_2` FOREIGN KEY (`quality`) REFERENCES `quality` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `algorithm_setup` (
  `sid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `parent` int(10) unsigned NOT NULL,
  `implementation_id` int(16) NOT NULL,
  `algorithm` varchar(128) DEFAULT NULL,
  `role` varchar(64) NOT NULL DEFAULT 'Learner',
  `isDefault` enum('true','false') DEFAULT 'false',
  `algorithm_structure` varchar(64) DEFAULT NULL,
  `setup_string` text DEFAULT NULL,
  PRIMARY KEY (`sid`),
  KEY `algorithm_setup_algorithm_isDefault_sid` (`algorithm`,`isDefault`,`sid`),
  KEY `algorithm_setup_algorithm` (`algorithm`),
  KEY `algorithm_setup_implementation_id` (`implementation_id`),
  KEY `algorithm_setup_isDefault` (`isDefault`),
  KEY `algorithm_setup_parent` (`parent`),
  KEY `algorithm_setup_role` (`role`),
  KEY `algorithm_setup_role_parent` (`role`,`parent`),
  KEY `algorithm_setup_role_sid` (`role`,`sid`),
  CONSTRAINT `algorithm_setup_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `algorithm_setup_ibfk_2` FOREIGN KEY (`algorithm`) REFERENCES `algorithm` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6436 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bibliographical_reference` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `implementation_id` int(16) NOT NULL,
  `citation` mediumtext NOT NULL,
  `url` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `bibliographical_reference_implementation_id` (`implementation_id`),
  CONSTRAINT `bibliographical_reference_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `data_feature` (
  `did` int(10) unsigned NOT NULL,
  `index` int(10) NOT NULL DEFAULT 0,
  `name` varchar(64) NOT NULL,
  `data_type` varchar(64) DEFAULT NULL,
  `nominal_values` text DEFAULT NULL,
  `is_target` enum('true','false') NOT NULL DEFAULT 'false',
  `is_row_identifier` enum('true','false') NOT NULL DEFAULT 'false',
  `is_ignore` enum('true','false') NOT NULL DEFAULT 'false',
  `NumberOfDistinctValues` int(11) DEFAULT NULL,
  `NumberOfUniqueValues` int(11) DEFAULT NULL,
  `NumberOfMissingValues` int(11) NOT NULL,
  `NumberOfIntegerValues` int(11) DEFAULT NULL,
  `NumberOfRealValues` int(11) DEFAULT NULL,
  `NumberOfNominalValues` varchar(512) NOT NULL,
  `NumberOfValues` int(11) NOT NULL,
  `MaximumValue` int(11) NOT NULL,
  `MinimumValue` int(11) NOT NULL,
  `MeanValue` int(11) NOT NULL,
  `StandardDeviation` int(11) NOT NULL,
  `ClassDistribution` text DEFAULT NULL,
  PRIMARY KEY (`did`,`index`),
  CONSTRAINT `data_feature_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `data_quality` (
  `data` int(10) unsigned NOT NULL DEFAULT 0,
  `quality` varchar(128) NOT NULL DEFAULT '',
  `implementation_id` int(16) NOT NULL,
  `label` varchar(128) NOT NULL,
  `value` varchar(128) DEFAULT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`data`,`quality`,`label`),
  KEY `data_quality_implementation_id` (`implementation_id`),
  KEY `data_quality_quality` (`quality`),
  CONSTRAINT `data_quality_ibfk_1` FOREIGN KEY (`quality`) REFERENCES `quality` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `data_quality_ibfk_2` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dataset` (
  `did` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `uploader` int(10) DEFAULT NULL,
  `source` int(10) unsigned DEFAULT NULL,
  `name` varchar(128) NOT NULL,
  `version` varchar(64) NOT NULL,
  `version_label` varchar(128) DEFAULT NULL,
  `description` text NOT NULL,
  `format` varchar(64) NOT NULL DEFAULT 'arff',
  `creator` text DEFAULT NULL,
  `contributor` text DEFAULT NULL,
  `collection_date` varchar(128) DEFAULT NULL,
  `upload_date` datetime NOT NULL,
  `language` varchar(128) DEFAULT NULL,
  `licence` varchar(64) NOT NULL DEFAULT 'Public',
  `citation` text DEFAULT NULL,
  `collection` varchar(64) DEFAULT NULL,
  `url` mediumtext NOT NULL,
  `isOriginal` enum('true','false') DEFAULT NULL,
  `file_id` int(10) DEFAULT NULL,
  `default_target_attribute` varchar(128) DEFAULT NULL,
  `row_id_attribute` varchar(128) DEFAULT NULL,
  `ignore_attribute` varchar(128) DEFAULT NULL,
  `paper_url` mediumtext DEFAULT NULL,
  `visibility` varchar(128) NOT NULL DEFAULT 'public',
  `original_data_id` int(10) DEFAULT NULL,
  `original_data_url` mediumtext DEFAULT NULL,
  `processed` datetime DEFAULT NULL,
  `error` enum('true','false') NOT NULL DEFAULT 'false',
  `error_message` text DEFAULT NULL,
  `status` enum('in_preparation','active','deactivated') NOT NULL DEFAULT 'in_preparation',
  `update_comment` text DEFAULT NULL,
  `last_update` datetime DEFAULT NULL,
  PRIMARY KEY (`did`),
  KEY `dataset_name` (`name`),
  KEY `dataset_name_did_version_version_label` (`name`,`did`,`version`,`version_label`)
) ENGINE=InnoDB AUTO_INCREMENT=23511 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `downloads` (
  `did` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `knowledge_type` varchar(1) NOT NULL,
  `knowledge_id` int(10) NOT NULL,
  `user_id` mediumint(8) NOT NULL,
  `count` smallint(6) NOT NULL DEFAULT 1,
  `time` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`knowledge_type`,`knowledge_id`,`user_id`),
  KEY `downloads_did` (`did`),
  CONSTRAINT `downloads_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB AUTO_INCREMENT=12567 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `downvotes` (
  `did` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `knowledge_type` varchar(1) NOT NULL,
  `knowledge_id` int(10) NOT NULL,
  `user_id` mediumint(8) NOT NULL,
  `reason` int(11) NOT NULL,
  `time` timestamp NOT NULL DEFAULT current_timestamp(),
  `original` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`knowledge_type`,`knowledge_id`,`user_id`),
  KEY `downvotes_did` (`did`),
  CONSTRAINT `downvotes_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `estimation_procedure` (
  `id` int(8) NOT NULL AUTO_INCREMENT,
  `ttid` int(11) NOT NULL,
  `name` varchar(128) NOT NULL,
  `type` varchar(64) NOT NULL,
  `repeats` int(8) DEFAULT NULL,
  `folds` int(8) DEFAULT NULL,
  `percentage` int(8) DEFAULT NULL,
  `stratified_sampling` enum('true','false') DEFAULT NULL,
  `custom_testset` enum('true','false') NOT NULL DEFAULT 'false',
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `estimation_procedure_ttid` (`ttid`),
  KEY `estimation_procedure__type` (`type`) USING BTREE,
  CONSTRAINT `estimation_procedure_ibfk_1` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `estimation_procedure_ibfk_2` FOREIGN KEY (`type`) REFERENCES `estimation_procedure_type` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `estimation_procedure_type` (
  `name` varchar(64) NOT NULL,
  `description` mediumtext NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `evaluation` (
  `did` int(10) unsigned NOT NULL DEFAULT 0,
  `source` int(10) unsigned NOT NULL,
  `implementation_id` int(16) NOT NULL,
  `function` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `label` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `value` double NOT NULL,
  `stdev` double DEFAULT NULL,
  UNIQUE KEY `did` (`did`,`function`,`label`),
  KEY `function` (`function`,`source`,`label`(32)),
  KEY `func` (`function`),
  KEY `implementation_id` (`implementation_id`),
  CONSTRAINT `evaluation_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`),
  CONSTRAINT `evaluation_ibfk_2` FOREIGN KEY (`function`) REFERENCES `math_function` (`name`),
  CONSTRAINT `evaluation_ibfk_3` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci
;


CREATE TABLE `implementation` (
  `id` int(16) NOT NULL AUTO_INCREMENT,
  `fullName` varchar(1024) NOT NULL,
  `uploader` int(10) DEFAULT NULL,
  `name` varchar(1024) NOT NULL,
  `version` int(16) NOT NULL,
  `external_version` varchar(128) NOT NULL,
  `creator` varchar(128) DEFAULT NULL,
  `contributor` text DEFAULT NULL,
  `uploadDate` datetime NOT NULL,
  `licence` varchar(64) DEFAULT NULL,
  `language` varchar(128) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `fullDescription` text DEFAULT NULL,
  `installationNotes` text DEFAULT NULL,
  `dependencies` text DEFAULT NULL,
  `implements` varchar(128) DEFAULT NULL,
  `binary_file_id` int(10) DEFAULT NULL,
  `source_file_id` int(10) DEFAULT NULL,
  `visibility` varchar(128) NOT NULL DEFAULT 'public',
  `citation` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `implementation_uploader` (`uploader`),
  KEY `implementation_id_external_version` (`id`,`external_version`),
  KEY `implementation_name` (`name`(255)) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=4052 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `implementation_component` (
  `parent` int(16) NOT NULL,
  `child` int(16) NOT NULL,
  `identifier` varchar(1024) DEFAULT NULL,
  PRIMARY KEY (`parent`,`child`),
  KEY `implementation_component_child` (`child`),
  CONSTRAINT `implementation_component_ibfk_1` FOREIGN KEY (`parent`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `implementation_component_ibfk_2` FOREIGN KEY (`child`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `input` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `fullName` varchar(128) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `implementation_id` int(16) NOT NULL,
  `name` varchar(128) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `description` text CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `dataType` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `defaultValue` varchar(256) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  `recommendedRange` varchar(256) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `input_implementation_id` (`implementation_id`),
  CONSTRAINT `input_ibfk_1` FOREIGN KEY (`implementation_id`) REFERENCES `implementation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=33477 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `math_function` (
  `name` varchar(64) CHARACTER SET utf8mb3 COLLATE utf8mb3_bin NOT NULL,
  `functionType` varchar(128) NOT NULL DEFAULT 'EvaluationFunction',
  `min` varchar(64) NOT NULL,
  `max` varchar(64) NOT NULL,
  `unit` varchar(64) NOT NULL,
  `higherIsBetter` varchar(16) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `source_code` text NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `quality` (
  `name` varchar(128) NOT NULL,
  `type` varchar(128) NOT NULL DEFAULT 'DataProperty',
  `formula` text DEFAULT NULL,
  `description` text DEFAULT NULL,
  `datatype` varchar(128) NOT NULL DEFAULT 'undefined',
  `min` float DEFAULT NULL,
  `max` float DEFAULT NULL,
  `unit` varchar(32) DEFAULT NULL,
  `priority` int(11) NOT NULL DEFAULT 9999,
  `showonline` enum('true','false') NOT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `run` (
  `rid` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `uploader` int(10) DEFAULT NULL,
  `parent` int(10) unsigned DEFAULT NULL,
  `setup` int(10) unsigned NOT NULL DEFAULT 0,
  `task_id` int(10) DEFAULT NULL,
  `start_time` datetime DEFAULT NULL,
  `status` varchar(64) NOT NULL,
  `priority` tinyint(8) NOT NULL DEFAULT 10,
  `error` varchar(512) DEFAULT NULL,
  `warning` varchar(512) DEFAULT NULL,
  `error_message` text DEFAULT NULL,
  `processed` datetime DEFAULT NULL,
  `experiment` int(10) unsigned DEFAULT NULL,
  `runner` varchar(16) DEFAULT NULL,
  `machine` varchar(64) DEFAULT NULL,
  `visibility` varchar(128) NOT NULL DEFAULT 'public',
  PRIMARY KEY (`rid`),
  KEY `run_setup_task_id` (`setup`,`task_id`),
  KEY `run_setup_uploader` (`setup`,`uploader`),
  KEY `run_task_id_uploader` (`task_id`,`uploader`),
  KEY `run_task_id_uploader_start_time` (`task_id`,`uploader`,`start_time`),
  CONSTRAINT `run_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=594069 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `runfile` (
  `did` int(16) unsigned NOT NULL AUTO_INCREMENT,
  `source` int(16) NOT NULL,
  `field` varchar(128) NOT NULL,
  `name` varchar(128) NOT NULL,
  `format` varchar(128) NOT NULL,
  `file_id` int(16) NOT NULL,
  PRIMARY KEY (`did`),
  KEY `runfile_source_field` (`source`,`field`),
  CONSTRAINT `runfile_ibfk_1` FOREIGN KEY (`did`) REFERENCES `dataset` (`did`)
) ENGINE=InnoDB AUTO_INCREMENT=22104 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `schedule` (
  `sid` int(8) NOT NULL,
  `task_id` int(8) NOT NULL,
  `experiment` varchar(128) NOT NULL DEFAULT '',
  `active` enum('true','false') NOT NULL DEFAULT 'true',
  `last_assigned` datetime DEFAULT NULL,
  `ttid` int(11) NOT NULL,
  `dependencies` varchar(128) NOT NULL,
  `setup_string` mediumtext NOT NULL,
  PRIMARY KEY (`sid`,`task_id`),
  KEY `schedule_dependencies_active_ttid_last_assigned` (`dependencies`,`active`,`ttid`,`last_assigned`),
  KEY `schedule_sid_task_id_active` (`sid`,`task_id`,`active`),
  KEY `schedule_sid_task_id_active_last_assigned` (`sid`,`task_id`,`active`,`last_assigned`),
  KEY `schedule_task_id` (`task_id`),
  KEY `schedule_ttid` (`ttid`),
  CONSTRAINT `schedule_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `schedule_ibfk_2` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `setup_differences` (
  `sidA` int(10) unsigned NOT NULL,
  `sidB` int(10) unsigned NOT NULL,
  `task_id` int(10) NOT NULL,
  `task_size` int(10) NOT NULL,
  `differences` int(10) NOT NULL,
  PRIMARY KEY (`sidA`,`sidB`,`task_id`),
  KEY `setup_differences_sidB` (`sidB`),
  KEY `setup_differences_task_id` (`task_id`),
  CONSTRAINT `setup_differences_ibfk_1` FOREIGN KEY (`sidA`) REFERENCES `algorithm_setup` (`sid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `setup_differences_ibfk_2` FOREIGN KEY (`sidB`) REFERENCES `algorithm_setup` (`sid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `setup_differences_ibfk_3` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task` (
  `task_id` int(10) NOT NULL AUTO_INCREMENT,
  `ttid` int(10) NOT NULL,
  `creator` int(10) DEFAULT NULL,
  `creation_date` datetime DEFAULT NULL,
  PRIMARY KEY (`task_id`),
  KEY `task_ttid` (`ttid`),
  CONSTRAINT `task_ibfk_1` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=52949 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_inputs` (
  `task_id` int(10) NOT NULL,
  `input` varchar(64) NOT NULL,
  `value` mediumtext NOT NULL,
  PRIMARY KEY (`task_id`,`input`),
  UNIQUE KEY `task_inputs_task_id_input_value` (`task_id`,`input`,`value`(16)) USING BTREE,
  CONSTRAINT `task_inputs_ibfk_1` FOREIGN KEY (`task_id`) REFERENCES `task` (`task_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_io_types` (
  `name` varchar(64) NOT NULL,
  `description` text NOT NULL,
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_type` (
  `ttid` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `description` mediumtext NOT NULL,
  `creator` varchar(128) NOT NULL,
  `contributors` mediumtext DEFAULT NULL,
  `creationDate` datetime NOT NULL,
  PRIMARY KEY (`ttid`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `task_type_inout` (
  `ttid` int(10) NOT NULL,
  `name` varchar(64) NOT NULL,
  `type` varchar(64) NOT NULL,
  `io` enum('input','output') NOT NULL,
  `requirement` enum('required','optional','hidden') NOT NULL,
  `description` varchar(256) NOT NULL,
  `order` int(8) NOT NULL,
  `template_api` text DEFAULT NULL,
  `template_search` text DEFAULT NULL,
  PRIMARY KEY (`ttid`,`name`,`type`),
  KEY `task_type_inout_type` (`type`),
  CONSTRAINT `task_type_inout_ibfk_1` FOREIGN KEY (`ttid`) REFERENCES `task_type` (`ttid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `task_type_inout_ibfk_2` FOREIGN KEY (`type`) REFERENCES `task_io_types` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `trace` (
  `run_id` int(10) unsigned NOT NULL,
  `repeat` int(11) NOT NULL,
  `fold` int(11) NOT NULL,
  `iteration` int(11) NOT NULL,
  `setup_string` mediumtext NOT NULL,
  `evaluation` varchar(265) NOT NULL,
  `selected` enum('true','false') NOT NULL,
  PRIMARY KEY (`run_id`,`repeat`,`fold`,`iteration`),
  CONSTRAINT `trace_ibfk_1` FOREIGN KEY (`run_id`) REFERENCES `run` (`rid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

