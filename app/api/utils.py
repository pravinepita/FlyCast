import os
import pandas as pd
from catboost import CatBoostRegressor
import joblib

# Load model and columns once when module loads (singleton pattern)
model_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'catboost_flight_price_model.cbm')
columns_path = os.path.join(os.path.dirname(__file__), '..', 'model', 'model_columns.pkl')

model = CatBoostRegressor()
model.load_model(model_path)

model_columns = joblib.load(columns_path)


def preprocess_input(input_dict):
    """
    Preprocess input dict to DataFrame matching model columns.

    input_dict example:
    {
        'Airline': 'IndiGo',
        'Source': 'Delhi',
        'Destination': 'Cochin',
        'Total_Stops': '1 stop',
        'Date_of_Journey': '24/03/2019',
        'Dep_Time': '22:20',
        'Arrival_Time': '01:10 25/03/2019',
        'Duration': '2h 50m'
    }
    """
    # 1. Map Total_Stops
    stops_mapping = {
        'non-stop': 0,
        '1 stop': 1,
        '2 stops': 2,
        '3 stops': 3,
        '4 stops': 4
    }
    total_stops = stops_mapping.get(input_dict['Total_Stops'].lower(), 0)

    # 2. Date_of_Journey features
    date = pd.to_datetime(input_dict['Date_of_Journey'], format='%d/%m/%Y')
    journey_day = date.day
    journey_month = date.month

    # 3. Dep_Time features
    dep_time = pd.to_datetime(input_dict['Dep_Time'], format='%H:%M')
    dep_hour = dep_time.hour
    dep_minute = dep_time.minute

    # 4. Arrival_Time features
    try:
        arrival_time = pd.to_datetime(input_dict['Arrival_Time'], format='%H:%M %d/%m/%Y')
    except Exception:
        arrival_time = pd.to_datetime(input_dict['Arrival_Time'], format='%H:%M')
    arrival_hour = arrival_time.hour
    arrival_minute = arrival_time.minute

    # 5. Duration in minutes
    def duration_to_minutes(duration):
        time_parts = duration.split()
        total_mins = 0
        for part in time_parts:
            if 'h' in part:
                total_mins += int(part.replace('h', ''))
                total_mins *= 60
            if 'm' in part:
                total_mins += int(part.replace('m', ''))
        return total_mins

    duration_mins = duration_to_minutes(input_dict['Duration'])

    # 6. Create base dataframe with all features except one-hot
    base_dict = {
        'Total_Stops': total_stops,
        'journey_day': journey_day,
        'journey_month': journey_month,
        'dep_hour': dep_hour,
        'dep_minute': dep_minute,
        'arrival_hour': arrival_hour,
        'arrival_minute': arrival_minute,
        'duration_mins': duration_mins
    }

    df = pd.DataFrame([base_dict])

    # 7. One-hot encode categorical columns manually to match model_columns
    categorical_columns = ['Airline', 'Source', 'Destination']

    for col in categorical_columns:
        unique_vals = [c for c in model_columns if c.startswith(col + '_')]
        for val in unique_vals:
            category = val.split('_', 1)[1]
            df[val] = 1 if input_dict[col] == category else 0

    # 8. Add any missing columns with 0 (if some columns were not set)
    missing_cols = set(model_columns) - set(df.columns)
    for col in missing_cols:
        df[col] = 0

    # 9. Reorder columns to match model input exactly
    df = df[model_columns]

    return df


def predict_price(input_dict):
    """
    Given raw input dict, preprocess and predict price using CatBoost model.
    Returns float predicted price.
    """
    df = preprocess_input(input_dict)
    prediction = model.predict(df)[0]
    return prediction
