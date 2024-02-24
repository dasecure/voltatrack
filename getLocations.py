import json
import requests
from geopy.distance import geodesic
import haversine as hs

# get current location from browser
def get_location_by_ip():
    try:
        response = requests.get('http://ip-api.com/json/')
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'success':
            return {
                'country': data.get('country'),
                'city': data.get('city'),
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'isp': data.get('isp')  # Internet Service Provider
            }
        else:
            return "Failed to get location"
    except requests.RequestException as e:
        return f"Error: {e}"

# Function to extract lon, lat from the 'geojson' string
def extract_coordinates(geojson_str):
    try:
        geojson = json.loads(geojson_str)
        if geojson['type'] == 'Point' and len(geojson['coordinates']) == 2:
            return tuple(geojson['coordinates'])  # Returns (longitude, latitude)
    except Exception as e:
        return None

# Function to check if a location is within a given radius from a point
def within_radius(coord1, coord2, radius):
    return geodesic(coord1, coord2).miles <= radius

# Load the JSON content from the fileimp
file_path = 'allStations.json'
with open(file_path, 'r') as file:
    data = json.load(file)

currentPos = get_location_by_ip()

current_coords = (currentPos['latitude'], currentPos['longitude'])
radius_miles = 5

def getLocationWithin(radius_miles, current_coords):
    # Extracting locations within 25 miles of Sunnyvale
    within_radius_locations = []
    for location in data.get('data', {}).get('locations', {}).get('edges', []):
        node = location.get('node', {})
        geojson_str = node.get('stationsByLocationId', {}).get('geolocationCentroid', {}).get('geojson')
        nodeId = node.get('nodeId')
        if geojson_str and nodeId:
            coordinates = extract_coordinates(geojson_str)
            if coordinates and within_radius(current_coords, coordinates[::-1], radius_miles):
                within_radius_locations.append((nodeId, coordinates))

    # return the locations within the radius, along with their nodeId, longitude, and latitude in array format and their respective distances
    locations = []
    for item in within_radius_locations[:]:
        # locations.append(item[0], item[1][0], item[1][1], f"{geodesic(current_coords, item[1]).miles:.2f} miles away")
        locations.append({
            "nodeId": item[0],
            "longitude": item[1][0],
            "latitude": item[1][1],
            "dist": hs.haversine(current_coords,(item[1][1], item[1][0]))
        })

    return locations