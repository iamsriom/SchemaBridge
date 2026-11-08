-- Schema for database: Bench4

CREATE TABLE `Employees` (
  `EmployeeID` int(11) NOT NULL,
  `FirstName` varchar(40) NOT NULL,
  `MiddleInitial` varchar(40) DEFAULT NULL,
  `LastName` varchar(40) NOT NULL,
  PRIMARY KEY (`EmployeeID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Products` (
  `ProductID` int(11) NOT NULL,
  `Name` varchar(50) NOT NULL,
  `Price` decimal(19,4) DEFAULT NULL,
  PRIMARY KEY (`ProductID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bill_of_materials` (
  `tube_assembly_id` varchar(255) DEFAULT NULL,
  `component_id` varchar(255) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  KEY `bill_of_materials_post_tube_assembly_id_fkey` (`tube_assembly_id`),
  KEY `bill_of_materials_post_component_id_fkey` (`component_id`),
  CONSTRAINT `bill_of_materials_post_component_id_fkey` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `bill_of_materials_post_tube_assembly_id_fkey` FOREIGN KEY (`tube_assembly_id`) REFERENCES `tube` (`tube_assembly_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `cars` (
  `id` int(11) NOT NULL,
  `train_id` int(11) DEFAULT NULL,
  `position` int(11) DEFAULT NULL,
  `shape` varchar(255) DEFAULT NULL,
  `len` varchar(255) DEFAULT NULL,
  `sides` varchar(255) DEFAULT NULL,
  `roof` varchar(255) DEFAULT NULL,
  `wheels` int(11) DEFAULT NULL,
  `load_shape` varchar(255) DEFAULT NULL,
  `load_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `train_id` (`train_id`),
  CONSTRAINT `cars_ibfk_1` FOREIGN KEY (`train_id`) REFERENCES `trains` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `comp_adaptor` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `adaptor_angle` int(11) DEFAULT NULL,
  `overall_length` decimal(65,30) DEFAULT NULL,
  `end_form_id_1` varchar(255) DEFAULT NULL,
  `connection_type_id_1` varchar(255) DEFAULT NULL,
  `length_1` decimal(65,30) DEFAULT NULL,
  `thread_size_1` decimal(65,30) DEFAULT NULL,
  `thread_pitch_1` decimal(65,30) DEFAULT NULL,
  `nomi l_size_1` decimal(65,30) DEFAULT NULL,
  `end_form_id_2` varchar(255) DEFAULT NULL,
  `connection_type_id_2` varchar(255) DEFAULT NULL,
  `length_2` decimal(65,30) DEFAULT NULL,
  `thread_size_2` decimal(65,30) DEFAULT NULL,
  `thread_pitch_2` decimal(65,30) DEFAULT NULL,
  `nomi l_size_2` decimal(65,30) DEFAULT NULL,
  `hex_size` decimal(65,30) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` decimal(65,30) DEFAULT NULL,
  KEY `comp_adaptor_post_component_id_fkey` (`component_id`),
  KEY `comp_adaptor_post_component_type_id_fkey` (`component_type_id`),
  KEY `comp_adaptor_post_end_form_id_2_fkey` (`end_form_id_2`),
  KEY `comp_adaptor_post_end_form_id_1_fkey` (`end_form_id_1`),
  KEY `comp_adaptor_post_connection_type_id_1_fkey` (`connection_type_id_1`),
  KEY `comp_adaptor_post_connection_type_id_2_fkey` (`connection_type_id_2`),
  CONSTRAINT `comp_adaptor_post_component_id_fkey` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_adaptor_post_component_type_id_fkey` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_adaptor_post_connection_type_id_1_fkey` FOREIGN KEY (`connection_type_id_1`) REFERENCES `type_connection` (`connection_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_adaptor_post_connection_type_id_2_fkey` FOREIGN KEY (`connection_type_id_2`) REFERENCES `type_connection` (`connection_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_adaptor_post_end_form_id_1_fkey` FOREIGN KEY (`end_form_id_1`) REFERENCES `type_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_adaptor_post_end_form_id_2_fkey` FOREIGN KEY (`end_form_id_2`) REFERENCES `type_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_boss` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `type` varchar(255) DEFAULT NULL,
  `connection_type_id` varchar(255) DEFAULT NULL,
  `outside_shape` varchar(255) DEFAULT NULL,
  `base_type` varchar(255) DEFAULT NULL,
  `height_over_tube` decimal(65,30) DEFAULT NULL,
  `bolt_pattern_long` decimal(65,30) DEFAULT NULL,
  `bolt_pattern_wide` decimal(65,30) DEFAULT NULL,
  `groove` varchar(255) DEFAULT NULL,
  `base_diameter` decimal(65,30) DEFAULT NULL,
  `shoulder_diameter` decimal(65,30) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` decimal(65,30) DEFAULT NULL,
  KEY `comp_boss_post_component_id_fkey` (`component_id`),
  KEY `comp_boss_post_component_type_id_fkey` (`component_type_id`),
  CONSTRAINT `comp_boss_post_component_id_fkey` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_boss_post_component_type_id_fkey` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_elbow` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `bolt_pattern_long` decimal(65,30) DEFAULT NULL,
  `bolt_pattern_wide` decimal(65,30) DEFAULT NULL,
  `extension_length` decimal(65,30) DEFAULT NULL,
  `overall_length` decimal(65,30) DEFAULT NULL,
  `thickness` decimal(65,30) DEFAULT NULL,
  `drop_length` decimal(65,30) DEFAULT NULL,
  `elbow_angle` decimal(65,30) DEFAULT NULL,
  `mj_class_code` varchar(255) DEFAULT NULL,
  `mj_plug_class_code` varchar(255) DEFAULT NULL,
  `plug_diameter` decimal(65,30) DEFAULT NULL,
  `groove` varchar(255) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` decimal(65,30) DEFAULT NULL,
  KEY `comp_elbow_post_component_id_fkey` (`component_id`),
  KEY `comp_elbow_post_component_type_id_fkey` (`component_type_id`),
  CONSTRAINT `comp_elbow_post_component_id_fkey` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_elbow_post_component_type_id_fkey` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_float` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `bolt_pattern_long` float DEFAULT NULL,
  `bolt_pattern_wide` float DEFAULT NULL,
  `thickness` float DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  KEY `comp_float_component_id` (`component_id`),
  KEY `comp_float_component_type_id` (`component_type_id`),
  CONSTRAINT `comp_float_ibfk_1` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_float_ibfk_2` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_hfl` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `hose_diameter` float DEFAULT NULL,
  `corresponding_shell` varchar(255) DEFAULT NULL,
  `coupling_class` varchar(255) DEFAULT NULL,
  `material` varchar(255) DEFAULT NULL,
  `plating` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  KEY `comp_hfl_component_id` (`component_id`),
  KEY `comp_hfl_component_type_id` (`component_type_id`),
  CONSTRAINT `comp_hfl_ibfk_1` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_hfl_ibfk_2` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_nut` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `hex_nut_size` decimal(65,30) DEFAULT NULL,
  `seat_angle` decimal(65,30) DEFAULT NULL,
  `length` decimal(65,30) DEFAULT NULL,
  `thread_size` varchar(255) DEFAULT NULL,
  `thread_pitch` decimal(65,30) DEFAULT NULL,
  `diameter` decimal(65,30) DEFAULT NULL,
  `blind_hole` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` decimal(65,30) DEFAULT NULL,
  KEY `comp_nut_pos_component_id_fkey` (`component_id`),
  KEY `comp_nut_pos_component_type_id_fkey` (`component_type_id`),
  CONSTRAINT `comp_nut_pos_component_id_fkey` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_nut_pos_component_type_id_fkey` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_other` (
  `component_id` varchar(255) DEFAULT NULL,
  `part_ me` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  KEY `comp_other_component_id` (`component_id`),
  CONSTRAINT `comp_other_ibfk_1` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_sleeve` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `connection_type_id` varchar(255) DEFAULT NULL,
  `length` float DEFAULT NULL,
  `intended_nut_thread` float DEFAULT NULL,
  `intended_nut_pitch` int(11) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `plating` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  KEY `comp_sleeve_component_id` (`component_id`),
  KEY `comp_sleeve_component_type_id` (`component_type_id`),
  KEY `comp_sleeve_connection_type_id` (`connection_type_id`),
  CONSTRAINT `comp_sleeve_ibfk_1` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_sleeve_ibfk_2` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_sleeve_ibfk_3` FOREIGN KEY (`connection_type_id`) REFERENCES `type_connection` (`connection_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_straight` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `bolt_pattern_long` decimal(65,30) DEFAULT NULL,
  `bolt_pattern_wide` decimal(65,30) DEFAULT NULL,
  `head_diameter` decimal(65,30) DEFAULT NULL,
  `overall_length` decimal(65,30) DEFAULT NULL,
  `thickness` decimal(65,30) DEFAULT NULL,
  `mj_class_code` varchar(255) DEFAULT NULL,
  `groove` varchar(255) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` decimal(65,30) DEFAULT NULL,
  KEY `comp_straight_pos_component_id_fkey` (`component_id`),
  KEY `comp_straight_pos_component_type_id_fkey` (`component_type_id`),
  CONSTRAINT `comp_straight_pos_component_id_fkey` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_straight_pos_component_type_id_fkey` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_tee` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `bolt_pattern_long` float DEFAULT NULL,
  `bolt_pattern_wide` float DEFAULT NULL,
  `extension_length` float DEFAULT NULL,
  `overall_length` float DEFAULT NULL,
  `thickness` int(11) DEFAULT NULL,
  `drop_length` float DEFAULT NULL,
  `mj_class_code` varchar(255) DEFAULT NULL,
  `mj_plug_class_code` varchar(255) DEFAULT NULL,
  `groove` varchar(255) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` float DEFAULT NULL,
  KEY `comp_tee_component_id` (`component_id`),
  KEY `comp_tee_component_type_id` (`component_type_id`),
  CONSTRAINT `comp_tee_ibfk_1` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comp_threaded` (
  `component_id` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  `adaptor_angle` decimal(65,30) DEFAULT NULL,
  `overall_length` decimal(65,30) DEFAULT NULL,
  `hex_size` decimal(65,30) DEFAULT NULL,
  `end_form_id_1` varchar(255) DEFAULT NULL,
  `connection_type_id_1` varchar(255) DEFAULT NULL,
  `length_1` decimal(65,30) DEFAULT NULL,
  `thread_size_1` decimal(65,30) DEFAULT NULL,
  `thread_pitch_1` decimal(65,30) DEFAULT NULL,
  `nomi l_size_1` decimal(65,30) DEFAULT NULL,
  `end_form_id_2` varchar(255) DEFAULT NULL,
  `connection_type_id_2` varchar(255) DEFAULT NULL,
  `length_2` decimal(65,30) DEFAULT NULL,
  `thread_size_2` decimal(65,30) DEFAULT NULL,
  `thread_pitch_2` decimal(65,30) DEFAULT NULL,
  `nomi l_size_2` decimal(65,30) DEFAULT NULL,
  `end_form_id_3` varchar(255) DEFAULT NULL,
  `connection_type_id_3` varchar(255) DEFAULT NULL,
  `length_3` decimal(65,30) DEFAULT NULL,
  `thread_size_3` decimal(65,30) DEFAULT NULL,
  `thread_pitch_3` decimal(65,30) DEFAULT NULL,
  `nomi l_size_3` decimal(65,30) DEFAULT NULL,
  `end_form_id_4` varchar(255) DEFAULT NULL,
  `connection_type_id_4` varchar(255) DEFAULT NULL,
  `length_4` decimal(65,30) DEFAULT NULL,
  `thread_size_4` decimal(65,30) DEFAULT NULL,
  `thread_pitch_4` decimal(65,30) DEFAULT NULL,
  `nomi l_size_4` decimal(65,30) DEFAULT NULL,
  `unique_feature` varchar(255) DEFAULT NULL,
  `orientation` varchar(255) DEFAULT NULL,
  `weight` decimal(65,30) DEFAULT NULL,
  KEY `comp_threaded_post_component_type_id_fkey` (`component_type_id`),
  KEY `comp_threaded_post_component_id_fkey` (`component_id`),
  KEY `comp_threaded_post_connection_type_id_4_fkey` (`connection_type_id_4`),
  KEY `comp_threaded_post_connection_type_id_3_fkey` (`connection_type_id_3`),
  KEY `comp_threaded_post_connection_type_id_2_fkey` (`connection_type_id_2`),
  KEY `comp_threaded_post_connection_type_id_1_fkey` (`connection_type_id_1`),
  KEY `comp_threaded_post_end_form_id_4_fkey` (`end_form_id_4`),
  KEY `comp_threaded_post_end_form_id_3_fkey` (`end_form_id_3`),
  KEY `comp_threaded_post_end_form_id_2_fkey` (`end_form_id_2`),
  KEY `comp_threaded_post_end_form_id_1_fkey` (`end_form_id_1`),
  CONSTRAINT `comp_threaded_post_component_id_fkey` FOREIGN KEY (`component_id`) REFERENCES `components` (`component_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_component_type_id_fkey` FOREIGN KEY (`component_type_id`) REFERENCES `type_component` (`component_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_connection_type_id_1_fkey` FOREIGN KEY (`connection_type_id_1`) REFERENCES `type_connection` (`connection_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_connection_type_id_2_fkey` FOREIGN KEY (`connection_type_id_2`) REFERENCES `type_connection` (`connection_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_connection_type_id_3_fkey` FOREIGN KEY (`connection_type_id_3`) REFERENCES `type_connection` (`connection_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_connection_type_id_4_fkey` FOREIGN KEY (`connection_type_id_4`) REFERENCES `type_connection` (`connection_type_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_end_form_id_1_fkey` FOREIGN KEY (`end_form_id_1`) REFERENCES `type_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_end_form_id_2_fkey` FOREIGN KEY (`end_form_id_2`) REFERENCES `type_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_end_form_id_3_fkey` FOREIGN KEY (`end_form_id_3`) REFERENCES `type_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comp_threaded_post_end_form_id_4_fkey` FOREIGN KEY (`end_form_id_4`) REFERENCES `type_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `components` (
  `component_id` varchar(255) NOT NULL,
  `me` varchar(255) DEFAULT NULL,
  `component_type_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`component_id`),
  UNIQUE KEY `components_component_id_key` (`component_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `spec` (
  `tube_assembly_id` varchar(255) DEFAULT NULL,
  `spec` varchar(255) DEFAULT NULL,
  KEY `spec2_tube_assembly_id_fkey` (`tube_assembly_id`),
  CONSTRAINT `spec2_tube_assembly_id_fkey` FOREIGN KEY (`tube_assembly_id`) REFERENCES `tube` (`tube_assembly_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target` (
  `id` bigint(20) NOT NULL,
  `tube_assembly_id` varchar(255) DEFAULT NULL,
  `supplier` varchar(255) DEFAULT NULL,
  `quote_date` date DEFAULT NULL,
  `annual_usage` int(11) DEFAULT NULL,
  `min_order_quantity` int(11) DEFAULT NULL,
  `bracket_pricing` varchar(255) DEFAULT NULL,
  `quantity` int(11) DEFAULT NULL,
  `cost` float DEFAULT NULL,
  `tube_assembly_num` int(11) DEFAULT NULL,
  `supplier_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `target_post_tube_assembly_id_fkey` (`tube_assembly_id`),
  CONSTRAINT `target_post_tube_assembly_id_fkey` FOREIGN KEY (`tube_assembly_id`) REFERENCES `tube` (`tube_assembly_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `trains` (
  `id` int(11) NOT NULL,
  `direction` varchar(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `tube` (
  `tube_assembly_id` varchar(255) NOT NULL,
  `material_id` varchar(255) DEFAULT NULL,
  `diameter` float DEFAULT NULL,
  `wall` float DEFAULT NULL,
  `length` int(11) DEFAULT NULL,
  `num_bends` int(11) DEFAULT NULL,
  `bend_radius` float DEFAULT NULL,
  `end_a_1x` varchar(255) DEFAULT NULL,
  `end_a_2x` varchar(255) DEFAULT NULL,
  `end_x_1x` varchar(255) DEFAULT NULL,
  `end_x_2x` varchar(255) DEFAULT NULL,
  `end_a` varchar(255) DEFAULT NULL,
  `end_x` varchar(255) DEFAULT NULL,
  `num_boss` int(11) DEFAULT NULL,
  `num_bracket` int(11) DEFAULT NULL,
  `other` int(11) DEFAULT NULL,
  PRIMARY KEY (`tube_assembly_id`),
  UNIQUE KEY `tube_tube_assembly_id_key` (`tube_assembly_id`),
  KEY `tube_end_a` (`end_a`),
  KEY `tube_end_a_2` (`end_a`),
  KEY `tube_end_x` (`end_x`),
  CONSTRAINT `tube_ibfk_1` FOREIGN KEY (`end_a`) REFERENCES `tube_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tube_ibfk_2` FOREIGN KEY (`end_x`) REFERENCES `tube_end_form` (`end_form_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tube_end_form` (
  `end_form_id` varchar(255) NOT NULL,
  `forming` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`end_form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `type_component` (
  `component_type_id` varchar(255) NOT NULL,
  `me` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`component_type_id`),
  UNIQUE KEY `type_component_component_type_id_key` (`component_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `type_connection` (
  `connection_type_id` varchar(255) NOT NULL,
  `me` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`connection_type_id`),
  UNIQUE KEY `type_connection_connection_type_id_key` (`connection_type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `type_end_form` (
  `end_form_id` varchar(255) NOT NULL,
  `me` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`end_form_id`),
  UNIQUE KEY `type_end_form_end_form_id_key` (`end_form_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

