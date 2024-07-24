import requests
import json

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
        # 'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        # 'sec-ch-ua-mobile': '?0',
        # 'sec-ch-ua-platform': '"macOS"',
        # 'sec-fetch-dest': 'empty',
        # 'sec-fetch-mode': 'cors',
        # 'sec-fetch-site': 'cross-site',
        # 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv'
    }

    # GraphQL query and variables
    data = {
        "query": """
            query getStation($locationNodeId: ID!) {
              locationByNodeId(nodeId: $locationNodeId) {
                stationsByLocationId(orderBy: STATION_NUMBER_ASC) {
                  edges {
                    node {
                      id
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

# Function to print stations and their charging state
def print_stations_with_charging_state(location_node_id):
    data = get_stations_data(location_node_id)
    stations = data['data']['locationByNodeId']['stationsByLocationId']['edges']

    for station in stations:
        station_node = station['node']
        print(f"Station Name: {station_node['name']}")
        print("Charging States:")
        for evse in station_node['evses']['edges']:
            print(f"  - {evse['node']['state']}")
        print("")

# Example usage
location_node_id = "WyJzaXRlcyIsIjYzNzVjZDViLTA4OTMtNDNlMi1iMTJlLTc1YTI2OGRkMThjNyJd"  # Replace with your desired Node ID
print_stations_with_charging_state(location_node_id)
