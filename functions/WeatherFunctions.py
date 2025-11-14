#!/usr/bin/python3
# Set of Python functions for retrieving weather data

### Imports
import os
import requests
from dotenv import load_dotenv # for variables

# Get tokens and ids from .env file
load_dotenv()  # loads
WeatherAPIKey = os.getenv('WeatherAPIKey')
LAT = os.getenv('LAT')
LONG = os.getenv('LONG')


## Create journal tables
absolute_path = os.path.dirname(__file__)
directory_path = absolute_path.replace("\setup","")
journal = os.path.join(directory_path, "databases", "journal.db")

### Database Functions

class WeatherFunctions:
    def get_weather(lat, lon, WeatherAPIKey):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WeatherAPIKey}"
        response = requests.get(url).json()
        return response['main']['temp'], response['weather'][0]['description'] 