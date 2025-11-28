# dashboard/ml/model.py
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style='whitegrid')
import io, base64

def _img_from_plt():
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=150)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.clf()
    return img_b64

def run_analysis(temp_file, rain_file, moisture_file, crop_file, num_regions=5, w1=0.4, w2=0.5, w3=0.1, quarter_choice=1):
    # Load CSVs as DataFrames (no header expected)
    temperature = pd.read_csv(temp_file, header=None)
    rainfall = pd.read_csv(rain_file, header=None)
    moisture = pd.read_csv(moisture_file, header=None)
    crop_type = pd.read_csv(crop_file, header=None)

    # Add Day column
    days = np.arange(1, temperature.shape[0] + 1)
    for df in [temperature, rainfall, moisture, crop_type]:
        df['Day'] = days

    regions = [f"Region {chr(65+i)}" for i in range(num_regions)]

    # Mean stats
    mean_temp_per_region = temperature.drop(columns=['Day']).mean().values[:num_regions]
    mean_rain_per_region = rainfall.drop(columns=['Day']).mean().values[:num_regions]
    mean_moist_per_region = moisture.drop(columns=['Day']).mean().values[:num_regions]

    stats = []
    for i, r in enumerate(regions):
        stats.append({
            "region": r,
            "mean_temp": float(mean_temp_per_region[i]),
            "mean_rain": float(mean_rain_per_region[i]),
            "mean_moisture": float(mean_moist_per_region[i]),
        })

    # Yield calculation per day and averaged
    yield_df = pd.DataFrame()
    for i, reg in enumerate(regions):
        yi = (w1 * temperature[i] + w2 * rainfall[i] + w3 * moisture[i])
        yield_df[reg] = yi

    yield_avg = yield_df.mean()

    # Correlation calculation (flattened as earlier)
    rain_flat = rainfall.drop(columns=['Day']).values.flatten()
    moist_flat = moisture.drop(columns=['Day']).values.flatten()
    corr = float(np.corrcoef(rain_flat, moist_flat)[0,1])

    # PLOTS -> base64 strings
    plots = {}

    # 1) Yield bar chart
    plt.figure(figsize=(7,5))
    sns.barplot(x=regions, y=yield_avg.values)
    plt.title("Average Yield Index by Region")
    plots['yield_chart'] = _img_from_plt()

    # 2) Rainfall trend region A
    plt.figure(figsize=(10,4))
    plt.plot(rainfall['Day'], rainfall[0])
    plt.title("Daily Rainfall Trend — Region A")
    plt.xlabel("Day")
    plt.ylabel("Rainfall (mm)")
    plots['rain_trend'] = _img_from_plt()

    # 3) Temperature trend region A
    plt.figure(figsize=(10,4))
    plt.plot(temperature['Day'], temperature[0])
    plt.title("Daily Temperature Trend — Region A")
    plt.xlabel("Day")
    plt.ylabel("Temperature (°C)")
    plots['temp_trend'] = _img_from_plt()

    # 4) Scatter rain vs yield region A
    plt.figure(figsize=(7,5))
    plt.scatter(rainfall[0], yield_df['Region A'], alpha=0.5)
    plt.title("Rainfall vs Yield Index — Region A")
    plt.xlabel("Rainfall (mm)")
    plt.ylabel("Yield Index")
    plots['scatter'] = _img_from_plt()

    # 5) Heatmap correlation region A
    df_corr = pd.DataFrame({
        'Temperature': temperature[0],
        'Rainfall': rainfall[0],
        'Moisture': moisture[0],
        'Yield': yield_df['Region A']
    })
    plt.figure(figsize=(6,5))
    sns.heatmap(df_corr.corr(), annot=True, cmap='coolwarm')
    plt.title("Correlation Heatmap — Region A")
    plots['heatmap'] = _img_from_plt()

    # Return results + a combined DataFrame useful for training/prediction:
    # Build a training-style DataFrame per day + region average yield (you may adapt)
    # Create a simple flattened DataFrame: each row = (Temp, Rain, Moisture, Yield) for Region A..E
    train_rows = []
    for i, reg in enumerate(regions):
        for day in range(temperature.shape[0]):
            train_rows.append({
                "Region": reg,
                "Temperature": float(temperature.iloc[day, i]),
                "Rainfall": float(rainfall.iloc[day, i]),
                "SoilMoisture": float(moisture.iloc[day, i]),
                "Yield": float(yield_df.iloc[day, i])
            })
    training_df = pd.DataFrame(train_rows)

    return {
        "stats": stats,
        "yield_avg": yield_avg.round(3).to_dict(),
        "corr_rain_moist": round(corr,3),
        "plots": plots,
        "training_df": training_df  # DataFrame (not JSON-serializable) — can be saved by caller
    }
