import random
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import SensorData

class SensorService:
    """
    Smart Freshness Box sensor data service.
    
    PLACEHOLDER FOR IOT INTEGRATION
    Currently returns mock data. Ready for ESP32/Arduino integration.
    
    Integration points:
    - MQTT broker connection
    - WebSocket for real-time updates
    - REST API for sensor data ingestion
    """
    
    def get_current_sensor_data(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get the most recent sensor reading - real or mock."""
        
        # Always return the latest record regardless of device type
        latest_record = db.query(SensorData).filter(
            SensorData.user_id == user_id
        ).order_by(SensorData.created_at.desc()).first()
        
        if latest_record:
            return {
                'device_id': latest_record.device_id,
                'temperature': latest_record.temperature,
                'humidity': latest_record.humidity,
                'gas_level': latest_record.gas_level,
                'light_level': latest_record.light_level,
                'status': latest_record.status,
                'timestamp': latest_record.created_at.isoformat(),
                'alerts': self._generate_alerts(
                    latest_record.temperature,
                    latest_record.humidity,
                    latest_record.gas_level
                ),
                'is_real_device': latest_record.device_id != "MOCK_DEVICE_001"
            }
        
        # No data at all - generate mock
        temperature = round(random.uniform(2.0, 8.0), 1)
        humidity    = round(random.uniform(40.0, 80.0), 1)
        gas_level   = round(random.uniform(0, 500), 1)
        light_level = round(random.uniform(0, 100), 1)
        status      = self._determine_status(temperature, humidity, gas_level)
        
        sensor_data = SensorData(
            user_id=user_id,
            device_id="MOCK_DEVICE_001",
            temperature=temperature,
            humidity=humidity,
            gas_level=gas_level,
            light_level=light_level,
            status=status
        )
        db.add(sensor_data)
        db.commit()
        db.refresh(sensor_data)
        
        return {
            'device_id': sensor_data.device_id,
            'temperature': temperature,
            'humidity': humidity,
            'gas_level': gas_level,
            'light_level': light_level,
            'status': status,
            'timestamp': sensor_data.created_at.isoformat(),
            'alerts': self._generate_alerts(temperature, humidity, gas_level),
            'is_real_device': False
        }
    
    def get_sensor_history(self, user_id: int, hours: int, db: Session) -> List[Dict[str, Any]]:
        """Get historical sensor data."""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        sensor_records = db.query(SensorData).filter(
            SensorData.user_id == user_id,
            SensorData.created_at >= cutoff_time
        ).order_by(SensorData.created_at.desc()).all()
        
        return [
            {
                'temperature': record.temperature,
                'humidity': record.humidity,
                'gas_level': record.gas_level,
                'status': record.status,
                'timestamp': record.created_at.isoformat()
            }
            for record in sensor_records
        ]
    
    def _determine_status(self, temperature: float, humidity: float, gas_level: float) -> str:
        """Determine overall status based on sensor readings."""
        
        # Ideal refrigerator conditions
        temp_ok = 2.0 <= temperature <= 8.0
        humidity_ok = 40.0 <= humidity <= 70.0
        gas_ok = gas_level < 300
        
        if temp_ok and humidity_ok and gas_ok:
            return 'normal'
        elif not temp_ok or not humidity_ok or (gas_level >= 300 and gas_level < 400):
            return 'warning'
        else:
            return 'critical'
    
    def _generate_alerts(self, temperature: float, humidity: float, gas_level: float) -> List[str]:
        """Generate alerts based on sensor readings."""
        
        alerts = []
        
        if temperature > 8.0:
            alerts.append(f'Temperature too high ({temperature}°C). Food may spoil faster.')
        elif temperature < 2.0:
            alerts.append(f'Temperature too low ({temperature}°C). Some foods may freeze.')
        
        if humidity > 70.0:
            alerts.append(f'High humidity ({humidity}%). Risk of mold growth.')
        elif humidity < 40.0:
            alerts.append(f'Low humidity ({humidity}%). Food may dry out.')
        
        if gas_level > 400:
            alerts.append(f'High gas levels detected ({gas_level} PPM). Food may be spoiling.')
        elif gas_level > 300:
            alerts.append(f'Elevated gas levels ({gas_level} PPM). Check for spoiled food.')
        
        if not alerts:
            alerts.append('All sensors within normal range.')
        
        return alerts
    
    async def ingest_sensor_data(self, device_id: str, data: Dict[str, Any], user_id: int, db: Session):
        """
        Ingest sensor data from IoT device.
        
        TODO: Implement when hardware is ready
        - Validate device_id
        - Authenticate device
        - Parse sensor payload
        - Store in database
        - Trigger real-time updates via WebSocket
        """
        
        sensor_data = SensorData(
            user_id=user_id,
            device_id=device_id,
            temperature=data.get('temperature'),
            humidity=data.get('humidity'),
            gas_level=data.get('gas_level'),
            light_level=data.get('light_level'),
            status=self._determine_status(
                data.get('temperature', 5.0),
                data.get('humidity', 50.0),
                data.get('gas_level', 100.0)
            )
        )
        
        db.add(sensor_data)
        db.commit()
        
        return {'status': 'success', 'message': 'Sensor data ingested'}

sensor_service = SensorService()
