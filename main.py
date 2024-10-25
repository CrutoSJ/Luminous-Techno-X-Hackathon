import requests
import random
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

# Constants
LOW_TARIFF_THRESHOLD = 0.10  # Example threshold for low tariffs
SOLAR_PRODUCTION_RATE = 5.0  # Default solar production rate in kWh
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # Replace with your OpenWeatherMap API key

# Function to fetch real-time tariff data from the Flask API
def fetch_tariff_data():
    try:
        response = requests.get("http://127.0.0.1:5000/tariff")  # Replace with a valid API endpoint if needed
        if response.status_code == 200:
            return round(response.json().get("rate", 0.1), 2)  # Round to 2 decimal places
    except Exception as e:
        print(f"Error fetching tariff data: {e}")

    # Randomize the tariff rate between 0.05 and 0.15 and round to 2 decimal places
    return round(random.uniform(0.05, 0.15), 2)

# Function to calculate real-time costs
def calculate_costs(power_usage_kwh, tariff_rate):
    return round(power_usage_kwh * tariff_rate, 2)

# Function to decide device scheduling based on tariff rate
def check_schedule(tariff_rate):
    return "Device scheduled ON" if tariff_rate < LOW_TARIFF_THRESHOLD else "Device OFF"

# Function to fetch weather data and adjust solar production rate
def fetch_weather():
    try:
        response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=City&appid={WEATHER_API_KEY}")
        if response.status_code == 200:
            data = response.json()
            weather_main = data["weather"][0]["main"]
            if weather_main == "Clear":
                return SOLAR_PRODUCTION_RATE * 1.2  # Increase production on clear days
            elif weather_main in ["Clouds", "Rain"]:
                return SOLAR_PRODUCTION_RATE * 0.8  # Decrease production on cloudy/rainy days
        return SOLAR_PRODUCTION_RATE  # Default if weather data is unavailable
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return SOLAR_PRODUCTION_RATE  # Return default if error

# Function to decide on using or storing solar energy based on tariff rate
def optimize_solar_usage(tariff_rate, solar_production_kwh):
    if tariff_rate > LOW_TARIFF_THRESHOLD:
        return f"Using stored solar energy: {solar_production_kwh} kWh"
    return "Storing solar energy"

# Function to log data to SQLite database
def log_data(tariff_rate, power_usage, cost, schedule_status):
    conn = sqlite3.connect('energy_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                  tariff REAL, usage REAL, cost REAL, status TEXT)''')
    # Insert data into logs table
    c.execute('INSERT INTO logs (tariff, usage, cost, status) VALUES (?, ?, ?, ?)', 
              (tariff_rate, power_usage, cost, schedule_status))
    conn.commit()
    conn.close()

# Main function to run the complete workflow
def main():
    # Simulate power usage in kWh
    power_usage_kwh = round(random.uniform(1, 10), 2)

    # Fetch tariff data
    tariff_rate = fetch_tariff_data()
    print(f"Tariff Rate: ${tariff_rate}/kWh")

    # Calculate and display real-time cost
    cost = calculate_costs(power_usage_kwh, tariff_rate)
    print(f"Power Usage: {power_usage_kwh} kWh")
    print(f"Real-Time Cost: ${cost}")

    # Check scheduling decision
    schedule_status = check_schedule(tariff_rate)
    print(f"Device Status: {schedule_status}")

    # Adjust solar production based on weather conditions
    solar_production = fetch_weather()
    solar_decision = optimize_solar_usage(tariff_rate, solar_production)
    print(solar_decision)

    # Log data to the database
    log_data(tariff_rate, power_usage_kwh, cost, schedule_status)
    print("-" * 30)

if __name__ == "__main__":
    main()
