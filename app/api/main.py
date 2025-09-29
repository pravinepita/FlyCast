from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.db import get_db, Prediction, Base, engine
from app.api.utils import predict_price
from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import List

class PredictionResponse(BaseModel):
    id: int
    airline: str
    source: str
    destination: str
    total_stops: int
    date_of_journey: date
    dep_datetime: datetime
    arrival_datetime: datetime
    duration_mins: int
    raw_duration: str | None = None
    predicted_price: float
    created_at: datetime

    class Config:
        orm_mode = True

# Create tables (run once or on startup)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkyFareCast Flight Price Prediction API")


# Request schema
class FlightRequest(BaseModel):
    Airline: str = Field(..., example="IndiGo")
    Source: str = Field(..., example="Delhi")
    Destination: str = Field(..., example="Cochin")
    Total_Stops: str = Field(..., example="1 stop")
    Date_of_Journey: str = Field(..., example="24/03/2019")  # dd/mm/yyyy
    Dep_Time: str = Field(..., example="22:20")  # HH:MM 24h
    Arrival_Time: str = Field(..., example="01:10 25/03/2019")  # HH:MM dd/mm/yyyy or HH:MM
    Duration: str = Field(..., example="2h 50m")


@app.post("/predict")
def predict_flight_price(request: FlightRequest, db: Session = Depends(get_db)):
    # 1. Get prediction from utils
    try:
        predicted_price = float(predict_price(request.dict()))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction error: {e}")

    # 2. Convert date/time strings to datetime/date objects for DB
    journey_date = datetime.strptime(request.Date_of_Journey, "%d/%m/%Y").date()
    dep_datetime = datetime.strptime(f"{request.Dep_Time} {request.Date_of_Journey}", "%H:%M %d/%m/%Y")
    try:
        arrival_datetime = datetime.strptime(request.Arrival_Time, "%H:%M %d/%m/%Y")
    except ValueError:
        # Arrival time without date, assume same day as journey
        arrival_datetime = datetime.strptime(f"{request.Arrival_Time} {request.Date_of_Journey}", "%H:%M %d/%m/%Y")

    # 3. Calculate duration in minutes (reuse your utils duration_to_minutes function logic)
    def duration_to_minutes(duration):
        total_mins = 0
        parts = duration.split()
        for part in parts:
            if 'h' in part:
                total_mins += int(part.replace('h', '')) * 60
            if 'm' in part:
                total_mins += int(part.replace('m', ''))
        return total_mins

    duration_mins = duration_to_minutes(request.Duration)

    # 4. Save prediction in DB
    prediction_record = Prediction(
        airline=request.Airline,
        source=request.Source,
        destination=request.Destination,
        total_stops=int(request.Total_Stops.split()[0]) if 'stop' in request.Total_Stops else 0,
        date_of_journey=journey_date,
        dep_datetime=dep_datetime,
        arrival_datetime=arrival_datetime,
        duration_mins=duration_mins,
        raw_duration=request.Duration,
        predicted_price=predicted_price
    )

    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)

    # 5. Return prediction and saved record id
    return {
        "prediction_id": prediction_record.id,
        "predicted_price": predicted_price
    }

@app.get("/predictions", response_model=List[PredictionResponse])
def get_predictions(limit: int = 20, db: Session = Depends(get_db)):
    """
    Fetch latest saved flight price predictions from DB.
    Optional query param:
    - limit: number of records to fetch (default 20)
    """
    predictions = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    return predictions
