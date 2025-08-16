import asyncio
import json
import httpx
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.core.config import settings
from app.models.schemas import AISource, TravelPlanResponse, VisionResponse, ChatResponse

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def generate_travel_plan(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate travel plan with fallback chain"""
        
        # Try IBM watsonx first
        try:
            result = await self._watsonx_travel_plan(request_data)
            if result:
                result["ai_source"] = AISource.WATSONX
                return result
        except Exception as e:
            logger.warning(f"Watson X failed: {e}")
        
        # Fallback to Hugging Face
        try:
            result = await self._huggingface_travel_plan(request_data)
            if result:
                result["ai_source"] = AISource.HUGGINGFACE
                return result
        except Exception as e:
            logger.warning(f"Hugging Face failed: {e}")
        
        # Fallback to Replicate (if enabled)
        if settings.USE_REPLICATE and settings.REPLICATE_API_TOKEN:
            try:
                result = await self._replicate_travel_plan(request_data)
                if result:
                    result["ai_source"] = AISource.REPLICATE
                    return result
            except Exception as e:
                logger.warning(f"Replicate failed: {e}")
        
        # Final fallback to baseline plan
        return await self._baseline_travel_plan(request_data)

    async def analyze_image(self, image_data: str) -> Dict[str, Any]:
        """Analyze landmark image with fallback chain"""
        
        # Try Hugging Face first (better for vision)
        try:
            result = await self._huggingface_vision(image_data)
            if result:
                result["ai_source"] = AISource.HUGGINGFACE
                return result
        except Exception as e:
            logger.warning(f"Hugging Face vision failed: {e}")
        
        # Fallback to Watson X
        try:
            result = await self._watsonx_vision(image_data)
            if result:
                result["ai_source"] = AISource.WATSONX
                return result
        except Exception as e:
            logger.warning(f"Watson X vision failed: {e}")
        
        # Fallback to Replicate
        if settings.USE_REPLICATE and settings.REPLICATE_API_TOKEN:
            try:
                result = await self._replicate_vision(image_data)
                if result:
                    result["ai_source"] = AISource.REPLICATE
                    return result
            except Exception as e:
                logger.warning(f"Replicate vision failed: {e}")
        
        # Baseline response
        return {
            "landmarks": [{"name": "Landmark tidak dikenali", "description": "Mohon coba dengan gambar yang lebih jelas", "confidence": 0.1}],
            "summary": "Tidak dapat mengidentifikasi landmark dalam gambar",
            "ai_source": "baseline",
            "confidence": 0.1
        }

    async def chat_response(self, message: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate chat response with fallback chain"""
        
        # Try IBM watsonx first
        try:
            result = await self._watsonx_chat(message, context)
            if result:
                result["ai_source"] = AISource.WATSONX
                return result
        except Exception as e:
            logger.warning(f"Watson X chat failed: {e}")
        
        # Fallback to Hugging Face
        try:
            result = await self._huggingface_chat(message, context)
            if result:
                result["ai_source"] = AISource.HUGGINGFACE
                return result
        except Exception as e:
            logger.warning(f"Hugging Face chat failed: {e}")
        
        # Fallback to Replicate
        if settings.USE_REPLICATE and settings.REPLICATE_API_TOKEN:
            try:
                result = await self._replicate_chat(message, context)
                if result:
                    result["ai_source"] = AISource.REPLICATE
                    return result
            except Exception as e:
                logger.warning(f"Replicate chat failed: {e}")
        
        # Baseline response
        return {
            "answer": "Maaf, saya sedang mengalami gangguan teknis. Silakan coba lagi nanti atau hubungi customer service.",
            "confidence": 0.1,
            "suggestions": ["Coba tanyakan tentang destinasi wisata populer", "Tanyakan tentang budget perjalanan"]
        }

    async def _watsonx_travel_plan(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """IBM watsonx travel planning"""
        if not settings.WATSONX_API_KEY or not settings.WATSONX_PROJECT_ID:
            return None
            
        prompt = self._create_travel_prompt(request_data)
        
        payload = {
            "model_id": "ibm-granite/granite-3.3-8b-instruct",
            "input": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "top_p": 0.9
            },
            "project_id": settings.WATSONX_PROJECT_ID
        }
        
        headers = {
            "Authorization": f"Bearer {settings.WATSONX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = await self.client.post(
            "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return self._parse_travel_response(result.get("results", [{}])[0].get("generated_text", ""))
        
        return None

    async def _huggingface_travel_plan(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Hugging Face travel planning"""
        if not settings.HF_API_KEY:
            return None

        prompt = self._create_travel_prompt(request_data)

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "return_full_text": False
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.HF_API_KEY}",
            "Content-Type": "application/json"
        }

        # Try multiple models for better Indonesian support
        models = [
            "microsoft/DialoGPT-medium",
            "facebook/blenderbot-400M-distill",
            "google/flan-t5-base"
        ]

        for model in models:
            try:
                response = await self.client.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    json=payload,
                    headers=headers
                )

                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        generated_text = result[0].get("generated_text", "")
                        parsed = self._parse_travel_response(generated_text)
                        if parsed:
                            return parsed
            except Exception as e:
                logger.warning(f"HF model {model} failed: {e}")
                continue

        return None

    async def _replicate_travel_plan(self, request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Replicate travel planning"""
        if not settings.REPLICATE_API_TOKEN:
            return None

        prompt = self._create_travel_prompt(request_data)

        payload = {
            "version": "latest",
            "input": {
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.7
            }
        }

        headers = {
            "Authorization": f"Token {settings.REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        response = await self.client.post(
            "https://api.replicate.com/v1/predictions",
            json=payload,
            headers=headers
        )

        if response.status_code == 201:
            prediction = response.json()
            # Poll for completion (simplified)
            await asyncio.sleep(2)

            get_response = await self.client.get(
                prediction["urls"]["get"],
                headers=headers
            )

            if get_response.status_code == 200:
                result = get_response.json()
                if result.get("status") == "succeeded":
                    output = result.get("output", "")
                    return self._parse_travel_response(output)

        return None

    async def _baseline_travel_plan(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Baseline travel plan when all AI services fail"""
        destination = request_data.get("destination", "Jakarta")
        duration = request_data.get("duration_days", 3)
        budget = request_data.get("budget_range", "sedang")

        # Simple baseline itinerary
        daily_routes = []
        for day in range(1, duration + 1):
            daily_routes.append({
                "day": day,
                "date": (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
                "activities": [
                    {
                        "time": "09:00",
                        "activity": f"Jelajahi {destination} - Hari {day}",
                        "location": destination,
                        "description": "Kunjungi tempat wisata populer di sekitar area",
                        "estimated_cost": 100000 if budget == "murah" else 200000 if budget == "sedang" else 500000
                    }
                ],
                "estimated_cost": 150000 if budget == "murah" else 300000 if budget == "sedang" else 750000
            })

        total_cost = sum(day["estimated_cost"] for day in daily_routes)

        return {
            "title": f"Perjalanan {duration} Hari ke {destination}",
            "destination": destination,
            "duration_days": duration,
            "daily_routes": daily_routes,
            "cost_estimate": {
                "accommodation": total_cost * 0.4,
                "food": total_cost * 0.3,
                "transport": total_cost * 0.2,
                "activities": total_cost * 0.1,
                "total": total_cost,
                "currency": "IDR"
            },
            "ai_source": "baseline",
            "confidence": 0.6
        }

    def _create_travel_prompt(self, request_data: Dict[str, Any]) -> str:
        """Create Indonesian travel planning prompt"""
        destination = request_data.get("destination", "")
        duration = request_data.get("duration_days", 3)
        budget = request_data.get("budget_range", "sedang")
        preferences = request_data.get("preferences", [])

        prompt = f"""
Buatkan rencana perjalanan wisata {duration} hari ke {destination} dengan budget {budget}.

Preferensi khusus: {', '.join(preferences) if preferences else 'Tidak ada'}

Format respons dalam JSON:
{{
    "title": "Judul perjalanan",
    "destination": "{destination}",
    "duration_days": {duration},
    "daily_routes": [
        {{
            "day": 1,
            "date": "2024-01-01",
            "activities": [
                {{
                    "time": "09:00",
                    "activity": "Nama aktivitas",
                    "location": "Lokasi",
                    "description": "Deskripsi singkat",
                    "estimated_cost": 100000
                }}
            ],
            "estimated_cost": 300000
        }}
    ],
    "cost_estimate": {{
        "accommodation": 500000,
        "food": 300000,
        "transport": 200000,
        "activities": 400000,
        "total": 1400000,
        "currency": "IDR"
    }},
    "confidence": 0.8
}}

Berikan rekomendasi yang realistis dan sesuai dengan budget serta preferensi yang diminta.
"""
        return prompt.strip()

    def _parse_travel_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse AI response to extract travel plan JSON"""
        try:
            # Try to find JSON in the response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)

                # Validate required fields
                required_fields = ["title", "destination", "duration_days", "daily_routes", "cost_estimate"]
                if all(field in parsed for field in required_fields):
                    return parsed

        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse travel response: {e}")

        return None
