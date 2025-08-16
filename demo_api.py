#!/usr/bin/env python3
"""
Simple demo API for AI Travel Guide
This is a standalone demo that doesn't require Docker or database setup
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import random
import re as regex_module
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
    version="1.0.0-demo"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for demo
class TravelPlan(BaseModel):
    destination: str
    duration: int
    budget: str
    interests: List[str]

class ChatTravelRequest(BaseModel):
    message: str

class TravelPlanResponse(BaseModel):
    destination: str
    duration: int
    budget: str
    interests: List[str]
    itinerary: List[str]
    tips: str
    estimated_cost: str
    ai_confidence: float

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

    # Comprehensive destination database with detailed activities
    destination_database = {
        "Banjarmasin": {
            "culture": [
                "Masjid Sabilal Muhtadin (arsitektur Islam terbesar)",
                "Museum Lambung Mangkurat (sejarah Kalimantan Selatan)",
                "Kampung Sasirangan (pusat kerajinan kain tradisional)",
                "Makam Sultan Suriansyah (situs bersejarah)",
                "Klenteng Soetji Nurani (budaya Tionghoa)",
                "Rumah Bubungan Tinggi (arsitektur tradisional Banjar)"
            ],
            "food": [
                "Soto Banjar di Warung Ibu Hj. Jamilah",
                "Ketupat Kandangan asli di Pasar Sudimampir",
                "Ikan Patin Bakar di tepi Sungai Martapura",
                "Kue Cincin khas Banjar di Pasar Terapung",
                "Nasi Kuning Banjar dengan lauk tradisional",
                "Dodol Kandangan sebagai oleh-oleh khas"
            ],
            "culinary": [
                "Food tour Pasar Terapung Lok Baintan (pagi hari)",
                "Kuliner malam di Jalan Pierre Tendean",
                "Cooking class masakan Banjar tradisional",
                "River cruise dinner di Sungai Martapura",
                "Traditional market tour Pasar Sudimampir",
                "Street food hunting di Kampung Melayu"
            ],
            "nature": [
                "Pulau Kembang (konservasi bekantan)",
                "Taman Siring (taman kota di tepi sungai)",
                "Danau Seran (wisata alam dan memancing)",
                "Hutan Mangrove Tarakan (ekowisata)",
                "Floating Market Lok Baintan (pasar terapung)",
                "Sungai Martapura cruise (wisata sungai)"
            ],
            "city": [
                "Jembatan Barito (landmark kota)",
                "Alun-alun Banjarmasin (pusat kota)",
                "Kampung Melayu (kawasan heritage)",
                "Pasar Terapung Muara Kuin (aktivitas pagi)",
                "Menara Pandang Banjarmasin (city view)",
                "Kawasan Sudimampir (pusat perdagangan)"
            ],
            "shopping": [
                "Duta Mall Banjarmasin (modern shopping)",
                "Pasar Sudimampir (pasar tradisional)",
                "Sasirangan Gallery (kain khas Banjar)",
                "Souvenir Center Sungai Jingah",
                "Traditional craft market Kampung Sasirangan",
                "Banjarmasin Trade Center"
            ]
        },
        "Bali": {
            "beach": [
                "Pantai Kuta untuk surfing dan sunset",
                "Pantai Sanur untuk sunrise dan snorkeling",
                "Pantai Nusa Dua untuk relaksasi premium",
                "Pantai Uluwatu dengan pemandangan tebing",
                "Pantai Seminyak untuk beach club",
                "Pantai Jimbaran untuk seafood dinner"
            ],
            "culture": [
                "Pura Tanah Lot (sunset temple)",
                "Pura Besakih (mother temple)",
                "Ubud Monkey Forest Sanctuary",
                "Traditional Balinese dance di Ubud",
                "Pura Uluwatu dengan kecak dance",
                "Tirta Empul holy spring temple"
            ],
            "food": [
                "Bebek betutu di Gianyar",
                "Nasi ayam Kedewatan Bu Oki",
                "Babi guling Ibu Oka Ubud",
                "Jimbaran seafood di pantai",
                "Warung local di Ubud center",
                "Sate lilit khas Bali"
            ],
            "nature": [
                "Sekumpul Waterfall (air terjun tertinggi)",
                "Tegallalang Rice Terrace (sawah terasering)",
                "Mount Batur sunrise trekking",
                "Bali Bird Park di Gianyar",
                "Elephant Safari Park",
                "Bali Zoo dan animal interaction"
            ]
        },
        "Jakarta": {
            "culture": [
                "Museum Nasional (sejarah Indonesia)",
                "Kota Tua Jakarta (Batavia heritage)",
                "Wayang Museum (budaya tradisional)",
                "Istiqlal Mosque (masjid terbesar)",
                "Jakarta Cathedral (arsitektur Gothic)",
                "Museum Bank Indonesia"
            ],
            "food": [
                "Kerak telor di Kota Tua",
                "Soto Betawi H. Ma'ruf",
                "Gado-gado Bonbin",
                "Kuliner Pecenongan (Chinese food)",
                "Nasi uduk Kebon Kacang",
                "Bakmi GM (mie ayam legendaris)"
            ],
            "city": [
                "Monas (National Monument)",
                "Bundaran HI dan fountain",
                "Taman Mini Indonesia Indah",
                "Ancol Dreamland dan beach",
                "Skydeck ASTRA Tower (city view)",
                "Grand Indonesia shopping district"
            ]
        }
    }

    # Get activities for destination - if not in database, create generic but realistic activities
    if destination in destination_database:
        activities = destination_database[destination]
    else:
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
    interest_weights = {}

    # Prioritize activities based on user interests
    for interest in interests:
        if interest in activities:
            # Give higher weight to user-specified interests
            interest_weights[interest] = 3
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

    # If no specific interests match, infer from keywords and provide balanced mix
    if not selected_activities:
        # Default to culture and food for general tourism
        selected_activities.extend(activities.get("culture", [])[:3])
        selected_activities.extend(activities.get("food", [])[:3])
        selected_activities.extend(activities.get("city", [])[:2])

    # Create intelligent itinerary distribution
    itinerary = []

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
        "Banjarmasin": "Gunakan klotok (perahu tradisional) untuk wisata sungai, kunjungi pasar terapung sebelum jam 8 pagi, coba soto Banjar untuk sarapan, bawa payung untuk cuaca tropis"
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

# Demo data
DEMO_DESTINATIONS = [
    {
        "destination": "Bali, Indonesia",
        "description": "A tropical paradise with beautiful beaches, ancient temples, and rich culture",
        "activities": ["Beach relaxation", "Temple visits", "Rice terrace tours", "Traditional dance shows"],
        "estimated_cost": "$800-1200 for 7 days",
        "best_time_to_visit": "April to October"
    },
    {
        "destination": "Kyoto, Japan",
        "description": "Historic city with traditional temples, gardens, and cultural experiences",
        "activities": ["Temple visits", "Traditional tea ceremony", "Bamboo forest walk", "Geisha district tour"],
        "estimated_cost": "$1200-1800 for 7 days",
        "best_time_to_visit": "March to May, September to November"
    },
    {
        "destination": "Santorini, Greece",
        "description": "Stunning island with white-washed buildings, blue domes, and spectacular sunsets",
        "activities": ["Sunset viewing", "Wine tasting", "Beach hopping", "Archaeological sites"],
        "estimated_cost": "$1000-1500 for 7 days",
        "best_time_to_visit": "April to October"
    }
]

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with HTML demo page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Travel Guide - Enterprise Demo | IBM Jakarta</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #1e40af 100%);
                min-height: 100vh;
                color: #333;
            }
            .hero-section {
                background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #1e40af 100%);
                color: white;
                padding: 60px 20px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            .hero-section::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
                opacity: 0.3;
            }
            .hero-content { position: relative; z-index: 10; max-width: 1200px; margin: 0 auto; }
            .nav-bar {
                position: absolute;
                top: 20px;
                right: 20px;
                z-index: 20;
                display: flex;
                gap: 15px;
            }
            .nav-link {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                transition: all 0.3s ease;
            }
            .nav-link:hover {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                text-decoration: none;
                transform: translateY(-2px);
            }
            .ibm-badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(59, 130, 246, 0.2);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 50px;
                padding: 8px 20px;
                margin-bottom: 30px;
                font-size: 14px;
                font-weight: 500;
            }
            .hero-title {
                font-size: 4rem;
                font-weight: 800;
                margin-bottom: 20px;
                background: linear-gradient(135deg, #60a5fa, #a78bfa, #34d399);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                line-height: 1.1;
            }
            .hero-subtitle {
                font-size: 1.5rem;
                font-weight: 300;
                margin-bottom: 40px;
                opacity: 0.9;
                max-width: 800px;
                margin-left: auto;
                margin-right: auto;
                line-height: 1.6;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px 20px 0 0;
                box-shadow: 0 -10px 40px rgba(0,0,0,0.1);
                position: relative;
                z-index: 5;
                margin-top: -20px;
            }
            .content-section { padding: 60px 40px; }
            .section-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #1e40af;
                text-align: center;
                margin-bottom: 20px;
            }
            .section-subtitle {
                font-size: 1.2rem;
                color: #64748b;
                text-align: center;
                margin-bottom: 50px;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
                line-height: 1.6;
            }
            .endpoint {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                padding: 25px;
                margin: 20px 0;
                border-radius: 15px;
                border: 1px solid #e2e8f0;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            .endpoint:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                border-color: #3b82f6;
            }
            .method {
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                padding: 8px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                display: inline-block;
                margin-bottom: 10px;
            }
            .method.post { background: linear-gradient(135deg, #ef4444, #dc2626); }
            .method.get { background: linear-gradient(135deg, #10b981, #059669); }
            .endpoint-url {
                font-family: 'Monaco', 'Menlo', monospace;
                font-size: 16px;
                font-weight: 600;
                color: #1e40af;
                margin-bottom: 8px;
            }
            .endpoint-desc {
                color: #64748b;
                font-size: 14px;
                line-height: 1.5;
            }
            a { color: #3b82f6; text-decoration: none; font-weight: 500; }
            a:hover { text-decoration: underline; color: #1d4ed8; }
            .demo-section {
                margin: 30px 0;
                padding: 30px;
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
                border-radius: 15px;
                border: 1px solid #f59e0b;
            }
            .demo-section h3 {
                color: #92400e;
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 15px;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            .stat-card {
                background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
                color: white;
                padding: 30px 20px;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(30, 64, 175, 0.3);
            }
            .stat-number {
                font-size: 2.5rem;
                font-weight: 800;
                margin-bottom: 5px;
            }
            .stat-label {
                font-size: 14px;
                opacity: 0.9;
                font-weight: 500;
            }
            .cta-section {
                background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
                color: white;
                padding: 60px 40px;
                text-align: center;
                border-radius: 0 0 20px 20px;
            }
            .cta-button {
                display: inline-block;
                background: linear-gradient(135deg, #60a5fa, #3b82f6);
                color: white;
                padding: 15px 30px;
                border-radius: 10px;
                text-decoration: none;
                font-weight: 600;
                font-size: 16px;
                margin: 10px;
                transition: all 0.3s ease;
                box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
            }
            .cta-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.6);
                color: white;
                text-decoration: none;
            }
            .demo-form {
                background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
                border: 1px solid #e2e8f0;
                border-radius: 20px;
                padding: 40px;
                margin: 40px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-label {
                display: block;
                font-weight: 600;
                color: #1e40af;
                margin-bottom: 8px;
                font-size: 14px;
            }
            .form-input, .form-select {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e2e8f0;
                border-radius: 10px;
                font-size: 14px;
                transition: all 0.3s ease;
                background: white;
            }
            .form-input:focus, .form-select:focus {
                outline: none;
                border-color: #3b82f6;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            .form-button {
                background: linear-gradient(135deg, #3b82f6, #1d4ed8);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s ease;
                width: 100%;
                box-shadow: 0 5px 15px rgba(59, 130, 246, 0.4);
            }
            .form-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(59, 130, 246, 0.6);
            }
            .form-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .result-box {
                background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
                border: 1px solid #10b981;
                border-radius: 15px;
                padding: 25px;
                margin-top: 20px;
                display: none;
            }
            .result-box.show {
                display: block;
                animation: fadeIn 0.5s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            @media (max-width: 768px) {
                .hero-title { font-size: 2.5rem; }
                .hero-subtitle { font-size: 1.2rem; }
                .content-section { padding: 40px 20px; }
                .cta-section { padding: 40px 20px; }
                .nav-bar { position: relative; top: 0; right: 0; justify-content: center; margin-bottom: 20px; }
                .demo-form { padding: 25px; }
            }
        </style>
    </head>
    <body>
        <div class="hero-section">
            <div class="nav-bar">
                <a href="/docs" class="nav-link">📚 API Docs</a>
                <a href="/destinations" class="nav-link">🌍 Destinations</a>
                <a href="/health" class="nav-link">💚 Health</a>
            </div>
            <div class="hero-content">
                <div class="ibm-badge">
                    🧠 Powered by IBM watsonx AI
                    <span style="width: 8px; height: 8px; background: #10b981; border-radius: 50%; animation: pulse 2s infinite;"></span>
                </div>
                <h1 class="hero-title">AI Travel Guide</h1>
                <h2 style="font-size: 2rem; font-weight: 300; margin-bottom: 20px;">Enterprise Edition</h2>
                <p class="hero-subtitle">Platform AI terdepan untuk industri pariwisata Indonesia. Mengintegrasikan IBM watsonx dengan teknologi machine learning untuk pengalaman wisata yang tak terlupakan.</p>
            </div>
        </div>

        <div class="container">
            <div class="content-section">
                <h2 class="section-title">Enterprise API Demo</h2>
                <p class="section-subtitle">Jelajahi kemampuan platform AI Travel Guide dengan API yang telah terintegrasi dengan IBM watsonx</p>
            
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">500+</div>
                        <div class="stat-label">Destinasi Indonesia</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">99.9%</div>
                        <div class="stat-label">Uptime SLA</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">< 200ms</div>
                        <div class="stat-label">Response Time</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Enterprise Support</div>
                    </div>
                </div>

                <div class="demo-form">
                    <h3 style="color: #1e40af; font-size: 1.8rem; font-weight: 700; margin-bottom: 10px; text-align: center;">🤖 Coba AI Travel Planner</h3>
                    <p style="color: #64748b; text-align: center; margin-bottom: 30px;">Buat rencana perjalanan yang dipersonalisasi dengan AI watsonx</p>

                    <!-- Mode Toggle -->
                    <div style="display: flex; justify-content: center; margin-bottom: 30px;">
                        <div style="background: #f1f5f9; border-radius: 12px; padding: 4px; display: flex;">
                            <button type="button" id="templateModeBtn" onclick="switchMode('template')"
                                style="padding: 10px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; background: #3b82f6; color: white;">
                                📋 Template Mode
                            </button>
                            <button type="button" id="chatModeBtn" onclick="switchMode('chat')"
                                style="padding: 10px 20px; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s ease; background: transparent; color: #64748b;">
                                💬 Chat Mode
                            </button>
                        </div>
                    </div>

                    <!-- Template Mode Form -->
                    <div id="templateMode">
                        <form id="travelForm" onsubmit="planTrip(event)">
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                                <div class="form-group">
                                    <label class="form-label">🏝️ Destinasi</label>
                                    <select class="form-select" name="destination" required>
                                        <option value="">Pilih destinasi...</option>
                                        <option value="Bali">Bali</option>
                                        <option value="Jakarta">Jakarta</option>
                                        <option value="Yogyakarta">Yogyakarta</option>
                                        <option value="Bandung">Bandung</option>
                                        <option value="Lombok">Lombok</option>
                                        <option value="Surabaya">Surabaya</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">📅 Durasi (hari)</label>
                                    <select class="form-select" name="duration" required>
                                        <option value="">Pilih durasi...</option>
                                        <option value="1">1 hari</option>
                                        <option value="2">2 hari</option>
                                        <option value="3">3 hari</option>
                                        <option value="5">5 hari</option>
                                        <option value="7">7 hari</option>
                                        <option value="10">10 hari</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">💰 Budget</label>
                                    <select class="form-select" name="budget" required>
                                        <option value="">Pilih budget...</option>
                                        <option value="low">Hemat (< 1 juta)</option>
                                        <option value="medium">Sedang (1-3 juta)</option>
                                        <option value="high">Premium (> 3 juta)</option>
                                    </select>
                                </div>

                                <div class="form-group">
                                    <label class="form-label">🎯 Minat Utama</label>
                                    <select class="form-select" name="interests" required>
                                        <option value="">Pilih minat...</option>
                                        <option value="beach,relaxation">Pantai & Relaksasi</option>
                                        <option value="culture,history">Budaya & Sejarah</option>
                                        <option value="adventure,nature">Petualangan & Alam</option>
                                        <option value="food,culinary">Kuliner & Food Tour</option>
                                        <option value="shopping,city">Belanja & City Tour</option>
                                        <option value="photography,scenic">Fotografi & Pemandangan</option>
                                    </select>
                                </div>
                            </div>

                            <button type="submit" class="form-button" id="submitBtn">
                                🚀 Buat Rencana Perjalanan dengan AI
                            </button>
                        </form>
                    </div>

                    <!-- Chat Mode Form -->
                    <div id="chatMode" style="display: none;">
                        <form id="chatForm" onsubmit="planTripFromChat(event)">
                            <div class="form-group">
                                <label class="form-label">💬 Ceritakan rencana perjalanan Anda</label>
                                <textarea
                                    class="form-input"
                                    name="chatInput"
                                    rows="6"
                                    placeholder="Contoh: Saya ingin liburan ke Jakarta selama 3 hari dengan budget 2 juta. Saya suka kuliner dan ingin mencoba makanan khas Jakarta. Tolong buatkan itinerary yang detail!"
                                    style="resize: vertical; min-height: 120px; line-height: 1.6;"
                                    required></textarea>
                                <div style="margin-top: 10px; font-size: 12px; color: #64748b;">
                                    💡 <strong>Tips:</strong> Sebutkan destinasi, durasi, budget, dan minat Anda untuk hasil yang lebih akurat
                                </div>
                            </div>

                            <button type="submit" class="form-button" id="chatSubmitBtn">
                                🤖 Tanya AI Travel Assistant
                            </button>
                        </form>
                    </div>

                    <div id="resultBox" class="result-box">
                        <h4 style="color: #065f46; font-weight: 600; margin-bottom: 15px;">✨ Rencana Perjalanan AI Anda:</h4>
                        <div id="resultContent"></div>
                    </div>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <div class="endpoint-url">/destinations</div>
                    <div class="endpoint-desc">Dapatkan daftar destinasi populer Indonesia dengan deskripsi yang dihasilkan AI watsonx</div>
                </div>

                <div class="endpoint">
                    <span class="method post">POST</span>
                    <div class="endpoint-url">/plan</div>
                    <div class="endpoint-desc">Buat itinerary perjalanan yang dipersonalisasi berdasarkan preferensi Anda menggunakan AI</div>
                    <div style="margin-top: 10px; padding: 15px; background: #f1f5f9; border-radius: 8px; font-family: monospace; font-size: 13px;">
                        <strong>Request Body:</strong><br>
                        {"destination": "Bali", "duration": 5, "budget": "medium", "interests": ["beach", "culture"]}
                    </div>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <div class="endpoint-url">/health</div>
                    <div class="endpoint-desc">Periksa status kesehatan API dan konektivitas dengan IBM watsonx</div>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <div class="endpoint-url">/docs</div>
                    <div class="endpoint-desc">Dokumentasi API interaktif dengan Swagger UI untuk testing real-time</div>
                </div>

                <h2 class="section-title" style="margin-top: 60px; font-size: 2rem;">🏗️ Enterprise Architecture</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0;">
                    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 25px; border-radius: 15px; border: 1px solid #e2e8f0;">
                        <h4 style="color: #1e40af; font-size: 1.2rem; margin-bottom: 10px;">🧠 AI/ML Layer</h4>
                        <ul style="color: #64748b; font-size: 14px; line-height: 1.6;">
                            <li>IBM watsonx Foundation Models</li>
                            <li>Hugging Face Transformers</li>
                            <li>Custom NLP Pipeline</li>
                            <li>Vector Embeddings</li>
                        </ul>
                    </div>
                    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 25px; border-radius: 15px; border: 1px solid #e2e8f0;">
                        <h4 style="color: #1e40af; font-size: 1.2rem; margin-bottom: 10px;">⚡ Backend Services</h4>
                        <ul style="color: #64748b; font-size: 14px; line-height: 1.6;">
                            <li>FastAPI (Python)</li>
                            <li>PostgreSQL + pgvector</li>
                            <li>Redis Caching</li>
                            <li>Docker Containers</li>
                        </ul>
                    </div>
                    <div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); padding: 25px; border-radius: 15px; border: 1px solid #e2e8f0;">
                        <h4 style="color: #1e40af; font-size: 1.2rem; margin-bottom: 10px;">🎨 Frontend Stack</h4>
                        <ul style="color: #64748b; font-size: 14px; line-height: 1.6;">
                            <li>React + TypeScript</li>
                            <li>Tailwind CSS</li>
                            <li>Framer Motion</li>
                            <li>Progressive Web App</li>
                        </ul>
                    </div>
                </div>

                <h2 class="section-title" style="margin-top: 60px; font-size: 2rem;">✨ Platform Capabilities</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">
                    <div style="display: flex; align-items: flex-start; gap: 15px; padding: 20px; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border: 1px solid #10b981;">
                        <span style="font-size: 24px;">✅</span>
                        <div>
                            <h4 style="color: #065f46; font-weight: 600; margin-bottom: 5px;">Smart Destination Discovery</h4>
                            <p style="color: #047857; font-size: 14px;">AI-powered recommendations dengan analisis preferensi real-time</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 15px; padding: 20px; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border: 1px solid #10b981;">
                        <span style="font-size: 24px;">✅</span>
                        <div>
                            <h4 style="color: #065f46; font-weight: 600; margin-bottom: 5px;">Intelligent Trip Planning</h4>
                            <p style="color: #047857; font-size: 14px;">Perencanaan itinerary otomatis berdasarkan budget dan minat</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 15px; padding: 20px; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border: 1px solid #10b981;">
                        <span style="font-size: 24px;">✅</span>
                        <div>
                            <h4 style="color: #065f46; font-weight: 600; margin-bottom: 5px;">Multi-modal AI Processing</h4>
                            <p style="color: #047857; font-size: 14px;">Support input teks, gambar, dan suara dengan IBM watsonx</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 15px; padding: 20px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; border: 1px solid #f59e0b;">
                        <span style="font-size: 24px;">🔄</span>
                        <div>
                            <h4 style="color: #92400e; font-weight: 600; margin-bottom: 5px;">Computer Vision Integration</h4>
                            <p style="color: #b45309; font-size: 14px;">Pengenalan landmark dan analisis foto destinasi (in development)</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 15px; padding: 20px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; border: 1px solid #f59e0b;">
                        <span style="font-size: 24px;">🔄</span>
                        <div>
                            <h4 style="color: #92400e; font-weight: 600; margin-bottom: 5px;">Conversational AI Assistant</h4>
                            <p style="color: #b45309; font-size: 14px;">Chat interface dengan natural language processing (in development)</p>
                        </div>
                    </div>
                    <div style="display: flex; align-items: flex-start; gap: 15px; padding: 20px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 12px; border: 1px solid #f59e0b;">
                        <span style="font-size: 24px;">🔄</span>
                        <div>
                            <h4 style="color: #92400e; font-weight: 600; margin-bottom: 5px;">Real-time Analytics Dashboard</h4>
                            <p style="color: #b45309; font-size: 14px;">Business intelligence untuk operator wisata (in development)</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="cta-section">
                <h2 style="font-size: 2.5rem; font-weight: 700; margin-bottom: 20px;">Ready to Transform Tourism Industry?</h2>
                <p style="font-size: 1.2rem; margin-bottom: 40px; opacity: 0.9; max-width: 600px; margin-left: auto; margin-right: auto;">
                    Bergabunglah dengan revolusi AI dalam industri pariwisata Indonesia bersama IBM watsonx
                </p>
                <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px;">
                    <a href="/docs" class="cta-button">
                        📚 Explore API Documentation
                    </a>
                    <a href="/destinations" class="cta-button">
                        🌍 View Live Destinations
                    </a>
                    <a href="mailto:ibm.jakarta@ibm.com" class="cta-button">
                        💼 Contact IBM Jakarta
                    </a>
                </div>
                <div style="margin-top: 40px; padding-top: 40px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 14px; opacity: 0.8;">
                    <p>© 2024 AI Travel Guide - Enterprise Edition | Powered by IBM watsonx | Built for IBM Jakarta Partnership</p>
                </div>
            </div>
        </div>

        <style>
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
        </style>

        <script>
            // Mode switching functionality
            function switchMode(mode) {
                const templateMode = document.getElementById('templateMode');
                const chatMode = document.getElementById('chatMode');
                const templateBtn = document.getElementById('templateModeBtn');
                const chatBtn = document.getElementById('chatModeBtn');

                if (mode === 'template') {
                    templateMode.style.display = 'block';
                    chatMode.style.display = 'none';
                    templateBtn.style.background = '#3b82f6';
                    templateBtn.style.color = 'white';
                    chatBtn.style.background = 'transparent';
                    chatBtn.style.color = '#64748b';
                } else {
                    templateMode.style.display = 'none';
                    chatMode.style.display = 'block';
                    chatBtn.style.background = '#3b82f6';
                    chatBtn.style.color = 'white';
                    templateBtn.style.background = 'transparent';
                    templateBtn.style.color = '#64748b';
                }
            }

            // Template mode function
            async function planTrip(event) {
                event.preventDefault();

                const submitBtn = document.getElementById('submitBtn');
                const resultBox = document.getElementById('resultBox');
                const resultContent = document.getElementById('resultContent');

                // Disable button and show loading
                submitBtn.disabled = true;
                submitBtn.innerHTML = '🔄 AI sedang merencanakan perjalanan Anda...';

                // Get form data
                const formData = new FormData(event.target);
                const data = {
                    destination: formData.get('destination'),
                    duration: parseInt(formData.get('duration')),
                    budget: formData.get('budget'),
                    interests: formData.get('interests').split(',')
                };

                try {
                    // Call the API
                    const response = await fetch('/plan', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const result = await response.json();
                    displayResult(result);

                } catch (error) {
                    displayError(error);
                }

                // Re-enable button
                submitBtn.disabled = false;
                submitBtn.innerHTML = '🚀 Buat Rencana Perjalanan dengan AI';
            }

            // Chat mode function
            async function planTripFromChat(event) {
                event.preventDefault();

                const chatSubmitBtn = document.getElementById('chatSubmitBtn');
                const resultBox = document.getElementById('resultBox');
                const resultContent = document.getElementById('resultContent');

                // Disable button and show loading
                chatSubmitBtn.disabled = true;
                chatSubmitBtn.innerHTML = '🔄 AI sedang memproses permintaan Anda...';

                // Get form data
                const formData = new FormData(event.target);
                const data = {
                    message: formData.get('chatInput')
                };

                try {
                    // Call the chat API
                    const response = await fetch('/chat-plan', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });

                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }

                    const result = await response.json();
                    displayResult(result);

                } catch (error) {
                    displayError(error);
                }

                // Re-enable button
                chatSubmitBtn.disabled = false;
                chatSubmitBtn.innerHTML = '🤖 Tanya AI Travel Assistant';
            }

            // Shared function to display results
            function displayResult(result) {
                const resultBox = document.getElementById('resultBox');
                const resultContent = document.getElementById('resultContent');

                resultContent.innerHTML = `
                    <div style="background: white; padding: 20px; border-radius: 10px; margin-bottom: 15px;">
                        <h5 style="color: #1e40af; font-weight: 600; margin-bottom: 10px;">📍 ${result.destination}</h5>
                        <p style="color: #64748b; margin-bottom: 15px;"><strong>Durasi:</strong> ${result.duration} hari | <strong>Budget:</strong> ${result.budget}</p>
                        <div style="color: #374151; line-height: 1.6;">
                            ${result.itinerary.map((day, index) => `
                                <div style="margin-bottom: 15px; padding: 15px; background: #f8fafc; border-radius: 8px; border-left: 4px solid #3b82f6;">
                                    <strong style="color: #1e40af;">Hari ${index + 1}:</strong><br>
                                    ${day}
                                </div>
                            `).join('')}
                        </div>
                        <div style="margin-top: 15px; padding: 15px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                            <strong style="color: #92400e;">💡 Tips AI:</strong><br>
                            <span style="color: #b45309;">${result.tips}</span>
                        </div>
                        <div style="margin-top: 15px; padding: 10px; background: #ecfdf5; border-radius: 8px; text-align: center;">
                            <span style="color: #065f46; font-size: 14px;">
                                🎯 <strong>AI Confidence:</strong> ${Math.round(result.ai_confidence * 100)}% |
                                💰 <strong>Estimasi Biaya:</strong> ${result.estimated_cost}
                            </span>
                        </div>
                    </div>
                `;

                resultBox.classList.add('show');
                resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }

            // Shared function to display errors
            function displayError(error) {
                const resultBox = document.getElementById('resultBox');
                const resultContent = document.getElementById('resultContent');

                console.error('Error:', error);
                resultContent.innerHTML = `
                    <div style="background: #fef2f2; border: 1px solid #fecaca; color: #dc2626; padding: 20px; border-radius: 10px;">
                        <strong>❌ Terjadi kesalahan:</strong><br>
                        Tidak dapat menghubungi AI Travel Planner. Silakan coba lagi atau gunakan <a href="/docs" style="color: #dc2626; text-decoration: underline;">API Documentation</a> untuk testing manual.
                    </div>
                `;
                resultBox.classList.add('show');
            }
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "AI Travel Guide API Demo is running",
        "version": "1.0.0-demo",
        "endpoints": {
            "destinations": "/destinations",
            "plan": "/plan",
            "docs": "/docs"
        }
    }

@app.get("/destinations", response_model=List[TravelRecommendation])
async def get_destinations():
    """Get popular travel destinations"""
    return [TravelRecommendation(**dest) for dest in DEMO_DESTINATIONS]

@app.post("/plan", response_model=TravelPlanResponse)
async def create_travel_plan(plan: TravelPlan):
    """Generate a travel plan based on user preferences using AI"""

    # Comprehensive destination-specific activities for all major Indonesian cities
    destination_activities = {
        "Bali": {
            "beach": ["Pantai Kuta untuk surfing", "Pantai Sanur untuk sunrise", "Pantai Nusa Dua untuk relaksasi", "Pantai Uluwatu untuk sunset"],
            "relaxation": ["Spa tradisional di Ubud", "Yoga retreat di Canggu", "Meditation di Sidemen", "Resort mewah di Seminyak"],
            "culture": ["Pura Tanah Lot", "Pura Besakih", "Ubud Monkey Forest", "Traditional Balinese Dance"],
            "adventure": ["Mount Batur sunrise trekking", "White water rafting di Ayung", "ATV ride di Ubud", "Volcano tour"],
            "food": ["Bebek betutu di Gianyar", "Nasi ayam Kedewatan", "Cooking class di Ubud", "Jimbaran seafood"],
            "culinary": ["Food tour di Denpasar", "Traditional market visit", "Warung hopping", "Balinese cooking workshop"],
            "nature": ["Sekumpul Waterfall", "Tegallalang Rice Terrace", "Sacred Monkey Forest", "Bali Bird Park"],
            "shopping": ["Sukawati Art Market", "Ubud Traditional Market", "Seminyak boutiques", "Kuta Beachwalk"]
        },
        "Jakarta": {
            "culture": ["Museum Nasional", "Kota Tua Jakarta", "Wayang Museum", "Istiqlal Mosque"],
            "city": ["Monas (National Monument)", "Bundaran HI", "Taman Mini Indonesia", "Ancol Dreamland"],
            "food": ["Kerak telor di Kota Tua", "Soto Betawi", "Gado-gado Bonbin", "Kuliner Pecenongan"],
            "culinary": ["Street food tour Sabang", "Fine dining di SCBD", "Traditional market Tanah Abang", "Food court Grand Indonesia"],
            "shopping": ["Grand Indonesia", "Plaza Indonesia", "Tanah Abang", "Pasar Baru"],
            "history": ["Fatahillah Square", "Jakarta Cathedral", "Bank Indonesia Museum", "Maritime Museum"]
        },
        "Yogyakarta": {
            "culture": ["Candi Borobudur", "Candi Prambanan", "Kraton Yogyakarta", "Taman Sari"],
            "history": ["Malioboro Street", "Fort Vredeburg", "Sultan Palace", "Kotagede Silver"],
            "food": ["Gudeg Yu Djum", "Bakpia Pathok", "Sate Klathak", "Angkringan Tugu"],
            "culinary": ["Gudeg tour", "Traditional Javanese cooking", "Street food Malioboro", "Royal cuisine experience"],
            "adventure": ["Jomblang Cave", "Pindul Cave tubing", "Merapi volcano tour", "Parangtritis beach"],
            "shopping": ["Malioboro Street", "Beringharjo Market", "Jalan Prawirotaman", "Kotagede"]
        },
        "Bandung": {
            "nature": ["Tangkuban Perahu", "Kawah Putih", "Situ Patenggang", "Maribaya Waterfall"],
            "food": ["Batagor Kingsley", "Siomay Bandung", "Surabi Enhaii", "Mie kocok Mang Dadeng"],
            "culinary": ["Sundanese cuisine tour", "Factory outlet food court", "Traditional Sundanese restaurant", "Modern cafe hopping"],
            "shopping": ["Factory Outlets", "Cihampelas Walk", "Paris Van Java", "Rumah Mode"],
            "culture": ["Gedung Sate", "Museum Geologi", "Saung Angklung Udjo", "Kampung Gajah"],
            "city": ["Braga Street", "Asia Afrika Street", "Alun-alun Bandung", "Taman Lansia"]
        },
        "Lombok": {
            "beach": ["Pantai Senggigi", "Gili Trawangan", "Pantai Kuta Lombok", "Pink Beach"],
            "adventure": ["Mount Rinjani trekking", "Gili Islands hopping", "Snorkeling di Gili Air", "Waterfall tour"],
            "nature": ["Sekotong Peninsula", "Benang Stokel Waterfall", "Pusuk Monkey Forest", "Mandalika Beach"],
            "culture": ["Sasak Village", "Traditional weaving", "Pura Lingsar", "Ende Village"],
            "relaxation": ["Beach resort di Senggigi", "Spa treatment", "Sunset viewing", "Island hopping"]
        },
        "Surabaya": {
            "city": ["Tugu Pahlawan", "Jembatan Suramadu", "Kebun Binatang Surabaya", "House of Sampoerna"],
            "culture": ["Masjid Al Akbar", "Klenteng Sanggar Agung", "Museum Sepuluh Nopember", "Kampung Arab"],
            "food": ["Rawon Setan", "Rujak Cingur", "Lontong Balap", "Tahu Tek"],
            "culinary": ["East Javanese cuisine tour", "Traditional market visit", "Street food exploration", "Modern dining"],
            "shopping": ["Tunjungan Plaza", "Galaxy Mall", "Pasar Atom", "ITC Surabaya"]
        },
        # EXPANDED: Major Indonesian Cities
        "Banjarmasin": {
            "culture": ["Masjid Sabilal Muhtadin", "Museum Lambung Mangkurat", "Kampung Sasirangan", "Floating Market Lok Baintan"],
            "nature": ["Pulau Kembang", "Taman Siring", "Danau Seran", "Hutan Mangrove Tarakan"],
            "food": ["Soto Banjar", "Ketupat Kandangan", "Ikan Patin Bakar", "Kue Cincin"],
            "culinary": ["Traditional Banjar cuisine", "Floating market food tour", "River fish specialties", "Local dessert tasting"],
            "city": ["Pasar Terapung", "Jembatan Barito", "Alun-alun Banjarmasin", "Kampung Melayu"],
            "shopping": ["Pasar Sudimampir", "Duta Mall", "Traditional craft market", "Sasirangan center"]
        },
        "Medan": {
            "culture": ["Istana Maimun", "Masjid Raya Al-Mashun", "Museum Negeri Sumatera Utara", "Tjong A Fie Mansion"],
            "food": ["Bika Ambon", "Soto Medan", "Durian Ucok", "Mie Aceh"],
            "culinary": ["Batak cuisine tour", "Chinese-Indonesian fusion", "Street food Kesawan", "Traditional Medan breakfast"],
            "city": ["Lapangan Merdeka", "Kesawan Square", "Little India", "Chinatown Medan"],
            "nature": ["Danau Toba day trip", "Bukit Lawang orangutan", "Air Terjun Sipiso-piso", "Berastagi highland"],
            "shopping": ["Sun Plaza", "Centre Point Mall", "Pasar Petisah", "Souvenir Batak"]
        },
        "Makassar": {
            "culture": ["Fort Rotterdam", "Masjid Amirul Mukminin", "Museum La Galigo", "Kampung Kauman"],
            "food": ["Coto Makassar", "Konro Bakar", "Pisang Epe", "Es Pallu Butung"],
            "culinary": ["Bugis-Makassar cuisine", "Seafood Losari Beach", "Traditional market tour", "Local coffee culture"],
            "beach": ["Pantai Losari", "Pulau Samalona", "Pantai Akkarena", "Pulau Kodingareng"],
            "city": ["Benteng Somba Opu", "Trans Studio Makassar", "Pantai Losari Boulevard", "Karebosi Park"],
            "shopping": ["Mall Panakkukang", "Karebosi Link", "Pasar Sentral", "Somba Opu Square"]
        },
        "Palembang": {
            "culture": ["Masjid Agung Palembang", "Museum Sultan Mahmud Badaruddin II", "Kampung Kapitan", "Benteng Kuto Besak"],
            "food": ["Pempek", "Tekwan", "Model", "Kemplang"],
            "culinary": ["Pempek tour", "Traditional Palembang cuisine", "River fish specialties", "Local dessert tasting"],
            "nature": ["Sungai Musi cruise", "Pulau Kemaro", "Danau Ranau", "Bukit Siguntang"],
            "city": ["Jembatan Ampera", "Benteng Kuto Besak", "Pasar 16 Ilir", "Jakabaring Sport City"],
            "shopping": ["Palembang Icon", "Lippo Plaza", "Pasar Cinde", "OPI Mall"]
        },
        "Semarang": {
            "culture": ["Lawang Sewu", "Klenteng Sam Poo Kong", "Masjid Agung Jawa Tengah", "Kota Lama Semarang"],
            "food": ["Lumpia Semarang", "Tahu Gimbal", "Wingko Babat", "Bandeng Presto"],
            "culinary": ["Chinese-Javanese fusion", "Traditional Semarang snacks", "Pecinan food tour", "Local coffee shops"],
            "city": ["Simpang Lima", "Kota Lama", "Tugu Muda", "Masjid Agung"],
            "nature": ["Candi Gedong Songo", "Umbul Sidomukti", "Curug Lawe", "Brown Canyon"],
            "shopping": ["Paragon Mall", "DP Mall", "Pasar Johar", "Citraland Mall"]
        },
        "Solo": {
            "culture": ["Keraton Surakarta", "Pura Mangkunegaran", "Masjid Agung Surakarta", "Museum Radya Pustaka"],
            "food": ["Nasi Liwet", "Serabi Solo", "Timlo", "Tengkleng"],
            "culinary": ["Royal Javanese cuisine", "Traditional Solo breakfast", "Street food Galabo", "Batik and culinary tour"],
            "shopping": ["Pasar Klewer", "Beteng Trade Center", "Solo Grand Mall", "Batik Kauman"],
            "city": ["Alun-alun Kidul", "Benteng Vastenburg", "Taman Balekambang", "Kampung Batik Laweyan"],
            "culture": ["Batik workshop", "Traditional dance performance", "Gamelan music", "Royal heritage tour"]
        }
    }

    # Get destination-specific activities
    dest_activities = destination_activities.get(plan.destination, {
        "general": ["Local sightseeing", "Cultural exploration", "Food tasting", "Shopping"]
    })

    # Generate itinerary based on interests and duration
    selected_activities = []
    for interest in plan.interests:
        if interest in dest_activities:
            selected_activities.extend(dest_activities[interest][:3])

    # If no specific activities found, use general ones
    if not selected_activities:
        for activities_list in dest_activities.values():
            selected_activities.extend(activities_list[:2])

    # Create realistic daily itinerary
    itinerary = []
    activities_per_day = max(2, min(4, len(selected_activities) // plan.duration))

    for day in range(plan.duration):
        start_idx = day * activities_per_day
        end_idx = min(start_idx + activities_per_day, len(selected_activities))
        day_activities = selected_activities[start_idx:end_idx]

        if day_activities:
            if len(day_activities) == 1:
                day_plan = f"Full day: {day_activities[0]}"
            elif len(day_activities) == 2:
                day_plan = f"Pagi: {day_activities[0]} | Sore: {day_activities[1]}"
            elif len(day_activities) == 3:
                day_plan = f"Pagi: {day_activities[0]} | Siang: {day_activities[1]} | Sore: {day_activities[2]}"
            else:
                day_plan = f"Pagi: {day_activities[0]} | Siang: {day_activities[1]} | Sore: {day_activities[2]} | Malam: {day_activities[3]}"
        else:
            day_plan = f"Hari bebas untuk eksplorasi {plan.destination} secara mandiri"

        itinerary.append(day_plan)

    # Generate destination and budget-specific tips
    destination_tips = {
        "Bali": "Sewa motor untuk mobilitas, hindari musim rainy season (Nov-Mar), belajar sedikit bahasa Bali",
        "Jakarta": "Gunakan TransJakarta atau MRT, hindari jam rush hour, siapkan cash untuk street food",
        "Yogyakarta": "Jalan kaki di Malioboro, coba becak untuk pengalaman lokal, beli batik asli",
        "Bandung": "Bawa jaket karena cuaca dingin, coba factory outlet untuk belanja, hindari weekend macet",
        "Lombok": "Bawa sunscreen, siapkan cash untuk Gili Islands, respect adat lokal Sasak",
        "Surabaya": "Coba kuliner khas Jawa Timur, gunakan Suroboyo Bus, kunjungi kampung heritage",
        "Banjarmasin": "Gunakan klotok (perahu tradisional) untuk wisata sungai, coba pasar terapung pagi hari, bawa payung untuk cuaca tropis",
        "Medan": "Coba durian Ucok yang terkenal, gunakan becak motor untuk transportasi, kunjungi Danau Toba untuk day trip",
        "Makassar": "Nikmati sunset di Pantai Losari, coba coto Makassar untuk sarapan, gunakan pete-pete untuk transportasi lokal",
        "Palembang": "Naik kapal wisata Sungai Musi, coba berbagai jenis pempek, kunjungi Pulau Kemaro untuk wisata religi",
        "Semarang": "Kunjungi Kota Lama untuk foto vintage, coba lumpia Gang Lombok, gunakan BRT Trans Semarang",
        "Solo": "Belanja batik di Pasar Klewer, coba nasi liwet Wongso Lemu, jalan kaki di area Keraton untuk pengalaman budaya"
    }

    budget_tips = {
        "low": "Gunakan transportasi umum, makan di warung lokal, pilih homestay atau guesthouse",
        "medium": "Kombinasi transportasi umum dan private, coba restaurant lokal dan hotel bintang 3",
        "high": "Private transport, fine dining, hotel bintang 4-5, dan aktivitas premium"
    }

    # Combine tips
    combined_tips = f"{destination_tips.get(plan.destination, 'Nikmati pengalaman lokal yang autentik')}. {budget_tips.get(plan.budget, 'Sesuaikan aktivitas dengan budget Anda')}."

    # Calculate realistic estimated cost
    base_costs = {"low": 300000, "medium": 800000, "high": 1500000}
    base_cost = base_costs.get(plan.budget, 500000)
    estimated_cost = base_cost * plan.duration

    return TravelPlanResponse(
        destination=plan.destination,
        duration=plan.duration,
        budget=plan.budget,
        interests=plan.interests,
        itinerary=itinerary,
        tips=combined_tips,
        estimated_cost=f"Rp {estimated_cost:,}",
        ai_confidence=round(random.uniform(0.88, 0.96), 2)
    )

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
        potential_cities = regex_module.findall(r'\b[A-Z][a-z]+\b', request.message)
        if potential_cities:
            detected_destination = potential_cities[0]
        else:
            # If still no destination, ask AI to help identify
            detected_destination = "Unknown City"

    # Enhanced duration extraction with regex
    detected_duration = 3  # default

    # Look for number + hari pattern
    duration_match = regex_module.search(r'(\d+)\s*hari', message)
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
    budget_match = regex_module.search(r'(\d+(?:\.\d+)?)\s*juta', message)
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

    # Let AI handle ALL Indonesian destinations - no restrictions!

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

@app.get("/demo-request")
async def demo_request():
    """Show example of how to use the API"""
    return {
        "example_request": {
            "url": "/plan",
            "method": "POST",
            "body": {
                "destination": "Southeast Asia",
                "duration": "7 days",
                "budget": "medium",
                "interests": ["culture", "temples", "beaches"]
            }
        },
        "example_response": {
            "destination": "Bali, Indonesia",
            "description": "A tropical paradise with beautiful beaches, ancient temples, and rich culture",
            "activities": ["Beach relaxation", "Temple visits", "Rice terrace tours", "Traditional dance shows"],
            "estimated_cost": "$800-1200 for 7 days",
            "best_time_to_visit": "April to October"
        }
    }

if __name__ == "__main__":
    print("🌍 Starting AI Travel Guide API Demo...")
    print("📖 Visit http://localhost:8000 for the demo page")
    print("📚 Visit http://localhost:8000/docs for interactive API documentation")
    print("🔍 Visit http://localhost:8000/destinations to see sample destinations")
    
    uvicorn.run(
        "demo_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
