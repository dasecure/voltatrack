import requests
import json

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
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'x-api-key': 'u74w38X44fa7m3calbsu69blJVcC739z8NWJggVv'
}

# Data (GraphQL query and variables)
data = {
    "query": """
        query getStation($locationNodeId: ID!) {
          locationByNodeId(nodeId: $locationNodeId) {
            name
            streetAddress
            city
            state
            zipCode
            tips
            imageUrl
            hoursByLocationId {
              edges {
                node {
                  dayOfWeek
                  chargerOperationStartTime
                  chargerOperationEndTime
                }
              }
            }
            stationsByLocationId(orderBy: STATION_NUMBER_ASC) {
              geolocationCentroid {
                latitude
                longitude
              }
              edges {
                node {
                  id
                  name
                  stationNumber
                  chargeDurationSeconds
                  status
                  evses {
                    edges {
                      node {
                        id
                        level
                        state
                        connectors {
                          nodes {
                            type
                          }
                        }
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
        "locationNodeId": "WyJzaXRlcyIsIjYzNzVjZDViLTA4OTMtNDNlMi1iMTJlLTc1YTI2OGRkMThjNyJd"
    }
}

# Making the POST request
response = requests.post(url, headers=headers, json=data)

# Assuming the response is JSON, print it formatted
print(json.dumps(response.json(), indent=2))
