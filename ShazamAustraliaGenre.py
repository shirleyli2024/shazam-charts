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
    ListOfGenre = ['POP','HIP_HOP_RAP','DANCE','ELECTRONIC','ALTERNATIVE','ROCK','COUNTRY','WORLDWIDE','SINGER_SONGWRITER']

    def truncate_data(conn):
        # Truncate old chart data
        cursor = conn.cursor()
        cursor.execute('''DROP TABLE IF EXISTS ShazamAustraliaGenre''')
        conn.commit()


    def fetch_and_store_genre_data(genreName, conn):
        url = "https://shazam-api7.p.rapidapi.com/charts/get-top-songs-in_country_by_genre"
        querystring = {"country_code":"AU","genre": genreName,"limit":"10"}
        headers = {
            "X-RapidAPI-Key": "a5d70efaffmsh0335d8f09b26e19p1d8e0fjsn4a769b191916",
            "X-RapidAPI-Host": "shazam-api7.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        responseData = response.json()

        # Extract relevant data from the response
        tracks_data = responseData.get('tracks', [])
        
        # List to hold the extracted data
        cleaned_data = []
        
        # Iterate over each track in the songs_data
        for track in tracks_data:
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

            df['genreColumn'] = f'{genreName}'

            # Inserting new records from source into the destination table
            df.to_sql('ShazamAustraliaGenre', conn, if_exists= 'append', index=False)

            print("Data successfully loaded into the ShazamData table.")

            # Return df for future functions to use
            return df 
        else:
            print("No data found in the response.")

    truncate_data(conn)

    for index, genre in enumerate(ListOfGenre): 
        print(f"Processing genre {index}: {genre}")
        country_df = fetch_and_store_genre_data(genre, conn)

    # Commit changes
    conn.commit()
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the connection
    conn.close()