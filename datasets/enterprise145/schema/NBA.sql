-- Schema for database: NBA

CREATE TABLE `Actions` (
  `GameId` int(11) NOT NULL,
  `TeamId` int(11) DEFAULT NULL,
  `PlayerId` int(11) NOT NULL,
  `Minutes` int(11) DEFAULT NULL,
  `FieldGoalsMade` int(11) DEFAULT NULL,
  `FieldGoalAttempts` int(11) DEFAULT NULL,
  `3PointsMade` int(11) DEFAULT NULL,
  `3PointAttempts` int(11) DEFAULT NULL,
  `FreeThrowsMade` int(11) DEFAULT NULL,
  `FreeThrowAttempts` int(11) DEFAULT NULL,
  `PlusMinus` int(11) DEFAULT NULL,
  `OffensiveRebounds` int(11) DEFAULT NULL,
  `DefensiveRebounds` int(11) DEFAULT NULL,
  `TotalRebounds` int(11) DEFAULT NULL,
  `Assists` int(11) DEFAULT NULL,
  `PersonalFouls` int(11) DEFAULT NULL,
  `Steals` int(11) DEFAULT NULL,
  `Turnovers` int(11) DEFAULT NULL,
  `BlockedShots` int(11) DEFAULT NULL,
  `BlocksAgainst` int(11) DEFAULT NULL,
  `Points` int(11) DEFAULT NULL,
  `Starter` int(11) DEFAULT NULL,
  PRIMARY KEY (`GameId`,`PlayerId`),
  KEY `GameId_idx` (`GameId`),
  KEY `PlayerId_idx` (`PlayerId`),
  KEY `TeamId_idx` (`TeamId`),
  CONSTRAINT `GameId` FOREIGN KEY (`GameId`) REFERENCES `Game` (`GameId`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `playerId-A` FOREIGN KEY (`PlayerId`) REFERENCES `Player` (`PlayerId`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `teamId_A` FOREIGN KEY (`TeamId`) REFERENCES `Team` (`TeamId`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Game` (
  `GameId` int(11) NOT NULL,
  `Team1Id` int(11) DEFAULT NULL,
  `Team2Id` int(11) DEFAULT NULL,
  `ResultOfTeam1` int(11) DEFAULT NULL,
  `URL` varchar(80) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  PRIMARY KEY (`GameId`),
  KEY `Team1Id_idx` (`Team1Id`),
  KEY `Team2Id_idx` (`Team2Id`),
  CONSTRAINT `Team1Id` FOREIGN KEY (`Team1Id`) REFERENCES `Team` (`TeamId`) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `Team2Id` FOREIGN KEY (`Team2Id`) REFERENCES `Team` (`TeamId`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Player` (
  `PlayerId` int(11) NOT NULL COMMENT '	',
  `PlayerName` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`PlayerId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `Team` (
  `TeamId` int(11) NOT NULL,
  `TeamName` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`TeamId`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `joined_drafted_all_players_original` (
  `ID` int(11) DEFAULT NULL,
  `age` int(11) DEFAULT NULL,
  `draft_g` int(11) DEFAULT NULL,
  `mp` int(11) DEFAULT NULL,
  `draft_fg` int(11) DEFAULT NULL,
  `fga` int(11) DEFAULT NULL,
  `3p` int(11) DEFAULT NULL,
  `3pa` int(11) DEFAULT NULL,
  `draft_ft` int(11) DEFAULT NULL,
  `fta` int(11) DEFAULT NULL,
  `orb` int(11) DEFAULT NULL,
  `draft_trb` int(11) DEFAULT NULL,
  `draft_ast` int(11) DEFAULT NULL,
  `draft_stl` int(11) DEFAULT NULL,
  `draft_blk` int(11) DEFAULT NULL,
  `draft_tov` int(11) DEFAULT NULL,
  `draft_pf` int(11) DEFAULT NULL,
  `draft_pts` int(11) DEFAULT NULL,
  `fg_per` double DEFAULT NULL,
  `3p_per` int(11) DEFAULT NULL,
  `ft_per` double DEFAULT NULL,
  `mp_per` double DEFAULT NULL,
  `pts_per` double DEFAULT NULL,
  `trb_per` double DEFAULT NULL,
  `ast_per` double DEFAULT NULL,
  `season` text DEFAULT NULL,
  `weight` int(11) DEFAULT NULL,
  `height` int(11) DEFAULT NULL,
  `position` text DEFAULT NULL,
  `shoots` text DEFAULT NULL,
  `born` text DEFAULT NULL,
  `draft_year` int(11) DEFAULT NULL,
  `pk` int(11) DEFAULT NULL,
  `amature_honor` int(11) DEFAULT NULL,
  `college` text DEFAULT NULL,
  `raw_data` int(11) DEFAULT NULL,
  `career_g` int(11) DEFAULT NULL,
  `career_per` double DEFAULT NULL,
  `career_ws` double DEFAULT NULL,
  `career_ws48` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

