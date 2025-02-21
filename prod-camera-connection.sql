DROP TABLE IF EXISTS `live_connection_log`;
CREATE TABLE `live_connection_log` (
  `os` STRING NULL,
  `app_version` STRING NULL,
  `view_mode` STRING NULL,
  `first_frame_time` DOUBLE NULL,
  `p2p_sdk_version` STRING NULL,
  `connect_retry_times` INT NULL,
  `video_definition` INT NULL,
  `net_mode` INT NULL,
  `iot_online` INT NULL,
  `entry_mode` INT NULL,
  `device_model` STRING NULL,
  `device_mac` STRING NULL,
  `device_mac_suffix` STRING NULL,
  `device_firmware_version` STRING NULL,
  `connect_step` STRING NULL,
  `connect_result` INT NULL,
  `connect_mode` String NULL,
  `connect_error` String NULL,
  `connect_id` STRING NULL,
  `connect_protocol` INT NULL,
  `transport_protocol` STRING NULL,
  `isCamSDK` INT NULL,
  `connect_step1_time` DOUBLE NULL,
  `connect_step2_time` DOUBLE NULL,
  `record_time` TIMESTAMP(9) NOT NULL,
  TIME INDEX (`record_time`),
  PRIMARY KEY (`device_model`,`device_mac_suffix`)
)
PARTITION ON COLUMNS (device_mac_suffix) (
   device_mac_suffix < '2',
   device_mac_suffix >= '2' AND device_mac_suffix < '4',
   device_mac_suffix >= '4' AND device_mac_suffix < '6',
   device_mac_suffix >= '6' AND device_mac_suffix < '8',
   device_mac_suffix >= '8' AND device_mac_suffix < 'A',
   device_mac_suffix >= 'A' AND device_mac_suffix < 'C',
   device_mac_suffix >= 'C' AND device_mac_suffix < 'E',
   device_mac_suffix >= 'E' AND device_mac_suffix < 'a',
   device_mac_suffix >= 'a' AND device_mac_suffix < 'c',
   device_mac_suffix >= 'c' AND device_mac_suffix < 'e',
   device_mac_suffix >= 'e'
)
WITH(
  append_mode = 'true',
  ttl = '3d'
);
DROP TABLE IF EXISTS `live_connection_statistics_rate_1h`;
CREATE TABLE IF NOT EXISTS `live_connection_statistics_rate_1h` (
  `os` STRING NULL,
  `app_version` STRING NULL,
  `device_model` STRING NULL,
  `connect_protocol` INT NULL,
  `device_firmware_version` STRING NULL,
  `avg_connect_retry_times` DOUBLE NULL,
  `total_connect_result_ok` BIGINT NULL,
  `total_connect_result_fail` BIGINT NULL,
  `total_connect` BIGINT NULL,
  `conection_rate` DOUBLE NULL,
  `record_time_window` TIMESTAMP(9) NOT NULL,
  `update_at` TIMESTAMP NULL,
  TIME INDEX (`record_time_window`),
  PRIMARY KEY (`os`, `app_version`,`device_model`, `connect_protocol`, `device_firmware_version`)
)
ENGINE=mito
WITH(
  ttl = '60d'
);
DROP FLOW IF EXISTS `live_connection_aggregation_rate_1h`;
CREATE FLOW live_connection_aggregation_rate_1h
SINK TO live_connection_statistics_rate_1h
EXPIRE AFTER INTERVAL '2 minutes'
AS 
SELECT 
  os,
  app_version,
  device_model, 
  connect_protocol,
  device_firmware_version,
  avg(connect_retry_times) AS avg_connect_retry_times, 
  sum(CASE WHEN connect_result = 1 THEN 1 ELSE 0 END) AS total_connect_result_ok, 
  sum(CASE WHEN connect_result = 0 THEN 1 ELSE 0 END) AS total_connect_result_fail, 
  count(connect_result) AS total_connect, 
  arrow_cast(sum(CASE WHEN connect_result = 1 THEN 1 ELSE 0 END), 'Float64') / arrow_cast(count(connect_result), 'Float64') AS conection_rate, 
  date_bin(INTERVAL '1 hour', record_time) AS record_time_window, 
FROM live_connection_log 
WHERE iot_online = 1
GROUP BY 
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;


DROP TABLE IF EXISTS `live_connection_statistics_speed_1h`;
CREATE TABLE IF NOT EXISTS `live_connection_statistics_speed_1h` (
  `os` STRING NULL,
  `app_version` STRING NULL,
  `device_model` STRING NULL,
  `connect_protocol` INT NULL,
  `device_firmware_version` STRING NULL,
  `avg_connect_retry_times` DOUBLE NULL,
  `total_connect` BIGINT NULL,
  `avg_first_frame_time` DOUBLE NULL,
  `max_first_frame_time` DOUBLE NULL,
  `record_time_window` TIMESTAMP(9) NOT NULL,
  `update_at` TIMESTAMP NULL,
  TIME INDEX (`record_time_window`),
  PRIMARY KEY (`os`, `app_version`,`device_model`, `connect_protocol`, `device_firmware_version`)
)
ENGINE=mito
WITH(
  ttl = '60d'
);
DROP FLOW IF EXISTS `live_connection_aggregation_speed_1h`;
CREATE FLOW live_connection_aggregation_speed_1h
SINK TO live_connection_statistics_speed_1h
EXPIRE AFTER INTERVAL '2 minutes'
AS 
SELECT 
  os,
  app_version,
  device_model, 
  connect_protocol,
  device_firmware_version,
  avg(connect_retry_times) AS avg_connect_retry_times, 
  count(connect_result) AS total_connect, 
  avg(first_frame_time) AS avg_first_frame_time, 
  max(first_frame_time) AS max_first_frame_time, 
  date_bin(INTERVAL '1 hour', record_time) AS record_time_window, 
FROM live_connection_log 
WHERE iot_online = 1 and connect_result = 1 and first_frame_time > 0 and first_frame_time < 60000
GROUP BY 
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;


DROP TABLE IF EXISTS `live_connection_statistics_common_1h`;
CREATE TABLE IF NOT EXISTS `live_connection_statistics_common_1h` (
  `os` STRING NULL,
  `app_version` STRING NULL,
  `device_model` STRING NULL,
  `connect_protocol` INT NULL,
  `connect_error` STRING NULL,
  `device_firmware_version` STRING NULL,
  `total_connect` BIGINT NULL,
  `record_time_window` TIMESTAMP(9) NOT NULL,
  `update_at` TIMESTAMP NULL,
  TIME INDEX (`record_time_window`),
  PRIMARY KEY (`os`, `app_version`, `device_model`, `connect_error`, `connect_protocol`, `device_firmware_version`)
)
ENGINE=mito
WITH(
  ttl = '60d'
);

DROP FLOW IF EXISTS `live_connection_aggregation_common_1h`;
CREATE FLOW live_connection_aggregation_common_1h
SINK TO live_connection_statistics_common_1h
EXPIRE AFTER INTERVAL '2 minutes'
AS
SELECT 
  os,
  app_version,
  device_model, 
  connect_protocol, 
  connect_error, 
  device_firmware_version,
  count(connect_protocol) AS total_connect, 
  date_bin(INTERVAL '1 hour', record_time) AS record_time_window, 
FROM live_connection_log 
WHERE iot_online = 1 and connect_result != 1
GROUP BY 
  os,
  app_version,
  device_model,
  connect_error, 
  connect_protocol,
  device_firmware_version,
  record_time_window;


DROP TABLE IF EXISTS `live_connection_statistics_first_frame_time_1h_v2`;
CREATE TABLE IF NOT EXISTS `live_connection_statistics_first_frame_time_1h_v2` (
  `os` STRING NULL,
  `app_version` STRING NULL,
  `device_model` STRING NULL,
  `connect_protocol` INT NULL,
  `avg_first_frame_time` DOUBLE NULL,
  `max_first_frame_time` DOUBLE NULL,
  `total_connect` BIGINT NULL,
  `buket0_connect` BIGINT NULL,
  `buket1_connect` BIGINT NULL,
  `buket2_connect` BIGINT NULL,
  `buket3_connect` BIGINT NULL,
  `buket4_connect` BIGINT NULL,
  `buket5_connect` BIGINT NULL,
  `buket6_connect` BIGINT NULL,
  `buket7_connect` BIGINT NULL,
  `buket8_connect` BIGINT NULL,
  `buket9_connect` BIGINT NULL,
  `buket10_connect` BIGINT NULL,
  `buket11_connect` BIGINT NULL,
  `record_time_window` TIMESTAMP(9) NOT NULL,
  `update_at` TIMESTAMP NULL,
  TIME INDEX (`record_time_window`),
  PRIMARY KEY (`os`, `app_version`,`device_model`, `connect_protocol`)
)
WITH(
  ttl = '60d'
);