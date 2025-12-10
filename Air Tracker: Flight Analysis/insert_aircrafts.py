import mysql.connector
import os  # os is to connect to the folder and retrieve the required files
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

# this is to insert items into the aircraft table in our SQL database
aircraft_path = f"project/data/raw/aircraft"

insert_sql = """
INSERT INTO aircraft
(registration, model, manufacturer, icao_type_code, owner)
VALUES (%s,%s,%s,%s,%s)
ON DUPLICATE KEY UPDATE
 model = VALUES(model),
 manufacturer = VALUES(manufacturer),
 icao_type_code = VALUES(icao_type_code),
 owner = VALUES(owner);
"""

for file in os.listdir(aircraft_path):  # os.listdir() lists all the folder in the file directory (here, aircraft_path)
    if file.endswith(".json"):
        path = os.path.join(aircraft_path, file)

        with open(path, "r") as f:
            data = json.load(f)

        type_name = data.get("typeName")
        manufacturer = type_name.split(" ")[0]

        values = (
            data.get("reg"),
            data.get("model"),
            manufacturer,
            data.get("icaoCode"),
            data.get("airlineName")
        )

        cursor.execute(insert_sql, values)


conn.commit()  # finally we perform commit() to actually make and save the changes in SQL database
cursor.close()  # close the cursor between python file and SQL database
conn.close()  # close the connection between python file and SQL database
print("Done inserting aircraft!")

