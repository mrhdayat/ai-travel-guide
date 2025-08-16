# AI Multimodal Travel Guide - Documentation

## 🎯 Overview

AI Travel Guide adalah aplikasi panduan wisata multimodal yang mendukung input teks, suara, dan gambar untuk merencanakan perjalanan di Indonesia. Aplikasi ini dibangun dengan teknologi AI terdepan dan dirancang khusus untuk demo IBM Jakarta.

## 🏗️ Architecture

### Frontend
- **React 18** + **Vite** + **TypeScript**
- **Tailwind CSS** untuk styling
- **ShadCN/UI** + **Radix UI** untuk komponen
- **Framer Motion** untuk animasi
- **React Spring** untuk efek parallax
- **MapLibre GL JS** untuk peta interaktif

### Backend
- **FastAPI** dengan Python 3.11
- **SQLAlchemy** + **Alembic** untuk database
- **SQLite** (default) / **PostgreSQL** (production)
- **JWT** untuk autentikasi
- **Uvicorn** sebagai ASGI server

### AI Services (Fallback Chain)
1. **Primary**: IBM watsonx (`granite-3.3-8b-instruct`)
2. **Secondary**: Hugging Face Inference API
3. **Tertiary**: Replicate (optional)
4. **Baseline**: Hardcoded responses

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (untuk development)
- Python 3.11+ (untuk development)

### 1. Clone & Setup
```bash
git clone <repository-url>
cd ai-guide-travel
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file dengan API keys Anda:
```env
# AI Services
WATSONX_API_KEY=your_watsonx_key
WATSONX_PROJECT_ID=your_project_id
HF_API_KEY=your_huggingface_key

# Optional
REPLICATE_API_TOKEN=your_replicate_token
USE_REPLICATE=false
```

### 3. Start Application
```bash
# One-command deployment
./start.sh

# Or manually with Docker
docker compose up -d
```

### 4. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📱 Features

### 🎤 Multimodal Input
- **Text**: Form input untuk planning
- **Voice**: Web Speech API (browser native)
- **Image**: Upload foto landmark untuk identifikasi

### 🤖 AI Fallback Chain
- Robust 3-tier fallback system
- 24/7 availability dengan minimal errors
- Consistent JSON output format
- Indonesian language support

### 🗺️ Interactive Maps
- MapLibre + OpenStreetMap integration
- Route visualization
- POI markers
- Mobile responsive

### 🎨 Modern UI/UX
- Responsive design (mobile-first)
- Smooth animations dengan Framer Motion
- Glass morphism effects
- Dark/light mode support

## 🔧 API Endpoints

### Travel Planning
```http
POST /api/plan
Content-Type: application/json

{
  "destination": "Bandung",
  "duration_days": 3,
  "budget_range": "sedang",
  "preferences": ["halal", "family_friendly"]
}
```

### Vision Analysis
```http
POST /api/vision
Content-Type: multipart/form-data

file: <image_file>
```

### Chat AI
```http
POST /api/chat
Content-Type: application/json

{
  "message": "Rekomendasi tempat wisata di Bali",
  "session_id": "optional-session-id"
}
```

### Authentication
```http
POST /api/auth/demo-login
POST /api/auth/token
GET /api/auth/me
```

## 🎭 Demo Scenarios

### 1. Jakarta-Bandung 3 Days
```bash
curl -X POST "http://localhost:8000/api/demo-plan"
```

### 2. Landmark Recognition
```bash
curl -X POST "http://localhost:8000/api/vision/demo"
```

### 3. Chat Demo
```bash
curl -X POST "http://localhost:8000/api/chat/demo"
```

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Database Migration
```bash
cd backend
alembic upgrade head
```

## 🧪 Testing

### Frontend Tests
```bash
cd frontend
npm run test
```

### Backend Tests
```bash
cd backend
pytest
```

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Demo endpoints
curl http://localhost:8000/api/demo-plan
curl http://localhost:8000/api/vision/demo
curl http://localhost:8000/api/chat/demo
```

## 📊 Monitoring

### Application Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f api
docker compose logs -f web
```

### Health Checks
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/health
- Database: Included in health endpoint

## 🔒 Security

### Authentication
- JWT tokens dengan expiry
- Demo user untuk testing
- Optional Supabase/Firebase integration

### Input Validation
- File size limits (5MB)
- Image format validation
- SQL injection protection
- XSS protection

## 🌍 Deployment

### Production Deployment
```bash
# Build images
docker compose -f docker-compose.prod.yml build

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

### Environment Variables
```env
# Production settings
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/db
CORS_ORIGINS=https://yourdomain.com
```

## 🎯 IBM Demo Preparation

### Demo Flow
1. **Landing Page**: Showcase features
2. **Demo Mode Button**: One-click demo
3. **Travel Planning**: Jakarta-Bandung scenario
4. **Vision Analysis**: Landmark recognition
5. **Chat AI**: Interactive Q&A

### Key Selling Points
- ✅ **Free & Open Source**: No licensing costs
- ✅ **Multimodal**: Text, voice, image input
- ✅ **Robust**: 3-tier AI fallback system
- ✅ **Indonesian**: Native language support
- ✅ **Scalable**: Docker-based deployment
- ✅ **Modern**: Latest tech stack

## 🐛 Troubleshooting

### Common Issues

**Docker not starting:**
```bash
# Check Docker status
docker info

# Restart Docker service
sudo systemctl restart docker
```

**Frontend build errors:**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install
```

**Backend API errors:**
```bash
# Check logs
docker compose logs api

# Restart API service
docker compose restart api
```

**AI services not responding:**
- Check API keys in `.env`
- Verify network connectivity
- Check service quotas/limits

## 📞 Support

### Demo Support
- **Email**: demo@travelguide.id
- **GitHub**: [Repository Issues](https://github.com/your-repo/issues)

### Documentation
- **API Docs**: http://localhost:8000/docs
- **Frontend Storybook**: http://localhost:6006 (if enabled)

---

**Built with ❤️ for IBM Jakarta Demo**
