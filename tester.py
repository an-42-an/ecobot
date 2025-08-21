import joblib
import pandas as pd
import os

# Models to test
MODEL_FILES = {
    "Coal": "model_coal.joblib",
    "Oil": "model_oil.joblib",
    "Natural Gas": "model_natural_gas.joblib"  # make sure filename matches your saved model
}

# Define sample input (with feature names)
sample_input = pd.DataFrame([{
    "max_capacity_mw": 150,
    "run_hours": 20,
    "temp_C": 30,
    "humidity_%": 50,
    "pressure_hPa": 1010
}])

# Actual generation (for comparison)
current_generation = 200.0

# Run tests
for fuel, model_file in MODEL_FILES.items():
    if not os.path.exists(model_file):
        print(f"❌ Model file not found for {fuel}: {model_file}")
        continue

    # Load model
    model = joblib.load(model_file)

    # Predict
    predicted = model.predict(sample_input)[0]

    # Calculate difference
    diff = current_generation - predicted
    diff_percent = (diff / current_generation) * 100

    # Print result
    print(f"✅ Model: {fuel}")
    print(f"Sample Input: {sample_input.to_dict(orient='records')[0]}")
    print(f"Predicted Generation (MW): {predicted:.2f}")
    print(f"Current Generation (MW): {current_generation:.2f}")
    print(f"Difference: {diff:.2f} MW ({diff_percent:.2f}%)")
    print("-" * 60)
