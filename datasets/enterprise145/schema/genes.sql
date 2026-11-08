-- Schema for database: genes

CREATE TABLE `Classification` (
  `GeneID` varchar(7) NOT NULL,
  `Localization` varchar(255) NOT NULL,
  PRIMARY KEY (`GeneID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `Genes` (
  `GeneID` varchar(7) NOT NULL,
  `Essential` varchar(255) NOT NULL,
  `Class` varchar(100) NOT NULL,
  `Complex` varchar(255) DEFAULT NULL,
  `Phenotype` varchar(255) NOT NULL,
  `Motif` varchar(255) NOT NULL,
  `Chromosome` int(11) NOT NULL,
  `Function` varchar(100) NOT NULL,
  `Localization` varchar(255) NOT NULL,
  KEY `GeneID` (`GeneID`),
  CONSTRAINT `Genes_ibfk_1` FOREIGN KEY (`GeneID`) REFERENCES `Classification` (`GeneID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `Interactions` (
  `GeneID1` varchar(7) NOT NULL,
  `GeneID2` varchar(7) NOT NULL,
  `Type` varchar(255) NOT NULL,
  `Expression_Corr` decimal(10,9) NOT NULL,
  PRIMARY KEY (`GeneID1`,`GeneID2`),
  KEY `GeneID2` (`GeneID2`),
  CONSTRAINT `Interactions_ibfk_1` FOREIGN KEY (`GeneID1`) REFERENCES `Classification` (`GeneID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `Interactions_ibfk_2` FOREIGN KEY (`GeneID2`) REFERENCES `Classification` (`GeneID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

