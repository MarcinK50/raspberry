CREATE TABLE 'config' (
  id INT,
  lat DOUBLE,
  lon DOUBLE,
  location STRING,
  description STRING
);
CREATE TABLE 'sensors' (
  timestamp TIMESTAMP,
  id INT,
  temperature DOUBLE,
  humidity DOUBLE,
  pm1 INT,
  pm25 INT,
  pm10 INT
) timestamp (timestamp) PARTITION BY MONTH WAL;

CREATE TABLE 'log' (id INT, timestamp TIMESTAMP, code INT, message STRING);