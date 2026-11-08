-- Schema for database: medical

CREATE TABLE `Examination` (
  `ID` int(11) DEFAULT NULL,
  `Examination Date` date DEFAULT NULL,
  `aCL IgG` float DEFAULT NULL,
  `aCL IgM` float DEFAULT NULL,
  `ANA` int(11) DEFAULT NULL,
  `ANA Pattern` varchar(255) DEFAULT NULL,
  `aCL IgA` int(11) DEFAULT NULL,
  `Diagnosis` varchar(255) DEFAULT NULL,
  `KCT` varchar(255) DEFAULT NULL,
  `RVVT` varchar(255) DEFAULT NULL,
  `LAC` varchar(255) DEFAULT NULL,
  `Symptoms` varchar(255) DEFAULT NULL,
  `Thrombosis` int(11) DEFAULT NULL,
  KEY `Examination_ID` (`ID`),
  CONSTRAINT `Examination_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `Patient` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Laboratory` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `Date` date NOT NULL DEFAULT '0000-00-00',
  `GOT` int(11) DEFAULT NULL,
  `GPT` int(11) DEFAULT NULL,
  `LDH` int(11) DEFAULT NULL,
  `ALP` int(11) DEFAULT NULL,
  `TP` decimal(5,1) DEFAULT NULL,
  `ALB` decimal(5,1) DEFAULT NULL,
  `UA` decimal(5,1) DEFAULT NULL,
  `UN` int(11) DEFAULT NULL,
  `CRE` decimal(5,1) DEFAULT NULL,
  `T-BIL` decimal(5,1) DEFAULT NULL,
  `T-CHO` int(11) DEFAULT NULL,
  `TG` int(11) DEFAULT NULL,
  `CPK` int(11) DEFAULT NULL,
  `GLU` int(11) DEFAULT NULL,
  `WBC` decimal(5,1) DEFAULT NULL,
  `RBC` decimal(5,1) DEFAULT NULL,
  `HGB` decimal(5,1) DEFAULT NULL,
  `HCT` decimal(5,1) DEFAULT NULL,
  `PLT` int(11) DEFAULT NULL,
  `PT` decimal(5,1) DEFAULT NULL,
  `APTT` int(11) DEFAULT NULL,
  `FG` decimal(5,1) DEFAULT NULL,
  `PIC` int(11) DEFAULT NULL,
  `TAT` int(11) DEFAULT NULL,
  `TAT2` int(11) DEFAULT NULL,
  `U-PRO` varchar(255) DEFAULT NULL,
  `IGG` int(11) DEFAULT NULL,
  `IGA` int(11) DEFAULT NULL,
  `IGM` int(11) DEFAULT NULL,
  `CRP` varchar(255) DEFAULT NULL,
  `RA` varchar(255) DEFAULT NULL,
  `RF` varchar(255) DEFAULT NULL,
  `C3` int(11) DEFAULT NULL,
  `C4` int(11) DEFAULT NULL,
  `RNP` varchar(255) DEFAULT NULL,
  `SM` varchar(255) DEFAULT NULL,
  `SC170` varchar(255) DEFAULT NULL,
  `SSA` varchar(255) DEFAULT NULL,
  `SSB` varchar(255) DEFAULT NULL,
  `CENTROMEA` varchar(255) DEFAULT NULL,
  `DNA` varchar(255) DEFAULT NULL,
  `DNA-II` int(11) DEFAULT NULL,
  PRIMARY KEY (`ID`,`Date`),
  KEY `Laboratory_ID` (`ID`),
  CONSTRAINT `Laboratory_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `Patient` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `Patient` (
  `ID` int(11) NOT NULL DEFAULT 0,
  `SEX` varchar(255) DEFAULT NULL,
  `Birthday` date DEFAULT NULL,
  `Description` date DEFAULT NULL,
  `First Date` date DEFAULT NULL,
  `Admission` varchar(255) DEFAULT NULL,
  `Diagnosis` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

