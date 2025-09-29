# app/api/db.py
import os
from sqlalchemy import (
    create_engine, Column, Integer, SmallInteger, Text,
    Date, DateTime, Numeric, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get DB connection string from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create SQLAlchemy engine (sync)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory to generate DB sessions
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for ORM models
Base = declarative_base()


class Prediction(Base):
    """
    ORM model mapping to the 'predictions' table.
    """
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    airline = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    destination = Column(Text, nullable=False)
    total_stops = Column(SmallInteger, nullable=False)
    date_of_journey = Column(Date, nullable=False)
    dep_datetime = Column(DateTime(timezone=False), nullable=False)
    arrival_datetime = Column(DateTime(timezone=False), nullable=False)
    duration_mins = Column(Integer, nullable=False)
    raw_duration = Column(Text)
    predicted_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())


def get_db():
    """
    FastAPI dependency function to provide a DB session.
    Use in endpoints with Depends(get_db).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
