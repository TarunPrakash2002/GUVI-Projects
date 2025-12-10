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
INSERT INTO flights
(flight_number, aircraft_registration, origin_iata, destination_iata,
 scheduled_departure, actual_departure, scheduled_arrival, actual_arrival,
 status, airline_code, is_cargo)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""

for code in airports:
    with open(f"project/data/raw/flights/{code}_combined.json", "r") as f:
        data = json.load(f)

    # Arrivals
    for flight1 in data.get("arrivals", []):
        arrival_values = (
            flight1.get("number"),
            flight1.get("aircraft", {}).get("reg"),
            flight1.get("movement", {}).get("airport", {}).get("iata"),
            code,
            None,
            None,
            flight1.get("movement", {}).get("scheduledTime", {}).get("utc"),
            flight1.get("movement", {}).get("revisedTime", {}).get("utc"),
            flight1.get("status"),
            flight1.get("airline", {}).get("iata"),
            flight1.get("isCargo")
        )

        cursor.execute(insert_sql, arrival_values)

    # Departures
    for flight2 in data.get("departures", []):
        departure_values = (
            flight2.get("number"),
            flight2.get("aircraft", {}).get("reg"),
            code,
            flight2.get("movement", {}).get("airport", {}).get("iata"),
            flight2.get("movement", {}).get("scheduledTime", {}).get("utc"),
            flight2.get("movement", {}).get("revisedTime", {}).get("utc"),
            None,
            None,
            flight2.get("status"),
            flight2.get("airline", {}).get("iata"),
            flight2.get("isCargo")
        )

        cursor.execute(insert_sql, departure_values)

conn.commit()  # finally we perform commit() to actually make and save the changes in SQL database
cursor.close()  # close the cursor between python file and SQL database
conn.close()  # close the connection between python file and SQL database
print("Done inserting flights!")


