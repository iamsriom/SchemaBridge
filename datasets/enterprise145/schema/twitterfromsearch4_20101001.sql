-- Schema for database: twitterfromsearch4_20101001

CREATE TABLE `active_follower_real` (
  `user_id` int(11) NOT NULL,
  `follower_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`follower_id`),
  KEY `NewIndex1` (`user_id`),
  KEY `NewIndex2` (`follower_id`),
  CONSTRAINT `active_follower_real_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `distinct_users_from_search_table_real_map` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `active_follower_real_ibfk_2` FOREIGN KEY (`follower_id`) REFERENCES `distinct_users_from_search_table_real_map` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `distinct_users_from_search_table_real_map` (
  `user_id` int(11) NOT NULL,
  `user_screen_name` varchar(255) DEFAULT NULL,
  `indegree` int(11) DEFAULT NULL,
  `outdegree` int(11) DEFAULT NULL,
  `bad_user_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

