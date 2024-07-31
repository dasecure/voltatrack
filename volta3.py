import streamlit as st
import pandas as pd
import math
import sqlite3
import requests
import json
import time
from streamlit_geolocation import streamlit_geolocation
from auth import create_users_table, login_page, signup_page, logout, get_current_user

# Globals
default_location = {
        'latitude': 37.352683,
        'longitude': -122.051426
    }
display_list = []

def handle_location_click(location):
    st.session_state.clicked_location = location
    current_user = get_current_user()
    if current_user:
        st.success(f"User {current_user} clicked on location: {location}")
    else:
        st.warning("No user is currently logged in.")

# Create users table if it doesn't exist
create_users_table()

# get station data
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

#function to retrieve charging state of stations
def get_stations_with_charging_state(location_node_id):
    data = get_stations_data(location_node_id)
    stations_data = data['data']['locationByNodeId']['stationsByLocationId']['edges']
    station_name = data['data']['locationByNodeId']['name']
    for station in stations_data:
        station_node = station['node']
        charging_states = [evse['node']['state'] for evse in station_node['evses']['edges']]
        colored_states = []
        for state in charging_states:
            if state == 'PLUGGED_OUT':
                colored_states.append(':green[PLUGGED_OUT]')
            elif state in ['PLUGGED_IN', 'IDLE']:
                colored_states.append(':orange[' + state + ']')
            elif state == 'CHARGING':
                colored_states.append(':red[CHARGING]')
            else:
                colored_states.append(state)
        display_list.append({
            "Location": station_node['name'],
            "Charger#": station_node['stationNumber'],
            "State": colored_states
        })

    return

# Function to calculate distance between two points using Haversine formula
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c

def display_title():
    # Get the current state
    state = st.session_state.get('title_state', True)
    st.title("Volta Tagger")
    # with placeholder1.container():
    #     if state:
    #         st.title(':red[Volta] Charging Tracker - v0.01b')
    #     else:
    #         st.title(':green[Volta] Charging Tracker - v0.01b')

    # Toggle the state
    st.session_state['title_state'] = not state

def get_current_location():
    current_location = streamlit_geolocation()
    # current location is default if location is not available
    if current_location['latitude'] == None:
        current_location = default_location
    return current_location

def main():
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if not st.session_state['logged_in']:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            login_page()
        with tab2:
            signup_page()
    else:
        # Display the title
        display_title()

        st.sidebar.title("Options")
        with st.sidebar:
            st.write("Select the maximum distance to search for nearby stations:")
            max_distance = st.slider("Maximum Distance (km)",  min_value=2, max_value=10, value=4, step=2)
            if st.button("Logout"):
                logout()

        # Connect to your SQLite database
        conn = sqlite3.connect('stations.sqlite')
        cursor = conn.cursor()

        currentLoc = get_current_location()
    
        current_lat = currentLoc['latitude']
        current_lon = currentLoc['longitude']

        # Query to fetch all stations
        cursor.execute("SELECT nodeId, name, latitude, longitude FROM stations")
        all_stations = cursor.fetchall()

        # Filter stations within the specified distance
        nearby_stations = []
        for station in all_stations:
            node_id, name, lat, lon = station
            if lat is not None and lon is not None:
                distance = haversine_distance(current_lat, current_lon, float(lat), float(lon))
                if distance <= max_distance:
                    nearby_stations.append((node_id, name, distance))

        # Sort the nearby stations by distance
        nearby_stations.sort(key=lambda x: x[2])

        # Print the results
        for station in nearby_stations:
            get_stations_with_charging_state(station[0])
        
        # Create a DataFrame
        df = pd.DataFrame(display_list)
        
        # Display the DataFrame with buttons
        for index, row in df.iterrows():
            if st.button(f"Location: {row['Location']}", key=f"location_button_{index}"):
                handle_location_click(row['Location'])
        
        # Display clicked location information
        if 'clicked_location' in st.session_state:
            st.write("---")
            st.write("Clicked Location Information:")
            clicked_row = df[df['Location'] == st.session_state.clicked_location].iloc[0]
            st.write(f"Location: {clicked_row['Location']}")
            st.write(f"Charger#: {clicked_row['Charger#']}")
            st.write("State:")
            for state in clicked_row['State']:
                st.markdown(state)
        
        # Close the database connection

        conn.close()

if __name__ == "__main__":
    main()
