import requests
import json
import pandas as pd

def get_stations_with_charging_state_dataframe(location_node_id):
    url = 'https://api.voltaapi.com/v1/pg-graphql'
    headers = {
        'authority': 'api.voltaapi.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://voltacharging.com',
        'referer': 'https://voltacharging.com/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv'
    }
    data = {
        "query": """
            query getStation($locationNodeId: ID!) {
              locationByNodeId(nodeId: $locationNodeId) {
              name
                stationsByLocationId(orderBy: STATION_NUMBER_ASC) {
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
        "variables": {
            "locationNodeId": location_node_id
        }
    }

    response = requests.post(url, headers=headers, json=data)
    json_data = response.json()

    # Extracting the relevant data and preparing for DataFrame creation
    stations_info = []
    # print(json_data['data'])
    stationName = json_data['data']['locationByNodeId']['name']
    for edge in json_data['data']['locationByNodeId']['stationsByLocationId']['edges']:
        node = edge['node']
        for evse in node['evses']['edges']:
            station_info = {
                'name': stationName,
                'stationNumber': node['stationNumber'],
                'state': evse['node']['state']
            }
            stations_info.append(station_info)

    # Creating DataFrame
    df_stations = pd.DataFrame(stations_info)
    return df_stations

# Example usage
location_node_id = "WyJzaXRlcyIsIjE4NThlZTRiLTA2ZDgtNGMzZC1iZDkwLWRmNWJjOWE2NmQwMiJd"  # Replace this with the actual node ID
df_stations = get_stations_with_charging_state_dataframe(location_node_id)
print(df_stations)