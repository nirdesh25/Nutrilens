"""
AI Prediction model for storing demand forecasts
"""
from datetime import datetime
from decimal import Decimal
from extensions import db

class AIPrediction(db.Model):
    """AI prediction model for demand forecasting"""
    
    __tablename__ = 'ai_predictions'
    
    # Prediction period constants
    PERIOD_WEEKLY = 'weekly'
    PERIOD_MONTHLY = 'monthly'
    PERIOD_QUARTERLY = 'quarterly'
    VALID_PERIODS = [PERIOD_WEEKLY, PERIOD_MONTHLY, PERIOD_QUARTERLY]
    
    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    predicted_demand = db.Column(db.Integer, nullable=False)
    confidence_score = db.Column(db.Numeric(3, 2), nullable=False)  # 0.00 to 1.00
    prediction_period = db.Column(db.String(20), nullable=False)
    prediction_date = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    actual_demand = db.Column(db.Integer)  # Filled in after the period ends
    accuracy_score = db.Column(db.Numeric(3, 2))  # Calculated after actual demand is known
    
    # Additional prediction metadata
    model_version = db.Column(db.String(50))
    features_used = db.Column(db.Text)  # JSON string of features used in prediction
    seasonal_factor = db.Column(db.Numeric(5, 2))
    trend_factor = db.Column(db.Numeric(5, 2))
    
    # Relationships defined in Product model via backref
    
    def __init__(self, product_id, predicted_demand, confidence_score, prediction_period, 
                 model_version=None, features_used=None, seasonal_factor=None, trend_factor=None):
        """Initialize AI prediction with validation"""
        self.product_id = product_id
        self.predicted_demand = self.validate_demand(predicted_demand)
        self.confidence_score = self.validate_confidence_score(confidence_score)
        self.prediction_period = self.validate_period(prediction_period)
        self.model_version = model_version
        self.features_used = features_used
        self.seasonal_factor = seasonal_factor
        self.trend_factor = trend_factor
    
    @staticmethod
    def validate_demand(demand):
        """Validate predicted demand"""
        try:
            demand = int(demand)
        except (ValueError, TypeError):
            raise ValueError("Predicted demand must be a valid integer")
        
        if demand < 0:
            raise ValueError("Predicted demand cannot be negative")
        
        if demand > 1000000:
            raise ValueError("Predicted demand is too large (maximum 1,000,000)")
        
        return demand
    
    @staticmethod
    def validate_confidence_score(score):
        """Validate confidence score"""
        try:
            score = Decimal(str(score))
        except (ValueError, TypeError):
            raise ValueError("Confidence score must be a valid number")
        
        if score < 0 or score > 1:
            raise ValueError("Confidence score must be between 0.00 and 1.00")
        
        return score
    
    @staticmethod
    def validate_period(period):
        """Validate prediction period"""
        if period not in AIPrediction.VALID_PERIODS:
            raise ValueError(f"Invalid period. Must be one of: {', '.join(AIPrediction.VALID_PERIODS)}")
        return period
    
    def update_actual_demand(self, actual_demand):
        """Update actual demand and calculate accuracy"""
        self.actual_demand = self.validate_demand(actual_demand)
        self.calculate_accuracy()
    
    def calculate_accuracy(self):
        """Calculate prediction accuracy score"""
        if self.actual_demand is None:
            return None
        
        if self.predicted_demand == 0 and self.actual_demand == 0:
            self.accuracy_score = Decimal('1.00')  # Perfect prediction
        elif self.predicted_demand == 0:
            self.accuracy_score = Decimal('0.00')  # Completely wrong
        else:
            # Calculate accuracy as 1 - (absolute error / predicted demand)
            error_rate = abs(self.actual_demand - self.predicted_demand) / self.predicted_demand
            accuracy = max(0, 1 - error_rate)
            self.accuracy_score = min(Decimal('1.00'), Decimal(str(accuracy)))
        
        return self.accuracy_score
    
    # Query methods
    @classmethod
    def get_latest_predictions(cls, product_id=None, period=None, limit=10):
        """Get latest predictions"""
        query = cls.query
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        if period:
            query = query.filter_by(prediction_period=period)
        
        return query.order_by(cls.prediction_date.desc()).limit(limit).all()
    
    @classmethod
    def get_predictions_for_product(cls, product_id):
        """Get all predictions for a specific product"""
        return cls.query.filter_by(product_id=product_id).order_by(cls.prediction_date.desc()).all()
    
    @classmethod
    def get_high_confidence_predictions(cls, min_confidence=0.8):
        """Get predictions with high confidence scores"""
        return cls.query.filter(cls.confidence_score >= min_confidence).order_by(cls.confidence_score.desc()).all()
    
    @classmethod
    def get_predictions_needing_validation(cls):
        """Get predictions that need actual demand validation"""
        return cls.query.filter(cls.actual_demand.is_(None)).order_by(cls.prediction_date.asc()).all()
    
    @classmethod
    def get_model_performance_stats(cls, model_version=None):
        """Get performance statistics for AI model"""
        from sqlalchemy import func
        
        query = db.session.query(
            func.count(cls.id).label('total_predictions'),
            func.avg(cls.confidence_score).label('avg_confidence'),
            func.avg(cls.accuracy_score).label('avg_accuracy'),
            func.count(cls.accuracy_score).label('validated_predictions')
        )
        
        if model_version:
            query = query.filter_by(model_version=model_version)
        
        # Only include predictions with accuracy scores
        query = query.filter(cls.accuracy_score.isnot(None))
        
        result = query.first()
        
        return {
            'total_predictions': result.total_predictions or 0,
            'validated_predictions': result.validated_predictions or 0,
            'average_confidence': float(result.avg_confidence or 0),
            'average_accuracy': float(result.avg_accuracy or 0)
        }
    
    # Prediction quality methods
    def is_high_confidence(self, threshold=0.8):
        """Check if prediction has high confidence"""
        return self.confidence_score >= threshold
    
    def is_accurate(self, threshold=0.8):
        """Check if prediction was accurate (requires actual demand)"""
        if self.accuracy_score is None:
            return None
        return self.accuracy_score >= threshold
    
    @property
    def error_percentage(self):
        """Calculate error percentage"""
        if self.actual_demand is None or self.predicted_demand == 0:
            return None
        
        error = abs(self.actual_demand - self.predicted_demand)
        return (error / self.predicted_demand) * 100
    
    @property
    def is_overestimate(self):
        """Check if prediction was an overestimate"""
        if self.actual_demand is None:
            return None
        return self.predicted_demand > self.actual_demand
    
    @property
    def is_underestimate(self):
        """Check if prediction was an underestimate"""
        if self.actual_demand is None:
            return None
        return self.predicted_demand < self.actual_demand
    
    # Restock suggestion methods
    def get_restock_suggestion(self, current_stock=0, safety_factor=1.2):
        """Generate restock suggestion based on prediction"""
        if not self.is_high_confidence():
            return None
        
        # Calculate suggested restock quantity
        predicted_need = max(0, self.predicted_demand - current_stock)
        suggested_quantity = int(predicted_need * float(safety_factor))
        
        return {
            'product_id': self.product_id,
            'current_stock': current_stock,
            'predicted_demand': self.predicted_demand,
            'suggested_restock': suggested_quantity,
            'confidence': float(self.confidence_score),
            'period': self.prediction_period,
            'safety_factor': safety_factor,
            'reasoning': f"Predicted demand: {self.predicted_demand}, Current stock: {current_stock}, Safety factor: {safety_factor}"
        }
    
    # String representation
    def __repr__(self):
        return f'<AIPrediction {self.id}: {self.predicted_demand} units for {self.product.name if self.product else "Unknown"} ({self.confidence_score:.2f} confidence)>'
    
    def to_dict(self):
        """Convert prediction to dictionary"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else None,
            'predicted_demand': self.predicted_demand,
            'confidence_score': float(self.confidence_score),
            'prediction_period': self.prediction_period,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'actual_demand': self.actual_demand,
            'accuracy_score': float(self.accuracy_score) if self.accuracy_score else None,
            'error_percentage': self.error_percentage,
            'is_high_confidence': self.is_high_confidence(),
            'is_accurate': self.is_accurate(),
            'model_version': self.model_version,
            'seasonal_factor': float(self.seasonal_factor) if self.seasonal_factor else None,
            'trend_factor': float(self.trend_factor) if self.trend_factor else None
        }