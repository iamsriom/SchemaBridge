-- Schema for database: university

CREATE TABLE `RA` (
  `capability` varchar(45) DEFAULT NULL,
  `prof_id` int(11) NOT NULL DEFAULT 0,
  `student_id` int(11) NOT NULL DEFAULT 0,
  `salary` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`prof_id`,`student_id`),
  KEY `RA_capability` (`capability`),
  KEY `RA_salary` (`salary`),
  KEY `RA_student_id` (`student_id`),
  KEY `RA_prof_id` (`prof_id`),
  CONSTRAINT `FK_RA_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_RA_2` FOREIGN KEY (`prof_id`) REFERENCES `prof` (`prof_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `course` (
  `course_id` int(11) NOT NULL,
  `rating` varchar(45) DEFAULT NULL,
  `diff` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`course_id`),
  KEY `course_rating` (`rating`),
  KEY `course_diff` (`diff`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `prof` (
  `prof_id` int(11) NOT NULL DEFAULT 0,
  `popularity` varchar(45) DEFAULT NULL,
  `teachingability` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`prof_id`),
  KEY `prof_popularity` (`popularity`),
  KEY `prof_teachingability` (`teachingability`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `registration` (
  `course_id` int(11) NOT NULL DEFAULT 0,
  `student_id` int(11) NOT NULL DEFAULT 0,
  `grade` varchar(45) NOT NULL,
  `sat` varchar(45) NOT NULL,
  PRIMARY KEY (`course_id`,`student_id`),
  KEY `registration_sat` (`sat`),
  KEY `registration_grade` (`grade`),
  KEY `registration_student_id` (`student_id`),
  KEY `registration_course_id` (`course_id`),
  CONSTRAINT `FK_registration_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `FK_registration_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `student` (
  `student_id` int(11) NOT NULL DEFAULT 0,
  `intelligence` varchar(45) DEFAULT NULL,
  `ranking` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  KEY `student_intelligence` (`intelligence`),
  KEY `student_ranking` (`ranking`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci ROW_FORMAT=COMPACT
;

