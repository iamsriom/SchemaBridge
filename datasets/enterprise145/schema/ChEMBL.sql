-- Schema for database: ChEMBL

CREATE TABLE `activities` (
  `activity_id` int(11) NOT NULL,
  `assay_id` int(11) DEFAULT NULL,
  `doc_id` int(11) DEFAULT NULL,
  `record_id` int(11) DEFAULT NULL,
  `molregno` int(11) DEFAULT NULL,
  `relation` varchar(50) DEFAULT NULL,
  `published_value` float DEFAULT NULL,
  `published_units` varchar(100) DEFAULT NULL,
  `standard_value` float DEFAULT NULL,
  `standard_units` varchar(100) DEFAULT NULL,
  `standard_flag` int(11) DEFAULT NULL,
  `standard_type` varchar(250) DEFAULT NULL,
  `activity_comment` varchar(255) DEFAULT NULL,
  `published_activity_type` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`activity_id`),
  KEY `activities_idx_assay_id` (`assay_id`),
  KEY `activities_idx_doc_id` (`doc_id`),
  KEY `activities_idx_molregno` (`molregno`),
  KEY `activities_idx_record_id` (`record_id`),
  CONSTRAINT `activities_fk_assay_id` FOREIGN KEY (`assay_id`) REFERENCES `assays` (`assay_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `activities_fk_doc_id` FOREIGN KEY (`doc_id`) REFERENCES `docs` (`doc_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `activities_fk_molregno` FOREIGN KEY (`molregno`) REFERENCES `compounds` (`molregno`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `activities_fk_record_id` FOREIGN KEY (`record_id`) REFERENCES `compound_records` (`record_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `assay2target` (
  `assay_id` int(11) NOT NULL,
  `tid` int(11) NOT NULL,
  `assay_tax_id` int(11) DEFAULT NULL,
  `assay_organism` varchar(250) DEFAULT NULL,
  `relationship_type` char(1) DEFAULT NULL,
  `complex` int(11) DEFAULT NULL,
  `multi` int(11) DEFAULT NULL,
  `confidence` int(11) DEFAULT NULL,
  `assay_strain` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`assay_id`,`tid`),
  KEY `assay2target_idx_assay_id` (`assay_id`),
  KEY `assay2target_idx_confidence` (`confidence`),
  KEY `assay2target_idx_tid` (`tid`),
  CONSTRAINT `assay2target_fk_assay_id` FOREIGN KEY (`assay_id`) REFERENCES `assays` (`assay_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `assay2target_fk_confidence` FOREIGN KEY (`confidence`) REFERENCES `confidence_lookup` (`confidence`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `assay2target_fk_tid` FOREIGN KEY (`tid`) REFERENCES `target_dictionary` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `assay_type` (
  `assay_type` varchar(1) NOT NULL,
  `assay_desc` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`assay_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `assays` (
  `assay_id` int(11) NOT NULL,
  `assay_type` varchar(250) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `doc_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`assay_id`),
  KEY `assays_idx_assay_type` (`assay_type`),
  KEY `assays_idx_doc_id` (`doc_id`),
  CONSTRAINT `assays_fk_assay_type` FOREIGN KEY (`assay_type`) REFERENCES `assay_type` (`assay_type`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `assays_fk_doc_id` FOREIGN KEY (`doc_id`) REFERENCES `docs` (`doc_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `compound_properties` (
  `molregno` int(11) NOT NULL,
  `mw_freebase` float DEFAULT NULL,
  `alogp` float DEFAULT NULL,
  `hba` int(11) DEFAULT NULL,
  `hbd` int(11) DEFAULT NULL,
  `psa` float DEFAULT NULL,
  `rtb` int(11) DEFAULT NULL,
  `ro3_pass` varchar(3) DEFAULT NULL,
  `num_ro5_violations` int(11) DEFAULT NULL,
  `med_chem_friendly` varchar(3) DEFAULT NULL,
  `mol_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`molregno`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `compound_records` (
  `record_id` int(11) NOT NULL,
  `molregno` int(11) DEFAULT NULL,
  `doc_id` int(11) DEFAULT NULL,
  `compound_key` varchar(250) DEFAULT NULL,
  `compound_name` text DEFAULT NULL,
  PRIMARY KEY (`record_id`),
  KEY `compound_records_idx_doc_id` (`doc_id`),
  KEY `compound_records_idx_molregno` (`molregno`),
  CONSTRAINT `compound_records_fk_doc_id` FOREIGN KEY (`doc_id`) REFERENCES `docs` (`doc_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `compound_records_fk_molregno` FOREIGN KEY (`molregno`) REFERENCES `compounds` (`molregno`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `compound_synonyms` (
  `molregno` int(11) NOT NULL,
  `synonyms` varchar(100) NOT NULL,
  PRIMARY KEY (`molregno`,`synonyms`),
  KEY `compound_synonyms_idx_molregno` (`molregno`),
  CONSTRAINT `compound_synonyms_fk_molregno` FOREIGN KEY (`molregno`) REFERENCES `compounds` (`molregno`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `compounds` (
  `molregno` int(11) NOT NULL,
  `molweight` float DEFAULT NULL,
  `molformula` varchar(250) DEFAULT NULL,
  `molfile` longtext DEFAULT NULL,
  `canonical_smiles` text DEFAULT NULL,
  `inchi` text DEFAULT NULL,
  `inchi_key` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`molregno`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `confidence_lookup` (
  `confidence` int(11) NOT NULL,
  `confidence_summary` varchar(100) DEFAULT NULL,
  `description` text DEFAULT NULL,
  PRIMARY KEY (`confidence`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `docs` (
  `doc_id` int(11) NOT NULL,
  `journal` varchar(50) DEFAULT NULL,
  `year` varchar(50) DEFAULT NULL,
  `volume` varchar(50) DEFAULT NULL,
  `issue` varchar(50) DEFAULT NULL,
  `first_page` varchar(50) DEFAULT NULL,
  `last_page` varchar(50) DEFAULT NULL,
  `pubmed_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`doc_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `relationship_type` (
  `relationship_type` varchar(25) NOT NULL,
  `relationship_desc` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`relationship_type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `target_class` (
  `tc_id` int(11) NOT NULL,
  `tid` int(11) DEFAULT NULL,
  `l1` varchar(100) DEFAULT NULL,
  `l2` varchar(100) DEFAULT NULL,
  `l3` varchar(100) DEFAULT NULL,
  `l4` varchar(100) DEFAULT NULL,
  `l5` varchar(100) DEFAULT NULL,
  `l6` varchar(100) DEFAULT NULL,
  `l7` varchar(100) DEFAULT NULL,
  `l8` varchar(100) DEFAULT NULL,
  `target_classification` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`tc_id`),
  KEY `target_class_idx_tid` (`tid`),
  CONSTRAINT `target_class_fk_tid` FOREIGN KEY (`tid`) REFERENCES `target_dictionary` (`tid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `target_dictionary` (
  `tid` int(11) NOT NULL,
  `target_type` varchar(25) DEFAULT NULL,
  `db_source` varchar(25) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `gene_names` text DEFAULT NULL,
  `pref_name` varchar(200) DEFAULT NULL,
  `synonyms` text DEFAULT NULL,
  `keywords` text DEFAULT NULL,
  `protein_sequence` longtext DEFAULT NULL,
  `protein_md5sum` varchar(32) DEFAULT NULL,
  `tax_id` int(11) DEFAULT NULL,
  `organism` varchar(100) DEFAULT NULL,
  `tissue` varchar(50) DEFAULT NULL,
  `strain` varchar(25) DEFAULT NULL,
  `db_version` varchar(25) DEFAULT NULL,
  `cell_line` varchar(50) DEFAULT NULL,
  `in_drugstore` tinyint(1) DEFAULT NULL,
  `in_starlite` tinyint(1) DEFAULT NULL,
  `protein_accession` varchar(25) DEFAULT NULL,
  `ec_number` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`tid`),
  KEY `target_dictionary_idx_target_type` (`target_type`),
  CONSTRAINT `target_dictionary_fk_target_type` FOREIGN KEY (`target_type`) REFERENCES `target_type` (`target_type`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `target_protein` (
  `canonical_smiles` text CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `relation` varchar(50) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `standard_units` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `standard_value` float DEFAULT NULL,
  `standard_type` varchar(250) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `assay_type` varchar(250) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `relationship_type` char(1) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `assay_organism` varchar(250) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `target_type` varchar(25) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `organism` varchar(100) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL,
  `protein_accession` varchar(25) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `target_type` (
  `target_type` varchar(25) NOT NULL,
  `target_desc` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`target_type`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `version` (
  `name` varchar(20) NOT NULL,
  `creation_date` date DEFAULT NULL,
  `comments` text DEFAULT NULL,
  PRIMARY KEY (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

