import streamlit as st
import pandas as pd
import math
import sqlite3
import requests
import json
import time
import getLocations as gl
from streamlit_geolocation import streamlit_geolocation

def getNodes(distance):
    newLocation = []
    newLocation = streamlit_geolocation()
    if newLocation == []:
        retValues = gl.getLocationWithin(distance, gl.current_coords)
    else:
        newPos = (newLocation['latitude'], newLocation['longitude'])
        retValues = gl.getLocationWithin(distance, newPos)

    location_node_ids = []
    for location in retValues:
        location_node_ids.append(location['nodeId'])
    return location_node_ids
# if newLocation == []:
#   retValues = gl.getLocationWithin(distance, gl.current_coords)
# else:
#   newPos = (newLocation['latitude'], newLocation['longitude'])
#   retValues = gl.getLocationWithin(distance, newPos)

# location_node_ids = []
# for location in retValues:
#     location_node_ids.append(location['nodeId'])

# location_node_ids = [
#     "WyJzaXRlcyIsIjE4NThlZTRiLTA2ZDgtNGMzZC1iZDkwLWRmNWJjOWE2NmQwMiJd",
#     "WyJzaXRlcyIsImEyYmQzZWMyLTNmMDEtNGZiOS1iNTM4LTU2OWEzNTY0NzM5MCJd",
#     "WyJzaXRlcyIsIjEzOTMyMGNiLTRjMzQtNGVjMC04OTAwLTJkNDgxZWE5MzMwMSJd", # Los Angeles, CA
#     # Add more Node IDs here as strings
# ]



def fetch_station_data(location_node_id):
    data = {
        "query": """
        query getStation($locationNodeId: ID!) {
          locationByNodeId(nodeId: $locationNodeId) {
            stationsByLocationId(orderBy: STATION_NUMBER_ASC) {
              geolocationCentroid {
                latitude
                longitude
              }
              edges {
                node {
                  name
                  stationNumber
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
        "variables": {"locationNodeId": location_node_id}
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

# if the charging state changes, notify the user with a sound
# https://stackoverflow.com/questions/16573051/sound-alarm-when-code-finishes

def display_title():
    # Get the current state
    state = st.session_state.get('title_state', True)

    with placeholder1.container():
        if state:
            st.title(':red[Volta] Charging Tracker - v0.01b')
        else:
            st.title(':green[Volta] Charging Tracker - v0.01b')

    # Toggle the state
    st.session_state['title_state'] = not state

def getColor(state):
    if state == 'PLUGGED_OUT' or state == 'IDLE':
        return ':green'
    elif state == 'CHARGING':
        return ':red'
    else:
        return ':orange'

def display_stations(location_node_ids):
    stations = []
    for node_id in location_node_ids:
        data = fetch_station_data(node_id)
        # Process and display your data here
        # For simplicity, we're just adding it to a list
        stations.append(data)
    
    # show location of station and respective stations with their charging state
    with placeholder.container():
        for station in stations:
            for location in station['data']['locationByNodeId']['stationsByLocationId']['edges']:
                node = location['node']
                name = node['name']
                station_number = node['stationNumber']
                # print(f"Location Node ID: {location_node_id}")
                # Assuming each station has at least one EVSE and we are interested in the first one
                if node['evses']['edges']:
                    state = node['evses']['edges'][0]['node']['state']
                    color_code = getColor(state)
                    state = f"{color_code}[{state}]"
                    st.write(f"{name} Station #: {station_number} Status: {state}")
                else:
                    st.write(f"Station #: {station_number} has no EVSEs.")
                    

placeholder1 = st.empty()
placeholder = st.empty()

def main(db_path, stations, poll, interval, dist):

  # poll display_stations with a variable seconds interval, interval can be incremented or decremented

  while poll:
      display_title()
      display_stations(getNodes(dist))
      time.sleep(interval)
      if poll == False:
          break  
      
  # Assuming you've defined your API URL and headers as in the original script
  url = 'https://api.voltaapi.com/v1/pg-graphql'
  headers = {
      'authority': 'api.voltaapi.com',
      # Add the rest of your headers here
      'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv',  # Make sure to use your actual API key
  }


if __name__ == "__main__":
# Assuming you've defined your API URL and headers as in the original script
    url = 'https://api.voltaapi.com/v1/pg-graphql'
    headers = {
        'authority': 'api.voltaapi.com',
        # Add the rest of your headers here
        'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv',  # Make sure to use your actual API key
    }
    # Using object notation
    add_stations = st.sidebar.selectbox(
        "How many stations do you want to find?",
        (5, 10, 15)
    )

    # Using "with" notation
    with st.sidebar:
        add_interval = st.slider('Polling Interval', min_value=1, max_value=10, value=2)
        add_poll = st.checkbox('Poll Stations', value=True)
        add_distance = st.slider('Search radius', min_value=2, max_value=10, value=2, step=2)
    
    db_path = 'stations.sqlite' 
    main(db_path, add_stations, add_poll, add_interval, add_distance)
