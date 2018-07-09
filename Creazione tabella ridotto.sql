CREATE TABLE ridotto AS
SELECT device_id, DATE_FORMAT(`timestamp`, '%Y-%m-%d %H:%i:00') AS event_date, latitude, longitude
FROM dataset
WHERE DAY(`timestamp`) = 15 AND
latitude >= 44.99 AND
longitude >= 7.59 AND

latitude <= 45.13 AND
longitude <= 7.77
