import base64
import httpx
import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class VisionService:
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def _huggingface_vision(self, image_data: str) -> Optional[Dict[str, Any]]:
        """Hugging Face image analysis"""
        if not settings.HF_API_KEY:
            return None
            
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
            
        image_bytes = base64.b64decode(image_data)
        
        headers = {
            "Authorization": f"Bearer {settings.HF_API_KEY}",
        }
        
        # Try BLIP for image captioning
        try:
            response = await self.client.post(
                "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-base",
                headers=headers,
                data=image_bytes
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    caption = result[0].get("generated_text", "")
                    return self._process_vision_result(caption)
                    
        except Exception as e:
            logger.warning(f"BLIP captioning failed: {e}")
        
        # Try CLIP as fallback
        try:
            payload = {
                "inputs": {
                    "image": image_data,
                    "candidates": [
                        "Monas Jakarta", "Borobudur Temple", "Prambanan Temple",
                        "Uluwatu Temple Bali", "Mount Bromo", "Lake Toba",
                        "Komodo Island", "Raja Ampat", "Tana Toraja",
                        "Yogyakarta Palace", "Bandung", "Malioboro Street"
                    ]
                }
            }
            
            response = await self.client.post(
                "https://api-inference.huggingface.co/models/openai/clip-vit-base-patch32",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    best_match = max(result, key=lambda x: x.get("score", 0))
                    return self._process_clip_result(best_match)
                    
        except Exception as e:
            logger.warning(f"CLIP analysis failed: {e}")
        
        return None

    async def _watsonx_vision(self, image_data: str) -> Optional[Dict[str, Any]]:
        """Watson X vision analysis"""
        if not settings.WATSONX_API_KEY:
            return None
            
        # Watson X doesn't have direct vision API, so we'll use text generation
        # with a description prompt
        prompt = """
        Analisis gambar ini dan identifikasi landmark atau tempat wisata yang terlihat.
        Berikan respons dalam format JSON:
        {
            "landmarks": [
                {
                    "name": "Nama landmark",
                    "description": "Deskripsi singkat",
                    "location": "Lokasi",
                    "confidence": 0.8
                }
            ],
            "summary": "Ringkasan analisis gambar"
        }
        """
        
        payload = {
            "model_id": "ibm-granite/granite-3.3-8b-instruct",
            "input": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.3
            },
            "project_id": settings.WATSONX_PROJECT_ID
        }
        
        headers = {
            "Authorization": f"Bearer {settings.WATSONX_API_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(
                "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("results", [{}])[0].get("generated_text", "")
                return self._parse_vision_json(generated_text)
                
        except Exception as e:
            logger.warning(f"Watson X vision failed: {e}")
        
        return None

    async def _replicate_vision(self, image_data: str) -> Optional[Dict[str, Any]]:
        """Replicate vision analysis"""
        if not settings.REPLICATE_API_TOKEN:
            return None
            
        payload = {
            "version": "latest",
            "input": {
                "image": f"data:image/jpeg;base64,{image_data}",
                "prompt": "Describe this landmark or tourist attraction in Indonesia"
            }
        }
        
        headers = {
            "Authorization": f"Token {settings.REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(
                "https://api.replicate.com/v1/predictions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 201:
                prediction = response.json()
                # Simplified polling
                import asyncio
                await asyncio.sleep(3)
                
                get_response = await self.client.get(
                    prediction["urls"]["get"],
                    headers=headers
                )
                
                if get_response.status_code == 200:
                    result = get_response.json()
                    if result.get("status") == "succeeded":
                        output = result.get("output", "")
                        return self._process_vision_result(output)
                        
        except Exception as e:
            logger.warning(f"Replicate vision failed: {e}")
        
        return None

    def _process_vision_result(self, description: str) -> Dict[str, Any]:
        """Process vision analysis result"""
        # Simple keyword matching for Indonesian landmarks
        landmarks_db = {
            "monas": {"name": "Monumen Nasional", "location": "Jakarta", "category": "monument"},
            "borobudur": {"name": "Candi Borobudur", "location": "Yogyakarta", "category": "temple"},
            "prambanan": {"name": "Candi Prambanan", "location": "Yogyakarta", "category": "temple"},
            "uluwatu": {"name": "Pura Uluwatu", "location": "Bali", "category": "temple"},
            "bromo": {"name": "Gunung Bromo", "location": "Jawa Timur", "category": "mountain"},
            "toba": {"name": "Danau Toba", "location": "Sumatera Utara", "category": "lake"},
        }
        
        description_lower = description.lower()
        detected_landmarks = []
        
        for keyword, info in landmarks_db.items():
            if keyword in description_lower:
                detected_landmarks.append({
                    "name": info["name"],
                    "description": f"Landmark terkenal di {info['location']}",
                    "location": info["location"],
                    "category": info["category"],
                    "confidence": 0.7
                })
        
        if not detected_landmarks:
            detected_landmarks.append({
                "name": "Tempat wisata Indonesia",
                "description": "Lokasi wisata yang menarik di Indonesia",
                "location": "Indonesia",
                "category": "tourism",
                "confidence": 0.4
            })
        
        return {
            "landmarks": detected_landmarks,
            "summary": f"Terdeteksi {len(detected_landmarks)} landmark dalam gambar",
            "confidence": max([l["confidence"] for l in detected_landmarks])
        }

    def _process_clip_result(self, clip_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process CLIP analysis result"""
        label = clip_result.get("label", "Unknown")
        score = clip_result.get("score", 0.0)
        
        return {
            "landmarks": [{
                "name": label,
                "description": f"Landmark yang teridentifikasi dengan tingkat kepercayaan {score:.2f}",
                "confidence": score
            }],
            "summary": f"Teridentifikasi sebagai {label}",
            "confidence": score
        }

    def _parse_vision_json(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON response from vision analysis"""
        try:
            import json
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                parsed = json.loads(json_str)
                
                if "landmarks" in parsed:
                    return parsed
                    
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse vision JSON: {e}")
            
        return None
