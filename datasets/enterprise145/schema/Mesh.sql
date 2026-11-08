-- Schema for database: Mesh

CREATE TABLE `circuit` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `circuit_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `circuit_hole` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `circuit_hole_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `cont_loaded` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `cont_loaded_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `element` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `equal` (
  `name1` varchar(5) NOT NULL DEFAULT '',
  `name2` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `name1` (`name1`),
  KEY `name2` (`name2`),
  CONSTRAINT `equal_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `equal_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `fixed` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `fixed_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `free` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `free_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `half_circuit` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `half_circuit_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `half_circuit_hole` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `half_circuit_hole_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `llong` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `llong_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `long_for_hole` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `long_for_hole_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mesh` (
  `name` varchar(5) NOT NULL DEFAULT '',
  `num` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  KEY `num` (`num`),
  CONSTRAINT `mesh_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `mesh_ibfk_2` FOREIGN KEY (`num`) REFERENCES `nnumber` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mesh_test` (
  `name` varchar(5) NOT NULL DEFAULT '',
  `num` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  KEY `num` (`num`),
  CONSTRAINT `mesh_test_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mesh_test_Neg` (
  `name` varchar(5) DEFAULT NULL,
  `num` varchar(5) DEFAULT NULL,
  KEY `name` (`name`),
  KEY `num` (`num`),
  CONSTRAINT `mesh_test_Neg_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `neighbour_xy` (
  `name1` varchar(5) NOT NULL DEFAULT '',
  `name2` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `name1` (`name1`),
  KEY `name2` (`name2`),
  CONSTRAINT `neighbour_xy_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `neighbour_xy_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `neighbour_yz` (
  `name1` varchar(5) NOT NULL,
  `name2` varchar(5) NOT NULL,
  KEY `name1` (`name1`),
  KEY `name2` (`name2`),
  CONSTRAINT `neighbour_yz_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `neighbour_yz_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `neighbour_zx` (
  `name1` varchar(5) NOT NULL DEFAULT '',
  `name2` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `name1` (`name1`),
  KEY `name2` (`name2`),
  CONSTRAINT `neighbour_zx_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `neighbour_zx_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nnumber` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `noload` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `noload_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `notimportant` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `notimportant_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `one_side_fixed` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `one_side_fixed_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `one_side_loaded` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `one_side_loaded_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `opposite` (
  `name1` varchar(5) NOT NULL DEFAULT '',
  `name2` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `name1` (`name1`),
  KEY `name2` (`name2`),
  CONSTRAINT `opposite_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `opposite_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `quarter_circuit` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `quarter_circuit_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `short_for_hole` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `short_for_hole_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sshort` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `sshort_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `two_side_fixed` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `two_side_fixed_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `two_side_loaded` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `two_side_loaded_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `usual` (
  `name` varchar(5) NOT NULL DEFAULT '',
  PRIMARY KEY (`name`),
  KEY `name` (`name`),
  CONSTRAINT `usual_ibfk_1` FOREIGN KEY (`name`) REFERENCES `element` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

