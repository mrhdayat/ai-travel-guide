from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import City, PointOfInterest, User
from app.core.config import settings
import bcrypt

async def create_seed_data(db: AsyncSession):
    """Create seed data for Indonesian destinations"""
    
    # Check if data already exists
    result = await db.execute(select(City))
    if result.first():
        return  # Data already exists
    
    # Cities data
    cities_data = [
        {
            "name": "Jakarta",
            "province": "DKI Jakarta",
            "latitude": -6.2088,
            "longitude": 106.8456,
            "description": "Ibu kota Indonesia dengan berbagai atraksi wisata modern dan bersejarah",
            "image_url": "https://example.com/jakarta.jpg"
        },
        {
            "name": "Bandung",
            "province": "Jawa Barat",
            "latitude": -6.9175,
            "longitude": 107.6191,
            "description": "Kota kembang dengan udara sejuk dan factory outlet terkenal",
            "image_url": "https://example.com/bandung.jpg"
        },
        {
            "name": "Yogyakarta",
            "province": "DI Yogyakarta",
            "latitude": -7.7956,
            "longitude": 110.3695,
            "description": "Kota budaya dengan warisan sejarah dan kuliner tradisional",
            "image_url": "https://example.com/yogyakarta.jpg"
        },
        {
            "name": "Denpasar",
            "province": "Bali",
            "latitude": -8.6500,
            "longitude": 115.2167,
            "description": "Gerbang utama Bali dengan pantai indah dan budaya Hindu yang kaya",
            "image_url": "https://example.com/bali.jpg"
        }
    ]
    
    # Create cities
    cities = []
    for city_data in cities_data:
        city = City(**city_data)
        db.add(city)
        cities.append(city)
    
    await db.commit()
    
    # Refresh to get IDs
    for city in cities:
        await db.refresh(city)
    
    # POIs data
    pois_data = [
        # Jakarta POIs
        {
            "name": "Monumen Nasional (Monas)",
            "category": "wisata",
            "description": "Monumen kemerdekaan setinggi 132 meter dengan museum di bawahnya",
            "latitude": -6.1754,
            "longitude": 106.8272,
            "rating": 4.5,
            "price_range": "murah",
            "city_name": "Jakarta",
            "opening_hours": {"weekday": "08:00-16:00", "weekend": "08:00-17:00"},
            "contact_info": {"phone": "021-3441703", "website": "monas.jakarta.go.id"}
        },
        {
            "name": "Kota Tua Jakarta",
            "category": "wisata",
            "description": "Kawasan bersejarah dengan bangunan kolonial Belanda",
            "latitude": -6.1352,
            "longitude": 106.8133,
            "rating": 4.2,
            "price_range": "murah",
            "city_name": "Jakarta"
        },
        {
            "name": "Ancol Dreamland",
            "category": "wisata",
            "description": "Taman rekreasi terpadu dengan pantai dan wahana permainan",
            "latitude": -6.1223,
            "longitude": 106.8317,
            "rating": 4.0,
            "price_range": "sedang",
            "city_name": "Jakarta"
        },
        {
            "name": "Grand Indonesia",
            "category": "belanja",
            "description": "Mall mewah di pusat Jakarta dengan berbagai brand internasional",
            "latitude": -6.1944,
            "longitude": 106.8231,
            "rating": 4.3,
            "price_range": "mahal",
            "city_name": "Jakarta"
        },
        
        # Bandung POIs
        {
            "name": "Tangkuban Perahu",
            "category": "wisata",
            "description": "Gunung berapi dengan kawah yang dapat dikunjungi",
            "latitude": -6.7599,
            "longitude": 107.6095,
            "rating": 4.4,
            "price_range": "murah",
            "city_name": "Bandung"
        },
        {
            "name": "Jalan Braga",
            "category": "wisata",
            "description": "Jalan bersejarah dengan arsitektur Art Deco",
            "latitude": -6.9147,
            "longitude": 107.6098,
            "rating": 4.1,
            "price_range": "murah",
            "city_name": "Bandung"
        },
        {
            "name": "Factory Outlet Rumah Mode",
            "category": "belanja",
            "description": "Factory outlet terkenal dengan produk fashion berkualitas",
            "latitude": -6.8957,
            "longitude": 107.6337,
            "rating": 4.2,
            "price_range": "sedang",
            "city_name": "Bandung"
        },
        
        # Yogyakarta POIs
        {
            "name": "Candi Borobudur",
            "category": "wisata",
            "description": "Candi Buddha terbesar di dunia, Situs Warisan Dunia UNESCO",
            "latitude": -7.6079,
            "longitude": 110.2038,
            "rating": 4.8,
            "price_range": "sedang",
            "city_name": "Yogyakarta"
        },
        {
            "name": "Keraton Yogyakarta",
            "category": "wisata",
            "description": "Istana Sultan dengan arsitektur Jawa tradisional",
            "latitude": -7.8053,
            "longitude": 110.3644,
            "rating": 4.3,
            "price_range": "murah",
            "city_name": "Yogyakarta"
        },
        {
            "name": "Malioboro Street",
            "category": "belanja",
            "description": "Jalan utama Yogyakarta dengan toko souvenir dan kuliner",
            "latitude": -7.7926,
            "longitude": 110.3656,
            "rating": 4.2,
            "price_range": "murah",
            "city_name": "Yogyakarta"
        },
        
        # Bali POIs
        {
            "name": "Pura Uluwatu",
            "category": "wisata",
            "description": "Pura di tebing dengan pemandangan sunset yang menakjubkan",
            "latitude": -8.8290,
            "longitude": 115.0849,
            "rating": 4.6,
            "price_range": "murah",
            "city_name": "Denpasar"
        },
        {
            "name": "Pantai Kuta",
            "category": "wisata",
            "description": "Pantai terkenal dengan ombak yang cocok untuk surfing",
            "latitude": -8.7184,
            "longitude": 115.1686,
            "rating": 4.1,
            "price_range": "murah",
            "city_name": "Denpasar"
        },
        {
            "name": "Pasar Sukawati",
            "category": "belanja",
            "description": "Pasar tradisional dengan kerajinan tangan Bali",
            "latitude": -8.5833,
            "longitude": 115.2833,
            "rating": 4.0,
            "price_range": "murah",
            "city_name": "Denpasar"
        }
    ]
    
    # Create POIs
    city_map = {city.name: city.id for city in cities}
    
    for poi_data in pois_data:
        city_name = poi_data.pop("city_name")
        poi_data["city_id"] = city_map[city_name]
        poi = PointOfInterest(**poi_data)
        db.add(poi)
    
    await db.commit()
    
    # Create demo user
    demo_user = User(
        email=settings.DEMO_EMAIL,
        hashed_password=bcrypt.hashpw(settings.DEMO_PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        full_name="Demo User",
        is_active=True,
        is_demo=True
    )
    
    db.add(demo_user)
    await db.commit()
    
    print("Seed data created successfully!")
