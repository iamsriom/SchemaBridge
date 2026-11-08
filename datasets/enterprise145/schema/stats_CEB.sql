-- Schema for database: stats_CEB

CREATE TABLE `badges` (
  `Id` int(11) NOT NULL,
  `UserId` int(11) NOT NULL,
  `Date` datetime NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `UserId` (`UserId`),
  CONSTRAINT `badges_ibfk_1` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `comments` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) NOT NULL,
  `Score` int(11) NOT NULL,
  `CreationDate` datetime NOT NULL,
  `UserId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `PostId` (`PostId`),
  KEY `UserId` (`UserId`),
  CONSTRAINT `comments_ibfk_1` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`),
  CONSTRAINT `comments_ibfk_2` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `postHistory` (
  `Id` int(11) NOT NULL,
  `PostHistoryTypeId` int(11) NOT NULL,
  `PostId` int(11) NOT NULL,
  `CreationDate` datetime NOT NULL,
  `UserId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `PostId` (`PostId`),
  KEY `UserId` (`UserId`),
  CONSTRAINT `postHistory_ibfk_1` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`),
  CONSTRAINT `postHistory_ibfk_2` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `postLinks` (
  `Id` int(11) NOT NULL,
  `CreationDate` datetime NOT NULL,
  `PostId` int(11) NOT NULL,
  `RelatedPostId` int(11) NOT NULL,
  `LinkTypeId` int(11) NOT NULL,
  PRIMARY KEY (`Id`),
  KEY `PostId` (`PostId`),
  KEY `RelatedPostId` (`RelatedPostId`),
  CONSTRAINT `postLinks_ibfk_1` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`),
  CONSTRAINT `postLinks_ibfk_2` FOREIGN KEY (`RelatedPostId`) REFERENCES `posts` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `posts` (
  `Id` int(11) NOT NULL,
  `PostTypeId` int(11) NOT NULL,
  `CreationDate` datetime NOT NULL,
  `Score` int(11) NOT NULL,
  `ViewCount` int(11) DEFAULT NULL,
  `OwnerUserId` int(11) DEFAULT NULL,
  `AnswerCount` int(11) DEFAULT NULL,
  `CommentCount` int(11) NOT NULL,
  `FavoriteCount` int(11) DEFAULT NULL,
  `LastEditorUserId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `LastEditorUserId` (`LastEditorUserId`),
  KEY `OwnerUserId` (`OwnerUserId`),
  CONSTRAINT `posts_ibfk_1` FOREIGN KEY (`LastEditorUserId`) REFERENCES `users` (`Id`),
  CONSTRAINT `posts_ibfk_2` FOREIGN KEY (`OwnerUserId`) REFERENCES `users` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `tags` (
  `Id` int(11) NOT NULL,
  `Count` int(11) NOT NULL,
  `ExcerptPostId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `ExcerptPostId` (`ExcerptPostId`),
  CONSTRAINT `tags_ibfk_1` FOREIGN KEY (`ExcerptPostId`) REFERENCES `posts` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `users` (
  `Id` int(11) NOT NULL,
  `Reputation` int(11) NOT NULL,
  `CreationDate` datetime NOT NULL,
  `Views` int(11) NOT NULL,
  `UpVotes` int(11) NOT NULL,
  `DownVotes` int(11) NOT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `votes` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) NOT NULL,
  `VoteTypeId` int(11) NOT NULL,
  `CreationDate` datetime NOT NULL,
  `UserId` int(11) DEFAULT NULL,
  `BountyAmount` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `PostId` (`PostId`),
  KEY `UserId` (`UserId`),
  CONSTRAINT `votes_ibfk_1` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`),
  CONSTRAINT `votes_ibfk_2` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

