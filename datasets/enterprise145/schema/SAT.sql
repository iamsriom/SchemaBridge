-- Schema for database: SAT

CREATE TABLE `class` (
  `cls` varchar(8) NOT NULL,
  PRIMARY KEY (`cls`),
  KEY `cls` (`cls`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `fault` (
  `tm` int(11) NOT NULL,
  `tf` varchar(1) NOT NULL,
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `tf` (`tf`),
  CONSTRAINT `fault_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fault_ibfk_2` FOREIGN KEY (`tf`) REFERENCES `trfl` (`tf`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `fault_test` (
  `tm` int(11) NOT NULL,
  `tf` varchar(1) NOT NULL,
  PRIMARY KEY (`tm`),
  KEY `tf` (`tf`),
  KEY `tm` (`tm`),
  CONSTRAINT `fault_test_ibfk_1` FOREIGN KEY (`tf`) REFERENCES `trfl` (`tf`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fault_test_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `gmt_mission_phase` (
  `tm` int(11) NOT NULL,
  `state` varchar(50) NOT NULL,
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  CONSTRAINT `gmt_mission_phase_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `succ` (
  `tm1` int(11) NOT NULL,
  `tm2` int(11) NOT NULL,
  PRIMARY KEY (`tm1`,`tm2`),
  KEY `tm1` (`tm1`),
  KEY `tm2` (`tm2`),
  CONSTRAINT `succ_ibfk_1` FOREIGN KEY (`tm1`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `succ_ibfk_2` FOREIGN KEY (`tm2`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `time` (
  `tm` int(11) NOT NULL,
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci
;


CREATE TABLE `tm001_eod_relay` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm001_eod_relay_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm001_eod_relay_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm002_battov_temp` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm002_battov_temp_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm002_battov_temp_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm004_eoc_signaled` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm004_eoc_signaled_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm004_eoc_signaled_ibfk_2` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm007_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm007_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm007_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm009_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm009_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm009_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm011_eod_override` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm011_eod_override_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm011_eod_override_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm013_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm013_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm013_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm015_eod_signaled` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm015_eod_signaled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm015_eod_signaled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm017_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm017_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm017_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm018_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm018_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm018_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm021_eoc_disabled` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm021_eoc_disabled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm021_eoc_disabled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm022_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm022_switch_ibfk_1` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm022_switch_ibfk_2` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm029_ovt_disabled` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm029_ovt_disabled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm029_ovt_disabled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm031_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm031_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm031_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm038_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm038_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm038_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm039_eod_disabled` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm039_eod_disabled_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm039_eod_disabled_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm040_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm040_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm040_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm042_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm042_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm042_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm043_switch` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm043_switch_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm043_switch_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm054_supply_1a` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm054_supply_1a_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm054_supply_1a_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm055_supply_1b` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm055_supply_1b_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm055_supply_1b_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm057_supply_2c` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm057_supply_2c_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm057_supply_2c_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm058_asr_or_switch_10` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm058_asr_or_switch_10_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm058_asr_or_switch_10_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm070_supply_3c` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm070_supply_3c_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm070_supply_3c_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm071_asr_or_switch_20` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm071_asr_or_switch_20_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm071_asr_or_switch_20_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm211_bus_voltage` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm211_bus_voltage_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm211_bus_voltage_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm220_supply_1c` (
  `tm` int(11) NOT NULL,
  `class` varchar(8) NOT NULL,
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm220_supply_1c_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm220_supply_1c_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm222_charging` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm222_charging_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm222_charging_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `tm257_battery_voltage` (
  `tm` int(11) NOT NULL DEFAULT 0,
  `class` varchar(8) NOT NULL DEFAULT '',
  PRIMARY KEY (`tm`),
  KEY `tm` (`tm`),
  KEY `class` (`class`),
  CONSTRAINT `tm257_battery_voltage_ibfk_1` FOREIGN KEY (`class`) REFERENCES `class` (`cls`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tm257_battery_voltage_ibfk_2` FOREIGN KEY (`tm`) REFERENCES `time` (`tm`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `trfl` (
  `tf` varchar(1) NOT NULL,
  PRIMARY KEY (`tf`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

