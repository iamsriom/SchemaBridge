-- Schema for database: Hockey_Yeti

CREATE TABLE `original_player_season_draftdata` (
  `eliteId` int(11) DEFAULT NULL,
  `PlayerName` text DEFAULT NULL,
  `BirthDate` text DEFAULT NULL,
  `BirthYear` int(11) DEFAULT NULL,
  `BirthMonth` int(11) DEFAULT NULL,
  `BirthDay` int(11) DEFAULT NULL,
  `Birthplace` text DEFAULT NULL,
  `Nation` text DEFAULT NULL,
  `Height_info` text DEFAULT NULL,
  `Height` int(11) DEFAULT NULL,
  `Weight_info` text DEFAULT NULL,
  `Weight` int(11) DEFAULT NULL,
  `Position_info` text DEFAULT NULL,
  `Position` text DEFAULT NULL,
  `Shoots` text DEFAULT NULL,
  `DraftYear` int(11) DEFAULT NULL,
  `DraftRound` int(11) DEFAULT NULL,
  `Overall` int(11) DEFAULT NULL,
  `OverallBy` text DEFAULT NULL,
  `Season` text DEFAULT NULL,
  `Team` text DEFAULT NULL,
  `League` text DEFAULT NULL,
  `GameType` text DEFAULT NULL,
  `GP` int(11) DEFAULT NULL,
  `G` int(11) DEFAULT NULL,
  `A` int(11) DEFAULT NULL,
  `P` int(11) DEFAULT NULL,
  `PIM` int(11) DEFAULT NULL,
  `PlusMinus` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `original_player_season_hockey_drafted` (
  `eliteId` int(11) DEFAULT NULL,
  `PlayerName` text DEFAULT NULL,
  `BirthDate` text DEFAULT NULL,
  `BirthYear` int(11) DEFAULT NULL,
  `BirthMonth` int(11) DEFAULT NULL,
  `BirthDay` int(11) DEFAULT NULL,
  `Birthplace` text DEFAULT NULL,
  `Nation` text DEFAULT NULL,
  `Height_info` text DEFAULT NULL,
  `Height` int(11) DEFAULT NULL,
  `Weight_info` text DEFAULT NULL,
  `Weight` int(11) DEFAULT NULL,
  `Position_info` text DEFAULT NULL,
  `Position` text DEFAULT NULL,
  `Shoots` text DEFAULT NULL,
  `DraftYear` int(11) DEFAULT NULL,
  `DraftRound` int(11) DEFAULT NULL,
  `Overall` int(11) DEFAULT NULL,
  `OverallBy` text DEFAULT NULL,
  `Season` text DEFAULT NULL,
  `Team` text DEFAULT NULL,
  `League` text DEFAULT NULL,
  `GameType` text DEFAULT NULL,
  `GP` int(11) DEFAULT NULL,
  `G` int(11) DEFAULT NULL,
  `A` int(11) DEFAULT NULL,
  `P` int(11) DEFAULT NULL,
  `PIM` int(11) DEFAULT NULL,
  `PlusMinus` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

