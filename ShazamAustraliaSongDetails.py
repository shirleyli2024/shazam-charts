import os
import requests
import pandas as pd
import sqlite3


# Set the directory path
# ~~~~~~~~~~~~~ EDIT THE PATH BELOW BEFORE RUNNING THIS SCRIPT ~~~~~~~~~~~~~
db_path = os.path.join(# Type the directory path here, e.g. "C:\\", "Programs", "SQLite")
os.chdir(db_path)

# Initialize SQLite connection
# ~~~~~~~~~~~~~ ENSURE A DATABASE IS CREATED FOR THE CONNECTION ~~~~~~~~~~~~~
conn = sqlite3.connect('Shazam.db')

#"DB_PATH" environment variable
#if not db_path:
#    raise ValueError("DB_PATH environment variable not set")#with sqlite3.connect(os.path.join(db_path, 'testDB.db')) as conn:
#Using Command Prompt: 
#set DB_PATH=C:\Path\To\Your\Database
#Using PowerShell:
#$env:DB_PATH = "C:\Path\To\Your\Database"
#Replace "/path/to/your/database" with the actual path to your database directory.

# A function to get the song IDs of the top 10 songs in each Australian cities
def get_australia_data(conn):
    sql_query = pd.read_sql_query('''
                                  SELECT key
                                  FROM ShazamAustraliaCities
                                  ''', conn)

    # sql_query is already a DataFrame containing the column 'key'
    ListOfSongsDf = sql_query
    
    # Convert the df into a list and flatten it
    ListOfSongs = [item for sublist in ListOfSongsDf.values.tolist() for item in sublist]

    return ListOfSongs

# Truncate old chart data
def truncate_data(conn):
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS ShazamAustraliaSongDetails''')
    conn.commit()
    
# A function to use song IDs to get the details of the songs
def fetch_and_store_song_details(songId, conn):
    # URL for API request
    # Go to https://rapidapi.com/yourdevmail/api/shazam-api7 to subscibe to the API and get the code snippet for songs/get_details
    url = "https://shazam-api7.p.rapidapi.com/songs/get_details"
    querystring = {"id":songId}
    headers = {
        "X-RapidAPI-Key": #Copy and paste the key from the '(Python) Requests' Code snippet section,
        "X-RapidAPI-Host": "shazam-api7.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)

    responseData = response.json()
    print(responseData)

    # Extract relevant data from the response
    songs_data = responseData
    
    # Check if there is any data
    if songs_data:
        # Normalize the data and create a DataFrame
        df = pd.json_normalize(songs_data)
        
        # Apply a lambda function to modify values
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: str(x) if x is not None else '')
            else:
                df[col] = df[col].fillna(0)  # Replace NaN with 0 for numeric columns

        # Inserting new records from source into the destination table
        df.to_sql('ShazamAustraliaSongDetails', conn, if_exists= 'append', index=False)
        print(df.dtypes)
        print("Data successfully loaded into the ShazamData table.")
        # Return df for future functions to use
        return df 
    else:
        print("No data found in the response.")  
        
# Using 'with' statement for database connection management
with sqlite3.connect('testDB.db') as conn:
    # Truncate old data
    truncate_data(conn)

    # Get list of songs
    ListOfSongs = get_australia_data(conn)

    for index, song in enumerate(ListOfSongs): 
        print(f"Processing song data {index}: {song}")
        try:
            song_df = fetch_and_store_song_details(song, conn)
        except Exception as e:
            print(f"An error occurred while processing song {song}: {e}")

# No need to explicitly commit and close the connection, 'with' statement handles it
