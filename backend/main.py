from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, scan, grocery, health, waste, sensor, ph, user, nutrition

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="NutriLens AI API",
    description="AI-powered food intelligence platform",
    version="1.0.0"
)

# CORS middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(scan.router)
app.include_router(grocery.router)
app.include_router(health.router)
app.include_router(waste.router)
app.include_router(sensor.router)
app.include_router(ph.router)
app.include_router(user.router)
app.include_router(nutrition.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to NutriLens AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
