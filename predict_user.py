import joblib
import pandas as pd
import requests


def get_gps_location():
    """Get user's current location (lat, lon) using IP-based geolocation (fallback safe)."""
    try:
        resp = requests.get("https://ipinfo.io/json", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        lat, lon = map(float, data["loc"].split(","))
        return lat, lon
    except Exception as e:
        raise RuntimeError(f"❌ Could not fetch GPS location: {e}")


def fetch_weather_forecast(lat, lon, days=7):
    """Fetch weather data from Open-Meteo (no API key needed)."""
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&daily=temperature_2m_max,temperature_2m_min,relative_humidity_2m_max,relative_humidity_2m_min"
        f"&pressure_msl"  # mean sea level pressure
        f"&timezone=auto"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    forecast = []
    daily_times = data["daily"]["time"]

    for i in range(min(days, len(daily_times))):
        date = daily_times[i]
        temp = (data["daily"]["temperature_2m_max"][i] + data["daily"]["temperature_2m_min"][i]) / 2
        humidity = (data["daily"]["relative_humidity_2m_max"][i] + data["daily"]["relative_humidity_2m_min"][i]) / 2
        # Use mean sea-level pressure (pressure_msl), if present
        pressure = data["daily"].get("pressure_msl", [1013] * len(daily_times))[i]

        forecast.append({
            "date": date,
            "temp_C": temp,
            "humidity_%": humidity,
            "pressure_hPa": pressure
        })
    return forecast


def calc_recommended_efficiency(fuel_type, temp_C, humidity, pressure_hPa):
    base_eff = {"coal": 0.38, "oil": 0.42, "natural_gas": 0.50}.get(fuel_type, 0.40)
    temp_factor = 1 - 0.002 * (temp_C - 25)
    humidity_factor = 1 - 0.001 * (humidity - 40)
    pressure_factor = 1 + 0.0005 * (pressure_hPa - 1013.25)
    return base_eff * temp_factor * humidity_factor * pressure_factor


def predict_outputs(input_data):
    fuel_type = input_data['fuel_type']
    try:
        model = joblib.load(f"model_{fuel_type}.joblib")
    except Exception:
        print(f"⚠️ No model found for {fuel_type}, using dummy output.")
        class DummyModel:
            def predict(self, X): return [input_data["max_capacity_mw"] * 0.7]
        model = DummyModel()

    features = ["max_capacity_mw", "run_hours", "temp_C", "humidity_%", "pressure_hPa"]
    X = pd.DataFrame([[input_data[feat] for feat in features]], columns=features)
    current_generation_mw = model.predict(X)[0]

    max_capacity = input_data["max_capacity_mw"]
    run_hours = input_data["run_hours"]

    # User-provided current fuel use
    fuel_used_current = input_data["fuel_used_current"]

    # Recommended scenario (weather-dependent)
    recommended_efficiency = calc_recommended_efficiency(
        fuel_type, input_data["temp_C"], input_data["humidity_%"], input_data["pressure_hPa"]
    )
    recommended_generation_mw = max_capacity * recommended_efficiency
    recommended_energy_kwh = recommended_generation_mw * 1000 * run_hours

    fuel_per_kwh_map = {"coal": 0.35, "oil": 0.25, "natural_gas": 0.20}
    fuel_per_kwh = fuel_per_kwh_map.get(fuel_type, 0.3)
    fuel_used_recommended = recommended_energy_kwh * fuel_per_kwh / 1000

    # Savings
    fuel_saved = fuel_used_current - fuel_used_recommended

    fuel_cost_map = {"coal": 6000, "oil": 700, "natural_gas": 300}
    fuel_cost_per_unit = fuel_cost_map.get(fuel_type, 500)
    cost_saved = fuel_saved * fuel_cost_per_unit

    co2_factor_map = {"coal": 2.42, "oil": 2.96, "natural_gas": 2.0}
    co2_factor = co2_factor_map.get(fuel_type, 2.5)
    co2_saved_tonnes = fuel_saved * co2_factor

    outputs = {
        "recommended_generation_mw": recommended_generation_mw,
        "fuel_used_recommended": fuel_used_recommended,
        "fuel_saved": fuel_saved,
        "cost_saved": cost_saved,
        "co2_saved_tonnes": co2_saved_tonnes,
        "recommended_efficiency":recommended_efficiency
    }
    return outputs
sample_input = {
        "fuel_type": "coal",
        "max_capacity_mw": 150,
        "run_hours": 20,
        "fuel_used_current": 9000  # ✅ user enters actual current fuel use (kg/litres/Nm3)
    }
def f2(no):
    return int(no*100)/100

def func1(sample_input):
    print("📍 Fetching GPS location...\n")
    try:
        lat, lon = get_gps_location()
        print(f"✅ Current Location: ({lat}, {lon})\n")
    except Exception as e:
        print("⚠️ Location fetch failed. Using fallback: Chennai, India.")
        lat, lon = 13.0895, 80.2739

    print("🌦️ Fetching 7-day weather forecast...\n")
    try:
        forecast = fetch_weather_forecast(lat, lon, days=7)
    except Exception as e:
        print("❌ Could not fetch weather data. Please check your internet connection or try again later.")
        print("Error details:", e)
        exit(1)

    print("\n7-Day Plant Output Forecast:\n")
    l=[]
    for day in forecast:
        input_data = sample_input.copy()
        input_data["temp_C"] = day["temp_C"]
        input_data["humidity_%"] = day["humidity_%"]
        input_data["pressure_hPa"] = day["pressure_hPa"]

        outputs = predict_outputs(input_data)

        print(f"📅 Date: {day['date']}")
        print(f"  Recommended Generation (MW): {outputs['recommended_generation_mw']:.4f}")
        print(f"  Recommended Fuel Use: {outputs['fuel_used_recommended']:.4f}")
        print(f"  Fuel Saved: {outputs['fuel_saved']:.4f}")
        print(f"  Cost Saved: {outputs['cost_saved']:.4f}")
        print(f"  CO2 Saved (tonnes): {outputs['co2_saved_tonnes']:.4f}")
        print("-" * 40)
        l.append([day['date'],f2(outputs['recommended_generation_mw']),f2(outputs['fuel_used_recommended']),\
                f2(outputs['fuel_saved']),f2(outputs['cost_saved']),f2(outputs['co2_saved_tonnes']),\
                    f2(outputs['recommended_efficiency'])])
    return l