DROP TABLE IF EXISTS `covid19_timeseries`;
CREATE TABLE `covid19_timeseries` (
  `country` varchar(50) DEFAULT NULL,
  `lat_` float DEFAULT NULL,
  `long_` float DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `confirmed` int DEFAULT NULL,
  `deaths` int DEFAULT NULL,
  `recovered` int DEFAULT NULL,
  `active` int DEFAULT NULL,
  `who_region` varchar(50) DEFAULT NULL,
  `uuid` int NOT NULL,
  PRIMARY KEY (`uuid`)
);




DROP TABLE IF EXISTS `worldometer`;
CREATE TABLE `worldometer` (
  `rank` int DEFAULT NULL,
  `cca3` char(3) DEFAULT NULL,
  `country` varchar(50) NOT NULL,
  `capital` varchar(50) DEFAULT NULL,
  `continent` varchar(50) DEFAULT NULL,
  `2022_population` varchar(50) DEFAULT NULL,
  `2020_population` varchar(50) DEFAULT NULL,
  `2015_population` varchar(50) DEFAULT NULL,
  `2010_population` varchar(50) DEFAULT NULL,
  `2000_population` varchar(50) DEFAULT NULL,
  `1990_population` varchar(50) DEFAULT NULL,
  `1980_population` varchar(50) DEFAULT NULL,
  `1970_population` varchar(50) DEFAULT NULL,
  `area` float DEFAULT NULL,
  `density` float DEFAULT NULL,
  `growth_rate` float DEFAULT NULL,
  `world_population_percentage` float DEFAULT NULL,
  PRIMARY KEY (`country`)
);
