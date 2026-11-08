-- Schema for database: geneea

CREATE TABLE `bod_schuze` (
  `id_bod` int(11) NOT NULL,
  `id_schuze` int(11) NOT NULL,
  `id_tisk` varchar(255) DEFAULT NULL,
  `id_typ` varchar(255) DEFAULT NULL,
  `bod` int(11) NOT NULL,
  `uplny_naz` text DEFAULT NULL,
  `uplny_kon` varchar(255) DEFAULT NULL,
  `poznamka` varchar(255) DEFAULT NULL,
  `id_bod_stav` int(11) NOT NULL,
  `pozvanka` varchar(255) DEFAULT NULL,
  `rj` varchar(255) DEFAULT NULL,
  `pozn2` varchar(255) DEFAULT NULL,
  `druh_bodu` varchar(255) DEFAULT NULL,
  `id_sd` varchar(255) DEFAULT NULL,
  `zkratka` varchar(255) DEFAULT NULL,
  KEY `bod_schuze_id_bod` (`id_bod`),
  KEY `bod_schuze_id_bod_stav` (`id_bod_stav`),
  KEY `bod_schuze_id_schuze` (`id_schuze`),
  CONSTRAINT `bod_schuze_ibfk_1` FOREIGN KEY (`id_schuze`) REFERENCES `schuze` (`id_schuze`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `bod_schuze_ibfk_2` FOREIGN KEY (`id_bod_stav`) REFERENCES `bod_stav` (`id_bod_stav`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `bod_stav` (
  `id_bod_stav` int(11) NOT NULL,
  `popis` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_bod_stav`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `funkce` (
  `id_funkce` int(11) NOT NULL,
  `id_organ` int(11) DEFAULT NULL,
  `id_typ_funkce` int(11) DEFAULT NULL,
  `nazev_funkce_cz` text DEFAULT NULL,
  `priorita` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_funkce`),
  KEY `funkce_id_organ` (`id_organ`),
  KEY `funkce_id_typ_funkce` (`id_typ_funkce`),
  CONSTRAINT `funkce_ibfk_1` FOREIGN KEY (`id_organ`) REFERENCES `organy` (`id_organ`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `funkce_ibfk_2` FOREIGN KEY (`id_typ_funkce`) REFERENCES `typ_funkce` (`id_typ_funkce`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `hl_check` (
  `id_hlasovani` int(11) DEFAULT NULL,
  `turn` int(11) DEFAULT NULL,
  `mode` int(11) DEFAULT NULL,
  `id_h2` varchar(255) DEFAULT NULL,
  `id_h3` varchar(255) DEFAULT NULL,
  KEY `hl_check_id_hlasovani` (`id_hlasovani`),
  CONSTRAINT `hl_check_ibfk_1` FOREIGN KEY (`id_hlasovani`) REFERENCES `hl_hlasovani` (`id_hlasovani`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `hl_hlasovani` (
  `id_hlasovani` int(11) NOT NULL,
  `id_organ` int(11) DEFAULT NULL,
  `schuze` int(11) DEFAULT NULL,
  `cislo` int(11) DEFAULT NULL,
  `bod` int(11) DEFAULT NULL,
  `datum` date DEFAULT NULL,
  `cas` time DEFAULT NULL,
  `pro` int(11) DEFAULT NULL,
  `proti` int(11) DEFAULT NULL,
  `zdrzel` int(11) DEFAULT NULL,
  `nehlasoval` int(11) DEFAULT NULL,
  `prihlaseno` int(11) DEFAULT NULL,
  `kvorum` int(11) DEFAULT NULL,
  `druh_hlasovani` varchar(255) DEFAULT NULL,
  `vysledek` varchar(255) DEFAULT NULL,
  `nazev_dlouhy` text DEFAULT NULL,
  `nazev_kratky` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_hlasovani`),
  KEY `hl_hlasovani_id_organ` (`id_organ`),
  CONSTRAINT `hl_hlasovani_ibfk_1` FOREIGN KEY (`id_organ`) REFERENCES `organy` (`id_organ`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `hl_poslanec` (
  `id_poslanec` int(11) NOT NULL,
  `id_hlasovani` int(11) NOT NULL,
  `vysledek` varchar(255) DEFAULT NULL,
  KEY `hl_poslanec_id_poslanec` (`id_poslanec`),
  CONSTRAINT `hl_poslanec_ibfk_1` FOREIGN KEY (`id_poslanec`) REFERENCES `poslanec` (`id_poslanec`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `hl_vazby` (
  `id_hlasovani` int(11) DEFAULT NULL,
  `turn` int(11) DEFAULT NULL,
  `typ` int(11) DEFAULT NULL,
  KEY `hl_vazby_id_hlasovani` (`id_hlasovani`),
  CONSTRAINT `hl_vazby_ibfk_1` FOREIGN KEY (`id_hlasovani`) REFERENCES `hl_hlasovani` (`id_hlasovani`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `hl_zposlanec` (
  `id_hlasovani` int(11) DEFAULT NULL,
  `id_osoba` int(11) DEFAULT NULL,
  `mode` int(11) DEFAULT NULL,
  KEY `hl_zposlanec_id_hlasovani` (`id_hlasovani`),
  KEY `hl_zposlanec_id_osoba` (`id_osoba`),
  CONSTRAINT `hl_zposlanec_ibfk_1` FOREIGN KEY (`id_hlasovani`) REFERENCES `hl_hlasovani` (`id_hlasovani`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `hl_zposlanec_ibfk_2` FOREIGN KEY (`id_osoba`) REFERENCES `osoby` (`id_osoba`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `omluvy` (
  `id_organ` int(11) NOT NULL,
  `id_poslanec` int(11) NOT NULL,
  `den` varchar(255) NOT NULL,
  `od` varchar(255) DEFAULT NULL,
  `do` varchar(255) DEFAULT NULL,
  KEY `omluvy_id_organ` (`id_organ`),
  KEY `omluvy_id_poslanec` (`id_poslanec`),
  CONSTRAINT `omluvy_ibfk_1` FOREIGN KEY (`id_organ`) REFERENCES `organy` (`id_organ`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `omluvy_ibfk_2` FOREIGN KEY (`id_poslanec`) REFERENCES `poslanec` (`id_poslanec`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `organy` (
  `id_organ` int(11) NOT NULL,
  `organ_id_organ` int(11) DEFAULT NULL,
  `id_typ_organu` int(11) DEFAULT NULL,
  `zkratka` varchar(255) DEFAULT NULL,
  `nazev_organu_cz` text DEFAULT NULL,
  `nazev_organu_en` text DEFAULT NULL,
  `od_organ` varchar(255) DEFAULT NULL,
  `do_organ` varchar(255) DEFAULT NULL,
  `priorita` varchar(255) DEFAULT NULL,
  `cl_organ_base` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_organ`),
  KEY `organy_id_typ_organu` (`id_typ_organu`),
  KEY `organy_organ_id_organ` (`organ_id_organ`),
  CONSTRAINT `organy_ibfk_1` FOREIGN KEY (`id_typ_organu`) REFERENCES `typ_organu` (`id_typ_org`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `osoby` (
  `id_osoba` int(11) NOT NULL,
  `pred` varchar(255) DEFAULT NULL,
  `jmeno` varchar(255) DEFAULT NULL,
  `prijmeni` varchar(255) DEFAULT NULL,
  `za` varchar(255) DEFAULT NULL,
  `narozeni` varchar(255) DEFAULT NULL,
  `pohlavi` varchar(255) DEFAULT NULL,
  `zmena` varchar(255) DEFAULT NULL,
  `umrti` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_osoba`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `pkgps` (
  `id_poslanec` int(11) DEFAULT NULL,
  `adresa` varchar(255) DEFAULT NULL,
  `sirka` float DEFAULT NULL,
  `delka` float DEFAULT NULL,
  KEY `pkgps_id_poslanec` (`id_poslanec`),
  CONSTRAINT `pkgps_ibfk_1` FOREIGN KEY (`id_poslanec`) REFERENCES `poslanec` (`id_poslanec`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `poslanec` (
  `id_poslanec` int(11) NOT NULL,
  `id_osoba` int(11) DEFAULT NULL,
  `id_kraj` int(11) DEFAULT NULL,
  `id_kandidatka` int(11) DEFAULT NULL,
  `id_obdobi` int(11) DEFAULT NULL,
  `web` varchar(255) DEFAULT NULL,
  `ulice` varchar(255) DEFAULT NULL,
  `obec` varchar(255) DEFAULT NULL,
  `psc` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `telefon` varchar(255) DEFAULT NULL,
  `fax` varchar(255) DEFAULT NULL,
  `psp_telefon` varchar(255) DEFAULT NULL,
  `facebook` varchar(255) DEFAULT NULL,
  `foto` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_poslanec`),
  KEY `poslanec_id_osoba` (`id_osoba`),
  CONSTRAINT `poslanec_ibfk_1` FOREIGN KEY (`id_osoba`) REFERENCES `osoby` (`id_osoba`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `schuze` (
  `id_schuze` int(11) NOT NULL,
  `id_organ` int(11) DEFAULT NULL,
  `schuze` int(11) DEFAULT NULL,
  `od_schuze` varchar(255) DEFAULT NULL,
  `do_schuze` varchar(255) DEFAULT NULL,
  `aktualizace` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_schuze`),
  KEY `schuze_id_organ` (`id_organ`),
  CONSTRAINT `schuze_ibfk_1` FOREIGN KEY (`id_organ`) REFERENCES `organy` (`id_organ`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `schuze_stav` (
  `id_schuze` int(11) DEFAULT NULL,
  `stav` int(11) DEFAULT NULL,
  `typ` varchar(255) DEFAULT NULL,
  `text_dt` varchar(255) DEFAULT NULL,
  `text_st` varchar(255) DEFAULT NULL,
  `tm_line` varchar(255) DEFAULT NULL,
  KEY `schuze_stav_id_schuze` (`id_schuze`),
  CONSTRAINT `schuze_stav_ibfk_1` FOREIGN KEY (`id_schuze`) REFERENCES `schuze` (`id_schuze`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `typ_funkce` (
  `id_typ_funkce` int(11) NOT NULL,
  `id_typ_org` int(11) DEFAULT NULL,
  `typ_funkce_cz` varchar(255) DEFAULT NULL,
  `typ_funkce_en` varchar(255) DEFAULT NULL,
  `priorita` int(11) DEFAULT NULL,
  `typ_funkce_obecny` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_typ_funkce`),
  KEY `typ_funkce_id_typ_org` (`id_typ_org`),
  CONSTRAINT `typ_funkce_ibfk_1` FOREIGN KEY (`id_typ_org`) REFERENCES `typ_organu` (`id_typ_org`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `typ_organu` (
  `id_typ_org` int(11) NOT NULL,
  `typ_id_typ_org` varchar(255) DEFAULT NULL,
  `nazev_typ_org_cz` varchar(255) DEFAULT NULL,
  `nazev_typ_org_en` varchar(255) DEFAULT NULL,
  `typ_org_obecny` varchar(255) DEFAULT NULL,
  `priorita` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_typ_org`),
  KEY `typ_organu_typ_id_typ_org` (`typ_id_typ_org`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `zarazeni` (
  `id_osoba` int(11) DEFAULT NULL,
  `id_of` int(11) DEFAULT NULL,
  `cl_funkce` int(11) DEFAULT NULL,
  `od_o` varchar(255) DEFAULT NULL,
  `do_o` varchar(255) DEFAULT NULL,
  `od_f` varchar(255) DEFAULT NULL,
  `do_f` varchar(255) DEFAULT NULL,
  KEY `zarazeni_id_osoba` (`id_osoba`),
  CONSTRAINT `zarazeni_ibfk_1` FOREIGN KEY (`id_osoba`) REFERENCES `osoby` (`id_osoba`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `zmatecne` (
  `id_hlasovani` int(11) DEFAULT NULL,
  KEY `zmatecne_id_hlasovani` (`id_hlasovani`),
  CONSTRAINT `zmatecne_ibfk_1` FOREIGN KEY (`id_hlasovani`) REFERENCES `hl_hlasovani` (`id_hlasovani`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

