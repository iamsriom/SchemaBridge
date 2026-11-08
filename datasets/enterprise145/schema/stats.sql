-- Schema for database: stats

CREATE TABLE `badges` (
  `Id` int(11) NOT NULL,
  `UserId` int(11) DEFAULT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Date` datetime DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `badges_UserId_fkey` (`UserId`),
  CONSTRAINT `badges_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `comments` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) DEFAULT NULL,
  `Score` int(11) DEFAULT NULL,
  `Text` longtext DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `UserDisplayName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `comment_staged_UserId_fkey` (`UserId`),
  KEY `comment_PostId_fkey` (`PostId`),
  CONSTRAINT `comment_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `comment_staged_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `postHistory` (
  `Id` int(11) NOT NULL,
  `PostHistoryTypeId` int(11) DEFAULT NULL,
  `PostId` int(11) DEFAULT NULL,
  `RevisionGUID` varchar(255) DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `Text` longtext DEFAULT NULL,
  `Comment` text DEFAULT NULL,
  `UserDisplayName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `postHistory_Id_key` (`Id`),
  KEY `postHistory_UserId_fkey` (`UserId`),
  KEY `postHistory_PostId_fkey` (`PostId`),
  CONSTRAINT `postHistory_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `postHistory_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `postLinks` (
  `Id` int(11) NOT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `PostId` int(11) DEFAULT NULL,
  `RelatedPostId` int(11) DEFAULT NULL,
  `LinkTypeId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `postlinks_stripped_PostId_fkey` (`PostId`),
  KEY `postlinks_stripped_RelatedPostId_fkey` (`RelatedPostId`),
  CONSTRAINT `postlinks_stripped_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `postlinks_stripped_RelatedPostId_fkey` FOREIGN KEY (`RelatedPostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `posts` (
  `Id` int(11) NOT NULL,
  `PostTypeId` int(11) DEFAULT NULL,
  `AcceptedAnswerId` int(11) DEFAULT NULL,
  `CreaionDate` datetime DEFAULT NULL,
  `Score` int(11) DEFAULT NULL,
  `ViewCount` int(11) DEFAULT NULL,
  `Body` longtext DEFAULT NULL,
  `OwnerUserId` int(11) DEFAULT NULL,
  `LasActivityDate` datetime DEFAULT NULL,
  `Title` varchar(255) DEFAULT NULL,
  `Tags` varchar(255) DEFAULT NULL,
  `AnswerCount` int(11) DEFAULT NULL,
  `CommentCount` int(11) DEFAULT NULL,
  `FavoriteCount` int(11) DEFAULT NULL,
  `LastEditorUserId` int(11) DEFAULT NULL,
  `LastEditDate` datetime DEFAULT NULL,
  `CommunityOwnedDate` datetime DEFAULT NULL,
  `ParentId` int(11) DEFAULT NULL,
  `ClosedDate` datetime DEFAULT NULL,
  `OwnerDisplayName` varchar(255) DEFAULT NULL,
  `LastEditorDisplayName` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `posts_Id_key` (`Id`),
  KEY `posts_ParentId_fkey` (`ParentId`),
  KEY `posts_OwnerUserId_fkey` (`OwnerUserId`),
  KEY `posts_LastEditorUserId_fkey` (`LastEditorUserId`),
  CONSTRAINT `posts_LastEditorUserId_fkey` FOREIGN KEY (`LastEditorUserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `posts_OwnerUserId_fkey` FOREIGN KEY (`OwnerUserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `posts_ParentId_fkey` FOREIGN KEY (`ParentId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tags` (
  `Id` int(11) NOT NULL,
  `TagName` varchar(255) DEFAULT NULL,
  `Count` int(11) DEFAULT NULL,
  `ExcerptPostId` int(11) DEFAULT NULL,
  `WikiPostId` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `tags_ExcerptPostId_fkey` (`ExcerptPostId`),
  CONSTRAINT `tags_ExcerptPostId_fkey` FOREIGN KEY (`ExcerptPostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `users` (
  `Id` int(11) NOT NULL,
  `Reputation` int(11) DEFAULT NULL,
  `CreationDate` datetime DEFAULT NULL,
  `DisplayName` varchar(255) DEFAULT NULL,
  `LastAccessDate` datetime DEFAULT NULL,
  `WebsiteUrl` varchar(255) DEFAULT NULL,
  `Location` varchar(255) DEFAULT NULL,
  `AboutMe` longtext DEFAULT NULL,
  `Views` int(11) DEFAULT NULL,
  `UpVotes` int(11) DEFAULT NULL,
  `DownVotes` int(11) DEFAULT NULL,
  `AccountId` int(11) DEFAULT NULL,
  `Age` int(11) DEFAULT NULL,
  `ProfileImageUrl` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  UNIQUE KEY `users_staged_Id_key` (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `votes` (
  `Id` int(11) NOT NULL,
  `PostId` int(11) DEFAULT NULL,
  `VoteTypeId` int(11) DEFAULT NULL,
  `CreationDate` date DEFAULT NULL,
  `UserId` int(11) DEFAULT NULL,
  `BountyAmount` int(11) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `votes_stripped_UserId_fkey` (`UserId`),
  KEY `votes_stripped_PostId_fkey` (`PostId`),
  CONSTRAINT `votes_stripped_PostId_fkey` FOREIGN KEY (`PostId`) REFERENCES `posts` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `votes_stripped_UserId_fkey` FOREIGN KEY (`UserId`) REFERENCES `users` (`Id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

