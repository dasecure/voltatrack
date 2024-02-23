import streamlit as st
import requests
import json
import time

# Assuming you've defined your API URL and headers as in the original script
url = 'https://api.voltaapi.com/v1/pg-graphql'
headers = {
    'authority': 'api.voltaapi.com',
    # Add the rest of your headers here
    'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv',  # Make sure to use your actual API key
}

location_node_ids = [
    "WyJzaXRlcyIsIjE4NThlZTRiLTA2ZDgtNGMzZC1iZDkwLWRmNWJjOWE2NmQwMiJd",
    "WyJzaXRlcyIsImEyYmQzZWMyLTNmMDEtNGZiOS1iNTM4LTU2OWEzNTY0NzM5MCJd",
    "WyJzaXRlcyIsIjEzOTMyMGNiLTRjMzQtNGVjMC04OTAwLTJkNDgxZWE5MzMwMSJd"
    # Add more Node IDs here as strings
]

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

import streamlit as st

def display_title():
    # Get the current state
    state = st.session_state.get('title_state', True)

    with placeholder1.container():
        if state:
            st.title(':blue[Volta] Charging Tracker')
        else:
            st.title(':green[Volta] Charging Tracker')

    # Toggle the state
    st.session_state['title_state'] = not state


def display_stations():
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
                    st.write(f"{name} Station #: {station_number} Status: {state}")
                else:
                    st.write(f"Station #: {station_number} has no EVSEs.")
                    
# st.title('Volta :blue Charging Tracker')
placeholder1 = st.empty()
placeholder = st.empty()

# poll display_stations with a variable seconds interval, interval can be incremented or decremented
interval = st.slider('Polling Interval', min_value=1, max_value=10, value=2)
poll = st.checkbox('Poll Stations', value=True)
while poll:
    display_title()
    display_stations()
    time.sleep(interval)
    if poll == False:
        break  