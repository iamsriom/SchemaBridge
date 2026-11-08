-- Schema for database: CraftBeer

CREATE TABLE `beers` (
  `id` int(11) NOT NULL,
  `brewery_id` int(11) NOT NULL,
  `abv` float DEFAULT NULL,
  `ibu` decimal(5,1) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `style` varchar(255) DEFAULT NULL,
  `ounces` decimal(5,1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `brewery_id` (`brewery_id`),
  CONSTRAINT `beers_ibfk_1` FOREIGN KEY (`brewery_id`) REFERENCES `breweries` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;


CREATE TABLE `breweries` (
  `id` int(11) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `city` varchar(255) DEFAULT NULL,
  `state` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
;

