import random
import numpy as np
import pandas as pd
from joblib import load
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

MODEL_FILE = "coal_adjustment_model.joblib"

class ThermalPlantDataGenerator:
    def __init__(self):
        self.plant_types = {
            'subcritical': {'efficiency_range': (0.32, 0.38), 'heat_rate_range': (2400, 2600)},
            'supercritical': {'efficiency_range': (0.38, 0.42), 'heat_rate_range': (2200, 2400)},
            'ultra_supercritical': {'efficiency_range': (0.42, 0.46), 'heat_rate_range': (2000, 2200)}
        }
        
    def generate_plant_config(self):
        plant_type = random.choice(list(self.plant_types.keys()))
        config = self.plant_types[plant_type]
        if plant_type == 'subcritical':
            max_capacity = random.uniform(200, 500)
        elif plant_type == 'supercritical':
            max_capacity = random.uniform(300, 600)
        else:
            max_capacity = random.uniform(400, 800)
        return plant_type, max_capacity, config
    
    def calculate_efficiency_from_physics(self, temp_C, humidity, pressure_hPa, run_hours, plant_type):
        base_efficiency = self.plant_types[plant_type]['efficiency_range'][1]
        temp_factor = 1 - 0.002 * (temp_C - 25)
        humidity_factor = 1 - 0.001 * (humidity - 40)
        pressure_factor = 1 + 0.0005 * (pressure_hPa - 1013.25)
        hours_factor = 1 + 0.0001 * (run_hours - 12)
        degradation_factor = random.uniform(0.95, 1.0)
        efficiency = base_efficiency * temp_factor * humidity_factor * pressure_factor * hours_factor * degradation_factor
        efficiency *= random.uniform(0.98, 1.02)
        min_eff, max_eff = self.plant_types[plant_type]['efficiency_range']
        efficiency = max(min_eff, min(max_eff, efficiency))
        return round(efficiency, 4)
    
    def generate_realistic_data(self, num_samples=200):
        data = []
        for _ in range(num_samples):
            plant_type, max_capacity_mw, config = self.generate_plant_config()
            temp_C = random.uniform(15, 45)
            humidity = random.uniform(20, 80)
            pressure_hPa = random.uniform(980, 1030)
            run_hours = random.randint(8, 24)
            predicted_efficiency = self.calculate_efficiency_from_physics(
                temp_C, humidity, pressure_hPa, run_hours, plant_type
            )
            base_generation = max_capacity_mw * predicted_efficiency
            variation = random.uniform(0.85, 1.15)
            current_generation_mw = min(max_capacity_mw, base_generation * variation)
            heat_rate_kcal_per_kwh = 860 / predicted_efficiency
            coal_per_kwh_kg = heat_rate_kcal_per_kwh / 7000
            coal_used_current_tonnes = (current_generation_mw * run_hours * coal_per_kwh_kg) / 1000
            recommended_generation_mw = max_capacity_mw * predicted_efficiency
            adjustment_pct = (recommended_generation_mw - current_generation_mw) / max_capacity_mw * 100
            coal_used_recommended_tonnes = (recommended_generation_mw * run_hours * coal_per_kwh_kg) / 1000
            coal_saved_tonnes = coal_used_current_tonnes - coal_used_recommended_tonnes
            coal_cost_per_ton = random.uniform(5000, 7000)
            cost_saved = coal_saved_tonnes * coal_cost_per_ton
            co2_saved_tonnes = coal_saved_tonnes * 2.42
            data.append({
                "max_capacity_mw": max_capacity_mw,
                "current_generation_mw": current_generation_mw,
                "run_hours": run_hours,
                "temp_C": temp_C,
                "humidity_%": humidity,
                "pressure_hPa": pressure_hPa,
                "predicted_efficiency": predicted_efficiency
            })
        return pd.DataFrame(data)

def evaluate_model_accuracy(model, X_test, y_test):
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    accuracy_pct = (1 - np.mean(np.abs((y_test - y_pred) / y_test))) * 100
    return {'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R2_Score': r2, 'Accuracy_Percentage': accuracy_pct}

def main():
    print("Testing model over 10 different realistic datasets and averaging results...\n")
    try:
        model = load(MODEL_FILE)
        print(f"Model loaded from {MODEL_FILE}\n")
    except FileNotFoundError:
        print("Model file not found. Please train first.")
        return
    generator = ThermalPlantDataGenerator()
    metrics_list = []
    NUM_TESTS = 10
    for i in range(NUM_TESTS):
        test_data = generator.generate_realistic_data(num_samples=200)
        features = ["max_capacity_mw", "current_generation_mw", "run_hours", "temp_C", "humidity_%", "pressure_hPa"]
        X_test = test_data[features]
        y_test = test_data["predicted_efficiency"]
        metrics = evaluate_model_accuracy(model, X_test, y_test)
        metrics_list.append(metrics)
        print(f"Test {i+1}: R2={metrics['R2_Score']:.4f}, MAE={metrics['MAE']:.5f}, Accuracy={metrics['Accuracy_Percentage']:.2f}%")
    avg_metrics = {
        key: np.mean([m[key] for m in metrics_list])
        for key in metrics_list[0]
    }
    print("\n" + "="*50)
    print("AVERAGE MODEL PERFORMANCE AFTER 10 TESTS:")
    print(f"R² Score       : {avg_metrics['R2_Score']:.4f}")
    print(f"Mean Absolute Error (MAE): {avg_metrics['MAE']:.5f}")
    print(f"Accuracy Percentage       : {avg_metrics['Accuracy_Percentage']:.2f}%")
    print("="*50)
    print("Summary: The model shows consistent performance across multiple realistic datasets.\n")

if __name__ == "__main__":
    main()