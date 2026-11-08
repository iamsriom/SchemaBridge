-- Schema for database: mutagenesis

CREATE TABLE `atom` (
  `atom_id` char(7) NOT NULL,
  `molecule_id` char(4) NOT NULL,
  `element` char(1) NOT NULL,
  `type` int(11) NOT NULL,
  `charge` double NOT NULL,
  PRIMARY KEY (`atom_id`),
  KEY `molecule_id` (`molecule_id`),
  CONSTRAINT `FK_molecule_atom` FOREIGN KEY (`molecule_id`) REFERENCES `molecule` (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bond` (
  `atom1_id` char(7) NOT NULL,
  `atom2_id` char(7) NOT NULL,
  `type` int(11) NOT NULL,
  PRIMARY KEY (`atom1_id`,`atom2_id`),
  KEY `atom2_id` (`atom2_id`),
  KEY `atom1_id` (`atom1_id`),
  CONSTRAINT `FK_atom1_bond` FOREIGN KEY (`atom1_id`) REFERENCES `atom` (`atom_id`),
  CONSTRAINT `FK_atom2_bond` FOREIGN KEY (`atom2_id`) REFERENCES `atom` (`atom_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `molecule` (
  `molecule_id` char(4) NOT NULL,
  `ind1` int(11) NOT NULL,
  `inda` int(11) NOT NULL,
  `logp` float NOT NULL,
  `lumo` double NOT NULL,
  `mutagenic` char(3) NOT NULL,
  PRIMARY KEY (`molecule_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

