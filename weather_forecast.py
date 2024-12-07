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
    """Brief Description: 

    Args: 


    Returns:
    
    
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
    """Brief Description: Extracts weather details from a forecast entry.

    Args: 


    Returns:
    
    
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
    """Brief Description: Show the weather forecast

    Args: 


    Returns:
    
    
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


    Returns:
    
    
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
    """Brief Description: 

    Args: 


    Returns:
    
    
    """
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

if __name__ == "__main__":
    main()
