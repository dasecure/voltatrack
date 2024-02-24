import json
import sqlite3

# Function to load JSON data
def load_json_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to create SQLite database and table
def setup_database(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stations (
            nodeId TEXT PRIMARY KEY,
            name TEXT,
            streetAddress TEXT,
            city TEXT,
            state TEXT,
            zipCode TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    return conn, cursor

# Function to insert data into the database
def insert_data(cursor, data):
    for item in data['data']['locations']['edges']:
        node = item['node']
        geolocation_json = json.loads(node['stationsByLocationId']['geolocationCentroid']['geojson'])
        latitude, longitude = geolocation_json['coordinates'][1], geolocation_json['coordinates'][0]

        cursor.execute('''
            INSERT INTO stations (nodeId, name, streetAddress, city, state, zipCode, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (node['nodeId'], node['name'], node['streetAddress'], node['city'], node['state'], node['zipCode'], latitude, longitude))

# Main function to orchestrate the JSON loading and database operations
def main(json_file_path, db_path):
    data = load_json_data(json_file_path)
    conn, cursor = setup_database(db_path)
    insert_data(cursor, data)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    json_file_path = 'allStations.json'  # Update this path
    db_path = 'stations.sqlite'  # Update this path
    main(json_file_path, db_path)
