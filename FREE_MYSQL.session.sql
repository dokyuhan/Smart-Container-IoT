USE `sql3678877`;

DROP TABLE IF EXISTS `sensor_bote`;

CREATE TABLE `sensor_bote` (
  `id` int NOT NULL AUTO_INCREMENT,
  `capacidad` float DEFAULT NULL,
  `porcentaje` int DEFAULT NULL,
  `date_time` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1;