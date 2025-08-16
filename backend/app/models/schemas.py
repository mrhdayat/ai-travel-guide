from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class BudgetRange(str, Enum):
    MURAH = "murah"
    SEDANG = "sedang"
    MAHAL = "mahal"

class PreferenceType(str, Enum):
    HALAL = "halal"
    VEGETARIAN = "vegetarian"
    ACCESSIBILITY = "accessibility"
    FAMILY_FRIENDLY = "family_friendly"

class AISource(str, Enum):
    WATSONX = "watsonx"
    HUGGINGFACE = "huggingface"
    REPLICATE = "replicate"

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_demo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Travel planning schemas
class TravelPlanRequest(BaseModel):
    destination: str = Field(..., description="Destinasi wisata")
    duration_days: int = Field(..., ge=1, le=14, description="Durasi perjalanan (1-14 hari)")
    budget_range: Optional[BudgetRange] = Field(None, description="Range budget")
    preferences: Optional[List[PreferenceType]] = Field(default=[], description="Preferensi khusus")
    departure_city: Optional[str] = Field(None, description="Kota keberangkatan")

class DailyItinerary(BaseModel):
    day: int
    date: str
    activities: List[Dict[str, Any]]
    estimated_cost: Optional[float] = None
    transport: Optional[Dict[str, Any]] = None

class CostEstimate(BaseModel):
    accommodation: Optional[float] = None
    food: Optional[float] = None
    transport: Optional[float] = None
    activities: Optional[float] = None
    total: float
    currency: str = "IDR"

class TravelPlanResponse(BaseModel):
    id: Optional[int] = None
    title: str
    destination: str
    duration_days: int
    daily_routes: List[DailyItinerary]
    cost_estimate: CostEstimate
    transport_options: Optional[Dict[str, Any]] = None
    preferences: Optional[List[str]] = None
    ai_source: AISource
    confidence_score: float
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Vision schemas
class VisionRequest(BaseModel):
    image_data: Optional[str] = Field(None, description="Base64 encoded image")
    
class LandmarkInfo(BaseModel):
    name: str
    description: str
    location: Optional[str] = None
    category: Optional[str] = None
    confidence: float

class VisionResponse(BaseModel):
    landmarks: List[LandmarkInfo]
    summary: str
    ai_source: AISource
    confidence: float

# Chat schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    answer: str
    session_id: str
    ai_source: AISource
    confidence: float
    suggestions: Optional[List[str]] = None

# POI schemas
class POIBase(BaseModel):
    name: str
    category: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    rating: Optional[float] = None
    price_range: Optional[str] = None

class POIResponse(POIBase):
    id: int
    city_id: int
    image_url: Optional[str] = None
    opening_hours: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# City schemas
class CityBase(BaseModel):
    name: str
    province: str
    country: str = "Indonesia"
    latitude: float
    longitude: float
    description: Optional[str] = None

class CityResponse(CityBase):
    id: int
    image_url: Optional[str] = None
    pois: Optional[List[POIResponse]] = None
    
    class Config:
        from_attributes = True
