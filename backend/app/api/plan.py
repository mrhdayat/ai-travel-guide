from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from app.core.database import get_db
from app.models.schemas import TravelPlanRequest, TravelPlanResponse
from app.models.models import TravelPlan, User
from app.services.ai_service import AIService
from app.utils.auth import get_current_user_optional

router = APIRouter()

@router.post("/plan", response_model=TravelPlanResponse)
async def create_travel_plan(
    request: TravelPlanRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Generate travel itinerary with AI fallback chain
    """
    try:
        # Initialize AI service
        ai_service = AIService()
        
        # Prepare request data
        request_data = {
            "destination": request.destination,
            "duration_days": request.duration_days,
            "budget_range": request.budget_range.value if request.budget_range else "sedang",
            "preferences": [p.value for p in request.preferences] if request.preferences else [],
            "departure_city": request.departure_city
        }
        
        # Generate travel plan using AI fallback chain
        plan_data = await ai_service.generate_travel_plan(request_data)
        
        if not plan_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gagal membuat rencana perjalanan. Silakan coba lagi."
            )
        
        # Save to database if user is logged in
        travel_plan = None
        if current_user:
            travel_plan = TravelPlan(
                title=plan_data["title"],
                destination=plan_data["destination"],
                duration_days=plan_data["duration_days"],
                budget_range=request.budget_range.value if request.budget_range else None,
                preferences=[p.value for p in request.preferences] if request.preferences else None,
                itinerary=plan_data["daily_routes"],
                cost_estimate=plan_data["cost_estimate"],
                transport_options=plan_data.get("transport_options"),
                user_id=current_user.id,
                ai_source=plan_data["ai_source"],
                confidence_score=plan_data.get("confidence", 0.0)
            )
            
            db.add(travel_plan)
            await db.commit()
            await db.refresh(travel_plan)
        
        # Return response
        return TravelPlanResponse(
            id=travel_plan.id if travel_plan else None,
            title=plan_data["title"],
            destination=plan_data["destination"],
            duration_days=plan_data["duration_days"],
            daily_routes=plan_data["daily_routes"],
            cost_estimate=plan_data["cost_estimate"],
            transport_options=plan_data.get("transport_options"),
            preferences=[p.value for p in request.preferences] if request.preferences else None,
            ai_source=plan_data["ai_source"],
            confidence_score=plan_data.get("confidence", 0.0),
            created_at=travel_plan.created_at if travel_plan else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan: {str(e)}"
        )

@router.get("/plans", response_model=List[TravelPlanResponse])
async def get_user_plans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
    skip: int = 0,
    limit: int = 10
):
    """
    Get user's travel plans
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login diperlukan untuk melihat rencana perjalanan"
        )
    
    from sqlalchemy import select
    
    query = select(TravelPlan).where(
        TravelPlan.user_id == current_user.id
    ).offset(skip).limit(limit).order_by(TravelPlan.created_at.desc())
    
    result = await db.execute(query)
    plans = result.scalars().all()
    
    return [
        TravelPlanResponse(
            id=plan.id,
            title=plan.title,
            destination=plan.destination,
            duration_days=plan.duration_days,
            daily_routes=plan.itinerary,
            cost_estimate=plan.cost_estimate,
            transport_options=plan.transport_options,
            preferences=plan.preferences,
            ai_source=plan.ai_source,
            confidence_score=plan.confidence_score,
            created_at=plan.created_at
        )
        for plan in plans
    ]

@router.get("/plan/{plan_id}", response_model=TravelPlanResponse)
async def get_travel_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Get specific travel plan
    """
    from sqlalchemy import select
    
    query = select(TravelPlan).where(TravelPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rencana perjalanan tidak ditemukan"
        )
    
    # Check if user owns the plan (if user is logged in)
    if current_user and plan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Anda tidak memiliki akses ke rencana perjalanan ini"
        )
    
    return TravelPlanResponse(
        id=plan.id,
        title=plan.title,
        destination=plan.destination,
        duration_days=plan.duration_days,
        daily_routes=plan.itinerary,
        cost_estimate=plan.cost_estimate,
        transport_options=plan.transport_options,
        preferences=plan.preferences,
        ai_source=plan.ai_source,
        confidence_score=plan.confidence_score,
        created_at=plan.created_at
    )

@router.post("/demo-plan", response_model=TravelPlanResponse)
async def create_demo_plan():
    """
    Create demo travel plan for presentation
    """
    # Demo plan: Jakarta-Bandung 3 days
    demo_plan = {
        "title": "Perjalanan 3 Hari Jakarta-Bandung",
        "destination": "Bandung",
        "duration_days": 3,
        "daily_routes": [
            {
                "day": 1,
                "date": "2024-01-15",
                "activities": [
                    {
                        "time": "08:00",
                        "activity": "Keberangkatan dari Jakarta",
                        "location": "Jakarta",
                        "description": "Perjalanan menuju Bandung dengan kereta api atau mobil",
                        "estimated_cost": 150000
                    },
                    {
                        "time": "12:00",
                        "activity": "Makan siang di Gedung Sate",
                        "location": "Gedung Sate, Bandung",
                        "description": "Menikmati kuliner khas Bandung sambil melihat arsitektur bersejarah",
                        "estimated_cost": 75000
                    },
                    {
                        "time": "14:00",
                        "activity": "Jalan-jalan di Jalan Braga",
                        "location": "Jalan Braga, Bandung",
                        "description": "Menjelajahi kawasan bersejarah dengan bangunan Art Deco",
                        "estimated_cost": 50000
                    }
                ],
                "estimated_cost": 275000
            },
            {
                "day": 2,
                "date": "2024-01-16",
                "activities": [
                    {
                        "time": "09:00",
                        "activity": "Wisata ke Tangkuban Perahu",
                        "location": "Tangkuban Perahu",
                        "description": "Melihat kawah vulkan dan menikmati pemandangan alam",
                        "estimated_cost": 100000
                    },
                    {
                        "time": "13:00",
                        "activity": "Belanja di Factory Outlet",
                        "location": "Dago, Bandung",
                        "description": "Berbelanja pakaian dengan harga terjangkau",
                        "estimated_cost": 200000
                    }
                ],
                "estimated_cost": 300000
            },
            {
                "day": 3,
                "date": "2024-01-17",
                "activities": [
                    {
                        "time": "10:00",
                        "activity": "Wisata kuliner di Kampung Gajah",
                        "location": "Kampung Gajah, Lembang",
                        "description": "Menikmati wahana dan kuliner di kawasan wisata",
                        "estimated_cost": 150000
                    },
                    {
                        "time": "15:00",
                        "activity": "Kembali ke Jakarta",
                        "location": "Bandung - Jakarta",
                        "description": "Perjalanan pulang ke Jakarta",
                        "estimated_cost": 150000
                    }
                ],
                "estimated_cost": 300000
            }
        ],
        "cost_estimate": {
            "accommodation": 600000,
            "food": 450000,
            "transport": 300000,
            "activities": 525000,
            "total": 1875000,
            "currency": "IDR"
        },
        "ai_source": "demo",
        "confidence": 0.95
    }
    
    return TravelPlanResponse(**demo_plan)
