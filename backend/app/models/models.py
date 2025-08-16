from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    is_demo = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    travel_plans = relationship("TravelPlan", back_populates="user")

class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    province = Column(String(255), nullable=False)
    country = Column(String(100), default="Indonesia")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pois = relationship("PointOfInterest", back_populates="city")

class PointOfInterest(Base):
    __tablename__ = "pois"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # wisata, kuliner, belanja, etc.
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    rating = Column(Float, default=0.0)
    price_range = Column(String(50), nullable=True)  # murah, sedang, mahal
    image_url = Column(String(500), nullable=True)
    opening_hours = Column(JSON, nullable=True)
    contact_info = Column(JSON, nullable=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    city = relationship("City", back_populates="pois")

class TravelPlan(Base):
    __tablename__ = "travel_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False)
    duration_days = Column(Integer, nullable=False)
    budget_range = Column(String(50), nullable=True)
    preferences = Column(JSON, nullable=True)  # halal, vegetarian, accessibility
    itinerary = Column(JSON, nullable=False)  # detailed daily plans
    cost_estimate = Column(JSON, nullable=True)
    transport_options = Column(JSON, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ai_source = Column(String(50), nullable=True)  # watsonx, huggingface, replicate
    confidence_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="travel_plans")

class KnowledgeCache(Base):
    __tablename__ = "knowledge_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(JSON, nullable=False)
    source = Column(String(100), nullable=False)  # wikivoyage, wikipedia, osm
    ttl = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), index=True, nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    ai_source = Column(String(50), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
