-- Schema for database: mutagenesis_42

CREATE TABLE `atoms` (
  `id` int(11) NOT NULL DEFAULT 0,
  `drug_id` int(11) DEFAULT NULL,
  `element` varchar(2) DEFAULT NULL,
  `atom_type` int(11) DEFAULT NULL,
  `charge` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `atoms_drug_id` (`drug_id`) USING BTREE,
  CONSTRAINT `atoms_ibfk_1` FOREIGN KEY (`drug_id`) REFERENCES `drugs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `bonds` (
  `id` int(11) NOT NULL DEFAULT 0,
  `drug_id` int(11) DEFAULT NULL,
  `atom1_id` int(11) DEFAULT NULL,
  `atom2_id` int(11) DEFAULT NULL,
  `bond_type` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `bonds_drug_id` (`drug_id`) USING BTREE,
  KEY `bonds_atom1_id` (`atom1_id`) USING BTREE,
  KEY `bonds_atom2_id` (`atom2_id`) USING BTREE,
  CONSTRAINT `bonds_ibfk_1` FOREIGN KEY (`drug_id`) REFERENCES `drugs` (`id`),
  CONSTRAINT `bonds_ibfk_2` FOREIGN KEY (`atom1_id`) REFERENCES `atoms` (`id`),
  CONSTRAINT `bonds_ibfk_3` FOREIGN KEY (`atom2_id`) REFERENCES `atoms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `drugs` (
  `id` int(11) NOT NULL DEFAULT 0,
  `ind1` float DEFAULT NULL,
  `inda` float DEFAULT NULL,
  `act` float DEFAULT NULL,
  `logp` float DEFAULT NULL,
  `lumo` float DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `ring_atom` (
  `id` int(11) NOT NULL DEFAULT 0,
  `ring_id` int(11) DEFAULT NULL,
  `atom_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ring_atom_ring_id` (`ring_id`) USING BTREE,
  KEY `ring_atom_atom_id` (`atom_id`) USING BTREE,
  CONSTRAINT `ring_atom_ibfk_1` FOREIGN KEY (`ring_id`) REFERENCES `rings` (`id`),
  CONSTRAINT `ring_atom_ibfk_2` FOREIGN KEY (`atom_id`) REFERENCES `atoms` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `ring_strucs` (
  `id` int(11) NOT NULL DEFAULT 0,
  `drug_id` int(11) DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ring_strucs_drug_id` (`drug_id`) USING BTREE,
  CONSTRAINT `ring_strucs_ibfk_1` FOREIGN KEY (`drug_id`) REFERENCES `drugs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `rings` (
  `id` int(11) NOT NULL DEFAULT 0,
  `ring_struc_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `rings_ring_struc_id` (`ring_struc_id`) USING BTREE,
  CONSTRAINT `rings_ibfk_1` FOREIGN KEY (`ring_struc_id`) REFERENCES `ring_strucs` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

