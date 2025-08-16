from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import uuid
import httpx
import logging

from app.core.database import get_db
from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse, AISource
from app.models.models import ChatHistory, User
from app.utils.auth import get_current_user_optional

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def generate_response(self, message: str, context: Optional[dict] = None) -> dict:
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
        return self._baseline_response(message)

    async def _watsonx_chat(self, message: str, context: Optional[dict] = None) -> Optional[dict]:
        """IBM watsonx chat"""
        if not settings.WATSONX_API_KEY or not settings.WATSONX_PROJECT_ID:
            return None
            
        prompt = self._create_chat_prompt(message, context)
        
        payload = {
            "model_id": "ibm-granite/granite-3.3-8b-instruct",
            "input": prompt,
            "parameters": {
                "max_new_tokens": 500,
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
            generated_text = result.get("results", [{}])[0].get("generated_text", "")
            return self._parse_chat_response(generated_text)
        
        return None

    async def _huggingface_chat(self, message: str, context: Optional[dict] = None) -> Optional[dict]:
        """Hugging Face chat"""
        if not settings.HF_API_KEY:
            return None
            
        prompt = self._create_chat_prompt(message, context)
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        headers = {
            "Authorization": f"Bearer {settings.HF_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Try multiple models
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
                        parsed = self._parse_chat_response(generated_text)
                        if parsed:
                            return parsed
            except Exception as e:
                logger.warning(f"HF model {model} failed: {e}")
                continue
        
        return None

    async def _replicate_chat(self, message: str, context: Optional[dict] = None) -> Optional[dict]:
        """Replicate chat"""
        if not settings.REPLICATE_API_TOKEN:
            return None
            
        prompt = self._create_chat_prompt(message, context)
        
        payload = {
            "version": "latest",
            "input": {
                "prompt": prompt,
                "max_tokens": 500,
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
            # Simplified polling
            import asyncio
            await asyncio.sleep(2)
            
            get_response = await self.client.get(
                prediction["urls"]["get"],
                headers=headers
            )
            
            if get_response.status_code == 200:
                result = get_response.json()
                if result.get("status") == "succeeded":
                    output = result.get("output", "")
                    return self._parse_chat_response(output)
        
        return None

    def _create_chat_prompt(self, message: str, context: Optional[dict] = None) -> str:
        """Create Indonesian travel chat prompt"""
        base_prompt = """
Anda adalah asisten wisata AI yang membantu wisatawan merencanakan perjalanan di Indonesia.
Berikan jawaban yang informatif, ramah, dan dalam bahasa Indonesia.

Fokus pada:
- Destinasi wisata populer di Indonesia
- Estimasi biaya perjalanan
- Tips perjalanan praktis
- Kuliner lokal
- Transportasi
- Akomodasi

Pertanyaan: {message}

Jawaban:"""
        
        if context:
            context_info = f"\nKonteks sebelumnya: {context.get('previous_topic', '')}"
            base_prompt = context_info + base_prompt
        
        return base_prompt.format(message=message)

    def _parse_chat_response(self, response_text: str) -> Optional[dict]:
        """Parse chat response"""
        if not response_text or len(response_text.strip()) < 10:
            return None
            
        # Clean up the response
        answer = response_text.strip()
        
        # Remove any prompt repetition
        if "Jawaban:" in answer:
            answer = answer.split("Jawaban:")[-1].strip()
        
        # Generate suggestions based on the answer
        suggestions = self._generate_suggestions(answer)
        
        return {
            "answer": answer,
            "confidence": 0.8,
            "suggestions": suggestions
        }

    def _generate_suggestions(self, answer: str) -> list:
        """Generate follow-up suggestions"""
        suggestions = []
        
        # Keyword-based suggestions
        if any(word in answer.lower() for word in ["jakarta", "bandung", "yogyakarta"]):
            suggestions.append("Tanyakan tentang transportasi antar kota")
        
        if any(word in answer.lower() for word in ["budget", "biaya", "harga"]):
            suggestions.append("Minta tips menghemat biaya perjalanan")
        
        if any(word in answer.lower() for word in ["kuliner", "makanan", "restoran"]):
            suggestions.append("Rekomendasi makanan khas daerah lain")
        
        if any(word in answer.lower() for word in ["hotel", "penginapan", "akomodasi"]):
            suggestions.append("Tips memilih akomodasi yang aman")
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "Tanyakan tentang destinasi wisata populer",
                "Minta estimasi budget perjalanan",
                "Tips perjalanan untuk pemula"
            ]
        
        return suggestions[:3]  # Limit to 3 suggestions

    def _baseline_response(self, message: str) -> dict:
        """Baseline response when all AI services fail"""
        return {
            "answer": "Maaf, saya sedang mengalami gangguan teknis. Untuk informasi wisata Indonesia, Anda bisa mengunjungi website resmi Kementerian Pariwisata atau menghubungi customer service kami.",
            "ai_source": "baseline",
            "confidence": 0.1,
            "suggestions": [
                "Coba tanyakan tentang destinasi wisata populer",
                "Tanyakan tentang budget perjalanan",
                "Minta tips perjalanan"
            ]
        }

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Chat with AI travel assistant
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize chat service
        chat_service = ChatService()
        
        # Generate response
        result = await chat_service.generate_response(request.message, request.context)
        
        # Save chat history if user is logged in
        if current_user:
            chat_history = ChatHistory(
                session_id=session_id,
                user_message=request.message,
                ai_response=result["answer"],
                ai_source=result["ai_source"],
                user_id=current_user.id
            )
            
            db.add(chat_history)
            await db.commit()
        
        return ChatResponse(
            answer=result["answer"],
            session_id=session_id,
            ai_source=result["ai_source"],
            confidence=result["confidence"],
            suggestions=result.get("suggestions")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan: {str(e)}"
        )

@router.post("/chat/demo", response_model=ChatResponse)
async def demo_chat():
    """
    Demo chat response for presentation
    """
    demo_response = {
        "answer": "Selamat datang di AI Travel Guide! Saya siap membantu Anda merencanakan perjalanan wisata di Indonesia. Anda bisa bertanya tentang destinasi wisata, estimasi biaya, transportasi, akomodasi, atau kuliner lokal. Mau mulai dari mana?",
        "session_id": str(uuid.uuid4()),
        "ai_source": "demo",
        "confidence": 0.95,
        "suggestions": [
            "Rekomendasi destinasi wisata populer",
            "Estimasi budget untuk liburan 3 hari",
            "Tips perjalanan hemat untuk backpacker"
        ]
    }
    
    return ChatResponse(**demo_response)
