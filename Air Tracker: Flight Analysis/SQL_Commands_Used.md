**SQL Commands Used** 
1. To create the database:
   
   CREATE DATABASE IF NOT EXISTS airtracker;
   USE airtracker;

   SHOW DATABASES LIKE 'airtracker';
   SHOW TABLES;

2. To create tables in the database:

   USE AirTracker;

   CREATE TABLE airports(
	  airport_id Integer AUTO_INCREMENT primary key,
    icao_code VARCHAR(10) UNIQUE,
    iata_code VARCHAR(10) UNIQUE,
    name VARCHAR(255),
    city VARCHAR(255),
    country VARCHAR(255),
    continent VARCHAR(255),
    latitude REAL,
    longitude REAL,
    timezone VARCHAR(100)
   );

   CREATE TABLE aircraft(
	  aircraft_id Integer AUTO_INCREMENT primary key,
    registration VARCHAR(20) UNIQUE,
    model VARCHAR(255),
    manufacturer VARCHAR(255),
    icao_type_code VARCHAR(20),
    owner VARCHAR(255)
   );

   CREATE TABLE flights (
    flight_id INT PRIMARY KEY AUTO_INCREMENT, 
    flight_number VARCHAR(20),
    aircraft_registration VARCHAR(20),
    origin_iata VARCHAR(10),
    destination_iata VARCHAR(10),
    scheduled_departure TEXT,
    actual_departure TEXT,
    scheduled_arrival TEXT,
    actual_arrival TEXT,
    status VARCHAR(20),
    airline_code VARCHAR(10),
    is_cargo BOOLEAN
   );

   CREATE TABLE airport_delays (
    delay_id INT PRIMARY KEY AUTO_INCREMENT,
    airport_icao VARCHAR(10),
    delay_date VARCHAR(30),
    
    arr_total_flights INT,
    arr_delayed_flights INT,
    arr_avg_delay_min FLOAT,
    arr_median_delay_min VARCHAR(30),
    arr_canceled_flights INT,
    
    dep_total_flights INT,
    dep_delayed_flights INT,
    dep_avg_delay_min FLOAT,
    dep_median_delay_min VARCHAR(30),
    dep_canceled_flights INT
   );

   SHOW tables;

3. To update the flights table data for betterment of data tables:

   SET SQL_SAFE_UPDATES = 0;  # safe updates prevents me from making some changes for data safety

   USE airtracker;

   UPDATE flights
   SET actual_arrival = scheduled_arrival
   WHERE actual_arrival IS NULL;

   UPDATE flights
   SET actual_departure = scheduled_departure
   WHERE actual_departure IS NULL;

   SET SQL_SAFE_UPDATES = 1;  # i reset the safe update back for safety of data in further progress
