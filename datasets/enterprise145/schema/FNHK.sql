-- Schema for database: FNHK

CREATE TABLE `pripady` (
  `Identifikace_pripadu` int(11) NOT NULL,
  `Identifikator_pacienta` int(11) NOT NULL,
  `Kod_zdravotni_pojistovny` int(11) NOT NULL,
  `Datum_prijeti` date NOT NULL,
  `Datum_propusteni` date NOT NULL,
  `Delka_hospitalizace` int(11) NOT NULL,
  `Vekovy_Interval_Pacienta` varchar(255) NOT NULL,
  `Pohlavi_pacienta` char(1) NOT NULL,
  `Zakladni_diagnoza` varchar(255) NOT NULL,
  `Seznam_vedlejsich_diagnoz` varchar(255) NOT NULL,
  `DRG_skupina` int(11) NOT NULL,
  `PSC` char(5) DEFAULT NULL,
  PRIMARY KEY (`Identifikace_pripadu`),
  KEY `pripady__identifikator_pacienta_indx` (`Identifikator_pacienta`),
  KEY `pripady__datum_prijeti_indx` (`Datum_prijeti`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `vykony` (
  `Identifikace_pripadu` int(11) NOT NULL,
  `Datum_provedeni_vykonu` date NOT NULL,
  `Typ_polozky` int(11) NOT NULL,
  `Kod_polozky` int(11) NOT NULL,
  `Pocet` int(11) NOT NULL,
  `Body` int(11) NOT NULL,
  PRIMARY KEY (`Identifikace_pripadu`,`Datum_provedeni_vykonu`,`Kod_polozky`),
  KEY `vykony_Identifikace_pripadu` (`Identifikace_pripadu`) USING BTREE,
  CONSTRAINT `vykony_ibfk_1` FOREIGN KEY (`Identifikace_pripadu`) REFERENCES `pripady` (`Identifikace_pripadu`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `zup` (
  `Identifikace_pripadu` int(11) NOT NULL,
  `Datum_provedeni_vykonu` date NOT NULL,
  `Typ_polozky` int(11) DEFAULT NULL,
  `Kod_polozky` int(11) NOT NULL,
  `Pocet` decimal(10,2) DEFAULT NULL,
  `Cena` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`Identifikace_pripadu`,`Datum_provedeni_vykonu`,`Kod_polozky`),
  KEY `zup_Identifikace_pripadu` (`Identifikace_pripadu`) USING BTREE,
  CONSTRAINT `zup_ibfk_1` FOREIGN KEY (`Identifikace_pripadu`) REFERENCES `pripady` (`Identifikace_pripadu`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

