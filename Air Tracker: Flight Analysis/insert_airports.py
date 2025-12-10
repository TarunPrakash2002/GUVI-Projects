import mysql.connector  # to connect a MySQL database
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

# this is to insert items into the airports table in our SQL database
insert_sql = """
INSERT INTO airports
(icao_code, iata_code, name, city, country, continent, latitude, longitude, timezone)
VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
 name = VALUES(name),
 city = VALUES(city),
 country = VALUES(country),
 continent = VALUES(continent),
 latitude = VALUES(latitude),
 longitude = VALUES(longitude),
 timezone = VALUES(timezone);
"""

airports = [
    "MAA", "BLR", "DEL", "DXB",
    "SYD", "FRA", "JFK", "LHR",
    "MEL", "HKG", "SIN", "DOH"
]

for code in airports:
    with open(f"project/data/raw/airports/{code}.json", "r") as f:
        data = json.load(f)

    values = (
        data.get("icao"),
        data.get("iata"),
        data.get("shortName"),
        data.get("municipalityName") or data.get("city"),
        data.get("country", {}).get("name"),
        data.get("continent", {}).get("name"),
        data.get("location", {}).get("lat"),
        data.get("location", {}).get("lon"),
        data.get("timeZone")
    )

    cursor.execute(insert_sql, values)

conn.commit()  # finally we perform commit() to actually make and save the changes in SQL database
cursor.close()  # close the cursor between python file and SQL database
conn.close()  # close the connection between python file and SQL database
print("Done inserting airports!")

