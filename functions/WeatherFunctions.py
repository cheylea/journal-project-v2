#!/usr/bin/python3
# Set of Python functions for retrieving weather data
# Uses OpenWeatherMap API https://openweathermap.org/

# Imports
import os
import requests


class WeatherFunctions:
    @staticmethod
    def get_weather(lat, lon, WeatherAPIKey):
        """ Get current weather data for given latitude and longitude.
        Args:
            lat: Latitude
            lon: Longitude
            WeatherAPIKey: API key for OpenWeatherMap https://openweathermap.org/"""
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={WeatherAPIKey}"
        response = requests.get(url).json()
        return response['main']['temp'], response['weather'][0]['description']
