import mysql.connector
import json

# this is to connect the python file to our MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MySQL71622!",
    database="airtracker"
)  # this is connector to our SQL database with password

cursor = conn.cursor()
# this is the command executor, that executes our SQL commands (int str form) as actual SQL commands in our SQL database
print("Connected to MySQL!")

airports = [
    "MAA", "BLR", "DEL", "DXB",
    "SYD", "FRA", "JFK", "LHR",
    "MEL", "HKG", "SIN", "DOH"
]

# this is to insert items into the airports table in our SQL database
insert_sql = """
INSERT INTO airport_delays
(airport_icao, delay_date,
 arr_total_flights, arr_delayed_flights, arr_avg_delay_min, arr_median_delay_min, arr_canceled_flights,
 dep_total_flights, dep_delayed_flights, dep_avg_delay_min, dep_median_delay_min, dep_canceled_flights)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

for code in airports:
    with open(f"project/data/raw/delays/{code}_delays.json", "r") as f:
        data = json.load(f)

    delay_date = data.get("from", {}).get("utc")
    del_date = delay_date.split(" ")[0]

    arrival_data = data.get("arrivalsDelayInformation")
    departure_data = data.get("departuresDelayInformation")

    # to calculate delayed flights
    arr_numTotal = arrival_data.get("numTotal")
    arr_delayIndex = arrival_data.get("delayIndex")
    dep_numTotal = departure_data.get("numTotal")
    dep_delayIndex = departure_data.get("delayIndex")
    # calculation
    delayed_flights_arr = round(arr_numTotal * arr_delayIndex) if arr_delayIndex is not None else None
    delayed_flights_dep = round(dep_numTotal * dep_delayIndex) if dep_delayIndex is not None else None

    values = (
        data.get("airportIcao"),
        del_date,
        # info for arrivals
        arr_numTotal,
        delayed_flights_arr,
        arr_delayIndex,
        arrival_data.get("medianDelay"),
        arrival_data.get("numCancelled"),
        # info for departures
        dep_numTotal,
        delayed_flights_dep,
        dep_delayIndex,
        departure_data.get("medianDelay"),
        departure_data.get("numCancelled")
    )

    cursor.execute(insert_sql, values)

conn.commit()  # finally we perform commit() to actually make and save the changes in SQL database
cursor.close()  # close the cursor between python file and SQL database
conn.close()  # close the connection between python file and SQL database
print("Done inserting Airport Delays!")