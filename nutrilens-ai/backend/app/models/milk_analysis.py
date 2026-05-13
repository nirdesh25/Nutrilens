from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class MilkAnalysis(Base):
    __tablename__ = "milk_analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Sensor Readings
    ph = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    taste = Column(Integer, nullable=False)
    odor = Column(Integer, nullable=False)
    fat = Column(Integer, nullable=False)
    turbidity = Column(Integer, nullable=False)
    color = Column(Integer, nullable=False)
    
    # Prediction Results
    prediction = Column(String, nullable=False)  # high, medium, low
    risk_score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="milk_analyses")
