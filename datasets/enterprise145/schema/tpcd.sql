-- Schema for database: tpcd

CREATE TABLE `dss_customer` (
  `c_custkey` int(11) NOT NULL,
  `c_name` varchar(25) NOT NULL,
  `c_address` varchar(40) NOT NULL,
  `c_nationkey` int(11) NOT NULL,
  `c_phone` char(15) NOT NULL,
  `c_acctbal` double NOT NULL,
  `c_mktsegment` char(10) NOT NULL,
  `c_comment` varchar(117) DEFAULT NULL,
  PRIMARY KEY (`c_custkey`),
  KEY `c_nationkey` (`c_nationkey`),
  CONSTRAINT `dss_customer_ibfk_1` FOREIGN KEY (`c_nationkey`) REFERENCES `dss_nation` (`n_nationkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_lineitem` (
  `l_orderkey` decimal(18,0) NOT NULL,
  `l_partkey` int(11) NOT NULL,
  `l_suppkey` int(11) NOT NULL,
  `l_linenumber` int(11) NOT NULL,
  `l_quantity` double NOT NULL,
  `l_extendedprice` double NOT NULL,
  `l_discount` double NOT NULL,
  `l_tax` double NOT NULL,
  `l_returnflag` char(1) NOT NULL,
  `l_linestatus` char(1) NOT NULL,
  `l_shipdate` date DEFAULT NULL,
  `l_commitdate` date DEFAULT NULL,
  `l_receiptdate` date DEFAULT NULL,
  `l_shipinstruct` char(25) NOT NULL,
  `l_shipmode` char(10) NOT NULL,
  `l_comment` varchar(44) DEFAULT NULL,
  PRIMARY KEY (`l_orderkey`,`l_linenumber`),
  KEY `lineitem_idx1` (`l_orderkey`,`l_returnflag`,`l_extendedprice`,`l_discount`),
  KEY `lineitem_idx2` (`l_partkey`,`l_quantity`,`l_extendedprice`,`l_suppkey`,`l_orderkey`,`l_discount`),
  KEY `l_suppkey` (`l_suppkey`),
  KEY `l_partkey` (`l_partkey`,`l_suppkey`),
  CONSTRAINT `dss_lineitem_ibfk_1` FOREIGN KEY (`l_orderkey`) REFERENCES `dss_order` (`o_orderkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_nation` (
  `n_nationkey` int(11) NOT NULL,
  `n_name` char(25) NOT NULL,
  `n_regionkey` int(11) NOT NULL,
  `n_comment` varchar(152) DEFAULT NULL,
  PRIMARY KEY (`n_nationkey`),
  KEY `n_regionkey` (`n_regionkey`),
  CONSTRAINT `dss_nation_ibfk_1` FOREIGN KEY (`n_regionkey`) REFERENCES `dss_region` (`r_regionkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_order` (
  `o_orderkey` decimal(18,0) NOT NULL,
  `o_custkey` int(11) NOT NULL,
  `o_orderstatus` char(1) NOT NULL,
  `o_totalprice` double NOT NULL,
  `o_orderdate` date DEFAULT NULL,
  `o_orderpriority` char(15) NOT NULL,
  `o_clerk` char(15) NOT NULL,
  `o_shippriority` int(11) NOT NULL,
  `o_comment` varchar(79) DEFAULT NULL,
  PRIMARY KEY (`o_orderkey`),
  KEY `orders_idx1` (`o_orderkey`),
  KEY `orders_idx2` (`o_clerk`,`o_orderkey`,`o_orderdate`),
  KEY `o_custkey` (`o_custkey`),
  CONSTRAINT `dss_order_ibfk_1` FOREIGN KEY (`o_custkey`) REFERENCES `dss_customer` (`c_custkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_part` (
  `p_partkey` int(11) NOT NULL,
  `p_name` varchar(55) NOT NULL,
  `p_mfgr` char(25) NOT NULL,
  `p_brand` char(10) NOT NULL,
  `p_type` varchar(25) NOT NULL,
  `p_size` int(11) NOT NULL,
  `p_container` char(10) NOT NULL,
  `p_retailprice` double NOT NULL,
  `p_comment` varchar(23) NOT NULL,
  PRIMARY KEY (`p_partkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_partsupp` (
  `ps_partkey` int(11) NOT NULL,
  `ps_suppkey` int(11) NOT NULL,
  `ps_availqty` int(11) NOT NULL,
  `ps_supplycost` double NOT NULL,
  `ps_comment` varchar(199) DEFAULT NULL,
  PRIMARY KEY (`ps_partkey`,`ps_suppkey`),
  KEY `partsupp_idx1` (`ps_partkey`),
  KEY `partsupp_idx2` (`ps_suppkey`,`ps_partkey`),
  KEY `ps_partkey` (`ps_partkey`,`ps_suppkey`),
  CONSTRAINT `dss_partsupp_ibfk_1` FOREIGN KEY (`ps_suppkey`) REFERENCES `dss_supplier` (`s_suppkey`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `dss_partsupp_ibfk_2` FOREIGN KEY (`ps_partkey`) REFERENCES `dss_part` (`p_partkey`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `dss_partsupp_ibfk_3` FOREIGN KEY (`ps_partkey`, `ps_suppkey`) REFERENCES `dss_lineitem` (`l_partkey`, `l_suppkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_region` (
  `r_regionkey` int(11) NOT NULL,
  `r_name` char(25) NOT NULL,
  `r_comment` varchar(152) DEFAULT NULL,
  PRIMARY KEY (`r_regionkey`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;


CREATE TABLE `dss_supplier` (
  `s_suppkey` int(11) NOT NULL,
  `s_name` char(25) NOT NULL,
  `s_address` varchar(40) NOT NULL,
  `s_nationkey` int(11) NOT NULL,
  `s_phone` char(15) NOT NULL,
  `s_acctbal` double NOT NULL,
  `s_comment` varchar(101) NOT NULL,
  PRIMARY KEY (`s_suppkey`),
  UNIQUE KEY `supplier_idx1` (`s_suppkey`),
  KEY `s_nationkey` (`s_nationkey`),
  CONSTRAINT `dss_supplier_ibfk_1` FOREIGN KEY (`s_nationkey`) REFERENCES `dss_nation` (`n_nationkey`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci
;

