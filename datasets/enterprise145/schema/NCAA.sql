-- Schema for database: NCAA

CREATE TABLE `regular_season_compact_results` (
  `season` int(11) NOT NULL,
  `daynum` int(11) NOT NULL,
  `wteam` int(11) NOT NULL,
  `wscore` int(11) DEFAULT NULL,
  `lteam` int(11) NOT NULL,
  `lscore` int(11) DEFAULT NULL,
  `wloc` varchar(255) DEFAULT NULL,
  `numot` int(11) DEFAULT NULL,
  PRIMARY KEY (`season`,`daynum`,`wteam`,`lteam`),
  KEY `regular_compact_season` (`season`) USING BTREE,
  KEY `regular_compact_wteam` (`wteam`) USING BTREE,
  KEY `regular_compact_lteam` (`lteam`) USING BTREE,
  CONSTRAINT `regular_season_compact_results_ibfk_1` FOREIGN KEY (`season`) REFERENCES `seasons` (`season`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `regular_season_compact_results_ibfk_2` FOREIGN KEY (`wteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `regular_season_compact_results_ibfk_3` FOREIGN KEY (`lteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `regular_season_detailed_results` (
  `season` int(11) NOT NULL,
  `daynum` int(11) NOT NULL,
  `wteam` int(11) NOT NULL,
  `wscore` int(11) NOT NULL,
  `lteam` int(11) NOT NULL,
  `lscore` int(11) NOT NULL,
  `wloc` varchar(255) DEFAULT NULL,
  `numot` int(11) DEFAULT NULL,
  `wfgm` int(11) DEFAULT NULL,
  `wfga` int(11) DEFAULT NULL,
  `wfgm3` int(11) DEFAULT NULL,
  `wfga3` int(11) DEFAULT NULL,
  `wftm` int(11) DEFAULT NULL,
  `wfta` int(11) DEFAULT NULL,
  `wor` int(11) DEFAULT NULL,
  `wdr` int(11) DEFAULT NULL,
  `wast` int(11) DEFAULT NULL,
  `wto` int(11) DEFAULT NULL,
  `wstl` int(11) DEFAULT NULL,
  `wblk` int(11) DEFAULT NULL,
  `wpf` int(11) DEFAULT NULL,
  `lfgm` int(11) DEFAULT NULL,
  `lfga` int(11) DEFAULT NULL,
  `lfgm3` int(11) DEFAULT NULL,
  `lfga3` int(11) DEFAULT NULL,
  `lftm` int(11) DEFAULT NULL,
  `lfta` int(11) DEFAULT NULL,
  `lor` int(11) DEFAULT NULL,
  `ldr` int(11) DEFAULT NULL,
  `last` int(11) DEFAULT NULL,
  `lto` int(11) DEFAULT NULL,
  `lstl` int(11) DEFAULT NULL,
  `lblk` int(11) DEFAULT NULL,
  `lpf` int(11) DEFAULT NULL,
  PRIMARY KEY (`season`,`daynum`,`wteam`,`lteam`),
  KEY `regular_detailed_season` (`season`) USING BTREE,
  KEY `regular_detailed_wteam` (`wteam`) USING BTREE,
  KEY `regular_detailed_lscore` (`lscore`) USING BTREE,
  KEY `regular_detailed_lteam` (`lteam`) USING BTREE,
  CONSTRAINT `regular_season_detailed_results_ibfk_1` FOREIGN KEY (`season`) REFERENCES `seasons` (`season`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `regular_season_detailed_results_ibfk_2` FOREIGN KEY (`wteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `regular_season_detailed_results_ibfk_3` FOREIGN KEY (`lteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `seasons` (
  `season` int(11) NOT NULL,
  `dayzero` datetime DEFAULT NULL,
  `regionW` varchar(255) DEFAULT NULL,
  `regionX` varchar(255) DEFAULT NULL,
  `regionY` varchar(255) DEFAULT NULL,
  `regionZ` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`season`),
  KEY `seasons_season` (`season`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `target` (
  `id` varchar(255) NOT NULL,
  `season` int(4) DEFAULT NULL,
  `team_id1` int(4) DEFAULT NULL,
  `team_id2` int(4) DEFAULT NULL,
  `pred` float DEFAULT NULL,
  `team_id1_wins` int(1) DEFAULT NULL,
  `team_id2_wins` int(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `target_team_id1` (`team_id1`) USING BTREE,
  KEY `target_team_id2` (`team_id2`) USING BTREE,
  CONSTRAINT `target_ibfk_1` FOREIGN KEY (`team_id1`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `target_ibfk_2` FOREIGN KEY (`team_id2`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `teams` (
  `team_id` int(11) NOT NULL,
  `team_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `tourney_compact_results` (
  `season` int(11) NOT NULL,
  `daynum` int(11) NOT NULL,
  `wteam` int(11) NOT NULL,
  `wscore` int(11) DEFAULT NULL,
  `lteam` int(11) NOT NULL,
  `lscore` int(11) DEFAULT NULL,
  `wloc` varchar(255) DEFAULT NULL,
  `numot` int(11) DEFAULT NULL,
  PRIMARY KEY (`season`,`daynum`,`wteam`,`lteam`),
  KEY `compact_season` (`season`) USING BTREE,
  KEY `compact_wteam` (`wteam`) USING BTREE,
  KEY `compact_lteam` (`lteam`) USING BTREE,
  CONSTRAINT `tourney_compact_results_ibfk_1` FOREIGN KEY (`season`) REFERENCES `seasons` (`season`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tourney_compact_results_ibfk_2` FOREIGN KEY (`wteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tourney_compact_results_ibfk_3` FOREIGN KEY (`lteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `tourney_detailed_results` (
  `season` int(11) NOT NULL,
  `daynum` int(11) NOT NULL,
  `wteam` int(11) NOT NULL,
  `wscore` int(11) DEFAULT NULL,
  `lteam` int(11) NOT NULL,
  `lscore` int(11) DEFAULT NULL,
  `wloc` varchar(255) DEFAULT NULL,
  `numot` int(11) DEFAULT NULL,
  `wfgm` int(11) DEFAULT NULL,
  `wfga` int(11) DEFAULT NULL,
  `wfgm3` int(11) DEFAULT NULL,
  `wfga3` int(11) DEFAULT NULL,
  `wftm` int(11) DEFAULT NULL,
  `wfta` int(11) DEFAULT NULL,
  `wor` int(11) DEFAULT NULL,
  `wdr` int(11) DEFAULT NULL,
  `wast` int(11) DEFAULT NULL,
  `wto` int(11) DEFAULT NULL,
  `wstl` int(11) DEFAULT NULL,
  `wblk` int(11) DEFAULT NULL,
  `wpf` int(11) DEFAULT NULL,
  `lfgm` int(11) DEFAULT NULL,
  `lfga` int(11) DEFAULT NULL,
  `lfgm3` int(11) DEFAULT NULL,
  `lfga3` int(11) DEFAULT NULL,
  `lftm` int(11) DEFAULT NULL,
  `lfta` int(11) DEFAULT NULL,
  `lor` int(11) DEFAULT NULL,
  `ldr` int(11) DEFAULT NULL,
  `last` int(11) DEFAULT NULL,
  `lto` int(11) DEFAULT NULL,
  `lstl` int(11) DEFAULT NULL,
  `lblk` int(11) DEFAULT NULL,
  `lpf` int(11) DEFAULT NULL,
  PRIMARY KEY (`season`,`daynum`,`wteam`,`lteam`),
  KEY `detailed_season` (`season`) USING BTREE,
  KEY `detailed_wteam` (`wteam`) USING BTREE,
  KEY `detailed_lteam` (`lteam`) USING BTREE,
  CONSTRAINT `tourney_detailed_results_ibfk_1` FOREIGN KEY (`season`) REFERENCES `seasons` (`season`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tourney_detailed_results_ibfk_2` FOREIGN KEY (`wteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tourney_detailed_results_ibfk_3` FOREIGN KEY (`lteam`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `tourney_seeds` (
  `season` int(11) NOT NULL,
  `seed` varchar(255) NOT NULL,
  `team` int(11) DEFAULT NULL,
  PRIMARY KEY (`season`,`seed`),
  KEY `seads_season` (`season`) USING BTREE,
  KEY `seads_team` (`team`) USING BTREE,
  CONSTRAINT `tourney_seeds_ibfk_1` FOREIGN KEY (`season`) REFERENCES `seasons` (`season`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tourney_seeds_ibfk_2` FOREIGN KEY (`team`) REFERENCES `teams` (`team_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;


CREATE TABLE `tourney_slots` (
  `season` int(11) NOT NULL,
  `slot` varchar(255) NOT NULL,
  `strongseed` varchar(255) DEFAULT NULL,
  `weakseed` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`slot`,`season`),
  KEY `slots_season` (`season`) USING BTREE,
  CONSTRAINT `tourney_slots_ibfk_1` FOREIGN KEY (`season`) REFERENCES `seasons` (`season`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci ROW_FORMAT=COMPACT
;

