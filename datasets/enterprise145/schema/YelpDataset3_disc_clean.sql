-- Schema for database: YelpDataset3_disc_clean

CREATE TABLE `Attributes` (
  `attribute_id` int(11) NOT NULL AUTO_INCREMENT,
  `attribute_name` varchar(280) DEFAULT NULL,
  PRIMARY KEY (`attribute_id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business` (
  `business_id` int(11) NOT NULL DEFAULT 0,
  `active` varchar(10) DEFAULT NULL,
  `city` varchar(30) DEFAULT NULL,
  `state` varchar(5) DEFAULT NULL,
  `stars` double DEFAULT NULL,
  `review_count` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes` (
  `attribute_id` int(11) NOT NULL DEFAULT 0,
  `business_id` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`attribute_id`,`business_id`),
  KEY `business_id` (`business_id`),
  CONSTRAINT `Business_Attributes_ibfk_1` FOREIGN KEY (`attribute_id`) REFERENCES `Attributes` (`attribute_id`),
  CONSTRAINT `Business_Attributes_ibfk_2` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Categories` (
  `business_id` int(11) NOT NULL DEFAULT 0,
  `category_id` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`business_id`,`category_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `Business_Categories_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Business_Categories_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `Categories` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Hours` (
  `business_id` int(11) NOT NULL DEFAULT 0,
  `day_id` int(11) NOT NULL DEFAULT 0,
  `opening_time` varchar(25) DEFAULT NULL,
  `closing_time` varchar(25) DEFAULT NULL,
  PRIMARY KEY (`business_id`,`day_id`),
  KEY `day_id` (`day_id`),
  CONSTRAINT `Business_Hours_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Business_Hours_ibfk_2` FOREIGN KEY (`day_id`) REFERENCES `Days` (`day_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Categories` (
  `category_id` int(11) NOT NULL AUTO_INCREMENT,
  `category_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`category_id`)
) ENGINE=InnoDB AUTO_INCREMENT=592 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Checkins` (
  `business_id` int(11) NOT NULL DEFAULT 0,
  `day_id` int(11) NOT NULL DEFAULT 0,
  `label_time_0` varchar(10) DEFAULT NULL,
  `label_time_1` varchar(10) DEFAULT NULL,
  `label_time_2` varchar(10) DEFAULT NULL,
  `label_time_3` varchar(10) DEFAULT NULL,
  `label_time_4` varchar(10) DEFAULT NULL,
  `label_time_5` varchar(10) DEFAULT NULL,
  `label_time_6` varchar(10) DEFAULT NULL,
  `label_time_7` varchar(10) DEFAULT NULL,
  `label_time_8` varchar(10) DEFAULT NULL,
  `label_time_9` varchar(10) DEFAULT NULL,
  `label_time_10` varchar(10) DEFAULT NULL,
  `label_time_11` varchar(10) DEFAULT NULL,
  `label_time_12` varchar(10) DEFAULT NULL,
  `label_time_13` varchar(10) DEFAULT NULL,
  `label_time_14` varchar(10) DEFAULT NULL,
  `label_time_15` varchar(10) DEFAULT NULL,
  `label_time_16` varchar(10) DEFAULT NULL,
  `label_time_17` varchar(10) DEFAULT NULL,
  `label_time_18` varchar(10) DEFAULT NULL,
  `label_time_19` varchar(10) DEFAULT NULL,
  `label_time_20` varchar(10) DEFAULT NULL,
  `label_time_21` varchar(10) DEFAULT NULL,
  `label_time_22` varchar(10) DEFAULT NULL,
  `label_time_23` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`business_id`,`day_id`),
  KEY `day_id` (`day_id`),
  CONSTRAINT `Checkins_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Checkins_ibfk_2` FOREIGN KEY (`day_id`) REFERENCES `Days` (`day_id`),
  CONSTRAINT `Checkins_ibfk_3` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Checkins_ibfk_4` FOREIGN KEY (`day_id`) REFERENCES `Days` (`day_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Compliments` (
  `compliment_id` int(11) NOT NULL AUTO_INCREMENT,
  `compliment_type` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`compliment_id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Days` (
  `day_id` int(11) NOT NULL DEFAULT 0,
  `day_of_week` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`day_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Elite` (
  `user_id` int(11) NOT NULL DEFAULT 0,
  `year_id` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`user_id`,`year_id`),
  KEY `year_id` (`year_id`),
  CONSTRAINT `Elite_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`),
  CONSTRAINT `Elite_ibfk_2` FOREIGN KEY (`year_id`) REFERENCES `Years` (`year_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Reviews` (
  `business_id` int(11) NOT NULL DEFAULT 0,
  `user_id` int(11) NOT NULL DEFAULT 0,
  `review_stars` double DEFAULT NULL,
  `review_votes_funny` varchar(10) DEFAULT NULL,
  `review_votes_useful` varchar(10) DEFAULT NULL,
  `review_votes_cool` varchar(10) DEFAULT NULL,
  `review_length` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`business_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `Reviews_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Reviews_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Tips` (
  `business_id` int(11) NOT NULL DEFAULT 0,
  `user_id` int(11) NOT NULL DEFAULT 0,
  `likes` int(11) DEFAULT NULL,
  `tip_length` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`business_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `Tips_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Tips_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Users` (
  `user_id` int(11) NOT NULL DEFAULT 0,
  `user_yelping_since_year` int(11) DEFAULT NULL,
  `user_average_stars` double DEFAULT NULL,
  `user_votes_funny` varchar(10) DEFAULT NULL,
  `user_votes_useful` varchar(10) DEFAULT NULL,
  `user_votes_cool` varchar(10) DEFAULT NULL,
  `user_review_count` varchar(10) DEFAULT NULL,
  `user_fans` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Users_Compliments` (
  `compliment_id` int(11) NOT NULL DEFAULT 0,
  `user_id` int(11) NOT NULL DEFAULT 0,
  `number_of_compliments` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`compliment_id`,`user_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `Users_Compliments_ibfk_1` FOREIGN KEY (`compliment_id`) REFERENCES `Compliments` (`compliment_id`),
  CONSTRAINT `Users_Compliments_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Years` (
  `year_id` int(11) NOT NULL DEFAULT 0,
  `actual_year` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`year_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

