# 🌍 AI Multimodal Travel Guide

> **Production-ready AI Travel Guide untuk IBM Jakarta Demo**

Aplikasi panduan wisata AI multimodal yang mendukung input teks, suara, dan gambar untuk merencanakan perjalanan di Indonesia. Dibangun dengan teknologi terdepan dan dirancang untuk demo IBM Jakarta.

## ✨ Highlights

🎯 **Demo Ready** - One-click deployment dengan Docker
🤖 **AI Fallback Chain** - IBM watsonx → Hugging Face → Replicate
🎤 **Multimodal Input** - Teks, suara, dan gambar
🇮🇩 **Bahasa Indonesia** - Native language support
📱 **Responsive** - Mobile-first design
⚡ **Fast & Reliable** - 24/7 availability dengan minimal errors

## 🚀 Quick Start

### One-Command Deployment

```bash
git clone <repository-url>
cd ai-guide-travel
cp .env.example .env
# Edit .env dengan API keys Anda
./start.sh
```

### Access Application

- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

## 🎭 Demo Scenarios

### 1. Travel Planning Demo

```bash
curl -X POST "http://localhost:8000/api/demo-plan"
```

### 2. Vision Analysis Demo

```bash
curl -X POST "http://localhost:8000/api/vision/demo"
```

### 3. Chat AI Demo

```bash
curl -X POST "http://localhost:8000/api/chat/demo"
```

## 🏗️ Architecture

### Frontend Stack

- **React 18** + **Vite** + **TypeScript**
- **Tailwind CSS** + **ShadCN/UI** + **Radix UI**
- **Framer Motion** + **React Spring**
- **MapLibre GL JS** untuk peta interaktif

### Backend Stack

- **FastAPI** + **Python 3.11**
- **SQLAlchemy** + **SQLite/PostgreSQL**
- **JWT Authentication**
- **Docker Compose**

### AI Services

1. **Primary**: IBM watsonx (`granite-3.3-8b-instruct`)
2. **Secondary**: Hugging Face Inference API
3. **Tertiary**: Replicate (optional)
4. **Baseline**: Hardcoded fallback responses

## � Configuration

### Required Environment Variables

```env
# AI Services (Required)
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
HF_API_KEY=your_huggingface_api_key

# Optional AI Services
REPLICATE_API_TOKEN=your_replicate_token
USE_REPLICATE=false

# Database (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///./travel_guide.db
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_key

# Demo Credentials
DEMO_EMAIL=demo@travelguide.id
DEMO_PASSWORD=demo123456
```

## 📱 Features

### 🎤 Multimodal Input

- **Text Input**: Form-based travel planning
- **Voice Input**: Web Speech API (browser native)
- **Image Upload**: Landmark recognition dengan AI vision

### 🤖 AI Capabilities

- **Travel Planning**: 1-7 day itineraries dengan cost estimates
- **Landmark Recognition**: Upload foto untuk identifikasi tempat wisata
- **Chat AI**: Q&A seputar wisata Indonesia
- **Fallback System**: Robust 3-tier AI fallback untuk 24/7 availability

### 🎨 Modern UI/UX

- **Responsive Design**: Mobile-first approach
- **Smooth Animations**: Framer Motion transitions
- **Glass Morphism**: Modern visual effects
- **Interactive Maps**: MapLibre + OpenStreetMap

## 🎯 API Endpoints

### Travel Planning

```http
POST /api/plan
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
{
  "message": "Rekomendasi tempat wisata di Bali"
}
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

### Docker Development

```bash
docker compose up -d
docker compose logs -f
```

## 🧪 Testing

### Health Check

```bash
curl http://localhost:8000/health
```

### Demo Endpoints

```bash
# Travel planning demo
curl http://localhost:8000/api/demo-plan

# Vision analysis demo
curl http://localhost:8000/api/vision/demo

# Chat demo
curl http://localhost:8000/api/chat/demo
```

## 📊 Monitoring

```bash
# View all logs
docker compose logs -f

# View specific service logs
docker compose logs -f api
docker compose logs -f web

# Check container status
docker compose ps
```

## 🔒 Security Features

- JWT authentication dengan token expiry
- Input validation dan sanitization
- File upload size limits (5MB)
- CORS protection
- SQL injection protection

## 🌍 Production Deployment

```bash
# Production build
docker compose -f docker-compose.prod.yml up -d

# Environment setup
export DATABASE_URL=postgresql://user:pass@host:5432/db
export CORS_ORIGINS=https://yourdomain.com
```

## 🎯 IBM Demo Highlights

### Key Selling Points

✅ **Free & Open Source** - No licensing costs
✅ **Production Ready** - Docker deployment
✅ **Multimodal AI** - Text, voice, image input
✅ **Robust Fallback** - 24/7 availability
✅ **Indonesian Native** - Local language support
✅ **Modern Tech Stack** - Latest technologies

### Demo Flow

1. **Landing Page** - Feature showcase
2. **Demo Mode** - One-click demonstration
3. **Travel Planning** - Jakarta-Bandung scenario
4. **Vision Analysis** - Landmark recognition
5. **Chat AI** - Interactive Q&A

## 📞 Support

- **Documentation**: [DOCUMENTATION.md](./DOCUMENTATION.md)
- **Demo Support**: demo@travelguide.id
- **GitHub Issues**: [Repository Issues](https://github.com/your-repo/issues)


**🚀 Built with ❤️ for IBM Jakarta Demo**
_Showcasing the power of AI-driven travel planning with Indonesian focus_
