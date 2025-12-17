# Django AI Supabase App

🚀 Production-ready Django application with Supabase, R2, and Upstash support.

## Features
- ✅ Django 4.2 with REST API (DRF)
- ✅ JWT Authentication
- ✅ PostgreSQL (Supabase/Render)
- ✅ Cloudflare R2 for storage (optional)
- ✅ Upstash Redis for caching (optional)
- ✅ Health monitoring endpoints
- ✅ Docker containerization
- ✅ CORS enabled for frontend

## Project Structure

django-ai-supabase-app/
├── accounts/ # User authentication & JWT
├── products/ # Product management
├── sales/ # Sales tracking
├── notifications/ # Notification system
├── config/ # Django settings
├── Dockerfile # Docker configuration
├── render.yaml # Render.com deployment
├── requirements.txt # Python dependencies
└── README.md # This file
cat > README.md << 'EOF'
# Django AI Supabase App

🚀 Production-ready Django application with Supabase, R2, and Upstash support.

## Features
- ✅ Django 4.2 with REST API (DRF)
- ✅ JWT Authentication
- ✅ PostgreSQL (Supabase/Render)
- ✅ Cloudflare R2 for storage (optional)
- ✅ Upstash Redis for caching (optional)
- ✅ Health monitoring endpoints
- ✅ Docker containerization
- ✅ CORS enabled for frontend

## Project Structure

django-ai-supabase-app/
├── accounts/ # User authentication & JWT
├── products/ # Product management
├── sales/ # Sales tracking
├── notifications/ # Notification system
├── config/ # Django settings
├── Dockerfile # Docker configuration
├── render.yaml # Render.com deployment
├── requirements.txt # Python dependencies
└── README.md # This file

docker build -t django-app .
docker run -p 10000:10000 django-app
Deployment
Render.com (Recommended)
Fork this repository

Go to Render Dashboard

Click "New Web Service"

Connect your GitHub repository

Render will use render.yaml automatically
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com,localhost
PORT=10000
DATABASE_URL=postgresql://...
API Endpoints
GET /health/ - Health check

POST /api/auth/login/ - JWT login

GET /admin/ - Django admin

License
MIT License
