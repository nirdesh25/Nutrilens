# NutriLens AI - Quick Start Guide

Get NutriLens AI running in 10 minutes!

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL database (local or cloud)
- Git

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd nutrilens-ai
```

## Step 2: Backend Setup (3 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### Edit `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/nutrilens
SECRET_KEY=your-secret-key-change-this
```

### Generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Start backend:
```bash
python main.py
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

## Step 3: Frontend Setup (3 minutes)

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
```

### Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Start frontend:
```bash
npm run dev
```

Frontend runs at: `http://localhost:3000`

## Step 4: Test the Application (2 minutes)

1. **Open browser**: Go to `http://localhost:3000`

2. **Register account**:
   - Click "Get Started"
   - Fill in name, email, password
   - Click "Create Account"

3. **Explore dashboard**:
   - View all modules
   - Click "Smart Freshness Box" to see IoT-ready interface
   - Try "Food Scanner" (mock predictions)

4. **Test API**:
   ```bash
   curl http://localhost:8000/health
   ```

## 🎉 You're Done!

The application is now running with mock data. You can:

- ✅ Register and login users
- ✅ Scan food (mock AI predictions)
- ✅ Manage groceries
- ✅ Set health profiles
- ✅ Track waste
- ✅ View Smart Freshness Box (mock sensors)

## Next Steps

### Add Real AI Models

1. **Download datasets**:
   ```bash
   cd datasets
   pip install kaggle
   # Configure ~/.kaggle/kaggle.json
   python download_datasets.py
   ```

2. **Train models**:
   ```bash
   cd ml_models
   python train_freshness_model.py
   ```

3. **Update backend** to use trained models

### Connect IoT Hardware

1. Build Smart Freshness Box with ESP32
2. Connect sensors (DHT22, MQ-135, LDR)
3. Configure MQTT or use REST API
4. Update `device_id` in sensor service
5. Sensor data automatically appears in dashboard!

### Deploy to Production

See `DEPLOYMENT.md` for complete deployment guide:
- Frontend → Vercel (free)
- Backend → Render/Railway ($7-25/month)
- Database → Supabase/Neon (free tier available)

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.10+)
- Check PostgreSQL is running
- Verify DATABASE_URL in `.env`

### Frontend won't start
- Check Node version: `node --version` (need 18+)
- Delete `node_modules` and run `npm install` again
- Check NEXT_PUBLIC_API_URL in `.env.local`

### Database errors
- Create database: `createdb nutrilens`
- Check connection string format
- Tables are created automatically on first run

### CORS errors
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL matches backend URL
- Backend CORS is configured for localhost:3000

## Project Structure

```
nutrilens-ai/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── models/    # Database models
│   │   ├── routes/    # API endpoints
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── services/  # Business logic
│   │   └── utils/     # Utilities
│   └── main.py        # Entry point
├── frontend/          # Next.js application
│   └── src/
│       ├── app/       # Pages
│       └── lib/       # API client
├── datasets/          # Dataset download scripts
├── ml_models/         # Model training scripts
└── docs/              # Documentation
```

## Key Features

1. **Food Scanner** - AI freshness detection
2. **Grocery Manager** - Track your food
3. **Health Profile** - Personalized recommendations
4. **Waste Tracker** - Reduce food waste
5. **pH Analysis** - Spoilage detection
6. **Smart Box** - IoT sensor monitoring (ready for hardware)
7. **Analytics** - Impact dashboard

## Support

- 📖 Read `PROJECT_SUMMARY.md` for complete overview
- 🚀 Read `DEPLOYMENT.md` for production deployment
- 📊 Read `datasets/README.md` for AI model training
- 🔧 Check `/docs` endpoint for API documentation

## Development Tips

### Backend Development
```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Check API docs
open http://localhost:8000/docs
```

### Frontend Development
```bash
# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm start
```

### Database Management
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Common Commands

```bash
# Backend
cd backend
source venv/bin/activate  # Activate venv
python main.py            # Start server
pip install <package>     # Add dependency

# Frontend
cd frontend
npm run dev              # Start dev server
npm run build            # Build for production
npm install <package>    # Add dependency

# Datasets
cd datasets
python download_datasets.py  # Download all datasets

# ML Models
cd ml_models
python train_freshness_model.py  # Train model
```

## Environment Variables Reference

### Backend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql://user:pass@localhost:5432/db |
| SECRET_KEY | JWT secret | random-32-char-hex-string |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry | 30 |
| ENVIRONMENT | Environment | development/production |

### Frontend (.env.local)
| Variable | Description | Example |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend URL | http://localhost:8000 |

## Ready to Deploy?

When you're ready for production:

1. Push code to GitHub
2. Deploy frontend to Vercel (1 click)
3. Deploy backend to Render (1 click)
4. Set up PostgreSQL database
5. Configure environment variables
6. Done! 🎉

See `DEPLOYMENT.md` for detailed instructions.

---

**Need Help?** Check the documentation or create an issue on GitHub.

**Happy Coding!** 🚀
