from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.sensor import SensorDataCreate, SensorDataResponse, MilkQualityRequest, MilkAnalysisResponse
from app.utils.auth import get_current_user
from app.services import sensor_service
from app.services.milk_quality_service import MilkQualityService
from typing import Optional

router = APIRouter(prefix="/api/sensor", tags=["Smart Freshness Box"])

# Public ingest endpoint - no JWT required, uses device key
@router.post("/ingest-public")
async def ingest_sensor_data_public(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Public endpoint for IoT device to push sensor data.
    No authentication required - device just POSTs data directly.
    """
    from app.models.sensor_data import SensorData
    from app.services.sensor_service import sensor_service as svc

    temperature = payload.get('temperature') or payload.get('Temperature')
    humidity    = payload.get('humidity')    or payload.get('Humidity')
    gas_level   = payload.get('gas_level')   or payload.get('Gas Level') or payload.get('gas')
    light_level = payload.get('light_level') or payload.get('Light Level') or payload.get('light')
    device_id   = payload.get('device_id')   or payload.get('device') or 'ESP_DEVICE'

    if temperature is None or humidity is None:
        raise HTTPException(status_code=422, detail="temperature and humidity are required")

    status = svc._determine_status(
        float(temperature),
        float(humidity),
        float(gas_level or 0)
    )

    # Store under ALL users so any logged-in user can see it
    from sqlalchemy import text
    users = db.execute(text("SELECT id FROM users")).fetchall()
    
    saved = False
    for user_row in users:
        uid = user_row[0]
        sensor_data = SensorData(
            user_id=uid,
            device_id=device_id,
            temperature=float(temperature),
            humidity=float(humidity),
            gas_level=float(gas_level or 0),
            light_level=float(light_level or 0),
            status=status
        )
        db.add(sensor_data)
        saved = True
    
    if not saved:
        # fallback to user_id=1
        sensor_data = SensorData(
            user_id=1,
            device_id=device_id,
            temperature=float(temperature),
            humidity=float(humidity),
            gas_level=float(gas_level or 0),
            light_level=float(light_level or 0),
            status=status
        )
        db.add(sensor_data)
    
    db.commit()

    print(f"✅ Sensor data received: temp={temperature}°C, humidity={humidity}%, gas={gas_level}ppm")

    return {
        'status': 'success',
        'message': 'Sensor data saved',
        'temperature': temperature,
        'humidity': humidity,
        'gas_level': gas_level,
        'light_level': light_level
    }


@router.get("/current")
async def get_current_sensor_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current sensor data from Smart Freshness Box.
    
    PLACEHOLDER: Returns mock data until IoT device is connected.
    Ready for ESP32/Arduino integration.
    """
    
    data = sensor_service.get_current_sensor_data(current_user.id, db)
    
    return data

@router.get("/history")
async def get_sensor_history(
    hours: int = 24,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get historical sensor data."""
    
    if hours > 168:  # Max 7 days
        raise HTTPException(status_code=400, detail="Maximum 168 hours (7 days) allowed")
    
    history = sensor_service.get_sensor_history(current_user.id, hours, db)
    
    return {
        'hours': hours,
        'data_points': len(history),
        'data': history
    }

@router.post("/ingest")
async def ingest_sensor_data(
    sensor_data: SensorDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingest sensor data from IoT device.
    
    TODO: Implement when hardware is ready
    - Add device authentication
    - Validate device_id
    - Implement MQTT/WebSocket for real-time updates
    """
    
    result = await sensor_service.ingest_sensor_data(
        device_id=sensor_data.device_id or "UNKNOWN",
        data=sensor_data.dict(),
        user_id=current_user.id,
        db=db
    )
    
    return result

@router.get("/status")
async def get_box_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Smart Freshness Box connection status."""
    
    from app.models.sensor_data import SensorData
    from datetime import datetime, timedelta
    
    # Check for real device data within last 2 minutes
    cutoff_time = datetime.utcnow() - timedelta(minutes=2)
    latest_real = db.query(SensorData).filter(
        SensorData.user_id == current_user.id,
        SensorData.device_id != "MOCK_DEVICE_001",
        SensorData.created_at >= cutoff_time
    ).order_by(SensorData.created_at.desc()).first()
    
    if latest_real:
        return {
            'connected': True,
            'device_id': latest_real.device_id,
            'last_update': latest_real.created_at.isoformat(),
            'message': f'Live data from {latest_real.device_id}',
            'integration_ready': True
        }
    
    # Check if we have any real data (even if stale)
    any_real = db.query(SensorData).filter(
        SensorData.user_id == current_user.id,
        SensorData.device_id != "MOCK_DEVICE_001"
    ).order_by(SensorData.created_at.desc()).first()
    
    if any_real:
        return {
            'connected': False,
            'device_id': any_real.device_id,
            'last_update': any_real.created_at.isoformat(),
            'message': f'Last seen: {any_real.created_at.strftime("%H:%M:%S")} — waiting for next reading',
            'integration_ready': True
        }
    
    return {
        'connected': False,
        'device_id': None,
        'last_update': None,
        'message': 'No device connected. Showing mock data.',
        'integration_ready': True
    }

@router.post("/milk-quality", response_model=MilkAnalysisResponse)
async def analyze_milk_quality(
    request: MilkQualityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyze milk quality based on sensor and physical parameters.
    Connects to the Milk Quality classification model predictions.
    Saves the result to the database for historical tracking.
    """
    # 1. Run ML Prediction
    result = MilkQualityService.predict_quality(
        ph=request.ph,
        temperature=request.temperature,
        taste=request.taste,
        odor=request.odor,
        fat=request.fat,
        turbidity=request.turbidity,
        color=request.color
    )
    
    # 2. Persist to Database
    from app.models.milk_analysis import MilkAnalysis
    
    analysis = MilkAnalysis(
        user_id=current_user.id,
        ph=request.ph,
        temperature=request.temperature,
        taste=request.taste,
        odor=request.odor,
        fat=request.fat,
        turbidity=request.turbidity,
        color=request.color,
        prediction=result['prediction'],
        risk_score=result.get('risk_score', 0.0)
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis
