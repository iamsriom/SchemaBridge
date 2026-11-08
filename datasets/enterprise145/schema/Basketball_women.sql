-- Schema for database: Basketball_women

CREATE TABLE `awards_players` (
  `playerID` varchar(255) DEFAULT NULL,
  `award` varchar(255) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `lgID` varchar(255) DEFAULT NULL,
  `note` varchar(255) DEFAULT NULL,
  `pos` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  KEY `awards_players_playerID` (`playerID`) USING BTREE,
  CONSTRAINT `awards_players_ibfk_1` FOREIGN KEY (`playerID`) REFERENCES `players` (`bioID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `coaches` (
  `coachID` varchar(255) NOT NULL,
  `fullName` varchar(255) DEFAULT NULL,
  `year` int(11) NOT NULL,
  `tmID` varchar(255) NOT NULL,
  `lgID` varchar(255) DEFAULT NULL,
  `stint` int(11) NOT NULL,
  `won` int(11) DEFAULT NULL,
  `lost` int(11) DEFAULT NULL,
  `post_wins` int(11) DEFAULT NULL,
  `post_losses` int(11) DEFAULT NULL,
  `playerCoach` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`coachID`,`year`,`tmID`,`stint`),
  KEY `coaches_tmID` (`tmID`,`year`) USING BTREE,
  CONSTRAINT `coaches_ibfk_1` FOREIGN KEY (`tmID`, `year`) REFERENCES `teams` (`tmID`, `year`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `draft` (
  `draftYear` int(11) DEFAULT NULL,
  `draftRound` int(11) DEFAULT NULL,
  `draftSelection` int(11) DEFAULT NULL,
  `draftOverall` int(11) DEFAULT NULL,
  `tmID` varchar(255) DEFAULT NULL,
  `firstName` varchar(255) DEFAULT NULL,
  `lastName` varchar(255) DEFAULT NULL,
  `fullName` varchar(255) DEFAULT NULL,
  `suffixName` varchar(255) DEFAULT NULL,
  `playerID` varchar(255) DEFAULT NULL,
  `draftFrom` varchar(255) DEFAULT NULL,
  `lgID` varchar(255) DEFAULT NULL,
  `playedPro` varchar(255) DEFAULT NULL,
  `notes` varchar(255) DEFAULT NULL,
  `pickRoute` varchar(255) DEFAULT NULL,
  KEY `draft_tmID` (`tmID`,`draftYear`) USING BTREE,
  CONSTRAINT `draft_ibfk_1` FOREIGN KEY (`tmID`, `draftYear`) REFERENCES `teams` (`tmID`, `year`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `players` (
  `bioID` varchar(255) NOT NULL,
  `firstName` varchar(255) DEFAULT NULL,
  `middleName` varchar(255) DEFAULT NULL,
  `lastName` varchar(255) DEFAULT NULL,
  `nameGiven` varchar(255) DEFAULT NULL,
  `fullGivenName` varchar(255) DEFAULT NULL,
  `marriedName` varchar(255) DEFAULT NULL,
  `nameNick` varchar(255) DEFAULT NULL,
  `pos` varchar(255) DEFAULT NULL,
  `firstseason` int(11) DEFAULT NULL,
  `lastseason` int(11) DEFAULT NULL,
  `height` float DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `college` varchar(255) DEFAULT NULL,
  `collegeOther` varchar(255) DEFAULT NULL,
  `birthDate` varchar(255) DEFAULT NULL,
  `birthCity` varchar(255) DEFAULT NULL,
  `birthState` varchar(255) DEFAULT NULL,
  `birthCountry` varchar(255) DEFAULT NULL,
  `highSchool` varchar(255) DEFAULT NULL,
  `hsCity` varchar(255) DEFAULT NULL,
  `hsState` varchar(255) DEFAULT NULL,
  `hsCountry` varchar(255) DEFAULT NULL,
  `deathDate` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`bioID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `players_teams` (
  `playerID` varchar(255) DEFAULT NULL,
  `playerName` varchar(255) DEFAULT NULL,
  `year` int(11) DEFAULT NULL,
  `stint` int(11) DEFAULT NULL,
  `tmID` varchar(255) DEFAULT NULL,
  `lgID` varchar(255) DEFAULT NULL,
  `GP` int(11) DEFAULT NULL,
  `GS` int(11) DEFAULT NULL,
  `minutes` int(11) DEFAULT NULL,
  `points` int(11) DEFAULT NULL,
  `oRebounds` int(11) DEFAULT NULL,
  `dRebounds` int(11) DEFAULT NULL,
  `rebounds` int(11) DEFAULT NULL,
  `assists` int(11) DEFAULT NULL,
  `steals` int(11) DEFAULT NULL,
  `blocks` int(11) DEFAULT NULL,
  `turnovers` int(11) DEFAULT NULL,
  `PF` int(11) DEFAULT NULL,
  `fgAttempted` int(11) DEFAULT NULL,
  `fgMade` int(11) DEFAULT NULL,
  `ftAttempted` int(11) DEFAULT NULL,
  `ftMade` int(11) DEFAULT NULL,
  `threeAttempted` int(11) DEFAULT NULL,
  `threeMade` int(11) DEFAULT NULL,
  `dq` int(11) DEFAULT NULL,
  `PostGP` int(11) DEFAULT NULL,
  `PostGS` int(11) DEFAULT NULL,
  `PostMinutes` int(11) DEFAULT NULL,
  `PostPoints` int(11) DEFAULT NULL,
  `PostoRebounds` int(11) DEFAULT NULL,
  `PostdRebounds` int(11) DEFAULT NULL,
  `PostRebounds` int(11) DEFAULT NULL,
  `PostAssists` int(11) DEFAULT NULL,
  `PostSteals` int(11) DEFAULT NULL,
  `PostBlocks` int(11) DEFAULT NULL,
  `PostTurnovers` int(11) DEFAULT NULL,
  `PostPF` int(11) DEFAULT NULL,
  `PostfgAttempted` int(11) DEFAULT NULL,
  `PostfgMade` int(11) DEFAULT NULL,
  `PostftAttempted` int(11) DEFAULT NULL,
  `PostftMade` int(11) DEFAULT NULL,
  `PostthreeAttempted` int(11) DEFAULT NULL,
  `PostthreeMade` int(11) DEFAULT NULL,
  `PostDQ` int(11) DEFAULT NULL,
  KEY `players_teams_playerID` (`playerID`) USING BTREE,
  KEY `players_teams_tmID` (`tmID`,`year`) USING BTREE,
  CONSTRAINT `players_teams_ibfk_1` FOREIGN KEY (`playerID`) REFERENCES `players` (`bioID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `players_teams_ibfk_2` FOREIGN KEY (`tmID`, `year`) REFERENCES `teams` (`tmID`, `year`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `series_post` (
  `year` int(11) DEFAULT NULL,
  `round` varchar(255) DEFAULT NULL,
  `series` varchar(255) DEFAULT NULL,
  `tmIDWinner` varchar(255) DEFAULT NULL,
  `lgIDWinner` varchar(255) DEFAULT NULL,
  `tmIDLoser` varchar(255) DEFAULT NULL,
  `lgIDLoser` varchar(255) DEFAULT NULL,
  `W` int(11) DEFAULT NULL,
  `L` int(11) DEFAULT NULL,
  KEY `tmIDWinner` (`tmIDWinner`,`year`),
  KEY `tmIDLoser` (`tmIDLoser`,`year`),
  CONSTRAINT `series_post_ibfk_1` FOREIGN KEY (`tmIDWinner`, `year`) REFERENCES `teams` (`tmID`, `year`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `series_post_ibfk_2` FOREIGN KEY (`tmIDLoser`, `year`) REFERENCES `teams` (`tmID`, `year`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `teams` (
  `year` int(11) NOT NULL,
  `lgID` varchar(255) DEFAULT NULL,
  `tmID` varchar(255) NOT NULL,
  `franchID` varchar(255) DEFAULT NULL,
  `confID` varchar(255) DEFAULT NULL,
  `divID` varchar(255) DEFAULT NULL,
  `rank` int(11) DEFAULT NULL,
  `playoff` varchar(255) DEFAULT NULL,
  `seeded` int(11) DEFAULT NULL,
  `firstRound` varchar(255) DEFAULT NULL,
  `semis` varchar(255) DEFAULT NULL,
  `finals` varchar(255) DEFAULT NULL,
  `name` varchar(255) DEFAULT NULL,
  `o_fgm` int(11) DEFAULT NULL,
  `o_fga` int(11) DEFAULT NULL,
  `o_ftm` int(11) DEFAULT NULL,
  `o_fta` int(11) DEFAULT NULL,
  `o_3pm` int(11) DEFAULT NULL,
  `o_3pa` int(11) DEFAULT NULL,
  `o_oreb` int(11) DEFAULT NULL,
  `o_dreb` int(11) DEFAULT NULL,
  `o_reb` int(11) DEFAULT NULL,
  `o_asts` int(11) DEFAULT NULL,
  `o_pf` int(11) DEFAULT NULL,
  `o_stl` int(11) DEFAULT NULL,
  `o_to` int(11) DEFAULT NULL,
  `o_blk` int(11) DEFAULT NULL,
  `o_pts` int(11) DEFAULT NULL,
  `d_fgm` int(11) DEFAULT NULL,
  `d_fga` int(11) DEFAULT NULL,
  `d_ftm` int(11) DEFAULT NULL,
  `d_fta` int(11) DEFAULT NULL,
  `d_3pm` int(11) DEFAULT NULL,
  `d_3pa` int(11) DEFAULT NULL,
  `d_oreb` int(11) DEFAULT NULL,
  `d_dreb` int(11) DEFAULT NULL,
  `d_reb` int(11) DEFAULT NULL,
  `d_asts` int(11) DEFAULT NULL,
  `d_pf` int(11) DEFAULT NULL,
  `d_stl` int(11) DEFAULT NULL,
  `d_to` int(11) DEFAULT NULL,
  `d_blk` int(11) DEFAULT NULL,
  `d_pts` int(11) DEFAULT NULL,
  `tmORB` int(11) DEFAULT NULL,
  `tmDRB` int(11) DEFAULT NULL,
  `tmTRB` int(11) DEFAULT NULL,
  `opptmORB` int(11) DEFAULT NULL,
  `opptmDRB` int(11) DEFAULT NULL,
  `opptmTRB` int(11) DEFAULT NULL,
  `won` int(11) DEFAULT NULL,
  `lost` int(11) DEFAULT NULL,
  `GP` int(11) DEFAULT NULL,
  `homeW` int(11) DEFAULT NULL,
  `homeL` int(11) DEFAULT NULL,
  `awayW` int(11) DEFAULT NULL,
  `awayL` int(11) DEFAULT NULL,
  `confW` int(11) DEFAULT NULL,
  `confL` int(11) DEFAULT NULL,
  `min` int(11) DEFAULT NULL,
  `attend` int(11) DEFAULT NULL,
  `arena` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`tmID`,`year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `teams_post` (
  `year` int(11) DEFAULT NULL,
  `tmID` varchar(255) DEFAULT NULL,
  `lgID` varchar(255) DEFAULT NULL,
  `W` int(11) DEFAULT NULL,
  `L` int(11) DEFAULT NULL,
  KEY `teams_post_tmID` (`tmID`,`year`) USING BTREE,
  CONSTRAINT `teams_post_ibfk_1` FOREIGN KEY (`tmID`, `year`) REFERENCES `teams` (`tmID`, `year`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

