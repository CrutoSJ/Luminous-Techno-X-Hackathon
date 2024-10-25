# app.py
from flask import Flask, jsonify , render_template
import random
from main import fetch_tariff_data, calculate_costs, check_schedule, optimize_solar_usage, fetch_weather , SOLAR_PRODUCTION_RATE

app = Flask(__name__)

tariff_history = []

@app.route('/')
def dashboard():
    # Fetch dynamic data
    tariff_rate = fetch_tariff_data()
    power_usage_kwh = round(random.uniform(1, 3), 2)
    cost = calculate_costs(power_usage_kwh, tariff_rate)
    schedule_status = check_schedule(tariff_rate)
    solar_production = fetch_weather()
    solar_decision = optimize_solar_usage(tariff_rate, solar_production)

    # Update the tariff history (keeping the latest 5 records only)
    if len(tariff_history) >= 5:
        tariff_history.pop(0)  # Remove the oldest record if we exceed 5
    tariff_history.append(tariff_rate)

    # Render the data in the template with tariff history
    return render_template("index.html", 
                           tariff_rate=tariff_rate,
                           power_usage=power_usage_kwh, 
                           cost=cost, 
                           schedule_status=schedule_status,
                           solar_decision=solar_decision,
                           tariff_history=tariff_history)

if __name__ == '__main__':
    app.run(debug=True)