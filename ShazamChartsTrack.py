import requests
import pandas as pd
import sqlite3
import os

def truncate_data(conn):
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS ShazamChartsTrack''')
    conn.commit()

def fetch_and_store_chart_data(conn):
    url = "https://shazam.p.rapidapi.com/charts/track"
    querystring = {"locale": "en-US", "pageSize": "10", "startFrom": "0"}
    headers = {
        "X-RapidAPI-Key": "300268471bmshfeb05846b012d95p13ad64jsn46325262a467",
        "X-RapidAPI-Host": "shazam.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        responseData = response.json()

        # Extract relevant data from the response
        songs_data = responseData.get('tracks', [])

        # List to hold the extracted data
        cleaned_data = []

        # Iterate over each track in the songs_data
        for track in songs_data:
            # Extract 'key', 'title', and 'subtitle' from each track
            key = track.get('key')
            title = track.get('title')
            subtitle = track.get('subtitle')
            url = track.get('url')

            # Accessing nested dictionary 'share'
            share = track.get('share', {})  # Get the 'share' dictionary, default to empty if not present
            share_subject = share.get('subject')
            share_text = share.get('text')

            # Accessing nested dictionary 'images'
            images = track.get('images', {})  # Get the 'images' dictionary, default to empty if not present
            images_background = images.get('background')
            images_coverart = images.get('coverart')
            images_coverarthq = images.get('coverarthq')
            images_joecolor = images.get('joecolor')

            # Add a dictionary of the extracted data to the list
            cleaned_data.append({
                'key': key,
                'title': title,
                'subtitle': subtitle,
                'url': url,
                'share.subject': share_subject,
                'share.text': share_text,
                'images.background': images_background,
                'images.coverart': images_coverart,
                'images.coverarthq': images_coverarthq,
                'images.joecolor': images_joecolor
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

            # Insert data into the table
            df.to_sql('ShazamChartsTrack', conn, if_exists='replace', index=False) 
            print("Data successfully loaded into the ShazamData table.")
            # Return df for future functions to use
            return df 
            
    except Exception as e:
        print("No data found in the response.")

# Set the directory path
# ~~~~~~~~~~~~~ EDIT THE PATH BELOW BEFORE RUNNING THIS SCRIPT ~~~~~~~~~~~~~
db_path = os.path.join(# Type the directory path here, e.g. "C:\\", "Programs", "SQLite")
os.chdir(db_path)
            
# Connect to SQLite database
# ~~~~~~~~~~~~~ ENSURE A DATABASE IS CREATED FOR THE CONNECTION ~~~~~~~~~~~~~
conn = sqlite3.connect('Shazam.db')
truncate_data(conn)
df = fetch_and_store_chart_data(conn)

#close the connection
conn.close()