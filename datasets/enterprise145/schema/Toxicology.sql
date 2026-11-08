-- Schema for database: Toxicology

CREATE TABLE `atom` (
  `atom_id` varchar(255) NOT NULL,
  `molecule_id` varchar(255) DEFAULT NULL,
  `element` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`atom_id`),
  KEY `molecule_id` (`molecule_id`),
  KEY `atom_id` (`atom_id`),
  CONSTRAINT `atom_ibfk_1` FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bond` (
  `bond_id` varchar(255) NOT NULL,
  `molecule_id` varchar(255) DEFAULT NULL,
  `bond_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`bond_id`),
  KEY `bond_id` (`bond_id`),
  KEY `molecule_id` (`molecule_id`),
  CONSTRAINT `bond_ibfk_1` FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `connected` (
  `atom_id` varchar(255) NOT NULL,
  `atom_id2` varchar(255) NOT NULL,
  `bond_id` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`atom_id`,`atom_id2`),
  KEY `atom_id` (`atom_id`),
  KEY `atom_id2` (`atom_id2`),
  KEY `bond_id` (`bond_id`),
  CONSTRAINT `connected_ibfk_1` FOREIGN KEY (`atom_id`) REFERENCES `atom` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `connected_ibfk_2` FOREIGN KEY (`atom_id2`) REFERENCES `atom` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `connected_ibfk_3` FOREIGN KEY (`bond_id`) REFERENCES `bond` (`bond_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `molecule` (
  `molecule_id` varchar(255) NOT NULL,
  `label` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`molecule_id`),
  KEY `molecule_id` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

