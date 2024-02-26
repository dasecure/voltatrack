import streamlit as st
import pandas as pd
import math
import sqlite3
from streamlit_geolocation import streamlit_geolocation

def load_data(db_path):
    """
    Load data from SQLite database into a pandas DataFrame.

    Parameters:
    db_path (str): The path to the SQLite database.

    Returns:
    pandas.DataFrame: The loaded data with columns 'name', 'address', 'latitude', and 'longitude'.
    """
    conn = sqlite3.connect(db_path)
    query = '''
        SELECT name, streetAddress, city, state, zipCode, latitude, longitude
        FROM stations
    '''
    df = pd.read_sql_query(query, conn)
    df['address'] = df['streetAddress'] + ', ' + df['city'] + ', ' + df['state'] + ' ' + df['zipCode']
    return df[['name', 'address', 'latitude', 'longitude']]
    

def find_adjacent_coords(db, lat, lon, step):
    """
    Find adjacent coordinates within a given step range.

    Parameters:
    db (str): The path to the SQLite database.
    lat (float): The latitude of the current location.
    lon (float): The longitude of the current location.
    step (float): The step range for adjacent coordinates.

    Returns:
    pandas.DataFrame: The adjacent coordinates with columns 'name', 'address', 'latitude', 'longitude', and 'distance'.
    """
    conn = sqlite3.connect(db_path)
    coords_range = lat-step, lat+step, lon-step, lon+step
    result = conn.execute("""select name, streetAddress, city, state, zipCode, latitude, longitude from stations where latitude > ? and latitude < ? and longitude > ? and longitude < ?""", coords_range).fetchall()
    df = pd.DataFrame(result, columns=['name', 'streetAddress', 'city', 'state', 'zipCode', 'latitude', 'longitude'])
    df['distance'] = df.apply(lambda row: calculate_distance(lat, lon, row['latitude'], row['longitude']), axis=1).round(2)
    df.sort_values(by='distance', inplace=True)
    df['address'] = df['streetAddress'] + ', ' + df['city'] + ', ' + df['state'] + ' ' + df['zipCode']
    return df[['name', 'address', 'latitude', 'longitude','distance']]

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points using the Haversine formula.

    Parameters:
    lat1 (float): The latitude of the first point.
    lon1 (float): The longitude of the first point.
    lat2 (float): The latitude of the second point.
    lon2 (float): The longitude of the second point.

    Returns:
    float: The distance between the two points.
    """
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 3956  # Radius of Earth in kilometers. Use 3956 for miles
    return c * r

def main(db_path):
    """
    Main function to display the map in a Streamlit app.

    Parameters:
    db_path (str): The path to the SQLite database.
    """
    current_location = streamlit_geolocation()
    if current_location['latitude'] == None:
        current_location = {'latitude': 37.3688, 'longitude': -122.0363}
    
    st.title("Station Locations")
    df = find_adjacent_coords(db_path, current_location['latitude'], current_location['longitude'], 0.15)

    if not df.empty:
        st.map(df[['latitude', 'longitude']].head(3))
        st.table(df.head(3))
    else:
        st.write("No data available to plot.")

if __name__ == "__main__":
    db_path = 'stations.sqlite' 
    main(db_path)

