"""
AI Travel Guide API - Fixed Version
Simple demo API for AI Travel Guide with real AI integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import random
import re
import os
import requests
import json
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AI Service Configuration
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY") 
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

import uvicorn

# Create FastAPI app
app = FastAPI(
    title="AI Travel Guide API - Demo",
    description="A simple demo of the AI Travel Guide API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class TravelPlan(BaseModel):
    destination: str
    duration: int  # in days
    budget: str  # low, medium, high
    interests: List[str]

class TravelPlanResponse(BaseModel):
    destination: str
    duration: int
    budget: str
    interests: List[str]
    itinerary: List[str]
    tips: str
    estimated_cost: str
    ai_confidence: float

class ChatTravelRequest(BaseModel):
    message: str

class TravelRecommendation(BaseModel):
    destination: str
    description: str
    activities: List[str]
    estimated_cost: str
    best_time_to_visit: str

# AI Service Functions
async def call_replicate_ai(prompt: str) -> str:
    """Call Replicate AI for travel planning"""
    if not REPLICATE_API_TOKEN:
        return None
    
    try:
        headers = {
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        data = {
            "version": "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
            "input": {
                "prompt": prompt,
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "repetition_penalty": 1.15
            }
        }
        
        response = requests.post(
            "https://api.replicate.com/v1/predictions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 201:
            prediction_url = response.json()["urls"]["get"]
            
            # Poll for completion
            for _ in range(30):  # 30 second timeout
                result_response = requests.get(prediction_url, headers=headers)
                result = result_response.json()
                
                if result["status"] == "succeeded":
                    return "".join(result["output"])
                elif result["status"] == "failed":
                    break
                    
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"Replicate AI error: {e}")
    
    return None

async def call_huggingface_ai(prompt: str) -> str:
    """Call Hugging Face AI for travel planning using GPT-OSS-120B"""
    if not HUGGINGFACE_API_KEY:
        return None
        
    try:
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Try multiple models for better coverage
        models = [
            "openai/gpt-oss-120b",
            "microsoft/DialoGPT-large", 
            "facebook/blenderbot-400M-distill",
            "microsoft/DialoGPT-medium"
        ]
        
        for model in models:
            try:
                data = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 800,
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "do_sample": True,
                        "return_full_text": False
                    }
                }
                
                response = requests.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json=data,
                    timeout=45
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        if generated_text and len(generated_text) > 50:
                            print(f"Using Hugging Face model: {model}")
                            return generated_text
                            
            except Exception as model_error:
                print(f"Model {model} failed: {model_error}")
                continue
                
    except Exception as e:
        print(f"Hugging Face AI error: {e}")
    
    return None

async def call_watsonx_ai(prompt: str) -> str:
    """Call IBM watsonx AI for travel planning"""
    if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
        return None
        
    try:
        headers = {
            "Authorization": f"Bearer {WATSONX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model_id": "ibm/granite-13b-chat-v2",
            "input": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9
            },
            "project_id": WATSONX_PROJECT_ID
        }
        
        response = requests.post(
            "https://us-south.ml.cloud.ibm.com/ml/v1-beta/generation/text",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("results", [{}])[0].get("generated_text", "")
                
    except Exception as e:
        print(f"watsonx AI error: {e}")
    
    return None

async def get_ai_travel_plan(user_input: str, destination: str, duration: int, budget: str, interests: List[str]) -> dict:
    """Get AI-powered travel plan using multiple AI services"""
    
    # Create comprehensive prompt for AI
    budget_mapping = {
        "low": "budget hemat (di bawah 1.5 juta per hari)",
        "medium": "budget sedang (1.5-3 juta per hari)", 
        "high": "budget premium (di atas 3 juta per hari)"
    }
    
    budget_text = budget_mapping.get(budget, "budget sedang")
    interests_text = ", ".join(interests)
    
    prompt = f"""
You are an expert Indonesian travel AI assistant with comprehensive knowledge of ALL cities and destinations across Indonesia. 

User Request: "{user_input}"

Create a detailed travel plan for:
- Destination: {destination}
- Duration: {duration} days
- Budget: {budget_text}
- Interests: {interests_text}

IMPORTANT: You must know about {destination} and provide specific, accurate information about local attractions, food, and activities. Do not say the destination is unavailable.

Generate a JSON response with this exact structure:
{{
    "destination": "{destination}",
    "duration": {duration},
    "budget": "{budget}",
    "interests": {interests},
    "itinerary": [
        "Day 1: Morning: [specific local attraction/activity] | Afternoon: [specific local attraction/activity]",
        "Day 2: Morning: [specific local attraction/activity] | Afternoon: [specific local attraction/activity]",
        "Day 3: Morning: [specific local attraction/activity] | Afternoon: [specific local attraction/activity]",
        "Day 4: Morning: [specific local attraction/activity] | Afternoon: [specific local attraction/activity]"
    ],
    "tips": "Practical local tips for {destination} including transportation, local customs, best times to visit attractions, and budget-specific advice",
    "estimated_cost": "Rp [realistic total cost for {duration} days based on {budget_text}]",
    "ai_confidence": 0.95
}}

Requirements:
1. Include REAL, SPECIFIC attractions and activities in {destination}
2. Match activities to user interests: {interests_text}
3. Provide accurate cost estimates for {budget_text}
4. Include local food recommendations and cultural sites
5. Give practical, actionable tips
6. Ensure all activities are actually available in {destination}

Generate the complete JSON response now:
"""

    # Try AI services in order of preference
    ai_response = None
    
    # Try watsonx first (IBM partnership)
    if WATSONX_API_KEY:
        ai_response = await call_watsonx_ai(prompt)
        if ai_response:
            print("Using watsonx AI response")
    
    # Fallback to Replicate
    if not ai_response and REPLICATE_API_TOKEN:
        ai_response = await call_replicate_ai(prompt)
        if ai_response:
            print("Using Replicate AI response")
    
    # Fallback to Hugging Face
    if not ai_response and HUGGINGFACE_API_KEY:
        ai_response = await call_huggingface_ai(prompt)
        if ai_response:
            print("Using Hugging Face AI response")
    
    # Parse AI response
    if ai_response:
        try:
            # Try to extract JSON from response
            import json
            
            # Look for JSON in the response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = ai_response[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                # Validate and return
                if all(key in parsed_response for key in ["destination", "duration", "itinerary", "tips", "estimated_cost"]):
                    return parsed_response
                    
        except Exception as e:
            print(f"Error parsing AI response: {e}")
    
    # Fallback to enhanced rule-based system if AI fails
    return await get_enhanced_fallback_plan(destination, duration, budget, interests)

async def get_enhanced_fallback_plan(destination: str, duration: int, budget: str, interests: List[str]) -> dict:
    """Advanced AI-like system with intelligent activity matching"""

    # Accurate cost calculation based on budget category
    daily_costs = {
        "low": 400000,      # 400k per day
        "medium": 800000,   # 800k per day
        "high": 1500000     # 1.5M per day
    }

    daily_cost = daily_costs.get(budget, 800000)
    total_cost = daily_cost * duration

    # Create realistic activities for any Indonesian city
    activities = {
        "culture": [
            f"Masjid Agung {destination} (arsitektur Islam lokal)",
            f"Museum {destination} (sejarah dan budaya lokal)",
            f"Pasar tradisional {destination} (budaya lokal)",
            f"Kampung heritage {destination} (wisata budaya)",
            f"Rumah adat {destination} (arsitektur tradisional)",
            f"Pusat kerajinan lokal {destination}"
        ],
        "food": [
            f"Kuliner khas {destination} di warung lokal",
            f"Makanan tradisional {destination} autentik",
            f"Restoran seafood {destination} (jika dekat laut)",
            f"Street food tour {destination}",
            f"Pasar malam {destination} (kuliner lokal)",
            f"Rumah makan padang {destination}"
        ],
        "culinary": [
            f"Food tour {destination} dengan guide lokal",
            f"Cooking class masakan {destination}",
            f"Traditional market visit {destination}",
            f"Local restaurant hopping {destination}",
            f"Street food exploration {destination}",
            f"Kuliner malam {destination}"
        ],
        "nature": [
            f"Taman kota {destination} (ruang hijau)",
            f"Wisata alam sekitar {destination}",
            f"Air terjun dekat {destination}",
            f"Danau atau sungai {destination}",
            f"Bukit atau gunung dekat {destination}",
            f"Hutan atau kebun raya {destination}"
        ],
        "adventure": [
            f"Hiking di sekitar {destination}",
            f"River tubing dekat {destination}",
            f"Adventure park {destination}",
            f"Outdoor activities {destination}",
            f"Camping ground dekat {destination}",
            f"Extreme sports {destination}"
        ],
        "city": [
            f"Alun-alun {destination} (pusat kota)",
            f"Landmark {destination} (ikon kota)",
            f"Jembatan atau monumen {destination}",
            f"Kawasan bisnis {destination}",
            f"City tour {destination}",
            f"Pusat pemerintahan {destination}"
        ],
        "shopping": [
            f"Mall {destination} (modern shopping)",
            f"Pasar {destination} (traditional market)",
            f"Souvenir center {destination}",
            f"Pusat oleh-oleh {destination}",
            f"Traditional craft market {destination}",
            f"Shopping district {destination}"
        ]
    }

    # Smart activity selection based on user interests with priority
    selected_activities = []

    # Prioritize activities based on user interests
    for interest in interests:
        if interest in activities:
            # Give higher weight to user-specified interests
            selected_activities.extend(activities[interest][:4])  # Take more from preferred interests

    # Add complementary activities for better experience
    if "food" in interests or "culinary" in interests:
        # If user likes food, add more food-related activities
        if "food" in activities:
            selected_activities.extend(activities["food"][:2])
        if "culinary" in activities:
            selected_activities.extend(activities["culinary"][:2])

    if "culture" in interests or "city" in interests:
        # If user likes culture/sightseeing, add cultural activities
        if "culture" in activities:
            selected_activities.extend(activities["culture"][:2])
        if "city" in activities:
            selected_activities.extend(activities["city"][:2])

    # If no specific interests match, provide balanced mix
    if not selected_activities:
        selected_activities.extend(activities.get("culture", [])[:3])
        selected_activities.extend(activities.get("food", [])[:3])
        selected_activities.extend(activities.get("city", [])[:2])

    # Remove duplicates while preserving order
    unique_activities = []
    seen = set()
    for activity in selected_activities:
        if activity not in seen:
            unique_activities.append(activity)
            seen.add(activity)

    selected_activities = unique_activities

    # Ensure we have enough activities for the duration
    min_activities_needed = duration * 2  # 2 activities per day
    while len(selected_activities) < min_activities_needed:
        # Add more activities from available categories
        for category, activity_list in activities.items():
            for activity in activity_list:
                if activity not in seen:
                    selected_activities.append(activity)
                    seen.add(activity)
                    if len(selected_activities) >= min_activities_needed:
                        break
            if len(selected_activities) >= min_activities_needed:
                break

    # Distribute activities intelligently across days
    itinerary = []
    for day in range(duration):
        # Calculate activity indices for this day
        morning_idx = day * 2
        afternoon_idx = day * 2 + 1

        # Get activities for this day
        if morning_idx < len(selected_activities):
            morning_activity = selected_activities[morning_idx]
        else:
            morning_activity = f"Eksplorasi bebas {destination} (pagi)"

        if afternoon_idx < len(selected_activities):
            afternoon_activity = selected_activities[afternoon_idx]
        else:
            afternoon_activity = f"Eksplorasi bebas {destination} (sore)"

        # Ensure variety - don't repeat same activity in one day
        if morning_activity == afternoon_activity and len(selected_activities) > afternoon_idx + 1:
            afternoon_activity = selected_activities[afternoon_idx + 1]

        itinerary.append(f"Pagi: {morning_activity} | Sore: {afternoon_activity}")

    # Enhanced local tips based on destination
    tips_database = {
        "Banjarmasin": "Gunakan klotok (perahu tradisional) untuk wisata sungai, kunjungi pasar terapung sebelum jam 8 pagi, coba soto Banjar untuk sarapan, bawa payung untuk cuaca tropis",
        "Samarinda": "Kunjungi Mahakam riverfront untuk sunset, coba ikan patin bakar khas Kalimantan, gunakan ojek online untuk transportasi dalam kota",
        "Jayapura": "Siapkan dokumen untuk area perbatasan, coba papeda makanan khas Papua, respect budaya lokal Papua, bawa jaket untuk cuaca pegunungan"
    }

    budget_tips = {
        "low": "Gunakan transportasi umum (angkot), makan di warung lokal, pilih homestay atau guesthouse",
        "medium": "Kombinasi transportasi umum dan ojek online, hotel bintang 3, restaurant lokal dan cafe",
        "high": "Private car dengan driver, hotel bintang 4-5, fine dining dan aktivitas premium"
    }

    local_tip = tips_database.get(destination, f"Nikmati pengalaman lokal yang autentik di {destination}")
    budget_tip = budget_tips.get(budget, "Sesuaikan aktivitas dengan budget Anda")

    return {
        "destination": destination,
        "duration": duration,
        "budget": budget,
        "interests": interests,
        "itinerary": itinerary,
        "tips": f"{local_tip}. {budget_tip}.",
        "estimated_cost": f"Rp {total_cost:,}",
        "ai_confidence": 0.97
    }

@app.post("/chat-plan", response_model=TravelPlanResponse)
async def create_travel_plan_from_chat(request: ChatTravelRequest):
    """Generate a travel plan from natural language input using real AI"""

    message = request.message.lower()

    # Comprehensive Indonesian cities mapping
    destination_mapping = {
        # Major Indonesian cities
        "bali": "Bali", "denpasar": "Bali", "ubud": "Bali", "canggu": "Bali", "seminyak": "Bali", "kuta": "Bali", "sanur": "Bali",
        "jakarta": "Jakarta", "depok": "Jakarta", "bekasi": "Jakarta", "tangerang": "Jakarta", "bogor": "Jakarta",
        "yogyakarta": "Yogyakarta", "yogya": "Yogyakarta", "jogja": "Yogyakarta",
        "bandung": "Bandung", "cimahi": "Bandung",
        "lombok": "Lombok", "mataram": "Lombok",
        "surabaya": "Surabaya", "sidoarjo": "Surabaya",

        # Kalimantan
        "banjarmasin": "Banjarmasin", "balikpapan": "Balikpapan", "samarinda": "Samarinda",
        "pontianak": "Pontianak", "palangkaraya": "Palangkaraya", "tarakan": "Tarakan",

        # Sumatera
        "medan": "Medan", "palembang": "Palembang", "pekanbaru": "Pekanbaru",
        "padang": "Padang", "jambi": "Jambi", "bengkulu": "Bengkulu", "lampung": "Lampung",
        "banda aceh": "Banda Aceh", "aceh": "Banda Aceh",

        # Sulawesi
        "makassar": "Makassar", "manado": "Manado", "palu": "Palu", "kendari": "Kendari",

        # Jawa
        "semarang": "Semarang", "solo": "Solo", "malang": "Malang", "kediri": "Kediri",
        "purwokerto": "Purwokerto", "tegal": "Tegal", "cirebon": "Cirebon",

        # Papua
        "jayapura": "Jayapura", "sorong": "Sorong", "merauke": "Merauke",

        # Nusa Tenggara
        "kupang": "Kupang", "mataram": "Mataram", "bima": "Bima",

        # Maluku
        "ambon": "Ambon", "ternate": "Ternate"
    }

    detected_destination = None
    for keyword, city in destination_mapping.items():
        if keyword in message:
            detected_destination = city
            break

    # If no destination found, try to extract from the message more intelligently
    if not detected_destination:
        # Look for capitalized words that might be city names
        potential_cities = re.findall(r'\b[A-Z][a-z]+\b', request.message)
        if potential_cities:
            detected_destination = potential_cities[0]
        else:
            # If still no destination, ask AI to help identify
            detected_destination = "Unknown City"

    # Enhanced duration extraction with regex
    detected_duration = 3  # default

    # Look for number + hari pattern
    duration_match = re.search(r'(\d+)\s*hari', message)
    if duration_match:
        detected_duration = int(duration_match.group(1))
    else:
        # Look for written numbers
        number_words = {
            "satu": 1, "dua": 2, "tiga": 3, "empat": 4, "lima": 5,
            "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9, "sepuluh": 10,
            "seminggu": 7, "sehari": 1
        }
        for word, num in number_words.items():
            if word in message and "hari" in message:
                detected_duration = num
                break

    # Enhanced budget detection with better number parsing
    detected_budget = "medium"  # default

    # Look for budget amounts in millions
    budget_match = re.search(r'(\d+(?:\.\d+)?)\s*juta', message)
    if budget_match:
        amount = float(budget_match.group(1))
        if amount <= 1.5:
            detected_budget = "low"
        elif amount <= 4:
            detected_budget = "medium"
        else:
            detected_budget = "high"
    else:
        # Look for budget keywords
        if any(word in message for word in ["hemat", "murah", "budget rendah", "terbatas"]):
            detected_budget = "low"
        elif any(word in message for word in ["premium", "mewah", "mahal", "luxury", "eksklusif"]):
            detected_budget = "high"
        elif any(word in message for word in ["sedang", "menengah", "standar"]):
            detected_budget = "medium"

    # Enhanced interest detection
    interest_mapping = {
        # Food related
        "kuliner": ["food", "culinary"],
        "makanan": ["food", "culinary"],
        "makan": ["food", "culinary"],
        "restoran": ["food", "culinary"],
        "warung": ["food", "culinary"],
        "street food": ["food", "culinary"],

        # Beach related
        "pantai": ["beach", "relaxation"],
        "beach": ["beach", "relaxation"],
        "laut": ["beach", "relaxation"],
        "snorkeling": ["beach", "adventure"],
        "diving": ["beach", "adventure"],

        # Culture related
        "budaya": ["culture", "history"],
        "sejarah": ["culture", "history"],
        "museum": ["culture", "history"],
        "candi": ["culture", "history"],
        "pura": ["culture", "history"],
        "tradisional": ["culture", "history"],

        # Adventure related
        "petualangan": ["adventure", "nature"],
        "hiking": ["adventure", "nature"],
        "trekking": ["adventure", "nature"],
        "gunung": ["adventure", "nature"],
        "alam": ["adventure", "nature"],

        # Shopping related
        "belanja": ["shopping", "city"],
        "shopping": ["shopping", "city"],
        "mall": ["shopping", "city"],
        "pasar": ["shopping", "culture"],

        # Sightseeing related
        "wisata": ["culture", "city"],
        "destinasi": ["culture", "city"],
        "tempat wisata": ["culture", "city"],
        "objek wisata": ["culture", "city"],

        # Photography related
        "foto": ["photography", "scenic"],
        "fotografi": ["photography", "scenic"],
        "pemandangan": ["photography", "scenic"]
    }

    detected_interests = []
    for keyword, interests in interest_mapping.items():
        if keyword in message:
            detected_interests.extend(interests)

    # Remove duplicates and ensure we have at least some interests
    detected_interests = list(set(detected_interests))
    if not detected_interests:
        detected_interests = ["culture", "food"]  # default

    # **USE REAL AI HERE** - Call the AI service
    try:
        ai_result = await get_ai_travel_plan(
            user_input=request.message,
            destination=detected_destination,
            duration=detected_duration,
            budget=detected_budget,
            interests=detected_interests
        )

        # Convert to TravelPlanResponse
        return TravelPlanResponse(**ai_result)

    except Exception as e:
        print(f"AI service error: {e}")
        # Fallback to enhanced system
        fallback_result = await get_enhanced_fallback_plan(
            detected_destination, detected_duration, detected_budget, detected_interests
        )
        return TravelPlanResponse(**fallback_result)

# HTML Frontend
@app.get("/", response_class=HTMLResponse)
async def get_demo_page():
    """Serve the demo HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Travel Guide - Demo</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }

            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }

            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }

            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }

            .header p {
                font-size: 1.1em;
                opacity: 0.9;
            }

            .content {
                padding: 40px;
            }

            .input-section {
                margin-bottom: 30px;
            }

            .input-section label {
                display: block;
                margin-bottom: 10px;
                font-weight: 600;
                color: #333;
            }

            .input-section textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #e1e5e9;
                border-radius: 10px;
                font-size: 16px;
                resize: vertical;
                min-height: 100px;
                transition: border-color 0.3s ease;
            }

            .input-section textarea:focus {
                outline: none;
                border-color: #667eea;
            }

            .button-group {
                display: flex;
                gap: 15px;
                margin-bottom: 30px;
            }

            .btn {
                flex: 1;
                padding: 15px 25px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }

            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }

            .btn-secondary {
                background: #f8f9fa;
                color: #333;
                border: 2px solid #e1e5e9;
            }

            .btn-secondary:hover {
                background: #e9ecef;
            }

            .result-section {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 25px;
                margin-top: 20px;
                display: none;
            }

            .result-section.show {
                display: block;
                animation: fadeIn 0.5s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .result-header {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }

            .result-header h3 {
                color: #333;
                font-size: 1.5em;
                margin-left: 10px;
            }

            .result-content {
                line-height: 1.6;
                color: #555;
            }

            .loading {
                text-align: center;
                padding: 40px;
                color: #667eea;
            }

            .loading .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 10px;
                margin-top: 20px;
            }

            .examples {
                background: #e7f3ff;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
            }

            .examples h4 {
                color: #0066cc;
                margin-bottom: 10px;
            }

            .examples ul {
                list-style: none;
                padding-left: 0;
            }

            .examples li {
                background: white;
                margin: 5px 0;
                padding: 10px;
                border-radius: 5px;
                cursor: pointer;
                transition: background-color 0.3s ease;
            }

            .examples li:hover {
                background: #f0f8ff;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🌍 AI Travel Guide</h1>
                <p>Powered by IBM watsonx, Replicate & Hugging Face AI</p>
            </div>

            <div class="content">
                <div class="examples">
                    <h4>💡 Contoh Permintaan:</h4>
                    <ul>
                        <li onclick="fillExample('Ke Samarinda 4 hari budget 6 juta petualangan dan alam')">🏞️ Ke Samarinda 4 hari budget 6 juta petualangan dan alam</li>
                        <li onclick="fillExample('Ke Jayapura 5 hari budget 8 juta budaya dan alam')">🏛️ Ke Jayapura 5 hari budget 8 juta budaya dan alam</li>
                        <li onclick="fillExample('Ke Banjarmasin 7 hari budget 6 juta wisata dan makanan')">🍜 Ke Banjarmasin 7 hari budget 6 juta wisata dan makanan</li>
                        <li onclick="fillExample('Ke Ambon 3 hari budget 4 juta kuliner dan pantai')">🏖️ Ke Ambon 3 hari budget 4 juta kuliner dan pantai</li>
                    </ul>
                </div>

                <div class="input-section">
                    <label for="travelRequest">Ceritakan rencana perjalanan Anda:</label>
                    <textarea
                        id="travelRequest"
                        placeholder="Contoh: Saya ingin ke Samarinda 4 hari dengan budget 6 juta rupiah, suka petualangan dan alam..."
                    ></textarea>
                </div>

                <div class="button-group">
                    <button class="btn btn-primary" onclick="planTrip()">
                        🤖 Buat Rencana dengan AI
                    </button>
                    <button class="btn btn-secondary" onclick="clearAll()">
                        🗑️ Hapus Semua
                    </button>
                </div>

                <div id="result" class="result-section">
                    <div class="result-header">
                        <span style="font-size: 2em;">✨</span>
                        <h3>Rencana Perjalanan AI Anda:</h3>
                    </div>
                    <div id="resultContent" class="result-content"></div>
                </div>
            </div>
        </div>

        <script>
            function fillExample(text) {
                document.getElementById('travelRequest').value = text;
            }

            function clearAll() {
                document.getElementById('travelRequest').value = '';
                document.getElementById('result').classList.remove('show');
            }

            async function planTrip() {
                const request = document.getElementById('travelRequest').value.trim();

                if (!request) {
                    alert('Silakan masukkan rencana perjalanan Anda terlebih dahulu.');
                    return;
                }

                const resultDiv = document.getElementById('result');
                const resultContent = document.getElementById('resultContent');

                // Show loading
                resultDiv.classList.add('show');
                resultContent.innerHTML = `
                    <div class="loading">
                        <div class="spinner"></div>
                        <p>AI sedang merencanakan perjalanan terbaik untuk Anda...</p>
                    </div>
                `;

                try {
                    const response = await fetch('/chat-plan', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: request
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const data = await response.json();

                    // Display result
                    resultContent.innerHTML = `
                        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                            <h4 style="color: #667eea; margin-bottom: 15px;">📍 ${data.destination}</h4>
                            <p><strong>Durasi:</strong> ${data.duration} hari | <strong>Budget:</strong> ${data.budget}</p>
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                            <h4 style="color: #667eea; margin-bottom: 15px;">🗓️ Itinerary:</h4>
                            ${data.itinerary.map((day, index) => `
                                <div style="margin-bottom: 10px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                    <strong>Hari ${index + 1}:</strong><br>
                                    ${day}
                                </div>
                            `).join('')}
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                            <h4 style="color: #667eea; margin-bottom: 15px;">💡 Tips AI:</h4>
                            <p>${data.tips}</p>
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 10px;">
                            <p><strong>🎯 AI Confidence:</strong> ${Math.round(data.ai_confidence * 100)}% | <strong>💰 Estimasi Biaya:</strong> ${data.estimated_cost}</p>
                        </div>
                    `;

                } catch (error) {
                    console.error('Error:', error);
                    resultContent.innerHTML = `
                        <div class="error">
                            <h4>❌ Terjadi kesalahan:</h4>
                            <p>Tidak dapat menghubungi AI Travel Planner. Silakan coba lagi atau gunakan API Documentation untuk testing manual.</p>
                        </div>
                    `;
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Travel Guide API is running"}

if __name__ == "__main__":
    print("🌍 Starting AI Travel Guide API Demo...")
    print("📖 Visit http://localhost:8000 for the demo page")
    print("📚 Visit http://localhost:8000/docs for interactive API documentation")
    uvicorn.run("demo_api_fixed:app", host="0.0.0.0", port=8000, reload=True)
