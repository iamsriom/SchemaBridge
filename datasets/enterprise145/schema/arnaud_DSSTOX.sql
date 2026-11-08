-- Schema for database: arnaud_DSSTOX

CREATE TABLE `DSSTOX` (
  `dsstox_substance_id` varchar(255) DEFAULT NULL,
  `dsstox_structure_id` varchar(255) DEFAULT NULL,
  `dsstox_qc_level` varchar(255) DEFAULT NULL,
  `substance_name` varchar(255) DEFAULT NULL,
  `substance_casrn` varchar(255) DEFAULT NULL,
  `substance_type` varchar(255) DEFAULT NULL,
  `substance_note` text DEFAULT NULL,
  `structure_smiles` text DEFAULT NULL,
  `structure_inchi` text DEFAULT NULL,
  `structure_inchikey` varchar(255) DEFAULT NULL,
  `structure_formula` varchar(255) DEFAULT NULL,
  `structure_molwt` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

