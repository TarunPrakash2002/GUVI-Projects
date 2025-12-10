**AirTracker — Flight, Airport & Delay Analytics Dashboard**

AirTracker is a complete end-to-end data and visualization project built using Python, MySQL, and Streamlit.
It automates the ingestion of real-world aviation datasets, stores them in a structured relational database, and provides an interactive dashboard to explore insights about flights, airports, aircraft, and delays.

**Features of the Application**

1. Home Dashboard

Shows:
	•	Total number of airports
	•	Total number of flights
	•	Average delay across all airports

2. Search and Filter Flights

Users can filter flights by:
	•	Flight number
	•	Airline code
	•	Status

The results appear in a data table.

3. Airport Details Viewer

For any chosen airport, the app displays:
	•	Airport information
	•	Outbound flights
	•	Arriving flights
	•	A map showing airport location

4. Delay Analysis

Shows delay statistics for arrivals and departures, including:
	•	Total flights
	•	Estimated delayed flights
	•	Median delay
	•	Average delay

5. Route Leaderboards

Provides insights on:
	•	The busiest flight routes
	•	Airports with the highest number of delays

6. Aviation Data Visualisation

A section containing all the SQL analysis queries used in the project, such as:
	•	Flights per aircraft model
	•	Aircraft with more than five flights
	•	Airports with no arrivals
	•	Domestic vs international classification
	•	Delay percentages per destination
	•	Cancelled flights
and several others.

**Database Structure**

The database contains the following tables:
	•	airports – airport location and identity details
	•	aircraft – aircraft registration and model information
	•	flights – flight-level arrival and departure details
	•	airport_delays – delay summaries for each airport

All tables were created in MySQL and populated using Python scripts.

**Technologies Used**
	•	Python
	•	Streamlit
	•	MySQL
	•	Pandas
	•	JSON data parsing

**What I Learned**

Through this project I learned:
	•	How to parse large JSON datasets
	•	How to design SQL schemas
	•	How to write insert scripts and handle missing data
	•	How to run analytical SQL queries
	•	How to build a Streamlit dashboard connected to a live database
	•	How to visualise aviation data in a clean and structured format
