from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import base64
import io
from PIL import Image

from app.core.database import get_db
from app.core.config import settings
from app.models.schemas import VisionRequest, VisionResponse
from app.models.models import User
from app.services.vision_service import VisionService
from app.utils.auth import get_current_user_optional

router = APIRouter()

@router.post("/vision", response_model=VisionResponse)
async def analyze_landmark_image(
    request: VisionRequest = None,
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Analyze landmark image using AI vision models
    """
    try:
        image_data = None
        
        # Get image data from either request body or file upload
        if file:
            # Validate file
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File harus berupa gambar"
                )
            
            if file.size > settings.MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ukuran file terlalu besar. Maksimal 5MB"
                )
            
            # Read and process image
            image_bytes = await file.read()
            
            # Convert to RGB if needed and resize
            try:
                image = Image.open(io.BytesIO(image_bytes))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Resize if too large
                max_size = (1024, 1024)
                if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert back to bytes
                img_buffer = io.BytesIO()
                image.save(img_buffer, format='JPEG', quality=85)
                image_bytes = img_buffer.getvalue()
                
                # Encode to base64
                image_data = base64.b64encode(image_bytes).decode('utf-8')
                
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Gagal memproses gambar: {str(e)}"
                )
                
        elif request and request.image_data:
            image_data = request.image_data
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gambar diperlukan (gunakan file upload atau base64 data)"
            )
        
        # Initialize vision service
        vision_service = VisionService()
        
        # Analyze image using fallback chain
        # Try Hugging Face first (better for vision)
        result = await vision_service._huggingface_vision(image_data)
        if result:
            result["ai_source"] = "huggingface"
        else:
            # Try Watson X
            result = await vision_service._watsonx_vision(image_data)
            if result:
                result["ai_source"] = "watsonx"
            else:
                # Try Replicate
                if settings.USE_REPLICATE and settings.REPLICATE_API_TOKEN:
                    result = await vision_service._replicate_vision(image_data)
                    if result:
                        result["ai_source"] = "replicate"
                
                # Fallback response
                if not result:
                    result = {
                        "landmarks": [{
                            "name": "Landmark tidak dikenali",
                            "description": "Mohon coba dengan gambar yang lebih jelas atau dari sudut yang berbeda",
                            "confidence": 0.1
                        }],
                        "summary": "Tidak dapat mengidentifikasi landmark dalam gambar",
                        "ai_source": "baseline",
                        "confidence": 0.1
                    }
        
        return VisionResponse(
            landmarks=result["landmarks"],
            summary=result["summary"],
            ai_source=result["ai_source"],
            confidence=result["confidence"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat menganalisis gambar: {str(e)}"
        )

@router.post("/vision/demo", response_model=VisionResponse)
async def demo_vision_analysis():
    """
    Demo vision analysis for presentation
    """
    # Demo response for Monas Jakarta
    demo_result = {
        "landmarks": [
            {
                "name": "Monumen Nasional (Monas)",
                "description": "Monumen setinggi 132 meter yang menjadi simbol kemerdekaan Indonesia, terletak di Jakarta Pusat",
                "location": "Jakarta Pusat, DKI Jakarta",
                "category": "monument",
                "confidence": 0.92
            }
        ],
        "summary": "Teridentifikasi Monumen Nasional (Monas), landmark ikonik Jakarta yang merupakan simbol kemerdekaan Indonesia",
        "ai_source": "demo",
        "confidence": 0.92
    }
    
    return VisionResponse(**demo_result)

@router.get("/landmarks/popular")
async def get_popular_landmarks():
    """
    Get list of popular Indonesian landmarks for reference
    """
    landmarks = [
        {
            "name": "Monumen Nasional (Monas)",
            "location": "Jakarta",
            "category": "monument",
            "description": "Simbol kemerdekaan Indonesia"
        },
        {
            "name": "Candi Borobudur",
            "location": "Yogyakarta",
            "category": "temple",
            "description": "Candi Buddha terbesar di dunia"
        },
        {
            "name": "Candi Prambanan",
            "location": "Yogyakarta",
            "category": "temple",
            "description": "Kompleks candi Hindu terbesar di Indonesia"
        },
        {
            "name": "Pura Uluwatu",
            "location": "Bali",
            "category": "temple",
            "description": "Pura di tebing dengan pemandangan laut"
        },
        {
            "name": "Gunung Bromo",
            "location": "Jawa Timur",
            "category": "mountain",
            "description": "Gunung berapi aktif dengan pemandangan sunrise"
        },
        {
            "name": "Danau Toba",
            "location": "Sumatera Utara",
            "category": "lake",
            "description": "Danau vulkanik terbesar di Indonesia"
        },
        {
            "name": "Pulau Komodo",
            "location": "Nusa Tenggara Timur",
            "category": "island",
            "description": "Habitat asli komodo dragon"
        },
        {
            "name": "Raja Ampat",
            "location": "Papua Barat",
            "category": "marine",
            "description": "Surga diving dengan biodiversitas laut tertinggi"
        }
    ]
    
    return {"landmarks": landmarks}

@router.get("/vision/supported-formats")
async def get_supported_formats():
    """
    Get supported image formats and limits
    """
    return {
        "supported_formats": ["JPEG", "PNG", "WebP"],
        "max_file_size": f"{settings.MAX_IMAGE_SIZE // (1024*1024)}MB",
        "max_dimensions": "1024x1024 pixels",
        "recommended_quality": "High quality, well-lit images work best"
    }
