import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import os

CSV_FILE = "plant_data.csv"

# Load existing data
if not os.path.exists(CSV_FILE) or os.stat(CSV_FILE).st_size == 0:
    print("No data available for training.")
    exit()

df = pd.read_csv(CSV_FILE)

# Features to use
FEATURES = ["max_capacity_mw", "run_hours", "temp_C", "humidity_%", "pressure_hPa"]

# Train a model for each fuel type
for fuel in df['fuel_type'].unique():
    fuel_df = df[df['fuel_type'] == fuel]

    # Skip if not enough data
    if len(fuel_df) < 5:
        print(f"⚠️ Skipping {fuel} - not enough samples ({len(fuel_df)})")
        continue

    X = fuel_df[FEATURES]
    y = fuel_df["current_generation_mw"]

    # Train-test split for validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train RandomForest efficiently
    model = RandomForestRegressor(
        n_estimators=200,   # more trees → better accuracy, still efficient
        random_state=42,
        n_jobs=-1,          # use all CPU cores
        max_depth=12        # limit depth → faster & less overfitting
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print(f"✅ Trained model for {fuel}: R²={r2:.3f}, MAE={mae:.2f}")

    # Save
    joblib.dump(model, f"model_{fuel}.joblib")

# Clear CSV after training (keep headers)
df.iloc[0:0].to_csv(CSV_FILE, index=False)
print("Training data cleared for fresh collection.")
