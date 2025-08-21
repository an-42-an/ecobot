import csv
import os
import random
import numpy as np
from datetime import datetime, timedelta

CSV_FILE = "plant_data.csv"
BACKUP_CSV_FILE = "backup.csv"

HEADERS = [
    "timestamp", "fuel_type", "max_capacity_mw", "current_generation_mw", "run_hours",
    "temp_C", "humidity_%", "pressure_hPa", "predicted_efficiency",
    "recommended_generation_mw", "adjustment_pct", "fuel_per_kwh", "fuel_unit",
    "heat_rate_kcal_per_kwh", "fuel_used_current", "fuel_used_recommended",
    "fuel_saved", "fuel_cost_per_unit", "cost_saved", "co2_saved_tonnes"
]

# Always overwrite CSVs with correct headers
for fname in [CSV_FILE, BACKUP_CSV_FILE]:
    with open(fname, mode="w", newline="") as file:
        csv.writer(file).writerow(HEADERS)

class MultiFuelPlantGenerator:
    def __init__(self):
        self.fuel_types = {
            'coal': {
                'efficiency_range': (0.32, 0.46),
                'heat_rate_range': (2000, 2600),
                'capacity_range': (200, 800),
                'temp_sensitivity': 0.0018,
                'humidity_sensitivity': 0.0008,
                'pressure_sensitivity': 0.0006,
                'fuel_lhv': 7000,  # kcal/kg
                'fuel_unit': 'kg',
                'fuel_cost_range': (5000, 7000),  # per ton
                'co2_factor': 2.42,  # tonnes CO2 per tonne coal
                'density': 1.0,
            },
            'oil': {
                'efficiency_range': (0.36, 0.42),
                'heat_rate_range': (2100, 2400),
                'capacity_range': (100, 400),
                'temp_sensitivity': 0.0015,
                'humidity_sensitivity': 0.0007,
                'pressure_sensitivity': 0.0005,
                'fuel_lhv': 10000,  # kcal/kg
                'fuel_unit': 'liters',
                'fuel_cost_range': (600, 900),  # per barrel (159 liters)
                'co2_factor': 2.96,  # tonnes CO2 per tonne oil
                'density': 0.85,  # kg/liter
            },
            'natural_gas': {
                'efficiency_range': (0.40, 0.60),
                'heat_rate_range': (1430, 2150),
                'capacity_range': (50, 600),
                'temp_sensitivity': 0.0012,
                'humidity_sensitivity': 0.0005,
                'pressure_sensitivity': 0.0008,
                'fuel_lhv': 8500,  # kcal/Nm3
                'fuel_unit': 'Nm3',
                'fuel_cost_range': (200, 400),  # per 1000 Nm3
                'co2_factor': 2.0,  # tonnes CO2 per 1000 Nm3
                'density': 0.72,
            }
        }
        self.seasonal_temp_base = {
            'winter': 15, 'spring': 22, 'summer': 32, 'autumn': 25
        }

    def get_seasonal_temperature(self, timestamp):
        dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        month = dt.month
        if month in [12, 1, 2]:
            season = 'winter'
        elif month in [3, 4, 5]:
            season = 'spring'
        elif month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'autumn'
        base_temp = self.seasonal_temp_base[season]
        daily_variation = 6 * np.sin(2 * np.pi * dt.hour / 24)  # daily cycle
        random_noise = random.uniform(-1, 1)  # smaller noise
        return base_temp + daily_variation + random_noise

    def calculate_efficiency(self, config, temp_C, humidity, pressure_hPa, run_hours, timestamp, load_factor):
        # Start at midpoint efficiency
        base_efficiency = np.mean(config['efficiency_range'])

        # Apply load factor (plants are more efficient near 80-90% capacity)
        load_factor_adj = 1 - abs(load_factor - 0.9) * 0.08
        base_efficiency *= load_factor_adj

        # Apply environmental factors
        temp_factor = 1 - config['temp_sensitivity'] * (temp_C - 25)
        humidity_factor = 1 - config['humidity_sensitivity'] * (humidity - 40)
        pressure_factor = 1 + config['pressure_sensitivity'] * (pressure_hPa - 1013.25)

        # Runtime effect
        if run_hours < 4:
            hours_factor = 0.95
        elif run_hours < 8:
            hours_factor = 0.98
        else:
            hours_factor = 1.0 + 0.00005 * (run_hours - 8)

        # Aging effect
        days_since_start = (datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") - datetime(2020, 1, 1)).days
        degradation_factor = 1 - (days_since_start * 0.00005)

        # Combine
        efficiency = base_efficiency * temp_factor * humidity_factor * pressure_factor * hours_factor * degradation_factor

        # Clip to range
        min_eff, max_eff = config['efficiency_range']
        efficiency = max(min_eff, min(max_eff, efficiency))

        # Small noise
        efficiency *= random.uniform(0.995, 1.005)

        return round(efficiency, 4)

    def generate_realistic_data(self, num_samples=50):
        data = []
        fuel_types = list(self.fuel_types.keys())
        for i in range(num_samples):
            timestamp = datetime.now() - timedelta(hours=num_samples - i)
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            for fuel_type in fuel_types:
                config = self.fuel_types[fuel_type]
                max_capacity_mw = random.uniform(*config['capacity_range'])
                temp_C = self.get_seasonal_temperature(timestamp_str)
                humidity = random.uniform(30, 70)  # narrower realistic band
                pressure_hPa = 1013.25 + random.uniform(-10, 10)

                run_hours = random.randint(12, 24)  # longer average operation
                load_factor = random.uniform(0.6, 1.0)  # realistic load

                predicted_efficiency = self.calculate_efficiency(
                    config, temp_C, humidity, pressure_hPa, run_hours, timestamp_str, load_factor
                )

                base_generation = max_capacity_mw * predicted_efficiency
                current_generation_mw = max_capacity_mw * load_factor

                heat_rate_kcal_per_kwh = 860 / predicted_efficiency

                # Fuel-specific calculations
                if fuel_type == 'coal':
                    fuel_per_kwh = heat_rate_kcal_per_kwh / config['fuel_lhv']  # kg/kWh
                    fuel_used_current = (current_generation_mw * 1000) * fuel_per_kwh * run_hours / 1000  # tonnes
                    fuel_used_recommended = (base_generation * 1000) * fuel_per_kwh * run_hours / 1000
                    fuel_cost_per_unit = random.uniform(*config['fuel_cost_range'])
                    fuel_unit = 'ton'
                    co2_saved = (fuel_used_current - fuel_used_recommended) * config['co2_factor']
                elif fuel_type == 'oil':
                    fuel_per_kwh = heat_rate_kcal_per_kwh / (config['fuel_lhv'] * config['density'])  # liters/kWh
                    fuel_used_current = (current_generation_mw * 1000) * fuel_per_kwh * run_hours / 1000  # m3
                    fuel_used_recommended = (base_generation * 1000) * fuel_per_kwh * run_hours / 1000
                    fuel_cost_per_unit = random.uniform(*config['fuel_cost_range'])
                    fuel_unit = 'barrel'
                    fuel_used_current_tonnes = fuel_used_current * config['density'] / 1000
                    fuel_used_recommended_tonnes = fuel_used_recommended * config['density'] / 1000
                    co2_saved = (fuel_used_current_tonnes - fuel_used_recommended_tonnes) * config['co2_factor']
                elif fuel_type == 'natural_gas':
                    fuel_per_kwh = heat_rate_kcal_per_kwh / config['fuel_lhv']  # Nm3/kWh
                    fuel_used_current = (current_generation_mw * 1000) * fuel_per_kwh * run_hours / 1000  # 1000 Nm3
                    fuel_used_recommended = (base_generation * 1000) * fuel_per_kwh * run_hours / 1000
                    fuel_cost_per_unit = random.uniform(*config['fuel_cost_range'])
                    fuel_unit = '1000Nm3'
                    co2_saved = (fuel_used_current - fuel_used_recommended) * config['co2_factor'] / 1000
                else:
                    continue

                adjustment_pct = (base_generation - current_generation_mw) / max_capacity_mw * 100
                fuel_saved = fuel_used_current - fuel_used_recommended
                cost_saved = fuel_saved * fuel_cost_per_unit

                data.append([
                    timestamp_str,
                    fuel_type,
                    round(max_capacity_mw, 2),
                    round(current_generation_mw, 3),
                    run_hours,
                    round(temp_C, 2),
                    round(humidity, 2),
                    round(pressure_hPa, 2),
                    predicted_efficiency,
                    round(base_generation, 3),
                    round(adjustment_pct, 2),
                    round(fuel_per_kwh, 4),
                    fuel_unit,
                    round(heat_rate_kcal_per_kwh, 2),
                    round(fuel_used_current, 4),
                    round(fuel_used_recommended, 4),
                    round(fuel_saved, 4),
                    round(fuel_cost_per_unit, 2),
                    round(cost_saved, 2),
                    round(co2_saved, 4)
                ])
        return data
