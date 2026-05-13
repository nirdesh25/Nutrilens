# NutriLens AI - Deployment Guide

Complete guide for deploying NutriLens AI to production.

## Architecture Overview

```
Frontend (Next.js) → Vercel
Backend (FastAPI) → Render/Railway
Database (PostgreSQL) → Supabase/Neon
ML Models → Backend server
IoT Device → MQTT/WebSocket → Backend
```

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- PostgreSQL database
- Kaggle account (for datasets)
- Git

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd nutrilens-ai
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database URL and secret key

# Create database tables
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run server
python main.py
```

Backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
cp .env.example .env.local

# Run development server
npm run dev
```

Frontend will run on `http://localhost:3000`

### 4. Download and Train Models (Optional)

```bash
cd datasets

# Install Kaggle CLI
pip install kaggle

# Configure Kaggle API (place kaggle.json in ~/.kaggle/)

# Download datasets
python download_datasets.py

# Train models
cd ../ml_models
python train_freshness_model.py
```

## Production Deployment

### Frontend Deployment (Vercel)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Deploy to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Set root directory to `frontend`
   - Add environment variable:
     - `NEXT_PUBLIC_API_URL`: Your backend URL
   - Deploy

3. **Custom Domain (Optional)**
   - Add custom domain in Vercel dashboard
   - Update DNS records

### Backend Deployment (Render)

1. **Create Render Account**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Create PostgreSQL Database**
   - New → PostgreSQL
   - Choose free tier or paid
   - Copy database URL

3. **Create Web Service**
   - New → Web Service
   - Connect GitHub repository
   - Settings:
     - Name: `nutrilens-ai-backend`
     - Root Directory: `backend`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment Variables:
     - `DATABASE_URL`: Your PostgreSQL URL
     - `SECRET_KEY`: Generate with `openssl rand -hex 32`
     - `ENVIRONMENT`: `production`
   - Deploy

4. **Upload ML Models**
   - Use Render disk or cloud storage (S3, GCS)
   - Update model paths in environment variables

### Alternative: Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy backend
cd backend
railway init
railway up

# Add PostgreSQL
railway add postgresql

# Set environment variables
railway variables set SECRET_KEY=<your-secret-key>
```

### Database Setup (Supabase)

1. **Create Supabase Project**
   - Go to [supabase.com](https://supabase.com)
   - Create new project
   - Copy connection string

2. **Update Backend .env**
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

3. **Run Migrations**
   ```bash
   # Tables will be created automatically on first run
   # Or use Alembic for migrations
   ```

## Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production

FRESHNESS_MODEL_PATH=./ml_models/freshness_model.h5
FOOD_RECOGNITION_MODEL_PATH=./ml_models/food_recognition_model.h5
WASTE_MODEL_PATH=./ml_models/waste_model.h5
```

## Post-Deployment

### 1. Test API
```bash
curl https://your-backend-url.com/health
```

### 2. Test Frontend
Visit your Vercel URL and test:
- User registration
- Login
- Food scanning (with mock data)
- All features

### 3. Monitor
- Vercel Analytics
- Render Logs
- Database metrics

## IoT Integration (Future)

When Smart Freshness Box hardware is ready:

1. **Setup MQTT Broker**
   - Use CloudMQTT or AWS IoT Core
   - Configure topics: `nutrilens/sensor/{device_id}`

2. **Update Backend**
   - Add MQTT client in `app/services/sensor_service.py`
   - Subscribe to sensor topics
   - Parse and store data

3. **ESP32/Arduino Code**
   - Connect sensors (DHT22, MQ-135, etc.)
   - Publish to MQTT broker
   - Use JSON format

4. **WebSocket for Real-time**
   - Add WebSocket endpoint in FastAPI
   - Push sensor updates to frontend
   - Update dashboard in real-time

## Scaling Considerations

### Performance
- Use Redis for caching
- CDN for static assets
- Load balancer for multiple backend instances

### ML Models
- Use TensorFlow Serving
- GPU instances for inference
- Model versioning

### Database
- Connection pooling
- Read replicas
- Regular backups

## Security Checklist

- [ ] HTTPS enabled
- [ ] Environment variables secured
- [ ] Database credentials rotated
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection

## Monitoring & Logging

- Sentry for error tracking
- LogRocket for session replay
- Prometheus + Grafana for metrics
- Database query monitoring

## Backup Strategy

- Daily database backups
- Model versioning in cloud storage
- Code in Git
- Environment variables documented

## Cost Estimation

### Free Tier
- Vercel: Free for hobby projects
- Render: Free tier available
- Supabase: 500MB database free
- Total: $0/month

### Production
- Vercel Pro: $20/month
- Render Standard: $25/month
- Supabase Pro: $25/month
- Total: ~$70/month

## Support

For issues or questions:
- GitHub Issues
- Documentation
- Community Discord
