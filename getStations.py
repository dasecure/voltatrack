import requests
import json
# import plotly.graph_objects as go
# import pandas as pd

# mapbox_access_token = 'your_mapbox_access_token'

# Define the locationNodeIds as a list of variables
location_node_ids = [
    "WyJzaXRlcyIsIjE4NThlZTRiLTA2ZDgtNGMzZC1iZDkwLWRmNWJjOWE2NmQwMiJd",
    "WyJzaXRlcyIsImEyYmQzZWMyLTNmMDEtNGZiOS1iNTM4LTU2OWEzNTY0NzM5MCJd"
    # Add more Node IDs here as strings
]

url = 'https://api.voltaapi.com/v1/pg-graphql'

headers = {
    'authority': 'api.voltaapi.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://voltacharging.com',
    'referer': 'https://voltacharging.com/',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv',
}

for location_node_id in location_node_ids:
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
    response_data = response.json()

    # Iterate through the response data to print locationNodeId, latitude, and longitude, station numbers and states for each location
    try:
        longitude = response_data['data']['locationByNodeId']['stationsByLocationId']['geolocationCentroid']['longitude']
        latitude = response_data['data']['locationByNodeId']['stationsByLocationId']['geolocationCentroid']['latitude']
        print(f"Location Node ID: {location_node_id} Latitude: {latitude} Longitude: {longitude}")
        for edge in response_data['data']['locationByNodeId']['stationsByLocationId']['edges']:
            node = edge['node']
            name = node['name']
            station_number = node['stationNumber']
            # print(f"Location Node ID: {location_node_id}")
            # Assuming each station has at least one EVSE and we are interested in the first one
            if node['evses']['edges']:
                state = node['evses']['edges'][0]['node']['state']
                print(f"{name} Station #: {station_number} Status: {state}")
            else:
                print(f"Station #: {station_number} has no EVSEs.")
    except KeyError as e:
        print(f"Error processing response data for Node ID {location_node_id}: {e}")

    # add the stations longitude and latitude to a list and plot them on a map

def get_all_stations():
    stations = []
    for location_node_id in location_node_ids:
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
        response_data = response.json()

        # Iterate through the response data to print locationNodeId, latitude, and longitude, station numbers and states for each location
        try:
            longitude = response_data['data']['locationByNodeId']['stationsByLocationId']['geolocationCentroid']['longitude']
            latitude = response_data['data']['locationByNodeId']['stationsByLocationId']['geolocationCentroid']['latitude']
            print(f"Location Node ID: {location_node_id} Latitude: {latitude} Longitude: {longitude}")
            for edge in response_data['data']['locationByNodeId']['stationsByLocationId']['edges']:
                node = edge['node']
                name = node['name']
                station_number = node['stationNumber']
                # print(f"Location Node ID: {location_node_id}")
                # Assuming each station has at least one EVSE and we are interested in the first one
                if node['evses']['edges']:
                    state = node['evses']['edges'][0]['node']['state']
                    print(f"{name} Station #: {station_number} Status: {state}")
                    stations.append({
                        'name': name,
                        'latitude': latitude,
                        'longitude': longitude,
                        'stationNumber': station_number,
                        'state': state
                    })
                else:
                    print(f"Station #: {station_number} has no EVSEs.")
        except KeyError as e:
            print(f"Error processing response data for Node ID {location_node_id}: {e}")
    return stations
