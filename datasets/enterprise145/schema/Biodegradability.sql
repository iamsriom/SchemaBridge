-- Schema for database: Biodegradability

CREATE TABLE `atom` (
  `atom_id` varchar(255) NOT NULL,
  `molecule_id` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  PRIMARY KEY (`atom_id`),
  KEY `atom_molecule_id` (`molecule_id`),
  CONSTRAINT `atom_ibfk_1` FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bond` (
  `atom_id` varchar(255) NOT NULL,
  `atom_id2` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  PRIMARY KEY (`atom_id`,`atom_id2`),
  KEY `bond_atom_id2` (`atom_id2`),
  CONSTRAINT `bond_ibfk_1` FOREIGN KEY (`atom_id`) REFERENCES `atom` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `bond_ibfk_2` FOREIGN KEY (`atom_id2`) REFERENCES `atom` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gmember` (
  `atom_id` varchar(255) NOT NULL,
  `group_id` varchar(255) NOT NULL,
  PRIMARY KEY (`atom_id`,`group_id`),
  KEY `gmember_group_id` (`group_id`),
  CONSTRAINT `gmember_ibfk_1` FOREIGN KEY (`atom_id`) REFERENCES `atom` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `gmember_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `group` (`group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `group` (
  `group_id` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  PRIMARY KEY (`group_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `molecule` (
  `molecule_id` varchar(255) NOT NULL,
  `activity` float NOT NULL,
  `logp` float NOT NULL,
  `mweight` float NOT NULL,
  PRIMARY KEY (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

