-- Schema for database: Mooney_Family

CREATE TABLE `aunt` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `aunt_name1` (`name1`),
  KEY `aunt_name2` (`name2`),
  CONSTRAINT `aunt_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `aunt_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `aunt1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `aunt1_name1` (`name1`),
  KEY `aunt1_name2` (`name2`),
  CONSTRAINT `aunt1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `aunt1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `aunt2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `aunt2_name1` (`name1`),
  KEY `aunt2_name2` (`name2`),
  CONSTRAINT `aunt2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `aunt2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `aunt3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `aunt3_name1` (`name1`),
  KEY `aunt3_name2` (`name2`),
  CONSTRAINT `aunt3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `aunt3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `aunt4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `aunt4_name1` (`name1`),
  KEY `aunt4_name2` (`name2`),
  CONSTRAINT `aunt4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `aunt4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `aunt5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `aunt5_name1` (`name1`),
  KEY `aunt5_name2` (`name2`),
  CONSTRAINT `aunt5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `aunt5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `brother` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother_name1` (`name1`),
  KEY `brother_name2` (`name2`),
  CONSTRAINT `brother_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `brother_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `brother1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother1_name1` (`name1`),
  KEY `brother1_name2` (`name2`),
  CONSTRAINT `brother1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `brother1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `brother2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother2_name1` (`name1`),
  KEY `brother2_name2` (`name2`),
  CONSTRAINT `brother2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `brother2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `brother3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother3_name1` (`name1`),
  KEY `brother3_name2` (`name2`),
  CONSTRAINT `brother3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `brother3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `brother4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother4_name1` (`name1`),
  KEY `brother4_name2` (`name2`),
  CONSTRAINT `brother4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `brother4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `brother5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `brother5_name1` (`name1`),
  KEY `brother5_name2` (`name2`),
  CONSTRAINT `brother5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `brother5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter_name1` (`name1`),
  KEY `daughter_name2` (`name2`),
  CONSTRAINT `daughter_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `daughter_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter1_name1` (`name1`),
  KEY `daughter1_name2` (`name2`),
  CONSTRAINT `daughter1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `daughter1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter2_name1` (`name1`),
  KEY `daughter2_name2` (`name2`),
  CONSTRAINT `daughter2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `daughter2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter3_name1` (`name1`),
  KEY `daughter3_name2` (`name2`),
  CONSTRAINT `daughter3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `daughter3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter4_name1` (`name1`),
  KEY `daughter4_name2` (`name2`),
  CONSTRAINT `daughter4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `daughter4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `daughter5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `daughter5_name1` (`name1`),
  KEY `daughter5_name2` (`name2`),
  CONSTRAINT `daughter5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `daughter5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `father_name1` (`name1`),
  KEY `father_name2` (`name2`),
  CONSTRAINT `father_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `father_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `father1_name1` (`name1`),
  KEY `father1_name2` (`name2`),
  CONSTRAINT `father1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `father1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `father2_name1` (`name1`),
  KEY `father2_name2` (`name2`),
  CONSTRAINT `father2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `father2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `father3_name1` (`name1`),
  KEY `father3_name2` (`name2`),
  CONSTRAINT `father3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `father3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `father4_name1` (`name1`),
  KEY `father4_name2` (`name2`),
  CONSTRAINT `father4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `father4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `father5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `father5_name1` (`name1`),
  KEY `father5_name2` (`name2`),
  CONSTRAINT `father5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `father5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband_name1` (`name1`),
  KEY `husband_name2` (`name2`),
  CONSTRAINT `husband_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `husband_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband1_name1` (`name1`),
  KEY `husband1_name2` (`name2`),
  CONSTRAINT `husband1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `husband1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband2_name1` (`name1`),
  KEY `husband2_name2` (`name2`),
  CONSTRAINT `husband2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `husband2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband3_name1` (`name1`),
  KEY `husband3_name2` (`name2`),
  CONSTRAINT `husband3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `husband3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband4_name1` (`name1`),
  KEY `husband4_name2` (`name2`),
  CONSTRAINT `husband4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `husband4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `husband5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `husband5_name1` (`name1`),
  KEY `husband5_name2` (`name2`),
  CONSTRAINT `husband5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `husband5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother_name1` (`name1`),
  KEY `mother_name2` (`name2`),
  CONSTRAINT `mother_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `mother_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother1_name1` (`name1`),
  KEY `mother1_name2` (`name2`),
  CONSTRAINT `mother1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `mother1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother2_name1` (`name1`),
  KEY `mother2_name2` (`name2`),
  CONSTRAINT `mother2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `mother2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother3_name1` (`name1`),
  KEY `mother3_name2` (`name2`),
  CONSTRAINT `mother3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `mother3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother4_name1` (`name1`),
  KEY `mother4_name2` (`name2`),
  CONSTRAINT `mother4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `mother4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `mother5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `mother5_name1` (`name1`),
  KEY `mother5_name2` (`name2`),
  CONSTRAINT `mother5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `mother5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nephew` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `nephew_name1` (`name1`),
  KEY `nephew_name2` (`name2`),
  CONSTRAINT `nephew_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `nephew_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nephew1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `nephew1_name1` (`name1`),
  KEY `nephew1_name2` (`name2`),
  CONSTRAINT `nephew1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `nephew1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nephew2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `nephew2_name1` (`name1`),
  KEY `nephew2_name2` (`name2`),
  CONSTRAINT `nephew2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `nephew2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nephew3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `nephew3_name1` (`name1`),
  KEY `nephew3_name2` (`name2`),
  CONSTRAINT `nephew3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `nephew3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nephew4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `nephew4_name1` (`name1`),
  KEY `nephew4_name2` (`name2`),
  CONSTRAINT `nephew4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `nephew4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `nephew5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `nephew5_name1` (`name1`),
  KEY `nephew5_name2` (`name2`),
  CONSTRAINT `nephew5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `nephew5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `niece` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `niece_name1` (`name1`),
  KEY `niece_name2` (`name2`),
  CONSTRAINT `niece_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `niece_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `niece1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `niece1_name1` (`name1`),
  KEY `niece1_name2` (`name2`),
  CONSTRAINT `niece1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `niece1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `niece2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `niece2_name1` (`name1`),
  KEY `niece2_name2` (`name2`),
  CONSTRAINT `niece2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `niece2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `niece3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `niece3_name1` (`name1`),
  KEY `niece3_name2` (`name2`),
  CONSTRAINT `niece3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `niece3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `niece4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `niece4_name1` (`name1`),
  KEY `niece4_name2` (`name2`),
  CONSTRAINT `niece4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `niece4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `niece5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `niece5_name1` (`name1`),
  KEY `niece5_name2` (`name2`),
  CONSTRAINT `niece5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `niece5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `person` (
  `name` varchar(10) NOT NULL,
  PRIMARY KEY (`name`),
  KEY `person_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister_name1` (`name1`),
  KEY `sister_name2` (`name2`),
  CONSTRAINT `sister_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `sister_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister1_name1` (`name1`),
  KEY `sister1_name2` (`name2`),
  CONSTRAINT `sister1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `sister1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister2_name1` (`name1`),
  KEY `sister2_name2` (`name2`),
  CONSTRAINT `sister2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `sister2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister3_name1` (`name1`),
  KEY `sister3_name2` (`name2`),
  CONSTRAINT `sister3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `sister3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister4_name1` (`name1`),
  KEY `sister4_name2` (`name2`),
  CONSTRAINT `sister4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `sister4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `sister5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `sister5_name1` (`name1`),
  KEY `sister5_name2` (`name2`),
  CONSTRAINT `sister5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `sister5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `son_name1` (`name1`),
  KEY `son_name2` (`name2`),
  CONSTRAINT `son_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `son_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `son1_name1` (`name1`),
  KEY `son1_name2` (`name2`),
  CONSTRAINT `son1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `son1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `son2_name1` (`name1`),
  KEY `son2_name2` (`name2`),
  CONSTRAINT `son2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `son2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `son3_name1` (`name1`),
  KEY `son3_name2` (`name2`),
  CONSTRAINT `son3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `son3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `son4_name1` (`name1`),
  KEY `son4_name2` (`name2`),
  CONSTRAINT `son4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `son4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `son5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `son5_name1` (`name1`),
  KEY `son5_name2` (`name2`),
  CONSTRAINT `son5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `son5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `uncle` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `uncle_name1` (`name1`),
  KEY `uncle_name2` (`name2`),
  CONSTRAINT `uncle_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `uncle_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `uncle1` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `uncle1_name1` (`name1`),
  KEY `uncle1_name2` (`name2`),
  CONSTRAINT `uncle1_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `uncle1_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `uncle2` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `uncle2_name1` (`name1`),
  KEY `uncle2_name2` (`name2`),
  CONSTRAINT `uncle2_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `uncle2_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `uncle3` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `uncle3_name1` (`name1`),
  KEY `uncle3_name2` (`name2`),
  CONSTRAINT `uncle3_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `uncle3_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `uncle4` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `uncle4_name1` (`name1`),
  KEY `uncle4_name2` (`name2`),
  CONSTRAINT `uncle4_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `uncle4_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `uncle5` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `uncle5_name1` (`name1`),
  KEY `uncle5_name2` (`name2`),
  CONSTRAINT `uncle5_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `uncle5_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `wife` (
  `name1` varchar(10) NOT NULL DEFAULT '',
  `name2` varchar(10) NOT NULL DEFAULT '',
  PRIMARY KEY (`name1`,`name2`),
  KEY `wife_name1` (`name1`),
  KEY `wife_name2` (`name2`),
  CONSTRAINT `wife_ibfk_1` FOREIGN KEY (`name1`) REFERENCES `person` (`name`),
  CONSTRAINT `wife_ibfk_2` FOREIGN KEY (`name2`) REFERENCES `person` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

