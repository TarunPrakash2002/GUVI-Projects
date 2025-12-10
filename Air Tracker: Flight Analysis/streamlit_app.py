import streamlit as st
import mysql.connector
import pandas as pd


# Database Connection
def sql_run_query(query_main, param=None):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MySQL71622!",
        database="airtracker"
    )

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query_main, param or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


st.set_page_config(page_title="AirTracker Dashboard", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["Home Dashboard",
     "Search and Filter Flights",
     "Airport Details Viewer",
     "Delay Analysis",
     "Route Leaderboards",
     "Aviation Data Visualisation"]
)

# Home Dashboard
if page == "Home Dashboard":
    st.title("AirTracker – Flight & Airport Analysis Dashboard")

    # Total Airports
    total_airports = sql_run_query("SELECT COUNT(*) AS c FROM airports")[0]["c"]

    # Total Flights
    total_flights = sql_run_query("SELECT COUNT(*) AS c FROM flights")[0]["c"]

    # Average Delay
    avg_delay = sql_run_query("""
        SELECT AVG(arr_avg_delay_min) AS avg_delay
        FROM airport_delays
    """)[0]["avg_delay"]

    st.subheader("Summary Statistics")
    st.write(f"Total Airports: **{total_airports}**")
    st.write(f"Total Flights: **{total_flights}**")
    st.write(f"Average Delay: **{avg_delay:.2f} minutes**")

# Search and filter flights
elif page == "Search and Filter Flights":
    st.title("Search and Filter Flights")

    search_number = st.text_input("Search by Flight Number")
    airline_filter = st.text_input("Filter by Airline Code (e.g., AI, EK)")
    status_filter = st.selectbox("Filter by Status", ["Unknown", "Departed", "Expected", "Cancelled", "Delayed"])

    query = "SELECT * FROM flights WHERE 1=1"
    params = []

    if search_number:
        query += " AND flight_number = %s"
        params.append(search_number)

    if airline_filter:
        query += " AND airline_code = %s"
        params.append(airline_filter)

    if status_filter:
        query += " AND status = %s"
        params.append(status_filter)

    results = sql_run_query(query, params)

    st.write("Results")
    st.dataframe(pd.DataFrame(results))

# Airport info
elif page == "Airport Details Viewer":
    st.title("Airport Details Viewer")

    airports = sql_run_query("SELECT iata_code FROM airports")
    airport_list = [a["iata_code"] for a in airports]

    selected_airport = st.selectbox("Choose an airport", airport_list)

    if selected_airport:
        info = sql_run_query(
            "SELECT * FROM airports WHERE iata_code = %s",
            (selected_airport,)
        )
        flights_from = sql_run_query(
            "SELECT * FROM flights WHERE origin_iata = %s",
            (selected_airport,)
        )
        flights_to = sql_run_query(
            "SELECT * FROM flights WHERE destination_iata = %s",
            (selected_airport,)
        )

        st.subheader("Airport Information")
        st.write(pd.DataFrame(info))

        st.subheader("Outbound Flights")
        st.dataframe(pd.DataFrame(flights_from))

        st.subheader("Arriving Flights")
        st.dataframe(pd.DataFrame(flights_to))

        # Airport Map: My Addition
        st.subheader("Airport Location Map")

        airport_info = sql_run_query(
            "SELECT name, latitude, longitude FROM airports WHERE iata_code = %s",
            (selected_airport,)
        )

        airport_df = pd.DataFrame(airport_info)

        if not airport_df.empty and airport_df["latitude"].notnull().all():
            st.map(airport_df, latitude="latitude", longitude="longitude")
        else:
            st.write("No map data available for this airport.")

# Delay analysis
elif page == "Delay Analysis":
    st.title("Airport Delay Analysis")

    delay_data = sql_run_query("SELECT * FROM airport_delays")
    df = pd.DataFrame(delay_data)

    st.subheader("Arrival Delay Overview")
    st.dataframe(df[[
        "airport_icao", "arr_total_flights", "arr_delayed_flights",
        "arr_avg_delay_min", "arr_median_delay_min"
    ]])

    st.subheader("Departure Delay Overview")
    st.dataframe(df[[
        "airport_icao", "dep_total_flights", "dep_delayed_flights",
        "dep_avg_delay_min", "dep_median_delay_min"
    ]])

# Route Leaderboards
elif page == "Route Leaderboards":
    st.title("Route Leaderboards")

    # Busiest routes
    busiest = sql_run_query("""
        SELECT origin_iata, destination_iata, COUNT(*) AS flights
        FROM flights
        GROUP BY origin_iata, destination_iata
        ORDER BY flights DESC
        LIMIT 10;
    """)

    st.subheader("Top 10 Busiest Routes")
    st.dataframe(pd.DataFrame(busiest))

    # Most delayed airports
    delayed = sql_run_query("""
        SELECT 
            airport_icao,
            (arr_delayed_flights + dep_delayed_flights) AS total_delays
        FROM airport_delays
        ORDER BY total_delays DESC
        LIMIT 10;
    """)

    st.subheader("Most Delayed Airports")
    st.dataframe(pd.DataFrame(delayed))

# SQL queries - custom data
elif page == "Aviation Data Visualisation":
    st.title("Custom Aviation Data – All SQL Queries")

    query_options = {
        # Query 1
        "Flights per aircraft model": """
        SELECT 
            a.model,
            COUNT(f.flight_id) AS flight_count
        FROM flights f
        LEFT JOIN aircraft a ON f.aircraft_registration = a.registration
        GROUP BY a.model;
        """,

        # Query 2
        "Aircraft with > 5 assigned flights": """
        SELECT 
            f.aircraft_registration,
            a.model,
            COUNT(*) AS flight_count
        FROM flights f
        LEFT JOIN aircraft a ON f.aircraft_registration = a.registration
        GROUP BY f.aircraft_registration, a.model
        HAVING COUNT(*) > 5;
        """,

        # Query 3
        "Airports with > 5 outbound flights": """
        SELECT 
            ap.name AS airport_name,
            COUNT(f.flight_id) AS outbound_flights
        FROM flights f
        JOIN airports ap 
            ON f.origin_iata = ap.iata_code
        GROUP BY ap.name
        HAVING outbound_flights > 5;
        """,

        # Query 4
        "Top 3 destination airports": """
        SELECT 
            ap.name,
            ap.city,
            COUNT(f.flight_id) AS arrivals
        FROM flights f
        JOIN airports ap 
            ON f.destination_iata = ap.iata_code
        GROUP BY ap.name, ap.city
        ORDER BY arrivals DESC
        LIMIT 3;
        """,

        # Query 5
        "Domestic vs International flights": """
        SELECT 
            f.flight_number,
            f.origin_iata,
            f.destination_iata,
            CASE 
                WHEN ap1.country = ap2.country THEN 'Domestic'
                ELSE 'International'
            END AS flight_type
        FROM flights f
        JOIN airports ap1 ON f.origin_iata = ap1.iata_code
        JOIN airports ap2 ON f.destination_iata = ap2.iata_code;
        """,

        # Query 6
        "Last 5 arrivals at DEL": """
        SELECT 
            f.flight_number,
            f.aircraft_registration,
            ap.name AS departure_airport,
            f.scheduled_arrival
        FROM flights f
        JOIN airports ap 
            ON f.origin_iata = ap.iata_code
        WHERE f.destination_iata = 'DEL'
        ORDER BY f.scheduled_arrival DESC
        LIMIT 5;
        """,

        # Query 7
        "Airports with no arriving flights": """
        SELECT 
            ap.name,
            ap.iata_code
        FROM airports ap
        LEFT JOIN flights f 
            ON ap.iata_code = f.destination_iata
        WHERE f.destination_iata IS NULL;
        """,

        # Query 8
        "Flight status count by airline": """
        SELECT 
            f.airline_code,
            SUM(CASE WHEN f.status = 'On Time' THEN 1 ELSE 0 END) AS on_time,
            SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) AS delayed_fl,
            SUM(CASE WHEN f.status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled
        FROM flights f
        GROUP BY f.airline_code;
        """,

        # Query 9
        "All cancelled flights (latest first)": """
        SELECT 
            f.flight_number,
            f.aircraft_registration,
            ap1.name AS origin_airport,
            ap2.name AS destination_airport,
            f.scheduled_departure
        FROM flights f
        JOIN airports ap1 ON f.origin_iata = ap1.iata_code
        JOIN airports ap2 ON f.destination_iata = ap2.iata_code
        WHERE f.status LIKE '%Cancel%'
        ORDER BY f.scheduled_departure DESC;
        """,

        # Query 10
        "City pairs with >2 aircraft models": """
        SELECT 
            f.origin_iata,
            f.destination_iata,
            COUNT(DISTINCT a.model) AS unique_models
        FROM flights f
        JOIN aircraft a 
            ON f.aircraft_registration = a.registration
        GROUP BY f.origin_iata, f.destination_iata
        HAVING unique_models > 2;
        """,

        # Query 11
        "% delayed flights by destination airport": """
        SELECT 
            ap.name,
            ap.iata_code,
            ROUND(
                100 * SUM(CASE WHEN f.status = 'Delayed' THEN 1 ELSE 0 END) 
                / COUNT(f.flight_id), 2
            ) AS delay_percentage
        FROM flights f
        JOIN airports ap 
            ON f.destination_iata = ap.iata_code
        GROUP BY ap.name, ap.iata_code
        ORDER BY delay_percentage DESC;
        """
    }

    selected_query = st.selectbox("Choose a SQL analysis query:", list(query_options.keys()))

    if selected_query:
        sql = query_options[selected_query]
        result = sql_run_query(sql)
        st.subheader(selected_query)
        st.dataframe(pd.DataFrame(result))