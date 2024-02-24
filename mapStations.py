import streamlit as st
import pandas as pd
import sqlite3

# Function to load data from SQLite database into a pandas DataFrame
def load_data(db_path):
    conn = sqlite3.connect(db_path)
    query = '''
        SELECT name, streetAddress, city, state, zipCode, latitude, longitude
        FROM stations
    '''
    df = pd.read_sql_query(query, conn)
    # Combine address components for hover text
    df['address'] = df['streetAddress'] + ', ' + df['city'] + ', ' + df['state'] + ' ' + df['zipCode']
    return df[['name', 'address', 'latitude', 'longitude']]

# Main function to display the map in a Streamlit app
def main(db_path):
    st.title("Station Locations")
    df = load_data(db_path)
    
    # Plot the map
    if not df.empty:
        st.map(df[['latitude', 'longitude']], zoom=4)
    else:
        st.write("No data available to plot.")

if __name__ == "__main__":
    db_path = 'stations.sqlite'  # Update this path to your SQLite database file
    main(db_path)
