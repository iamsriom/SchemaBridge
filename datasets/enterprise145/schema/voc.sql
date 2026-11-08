-- Schema for database: voc

CREATE TABLE `craftsmen` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) NOT NULL,
  `trip_sup` char(1) NOT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `craftsmen_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `impotenten` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) NOT NULL,
  `trip_sup` char(1) NOT NULL,
  `onboard_at_departure` int(11) NOT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `impotenten_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `invoices` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) NOT NULL,
  `trip_sup` char(1) NOT NULL,
  `invoice` int(11) DEFAULT NULL,
  `chamber` char(1) DEFAULT NULL,
  KEY `invoices_number_fkey` (`number`,`number_sup`),
  CONSTRAINT `invoices_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `passengers` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) NOT NULL,
  `trip_sup` char(1) NOT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `passengers_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `seafarers` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) NOT NULL,
  `trip_sup` char(1) NOT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `seafarers_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `soldiers` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) NOT NULL,
  `trip_sup` char(1) NOT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `soldiers_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `total` (
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) NOT NULL,
  `onboard_at_departure` int(11) DEFAULT NULL,
  `death_at_cape` int(11) DEFAULT NULL,
  `left_at_cape` int(11) DEFAULT NULL,
  `onboard_at_cape` int(11) DEFAULT NULL,
  `death_during_voyage` int(11) DEFAULT NULL,
  `onboard_at_arrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`),
  CONSTRAINT `total_number_fkey` FOREIGN KEY (`number`, `number_sup`) REFERENCES `voyages` (`number`, `number_sup`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `voyages` (
  `artificial_id` char(12) NOT NULL,
  `number` int(11) NOT NULL,
  `number_sup` char(1) NOT NULL,
  `trip` int(11) DEFAULT NULL,
  `trip_sup` char(1) NOT NULL,
  `boatname` varchar(50) DEFAULT NULL,
  `master` varchar(50) DEFAULT NULL,
  `tonnage` int(11) DEFAULT NULL,
  `type_of_boat` varchar(30) DEFAULT NULL,
  `built` varchar(15) DEFAULT NULL,
  `bought` varchar(15) DEFAULT NULL,
  `hired` varchar(15) DEFAULT NULL,
  `yard` char(1) DEFAULT NULL,
  `chamber` char(1) DEFAULT NULL,
  `departure_date` date DEFAULT NULL,
  `departure_harbour` varchar(30) DEFAULT NULL,
  `cape_arrival` date DEFAULT NULL,
  `cape_departure` date DEFAULT NULL,
  `cape_call` varchar(5) DEFAULT NULL,
  `arrival_date` date DEFAULT NULL,
  `arrival_harbour` varchar(30) DEFAULT NULL,
  `next_voyage` int(11) DEFAULT NULL,
  `particulars` text DEFAULT NULL,
  PRIMARY KEY (`number`,`number_sup`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

