"""
INST 326 Weather Forecast Final Project
Group Members: Weston Marhefka,  Tiffany Bixler, Alex Lopez
"""

import requests
from datetime import datetime
from timezonefinder import TimezoneFinder
import pytz

def get_weather_data(city_name, api_key):
    # Get city coordinates
    geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"
    geocode_response = requests.get(geocode_url)
    
    if geocode_response.status_code != 200 or not geocode_response.json():
        print("Couldn't get location data. Please check the city name and try again.")
        return None, None, None
    
    city_data = geocode_response.json()[0]
    lat, lon = city_data['lat'], city_data['lon']
    
    #Add code to get the weather forecast for the coordinates
   

def process_forecast(forecast_data, timezone):
    daily_forecast = {}
    
    for entry in forecast_data['list']:
        local_time = datetime.fromtimestamp(entry['dt'], tz=timezone)
        date_str = local_time.strftime('%A, %B %d, %Y')
        
        if date_str not in daily_forecast:
            daily_forecast[date_str] = []
        
        # Add code for weather details for each time slot
        
    
    return 

def display_forecast(daily_forecast, city_name):
    # Show the weather forecast
    print(f"\nWeather forecast for {city_name}:\n")
    for date, entries in daily_forecast.items():
        print(f"--- {date} ---")
        for entry in entries:
            print(f"{entry['time']}: {entry['description']}, {entry['temp']}°C (Low: {entry['temp_min']}°C, High: {entry['temp_max']}°C)")
            print(f"  Humidity: {entry['humidity']}%, Wind: {entry['wind_speed']} m/s\n")

def main():
    api_key = '37eff77313390fb273b82a494b012c65'
    city_name = input("Enter city name: ").strip()
    #add if statements for 
    if not city_name:
        print("City name is required.")
        return
    
    weather_data, timezone, city_name = get_weather_data(city_name, api_key)
    
    if weather_data is None:
        print("Unable to retrieve weather information.")
        return
    
    daily_forecast = process_forecast(weather_data, timezone)
    display_forecast(daily_forecast, city_name)

if __name__ == "__main__":
    main()
