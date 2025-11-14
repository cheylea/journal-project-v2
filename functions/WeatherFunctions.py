#!/usr/bin/python3
# Set of Python functions for retrieving weather data

### Imports
import os
import requests


### Weather Functions

class WeatherFunctions:
    def get_weather(lat, lon, WeatherAPIKey):
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WeatherAPIKey}"
        response = requests.get(url).json()
        return response['main']['temp'], response['weather'][0]['description'] 