"""
INST 326 Weather Forecast Final Project
Group Members: Weston Marhefka, Tiffany Bixler, Alex Lopez
"""

import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
from dotenv import load_dotenv
import pytz
import os
import unittest
from unittest.mock import patch

# Load API key from .env file
load_dotenv()

def get_weather_data(city_name, api_key, units):
    """Brief Description: Grab city coordinates from the api using the designated city name and units of measurement, accessing it through the api key.

    Args: 
    city_name(str): This value is input by the user, and denotes which city the weather data will be grabbed for
    api_key(int): This value is taken from the separate .env file that the user will have stored on their local computer and is used
    to access the api. Storing the api key in this way helps to protect the api. 
    units(str): This value will be either "F" or "C" depending on whether or not the user would like to view the temperature in metric or imperial degrees. 

    Returns:
    Three values, the forecast data with a given longitude and latitude, the timezone variable which uses the timezonefinder module to determine timezone based
    on location, and the geographic code for the given city. 
    """
    
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"
    geocode_response = requests.get(geocode_url)
    
    if geocode_response.status_code != 200 or not geocode_response.json():
        print("Couldn't get location data. Please check the city name and try again.")
        return None, None, None
    
    city_data = geocode_response.json()[0]
    lat, lon = city_data['lat'], city_data['lon']
    
    # Get the weather forecast for the coordinates
    forecast_data = get_forecast_data(lat, lon, api_key, units)
    
    if forecast_data is None:
        return None, None, None
    
    # Get the timezone for the location
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=lon, lat=lat)
    if timezone_str is None:
        timezone_str = 'UTC'
    timezone = pytz.timezone(timezone_str)
    
    return forecast_data, timezone, city_data['name']

def choose_units():  
    """Brief Description: Asks the user to choose temperature unit 'metric' for Celsius or 'imperial' for Fahrenheit. This ensures that the user is
    able to view the temperature in their preferred unit of degrees. It uses a while loop and an if/else statement to consider the user's potential input. 

    Args: This function takes no arguments. 
    Returns: This function does not return anything
    """
    
    while True:
        choice = input("Choose temperature unit - Celsius (C) or Fahrenheit (F): ").strip().upper()
        if choice == 'C':
            return 'metric'
        elif choice == 'F':
            return 'imperial'
        else:
            print("Invalid choice. Please enter 'C' for Celsius or 'F' for Fahrenheit.")

def get_forecast_data(lat, lon, api_key, units):
    """Brief Description: Gets the weather forecast data for the given latitude and longitude, accessing the api via the api key, and using the user input
    choice of units. 
    
    Args: 
    lat(int): This value holds the latitude of the location given by the user
    lon(int): This value holds the longitude of the location given by the user.
    api_key(int): This value is taken from the separate .env file that the user will have stored on their local computer and is used
    to access the api. Storing the api key in this way helps to protect the api. 
    units(str): This value will be either "F" or "C" depending on whether or not the user would like to view the temperature in metric or imperial degrees.
    Returns:
    The converted JSON file of the data from the forecast url. 
    """
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units={units}"
    forecast_response = requests.get(forecast_url)
    
    if forecast_response.status_code != 200:
        print("Couldn't get weather forecast data.")
        return None
    
    return forecast_response.json()

def process_forecast(forecast_data, timezone):
    """Brief Description: Creates an empty dictionary to then assign daily
    forcast information to, based on the data collected from the OpenWeather API.
    
    Args: 
    forecast_data(list) = input by user, a list of forecast data
    timezone(str) = input by user, indicates the appropriate timezone for the forecast data collection
    Returns: daily_forecast, the dictionary of daily forecast data that is initialized in this  function. 
    """
    daily_forecast = {}
    
    for entry in forecast_data['list']:
        local_time = datetime.fromtimestamp(entry['dt'], tz=timezone)
        date_str = local_time.strftime('%A, %B %d, %Y')
        
        if date_str not in daily_forecast:
            daily_forecast[date_str] = []
        
        weather_details = extract_weather_details(entry, local_time)
        daily_forecast[date_str].append(weather_details)
    
    return daily_forecast

def extract_weather_details(entry, local_time):
  """Brief Description: Extracts weather details from a forecast entry and returns the information in a
  simple, easy to read format, which includes the time, description of the weather, the average temperature,
  max temperature, and minimum temperature, the humidity percentage, and the average wind speed for that
  time frame.  

    Args: 
    entry(str): This refers to the object we have selected within the API database.  
    local_time(str): This is the time in the city that the user has input
    Returns:
    time, weather description, temperature, temperature max, temperature min, humidity percentage, and wind speed, 
    based on the user's entry for city and units. 
    """
    return {
        'time': local_time.strftime('%I:%M %p'),
        'description': entry['weather'][0]['description'],
        'temp': entry['main']['temp'],
        'temp_min': entry['main']['temp_min'],
        'temp_max': entry['main']['temp_max'],
        'humidity': entry['main']['humidity'],
        'wind_speed': entry['wind']['speed']
    }

def display_forecast(daily_forecast, city_name, units):
    """Brief Description: Shows the weather forecast and adds unit symbol depending upon the user's choice of
    units. Adds details to the way the forecast information is presented. 

    Args: 
    daily_forecast(list): This is a list of forecast information for a specific day
    city_name(str): This is input by the user and is their choice of city for weather
    units(str): This is input by the user and is either "F" or "C" to choose between imperial and SI units
    Returns:
    This function returns nothing.
    """
    unit_symbol = '°C' if units == 'metric' else '°F'
    print(f"\nWeather forecast for {city_name}:\n")
    for date, entries in daily_forecast.items():
        print(f"--- {date} ---")
        for entry in entries:
            print(f"{entry['time']}: {entry['description']}, {entry['temp']}{unit_symbol} (Low: {entry['temp_min']}{unit_symbol}, High: {entry['temp_max']}{unit_symbol})")
            print(f"  Humidity: {entry['humidity']}% | Wind: {entry['wind_speed']} m/s\n")
        print("\n")

def save_forecast(daily_forecast, city_name, units):
    """Brief Description: Saves the weather forecast to a text file.

    Args: 
    daily_forecast(list): This is a list of forecast information for a specific day
    city_name(str): This is input by the user and is their choice of city for weather
    units(str): This is input by the user and is either "F" or "C" to choose between imperial and SI units
    Returns:
    This function returns nothing.
    """
    unit_symbol = '°C' if units == 'metric' else '°F'
    filename = f"{city_name}_weather_forecast.txt"
   
    with open(filename, 'w') as file:
        file.write(f"Weather forecast for {city_name}:\n\n")
        for date, entries in daily_forecast.items():
            file.write(f"--- {date} ---\n")
            for entry in entries:
                file.write(f"{entry['time']}: {entry['description']}, {entry['temp']}{unit_symbol} (Low: {entry['temp_min']}{unit_symbol}, High: {entry['temp_max']}{unit_symbol})\n")
                file.write(f"  Humidity: {entry['humidity']}%, Wind: {entry['wind_speed']} m/s\n\n")
    print(f"Forecast saved to {filename}")

def main():
    api_key = os.getenv('OPENWEATHER_API_KEY')
    city_name = input("Enter city name: ").strip()
    if not city_name:
        print("City name is required.")
        return
    
    units = choose_units()
    
    weather_data, timezone, city_name = get_weather_data(city_name, api_key, units)
    
    if weather_data is None:
        print("Unable to retrieve weather information.")
        return
    
    daily_forecast = process_forecast(weather_data, timezone)
    display_forecast(daily_forecast, city_name, units)
    
    save_choice = input("Would you like to save the forecast to a file? (Y/N): ").strip().upper()
    if save_choice == 'Y':
        save_forecast(daily_forecast, city_name, units)
    else:
        print("Forecast not saved.")
        
class test_functions(unittest.TestCase):

    @patch('__main__.requests.get')
    def test_get_weather_data(self, mock_api):
        #creates mock api for testing
        #mocks api json 
        #checks for correct city name
        mock_api.return_value.json.return_value = [{'lat':39.2904, 'lon':76.6122, 'name': 'Baltimore'}]
        result = get_weather_data('Baltimore', 'fake_api_key','imperial')
        self.assertEqual(result[2], 'Baltimore')
        self.assertIsNotNone(result[0])

    def test_choose_units(self):
        #uses builtins.input to use user input
        #checks for imperial units
        with patch('builtins.input', return_value='F'):
            self.assertEqual(choose_units(), 'imperial')

    @patch('__main__.requests.get')
    def test_get_forecast_data(self, mock_api):
        mock_api.return_value.json.return_value = {'list': [{}]}
        result = get_forecast_data(39.2904, 76.6122, 'fake_api_key', 'metric')
        self.assertIn('list', result)

    def test_process_forecast(self):
        timezone = pytz.timezone('US/Eastern')
        forecast_data = {'list': [{'dt': 1734004800 }]}  
        result = process_forecast(forecast_data, timezone)
        self.assertTrue(result)

    def test_extract_weather_details(self):
        entry = {
            'dt': 1734004800,
            'main': {'temp': 53, 'temp_min': 37, 'temp_max': 64, 'humidity': 90},
            'weather': [{'description': 'light rain'}],
            'wind': {'speed': 12} 
        }
        local_time = datetime.fromtimestamp(1734004800, pytz.timezone('US/Eastern'))
        result = extract_weather_details(entry, local_time)
        self.assertEqual(result['temp'], 53)

    def test_display_forecast(self):
        forecast = { 'Wednesday, December 11, 2024': [{'time': '12:00 PM', 'description': 'light rain', 'temp': 53}]}
        with patch('builtins.print') as mock_display:
            display_forecast(forecast, 'Baltimore', 'imperial')
            mock_display.assert_called()

    def test_save_forecast(self):
        forecast = { 'Wednesday, December 11, 2024': [{'time': '12:00 PM', 'description': 'light rain', 'temp': 53}]}
        with patch('builtins.open', unittest.mock.mock_open()) as mock_open:
            save_forecast(forecast, 'Baltimore', 'imperial')
            mock_open.assert_called_with('Baltimore_weather_forecast.txt', 'w')
            
if __name__ == "__main__":
    main()
    unittest.main()
