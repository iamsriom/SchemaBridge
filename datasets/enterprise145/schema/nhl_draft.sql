-- Schema for database: nhl_draft

CREATE TABLE `PlayerInfo` (
  `ELITEID` int(11) NOT NULL,
  `PlayerName` varchar(255) NOT NULL,
  `birthdate` varchar(255) NOT NULL,
  `birthyear` varchar(255) NOT NULL,
  `birthmonth` int(11) NOT NULL,
  `birthday` int(11) NOT NULL,
  `birthplace` varchar(255) NOT NULL,
  `nation` varchar(255) NOT NULL,
  `height_info` varchar(255) NOT NULL,
  `height` int(11) NOT NULL,
  `weight_info` varchar(255) NOT NULL,
  `weight` int(11) NOT NULL,
  `position_info` varchar(255) NOT NULL,
  `position` varchar(255) NOT NULL,
  `shoots` varchar(255) NOT NULL,
  `draftyear` int(11) NOT NULL,
  `draftround` int(11) NOT NULL,
  `overall` int(11) NOT NULL,
  `overallby` varchar(255) NOT NULL,
  `CSS_rank` int(11) NOT NULL,
  `sum_7yr_GP` int(11) NOT NULL,
  `sum_7yr_TOI` int(11) NOT NULL,
  `GP_greater_than_0` varchar(255) NOT NULL,
  PRIMARY KEY (`ELITEID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `SeasonStatus` (
  `ELITEID` int(11) NOT NULL,
  `SEASON` varchar(255) NOT NULL,
  `TEAM` varchar(255) NOT NULL,
  `LEAGUE` varchar(255) NOT NULL,
  `GAMETYPE` varchar(255) NOT NULL,
  `GP` int(11) NOT NULL,
  `G` int(11) NOT NULL,
  `A` int(11) NOT NULL,
  `P` int(11) NOT NULL,
  `PIM` int(11) NOT NULL,
  `PLUSMINUS` int(11) NOT NULL,
  KEY `SeasonStatus_PlayerInfo_FK` (`ELITEID`),
  CONSTRAINT `SeasonStatus_PlayerInfo_FK` FOREIGN KEY (`ELITEID`) REFERENCES `PlayerInfo` (`ELITEID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;

