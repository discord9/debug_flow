-- validate the result of flow live_connection_aggregation_rate_1h
SELECT
  'Flow result of live_connection_statistics_rate_1h';

SELECT
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  avg_connect_retry_times,
  total_connect_result_ok,
  total_connect_result_fail,
  total_connect,
  conection_rate,
  record_time_window
FROM
  live_connection_statistics_rate_1h
ORDER BY
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;

SELECT
  'Direct query result of live_connection_statistics_rate_1h';

SELECT
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  avg(connect_retry_times) AS avg_connect_retry_times,
  sum(
    CASE
      WHEN connect_result = 1 THEN 1
      ELSE 0
    END
  ) AS total_connect_result_ok,
  sum(
    CASE
      WHEN connect_result = 0 THEN 1
      ELSE 0
    END
  ) AS total_connect_result_fail,
  count(connect_result) AS total_connect,
  arrow_cast(
    sum(
      CASE
        WHEN connect_result = 1 THEN 1
        ELSE 0
      END
    ),
    'Float64'
  ) / arrow_cast(count(connect_result), 'Float64') AS conection_rate,
  date_bin(INTERVAL '1 hour', record_time) AS record_time_window,
FROM
  live_connection_log
WHERE
  iot_online = 1
GROUP BY
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window
ORDER BY
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;

-- validate the result of flow live_connection_statistics_speed_1h
SELECT 'Flow result of live_connection_statistics_speed_1h';
SELECT
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  avg_connect_retry_times,
  total_connect,
  avg_first_frame_time,
  max_first_frame_time,
  record_time_window
FROM 
  live_connection_statistics_speed_1h
ORDER BY
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;

SELECT
  'Direct query result of live_connection_statistics_speed_1h';

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
  record_time_window
ORDER BY
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;

-- validate the result of flow live_connection_statistics_common_1h
SELECT 'Flow result of live_connection_statistics_common_1h';
SELECT 
  os,
  app_version,
  device_model,
  connect_protocol,
  connect_error,
  device_firmware_version,
  total_connect,
  record_time_window
FROM live_connection_statistics_common_1h
ORDER BY
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;

SELECT
  'Direct query result of live_connection_statistics_common_1h';
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
  record_time_window
ORDER BY
  os,
  app_version,
  device_model,
  connect_protocol,
  device_firmware_version,
  record_time_window;