import requests
import pandas as pd
import sqlite3
import os


# Set the directory path
# ~~~~~~~~~~~~~ EDIT THE PATH BELOW BEFORE RUNNING THIS SCRIPT ~~~~~~~~~~~~~
db_path = os.path.join(# Type the directory path here, e.g. "C:\\", "Programs", "SQLite")
os.chdir(db_path)

# Initialize SQLite connection
# ~~~~~~~~~~~~~ ENSURE A DATABASE IS CREATED FOR THE CONNECTION ~~~~~~~~~~~~~
conn = sqlite3.connect('Shazam.db')

try:
    # List of Australia cities
    ListOfCities = ['Melbourne', 'Sydney', 'Brisbane', 'Perth', 'Adelaide', 'Hobart', 'Darwin']
    print (ListOfCities)
 
    # Truncate or create table
    def truncate_data(conn):
        cursor = conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS ShazamAustraliaCities''')
        # Consider adding CREATE TABLE statement here
        conn.commit()
        
    # Fetch and store city data function
    def fetch_and_store_city_data(cityName, conn):
        # URL for API request
        url = "https://shazam-api7.p.rapidapi.com/charts/get-top-songs-in-city"
        querystring = {"country_code":"AU","city_name": cityName,"limit":"10"}
        headers = {
            "X-RapidAPI-Key": "a5d70efaffmsh0335d8f09b26e19p1d8e0fjsn4a769b191916",
            "X-RapidAPI-Host": "shazam-api7.p.rapidapi.com"
        }
        response = requests.get(url, headers=headers, params=querystring)
        responseData = response.json()
        print(responseData)
        songs_data = responseData
        
                # List to hold the extracted data
        cleaned_data = []

        # Iterate over each track in the songs_data
        for track in songs_data:
            # Extract 'key', 'title', and 'subtitle' from each track
            apple_music_url = track['apple_music_url']
            key = track['key']
            ringtone= track['ringtone']
            subtitle = track['subtitle']
            title = track['title']

            # Add a dictionary of the extracted data to the list
            cleaned_data.append({
                'apple_music_url': apple_music_url,
                'key': key,
                'ringtone': ringtone,
                'subtitle': subtitle,
                'title': title
            })
        
        # Check if there is any data
        if cleaned_data:
            # Normalize the data and create a DataFrame
            df = pd.json_normalize(cleaned_data)
            # Apply a lambda function to modify 'hasTimeSyncedLyrics' values
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(lambda x: str(x) if x is not None else '')
                else:
                    df[col] = df[col].fillna(0)  # Replace NaN with 0 for numeric columns

            df['city_column'] = f'{cityName}'

            # Inserting new records from source into the destination table
            df.to_sql('ShazamAustraliaCities', conn, if_exists= 'append', index=False)
            # Return df for future functions to use
            print("Data successfully loaded into the ShazamData table.")
            return df 
        else:
            print("No data found in the response.")
            return None

    truncate_data(conn)
 
    for index, cities in enumerate(ListOfCities): 
        print(f"Processing city {index}: {cities}")
        city_df = fetch_and_store_city_data(cities, conn)
        
    # Commit changes
    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the connection
    conn.close()