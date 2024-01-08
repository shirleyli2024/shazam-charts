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

# A function to get the list of countries in the ShazamCountryList table
def get_list_of_countries(conn):
    sql_query = pd.read_sql_query (f'''
                                   SELECT id
                                   FROM ShazamCountryList
                                   ''', conn)

    #Create a df that contains all the country IDs
    ListOfPlacesDf = pd.DataFrame(sql_query, columns = ['id'])

    # Convert the df into a list
    ListOfPlacesList = ListOfPlacesDf.values.tolist()

    # Flatten the list 
    ListOfPlaces = [item for sublist in ListOfPlacesList for item in sublist]

    print (ListOfPlaces)
    return ListOfPlaces

def truncate_data(conn):
    # Truncate old chart data
    cursor = conn.cursor()
    cursor.execute('''DROP TABLE IF EXISTS ShazamChartsAll''')
    conn.commit()

def fetch_and_store_country_data(countryId, conn):
    try:
        # URL for API request
        # Go to https://rapidapi.com/diyorbekkanal/api/shazam-api6 to subscibe to the API and get the code snippet for Top, Top tracks in country
        url = "https://shazam-api6.p.rapidapi.com/shazam/top_tracks_country"
        querystring = {"country_code":countryId,"limit":"10"}
        headers = {
        'X-RapidAPI-Key': #Copy and paste the key from the '(Python) Requests' Code snippet section,
        'X-RapidAPI-Host': 'shazam-api6.p.rapidapi.com'
        }
        response = requests.get(url, headers=headers, params=querystring)

        responseData = response.json()
        print(responseData)

        # Extract relevant data from the response
        songs_data = responseData.get('result', {}).get('tracks', [])

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

            df['countryColumn'] = f'{countryId}'

            # Inserting new records from source into the destination table
            df.to_sql('ShazamChartsAll', conn, if_exists= 'append', index=False)
            print(f"Data for country {countryId} successfully loaded into the database.")
            # Return df for future functions to use
            return df 
        else:
            print(f"No data found for country {countryId}.")
    except Exception as e:
        print(f"An error occurred while fetching data for country {countryId}: {e}")

truncate_data(conn)

# Get the list of countries
ListOfPlaces = get_list_of_countries(conn)

for index, countries in enumerate(ListOfPlaces): 
    print(f"Processing country {index}: {countries}")
    try:
        country_df = fetch_and_store_country_data(countries, conn)
    except Exception as e:
        print(f"An error occurred while processing country {countries}: {e}")
    
# Commit and close the connection
conn.commit()
conn.close()
