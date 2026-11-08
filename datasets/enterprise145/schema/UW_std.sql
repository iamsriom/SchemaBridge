-- Schema for database: UW_std

CREATE TABLE `advisedBy` (
  `p_id` int(11) NOT NULL DEFAULT 0,
  `p_id_dummy` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`p_id_dummy`,`p_id`),
  KEY `FK_u2base_1` (`p_id`),
  KEY `FK_u2base_2` (`p_id_dummy`),
  CONSTRAINT `FK_advisedBy_person` FOREIGN KEY (`p_id`) REFERENCES `person` (`p_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_advisedBy_person_2` FOREIGN KEY (`p_id_dummy`) REFERENCES `person` (`p_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `course` (
  `course_id` int(11) NOT NULL,
  `courseLevel` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `course_courseLevel` (`courseLevel`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `person` (
  `p_id` int(11) NOT NULL DEFAULT 0,
  `professor` varchar(11) NOT NULL DEFAULT '0',
  `student` varchar(11) NOT NULL DEFAULT '0',
  `hasPosition` varchar(11) NOT NULL DEFAULT '0',
  `inPhase` varchar(40) DEFAULT NULL,
  `yearsInProgram` varchar(40) DEFAULT NULL,
  PRIMARY KEY (`p_id`),
  KEY `person_hasPosition` (`hasPosition`),
  KEY `person_inPhase` (`inPhase`),
  KEY `person_yearInProgram` (`yearsInProgram`),
  KEY `person_professor` (`professor`),
  KEY `person_student` (`student`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `taughtBy` (
  `course_id` int(11) NOT NULL DEFAULT 0,
  `p_id` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`course_id`,`p_id`),
  KEY `FK_2` (`course_id`),
  KEY `FK_1` (`p_id`),
  CONSTRAINT `FK_taught_course` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_taught_person` FOREIGN KEY (`p_id`) REFERENCES `person` (`p_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

