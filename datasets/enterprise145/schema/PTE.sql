-- Schema for database: PTE

CREATE TABLE `active` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`),
  KEY `active_Arg0` (`Arg0`) USING BTREE,
  CONSTRAINT `active_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `postestactive` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`),
  KEY `postestactive_Arg0` (`Arg0`) USING BTREE,
  CONSTRAINT `postestactive_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `postestactive_Neg` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`),
  KEY `postestactive_Neg_Arg0` (`Arg0`) USING BTREE,
  CONSTRAINT `postestactive_Neg_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_active` (
  `drug_id` varchar(80) NOT NULL,
  `is_active` varchar(80) DEFAULT 'F',
  KEY `pte_active_drug_id` (`drug_id`) USING BTREE,
  KEY `pte_active_is_active` (`is_active`) USING BTREE,
  CONSTRAINT `pte_active_ibfk_2` FOREIGN KEY (`is_active`) REFERENCES `pte_number` (`Binary`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pte_active_ibfk_3` FOREIGN KEY (`drug_id`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_alcohol` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_alcohol_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_alcohol_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_alcohol_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_alkyl_halide` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_alkyl_halide_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_alkyl_halide_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_alkyl_halide_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_ames` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`),
  KEY `pte_ames_Arg0` (`Arg0`) USING BTREE,
  CONSTRAINT `pte_ames_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_amine` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_amine_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_amine_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_amine_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_atm` (
  `drug_id` varchar(80) DEFAULT NULL,
  `atom_id` varchar(80) NOT NULL,
  `atom_type` varchar(80) DEFAULT NULL,
  `Arg3` varchar(80) DEFAULT NULL,
  `Arg4` decimal(18,3) DEFAULT 0.000,
  PRIMARY KEY (`atom_id`),
  KEY `pte_atm_drug_id` (`drug_id`) USING BTREE,
  KEY `pte_atm_atom_id` (`atom_id`) USING BTREE,
  CONSTRAINT `pte_atm_ibfk_1` FOREIGN KEY (`drug_id`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_atm_bond_count` (
  `atom_id` varchar(80) NOT NULL DEFAULT '',
  `Cnt` int(11) DEFAULT 0,
  PRIMARY KEY (`atom_id`),
  KEY `pte_atm_bond_count_Arg0` (`atom_id`) USING BTREE,
  KEY `pte_atm_bond_count_Cnt` (`Cnt`) USING BTREE,
  CONSTRAINT `pte_atm_bond_count_ibfk_1` FOREIGN KEY (`atom_id`) REFERENCES `pte_atm` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_atm_count` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Cnt` int(11) DEFAULT 0,
  PRIMARY KEY (`Arg0`),
  KEY `pte_atm_count_Cnt` (`Cnt`) USING BTREE,
  KEY `pte_atm_count_Arg0` (`Arg0`) USING BTREE,
  CONSTRAINT `pte_atm_count_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_atm_max_charge` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Mx` decimal(18,3) DEFAULT 0.000,
  PRIMARY KEY (`Arg0`),
  KEY `pte_atm_max_charge_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_atm_max_charge_Mx` (`Mx`) USING BTREE,
  CONSTRAINT `pte_atm_max_charge_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_atm_min_charge` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Mn` decimal(18,3) DEFAULT 0.000,
  PRIMARY KEY (`Arg0`),
  KEY `pte_atm_min_charge_Mn` (`Mn`) USING BTREE,
  KEY `pte_atm_min_charge_Arg0` (`Arg0`) USING BTREE,
  CONSTRAINT `pte_atm_min_charge_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_bond` (
  `drug_id` varchar(80) DEFAULT NULL,
  `atom_id1` varchar(80) NOT NULL,
  `atom_id2` varchar(80) NOT NULL,
  `Arg3` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`atom_id1`,`atom_id2`),
  KEY `pte_bond_drug_id` (`drug_id`) USING BTREE,
  KEY `pte_bond_atom_id1` (`atom_id1`) USING BTREE,
  KEY `pte_bond_atom_id2` (`atom_id2`) USING BTREE,
  CONSTRAINT `pte_bond_ibfk_1` FOREIGN KEY (`atom_id1`) REFERENCES `pte_atm` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pte_bond_ibfk_2` FOREIGN KEY (`atom_id2`) REFERENCES `pte_atm` (`atom_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `pte_bond_ibfk_3` FOREIGN KEY (`drug_id`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_bond_count` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Cnt` int(11) DEFAULT 0,
  PRIMARY KEY (`Arg0`),
  KEY `pte_bond_count_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_bond_count_Cnt` (`Cnt`) USING BTREE,
  CONSTRAINT `pte_bond_count_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_drug` (
  `drug_id` varchar(80) NOT NULL,
  PRIMARY KEY (`drug_id`),
  KEY `pte_drug_drug_id` (`drug_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_ester` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_ester_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_ester_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_ester_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_ether` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_ether_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_ether_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_ether_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_five_ring` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_five_ring_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_five_ring_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_five_ring_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_has_property` (
  `Arg0` varchar(80) NOT NULL,
  `Arg1` varchar(80) NOT NULL,
  `Arg2` varchar(80) NOT NULL,
  KEY `pte_has_property_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_has_property_Arg1` (`Arg1`) USING BTREE,
  KEY `pte_has_property_Arg2` (`Arg2`) USING BTREE,
  CONSTRAINT `pte_has_property_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_imine` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_imine_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_imine_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_imine_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_ind` (
  `Arg0` varchar(80) NOT NULL,
  `Arg1` varchar(80) NOT NULL,
  `Arg2` varchar(80) NOT NULL,
  PRIMARY KEY (`Arg0`,`Arg1`),
  KEY `pte_ind_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_ind_Arg1` (`Arg1`) USING BTREE,
  KEY `pte_ind_Arg2` (`Arg2`) USING BTREE,
  CONSTRAINT `pte_ind_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_ketone` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_ketone_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_ketone_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_ketone_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_methoxy` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_methoxy_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_methoxy_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_methoxy_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_methyl` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_methyl_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_methyl_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_methyl_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_mutagenic` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`),
  KEY `pte_mutagenic_Arg0` (`Arg0`) USING BTREE,
  CONSTRAINT `pte_mutagenic_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_nitro` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_nitro_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_nitro_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_nitro_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_non_ar_5c_ring` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_non_ar_5c_ring_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_non_ar_5c_ring_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_non_ar_5c_ring_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_non_ar_6c_ring` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_non_ar_6c_ring_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_non_ar_6c_ring_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_non_ar_6c_ring_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_non_ar_hetero_5_ring` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_non_ar_hetero_5_ring_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_non_ar_hetero_5_ring_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_non_ar_hetero_5_ring_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_non_ar_hetero_6_ring` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_non_ar_hetero_6_ring_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_non_ar_hetero_6_ring_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_non_ar_hetero_6_ring_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_number` (
  `Binary` varchar(5) NOT NULL,
  PRIMARY KEY (`Binary`),
  KEY `pte_number_Binary` (`Binary`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_phenol` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_phenol_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_phenol_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_phenol_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_six_ring` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_six_ring_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_six_ring_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_six_ring_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_sulfide` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_sulfide_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_sulfide_Arg1` (`Set`) USING BTREE,
  CONSTRAINT `pte_sulfide_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_sulfo` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) NOT NULL DEFAULT '',
  PRIMARY KEY (`Arg0`,`Set`),
  KEY `pte_sulfo_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_sulfo_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_sulfo_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_testactive` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Set` varchar(80) DEFAULT 'F',
  PRIMARY KEY (`Arg0`),
  KEY `pte_testactive_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_testactive_Set` (`Set`) USING BTREE,
  CONSTRAINT `pte_testactive_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pte_testactive_Neg` (
  `Arg0` varchar(80) NOT NULL DEFAULT '',
  `Binary` varchar(5) DEFAULT 'F',
  PRIMARY KEY (`Arg0`),
  KEY `pte_testactive_Neg_Arg0` (`Arg0`) USING BTREE,
  KEY `pte_testactive_Neg_Binary` (`Binary`) USING BTREE,
  CONSTRAINT `pte_testactive_Neg_ibfk_1` FOREIGN KEY (`Arg0`) REFERENCES `pte_drug` (`drug_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

