import requests
from API_helpers.helperFunctions import str2frame
import pandas as pd

def get_data(country, species):
    url = f"http://gbadske.org:9000/GBADsLivestockPopulation/oie?year=*&country={country}&species={species}&format=file"
    response = requests.get(url)
    return response.text

def formatWoahData(woah_data):
    woah_data = str2frame(woah_data, "oie")
    woah_data['source'] = "woah"
    woah_data = woah_data.drop(columns=['country'])
    woah_data = woah_data.replace('"','', regex=True)
    woah_data.sort_values(by=['year'], inplace=True)

    years = woah_data['year']
    woah_data['year'] = pd.to_numeric(years)

    return woah_data