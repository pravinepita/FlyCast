import streamlit as st
import requests
from datetime import datetime

API_URL = "http://127.0.0.1:8000"  # FastAPI URL

st.title("SkyFareCast Flight Price Prediction")

# Input form
with st.form("flight_form"):
    airline = st.selectbox("Airline", ["IndiGo", "Air India", "SpiceJet", "GoAir", "Jet Airways"])
    source = st.selectbox("Source", ["Delhi", "Mumbai", "Chennai", "Kolkata"])
    destination = st.selectbox("Destination", ["Cochin", "Delhi", "Hyderabad", "Kolkata", "New Delhi"])
    total_stops = st.selectbox("Total Stops", ["non-stop", "1 stop", "2 stops", "3 stops", "4 stops"])
    date_of_journey = st.date_input("Date of Journey", datetime.now())
    dep_time = st.time_input("Departure Time")
    arrival_time = st.time_input("Arrival Time")
    duration = st.text_input("Duration (e.g. 2h 50m)", "2h 50m")
    
    submitted = st.form_submit_button("Predict Price")

if submitted:
    # Prepare request data in expected format
    payload = {
        "Airline": airline,
        "Source": source,
        "Destination": destination,
        "Total_Stops": total_stops,
        "Date_of_Journey": date_of_journey.strftime("%d/%m/%Y"),
        "Dep_Time": dep_time.strftime("%H:%M"),
        "Arrival_Time": arrival_time.strftime("%H:%M %d/%m/%Y"),
        "Duration": duration
    }
    
    try:
        response = requests.post(f"{API_URL}/predict", json=payload)
        response.raise_for_status()
        data = response.json()
        st.success(f"Predicted Flight Price: ₹{data['predicted_price']:.2f}")
    except Exception as e:
        st.error(f"Error: {e}")

st.header("Recent Predictions")

try:
    resp = requests.get(f"{API_URL}/predictions?limit=10")
    resp.raise_for_status()
    predictions = resp.json()

    for pred in predictions:
        st.write(
            f"✈️ **{pred['airline']}** | From **{pred['source']}** to **{pred['destination']}** | "
            f"Date: {pred['date_of_journey']} | Stops: {pred['total_stops']} | "
            f"Price: ₹{pred['predicted_price']:.2f} | Predicted at: {pred['created_at']}"
        )
except Exception as e:
    st.error(f"Failed to load recent predictions: {e}")
