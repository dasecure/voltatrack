# Search bar for address 

# After address lookup SELECT and DISPLAY in a dataframe

# Choose selection and display the status

# Multiple selection is possible

# Create a favorites list, SQLITE

# Display a map? or is Distance sufficient?

# Create routine to retrieve state of stations with just nodeId

# Poll for state, interval

# notify user on state change, SQLITE or session_state

# Push over equivalent project? or use Twilio for now

# Add logo, copyright info, credits etc

# encapsulate into raspberry pi 5

import streamlit as st
import requests
import json
import pandas as pd
import time
import sqlite3
import math
from streamlit_geolocation import streamlit_geolocation

default_location = {'latitude': 37.3688, 'longitude': -122.0363}
# current_location = default_location

def add_footer():
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <div class="footer">
            <p>Made with ❤️ by Vincent 2024. Donate is useful</p>
        </div>
        """,
        unsafe_allow_html=True)

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
    result = conn.execute("""select nodeId, name, streetAddress, city, state, zipCode, latitude, longitude from stations where latitude > ? and latitude < ? and longitude > ? and longitude < ?""", coords_range).fetchall()
    df = pd.DataFrame(result, columns=['nodeId','name', 'streetAddress', 'city', 'state', 'zipCode', 'latitude', 'longitude'])
    df['distance'] = df.apply(lambda row: calculate_distance(lat, lon, row['latitude'], row['longitude']), axis=1).round(2)
    df.sort_values(by='distance', inplace=True)
    # update charging state with get_stations_with_charging_state and add to df
    # df['charging_state'] = df.apply(lambda row: get_stations_with_charging_state(row['nodeId']), axis=1)
    # df['charging'] = df['charging_state'].apply(lambda x: 'Charging' if 'CHARGING' in x else 'Not Charging')    
    df['address'] = df['streetAddress'] + ', ' + df['city'] + ', ' + df['state'] + ' ' + df['zipCode']
    
    return df[['nodeId','name', 'address', 'latitude', 'longitude','distance',]]

# Function to get stations data
def get_stations_data(location_node_id):
    # API endpoint
    url = 'https://api.voltaapi.com/v1/pg-graphql'

    # Headers
    headers = {
        'authority': 'api.voltaapi.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://voltacharging.com',
        'referer': 'https://voltacharging.com/',
        'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv'
    }

    # GraphQL query and variables
    data = {
        "query": """
            query getStation($locationNodeId: ID!) {
              locationByNodeId(nodeId: $locationNodeId) {
              name
                stationsByLocationId(orderBy: STATION_NUMBER_ASC) {
                  edges {
                    node {
                      id
                      stationNumber
                      name
                      evses {
                        edges {
                          node {
                            state
                          }
                        }
                      }
                    }
                  }
                }
              }
            }
        """,
        "variables": {
            "locationNodeId": location_node_id
        }
    }

    # Making the POST request
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def get_stations_with_charging_state(location_node_id):
    data = get_stations_data(location_node_id)
    stations_data = data['data']['locationByNodeId']['stationsByLocationId']['edges']
    stations_list = []
    station_name = data['data']['locationByNodeId']['name']
    for station in stations_data:
        station_node = station['node']
        charging_states = [evse['node']['state'] for evse in station_node['evses']['edges']]
        stations_list.append({
            "name": station_name,
            "node_name": station_node['name'],
            "stationNumber": station_node['stationNumber'],
            "charging_states": charging_states
        })
    df_stations = pd.DataFrame(stations_list)
    df_expanded = df_stations.explode('charging_states')
    df_expanded.reset_index(drop=True, inplace=True)
    update_stationsDB(df_stations)
    # print(df_expanded)
    # print (df_stations)
    return df_expanded

def update_stationsDB(df_stations):
    # Connect to the SQLite database
    conn = sqlite3.connect('stations.sqlite')
    cursor = conn.cursor()

    # Ensure there's a 'charging' column in your 'stations' table; if not, you may need to add it
    # cursor.execute('''ALTER TABLE stations ADD COLUMN charging TEXT''')

    # Update database based on DataFrame
    chargers = []
    for index, row in df_stations.iterrows():
        chargers.append(row['charging_states'][0])
    # print(chargers)    
    cursor.execute('''UPDATE stations SET charging = ? WHERE name = ?''', (', '.join(chargers), row['name']))

    # Commit changes and close connection
    conn.commit()
    conn.close()

# main function
def main(db_path):
    # Set up the sidebar
    current_location = streamlit_geolocation()
    if current_location['latitude'] == None:
        current_location = default_location
        df = find_adjacent_coords(db_path, current_location['latitude'], current_location['longitude'], 0.05)
    else:
        df = find_adjacent_coords(db_path, current_location['latitude'], current_location['longitude'], 0.05)

    df['distance'] = df['distance'].round(1)

    # show location of station and respective stations with their charging state
    with st.container():
        combined_df = pd.DataFrame()
        for station in df['nodeId']:
            temp = get_stations_with_charging_state(station)
            combined_df = pd.concat([combined_df, temp])
        merged_df = pd.merge(df, combined_df, on='name', how='inner')
        st.write(merged_df[['node_name', 'charging_states', 'distance']].head(locCount))

    add_footer()

if __name__ == "__main__":
    # Global stuff
    with st.sidebar:
        # st.title("Search address:")
        # add_searchbar = st.text_input("Search address")
        locCount = st.selectbox(
            "How many locations?",
            (2, 4, 8, 10), key = "location_count"
        )
        interval = st.slider(
            'Polling Interval', min_value=1, max_value=10, value=2)
        # add_distance = st.slider(
        #     'Search radius (miles)', min_value=2, max_value=10, value=2, step=1)
        poll = st.checkbox(
            'Poll?', value=True)
    # Assuming you've defined your API URL and headers as in the original script
    url = 'https://api.voltaapi.com/v1/pg-graphql'
    headers = {
        'authority': 'api.voltaapi.com',
        # Add the rest of your headers here
        'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv',  # Make sure to use your actual API key
    }
    # st.title(':blue[Volta] Charging Stations')
    db_path = 'stations.sqlite' 
    # This is the main routine
    # while poll:
    #   main(db_path)
    #   time.sleep(interval)
    #   if poll == False:
    #       break  
    main(db_path)
