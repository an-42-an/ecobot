# 🔥 Enhanced Thermal Plant Prediction System

A sophisticated machine learning system that predicts thermal power plant efficiency using realistic physics-based data generation and comprehensive accuracy evaluation.

## 🌟 Key Features

### Realistic Data Generation
- **Physics-based formulas** for thermal efficiency calculations
- **Real plant parameters** including subcritical, supercritical, and ultra-supercritical plants
- **Seasonal temperature variations** with realistic daily cycles
- **Environmental correlations** between temperature, humidity, and pressure
- **Equipment degradation** simulation over time

### Advanced Model Evaluation
- **Multiple accuracy metrics**: MAE, MSE, RMSE, R² Score
- **Percentage accuracy** calculations
- **Sample prediction comparisons**
- **Statistical analysis** of predictions vs. actual values
- **Performance interpretation** with color-coded results

### Realistic Plant Types
- **Subcritical**: 200-500 MW, 32-38% efficiency
- **Supercritical**: 300-600 MW, 38-42% efficiency  
- **Ultra-supercritical**: 400-800 MW, 42-46% efficiency

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Complete Pipeline Test
```bash
python test_pipeline.py
```

This will:
- Generate realistic training data
- Train the model
- Test predictions and show accuracy metrics

### 3. Individual Components

#### Generate Training Data
```bash
python generator.py
```

#### Train Model
```bash
python trainer.py
```

#### Test Predictions & Get Accuracy
```bash
python predict.py
```

## 📊 Output Files

- **`coal_plant_data.csv`**: Training data with realistic thermal plant parameters
- **`coal_adjustment_model.joblib`**: Trained machine learning model
- **`test_results.csv`**: Comprehensive test results and predictions

## 🔬 Physics Formulas Used

### Efficiency Calculation
```
Efficiency = Base_Efficiency × Temp_Factor × Humidity_Factor × Pressure_Factor × Hours_Factor × Degradation_Factor
```

### Temperature Effect
```
Temp_Factor = 1 - Sensitivity × (Temperature - 25°C)
```

### Heat Rate
```
Heat_Rate = 860 / Efficiency  # kcal/kWh
```

### Coal Consumption
```
Coal_per_kWh = Heat_Rate / 7000  # kg/kWh (assuming 7000 kcal/kg coal)
```

## 📈 Accuracy Metrics Explained

- **MAE (Mean Absolute Error)**: Average absolute difference between predicted and actual values
- **MSE (Mean Squared Error)**: Average squared difference (penalizes larger errors more)
- **RMSE (Root Mean Square Error)**: Square root of MSE, in same units as target
- **R² Score**: Proportion of variance explained by the model (0-1, higher is better)
- **Accuracy Percentage**: How close predictions are to actual values on average

## 🏭 Plant Type Characteristics

| Plant Type | Capacity Range | Efficiency Range | Heat Rate Range | Temperature Sensitivity |
|------------|----------------|------------------|-----------------|------------------------|
| Subcritical | 200-500 MW | 32-38% | 2400-2600 kcal/kWh | 0.002/°C |
| Supercritical | 300-600 MW | 38-42% | 2200-2400 kcal/kWh | 0.0018/°C |
| Ultra-supercritical | 400-800 MW | 42-46% | 2000-2200 kcal/kWh | 0.0015/°C |

## 🔧 Customization

### Modify Plant Parameters
Edit the `plant_types` dictionary in `generator.py` to adjust:
- Efficiency ranges
- Capacity ranges
- Environmental sensitivity factors

### Adjust Data Generation
Modify `generate_realistic_data()` method to:
- Change number of samples
- Adjust environmental ranges
- Modify seasonal variations

### Custom Accuracy Metrics
Add new metrics in `evaluate_model_accuracy()` function in `predict.py`

## 📋 Sample Output

```
🔥 Enhanced Thermal Plant Predictor with Realistic Data Generation
======================================================================

✅ Model loaded successfully from coal_adjustment_model.joblib

📊 Generating realistic thermal plant test data...
✅ Generated 200 realistic test samples

🔍 Evaluating model accuracy...

📈 MODEL ACCURACY RESULTS:
----------------------------------------
Mean Absolute Error (MAE): 0.023456
Mean Squared Error (MSE): 0.000789
Root Mean Squared Error (RMSE): 0.028091
R² Score: 0.8234
Accuracy Percentage: 89.67%

📊 INTERPRETATION:
----------------------------------------
🟢 Excellent model performance - High accuracy in predictions

🎯 SAMPLE PREDICTIONS (First 10 samples):
------------------------------------------------------------
Sample | Actual Eff | Predicted Eff | Difference | Plant Type
------------------------------------------------------------
     1 |     0.3845 |        0.3812 |    -0.0033 | supercritical
     2 |     0.3567 |        0.3598 |     0.0031 | subcritical
     3 |     0.4234 |        0.4201 |    -0.0033 | ultra_supercritical
```

## 🎯 Use Cases

- **Power Plant Optimization**: Predict optimal operating conditions
- **Efficiency Monitoring**: Track plant performance over time
- **Maintenance Planning**: Identify efficiency degradation patterns
- **Environmental Impact**: Calculate CO2 emissions and coal savings
- **Cost Analysis**: Estimate operational cost savings

## 🔍 Troubleshooting

### Common Issues

1. **Model file not found**: Run `python trainer.py` first
2. **Insufficient training data**: Run `python generator.py` to generate more data
3. **Import errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

### Performance Tips

- Generate at least 100 training samples for good model performance
- Use realistic parameter ranges for your specific plant type
- Monitor R² score - aim for >0.6 for acceptable performance

## 📚 Technical Details

### Data Features
- `max_capacity_mw`: Plant maximum capacity in MW
- `current_generation_mw`: Current power generation in MW
- `run_hours`: Operating hours
- `temp_C`: Ambient temperature in °C
- `humidity_%`: Relative humidity percentage
- `pressure_hPa`: Atmospheric pressure in hPa

### Target Variable
- `predicted_efficiency`: Plant thermal efficiency (0.32-0.46)

### Model Type
- **Linear Regression** with scikit-learn
- Suitable for continuous efficiency prediction
- Handles multiple input features effectively

## 🤝 Contributing

Feel free to enhance the system by:
- Adding new plant types
- Implementing more sophisticated physics models
- Adding new accuracy metrics
- Improving data generation algorithms

## 📄 License

This project is open source and available under the MIT License.
