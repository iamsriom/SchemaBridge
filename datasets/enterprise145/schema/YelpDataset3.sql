-- Schema for database: YelpDataset3

CREATE TABLE `Business` (
  `business_id` varchar(30) NOT NULL DEFAULT '',
  `full_address` varchar(200) DEFAULT NULL,
  `active` varchar(10) DEFAULT NULL,
  `city` varchar(30) DEFAULT NULL,
  `review_count` int(11) DEFAULT NULL,
  `business_name` varchar(100) DEFAULT NULL,
  `neighborhoods` varchar(200) DEFAULT NULL,
  `latitude` double DEFAULT NULL,
  `longitude` double DEFAULT NULL,
  `state` varchar(5) DEFAULT NULL,
  `stars` double DEFAULT NULL,
  PRIMARY KEY (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes` (
  `business_id` varchar(30) DEFAULT NULL,
  `attribute_name` varchar(255) DEFAULT NULL,
  `attribute_value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_AcceptsCreditCards` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_Ambience` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_DietaryRestrictions` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_GoodFor` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_HairTypesSpecializedIn` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_Music` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_Parking` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Attributes_PaymentTypes` (
  `business_id` varchar(30) DEFAULT NULL,
  `subattribute` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Categories` (
  `business_id` varchar(255) DEFAULT NULL,
  `category` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Business_Hours` (
  `business_id` varchar(30) DEFAULT NULL,
  `day_of_week` varchar(12) DEFAULT NULL,
  `opening_time_hours` int(11) DEFAULT 0,
  `closing_time_hours` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Checkins` (
  `business_id` varchar(30) DEFAULT NULL,
  `day_of_week` varchar(30) DEFAULT NULL,
  `time_0` int(11) DEFAULT NULL,
  `time_1` int(11) DEFAULT NULL,
  `time_2` int(11) DEFAULT NULL,
  `time_3` int(11) DEFAULT NULL,
  `time_4` int(11) DEFAULT NULL,
  `time_5` int(11) DEFAULT NULL,
  `time_6` int(11) DEFAULT NULL,
  `time_7` int(11) DEFAULT NULL,
  `time_8` int(11) DEFAULT NULL,
  `time_9` int(11) DEFAULT NULL,
  `time_10` int(11) DEFAULT NULL,
  `time_11` int(11) DEFAULT NULL,
  `time_12` int(11) DEFAULT NULL,
  `time_13` int(11) DEFAULT NULL,
  `time_14` int(11) DEFAULT NULL,
  `time_15` int(11) DEFAULT NULL,
  `time_16` int(11) DEFAULT NULL,
  `time_17` int(11) DEFAULT NULL,
  `time_18` int(11) DEFAULT NULL,
  `time_19` int(11) DEFAULT NULL,
  `time_20` int(11) DEFAULT NULL,
  `time_21` int(11) DEFAULT NULL,
  `time_22` int(11) DEFAULT NULL,
  `time_23` int(11) DEFAULT NULL,
  KEY `Checkins_business_id` (`business_id`),
  CONSTRAINT `Checkins_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Compliments` (
  `user_id` varchar(255) DEFAULT NULL,
  `compliment_type` varchar(255) DEFAULT NULL,
  `number_of_compliments` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Elite` (
  `user_id` varchar(255) DEFAULT NULL,
  `year` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Friends` (
  `user_id1` varchar(255) DEFAULT NULL,
  `user_id2` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Reviews` (
  `review_id` varchar(30) NOT NULL DEFAULT '',
  `business_id` varchar(30) DEFAULT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `stars` double DEFAULT NULL,
  `review_date` date DEFAULT NULL,
  `votes_funny` int(11) DEFAULT NULL,
  `votes_useful` int(11) DEFAULT NULL,
  `votes_cool` int(11) DEFAULT NULL,
  `review_text` text DEFAULT NULL,
  PRIMARY KEY (`review_id`),
  KEY `Reviews_business_id` (`business_id`),
  KEY `Reviews_user_id` (`user_id`),
  KEY `Reviews_user_id_2` (`user_id`),
  CONSTRAINT `Reviews_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Tips` (
  `business_id` varchar(30) DEFAULT NULL,
  `user_id` varchar(30) DEFAULT NULL,
  `date_year` int(11) DEFAULT NULL,
  `date_month` int(11) DEFAULT NULL,
  `date_day` int(11) DEFAULT NULL,
  `likes` int(11) DEFAULT NULL,
  `tip_text` text DEFAULT NULL,
  KEY `Tips_business_id` (`business_id`),
  KEY `Tips_user_id` (`user_id`),
  CONSTRAINT `Tips_ibfk_1` FOREIGN KEY (`business_id`) REFERENCES `Business` (`business_id`),
  CONSTRAINT `Tips_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `Users` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Users` (
  `user_id` varchar(30) NOT NULL DEFAULT '',
  `votes_funny` int(11) DEFAULT NULL,
  `votes_useful` int(11) DEFAULT NULL,
  `votes_cool` int(11) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `average_stars` double DEFAULT NULL,
  `review_count` int(11) DEFAULT NULL,
  `fans` int(11) DEFAULT NULL,
  `yelping_since_year` int(11) DEFAULT NULL,
  `yelping_since_month` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

