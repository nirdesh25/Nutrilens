"""
AI Prediction Service for Smart Inventory Management System
Provides demand prediction, model training, and restocking suggestions
"""

import os
import pickle
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from extensions import db
from models.sale import Sale
from models.product import Product
from models.ai_prediction import AIPrediction


class AIPredictionService:
    """Service for AI-powered demand prediction and restocking suggestions"""
    
    MODEL_DIR = 'ai_models'
    MODEL_FILE = 'demand_prediction_model.pkl'
    SCALER_FILE = 'feature_scaler.pkl'
    MODEL_VERSION = '1.0'
    
    def __init__(self):
        """Initialize AI prediction service"""
        self.model = None
        self.scaler = None
        self.feature_columns = [
            'avg_daily_sales_7d',
            'avg_daily_sales_30d',
            'trend_7d',
            'trend_30d',
            'seasonal_factor',
            'days_since_last_sale',
            'current_stock',
            'price_ratio',
            'category_performance'
        ]
        self._ensure_model_directory()
    
    def _ensure_model_directory(self):
        """Ensure model directory exists"""
        if not os.path.exists(self.MODEL_DIR):
            os.makedirs(self.MODEL_DIR)
    
    def train_model(self, retrain: bool = False) -> Dict:
        """
        Train the demand prediction model using historical sales data
        
        Args:
            retrain: Whether to retrain even if model exists
            
        Returns:
            Dictionary with training results and metrics
        """
        model_path = os.path.join(self.MODEL_DIR, self.MODEL_FILE)
        scaler_path = os.path.join(self.MODEL_DIR, self.SCALER_FILE)
        
        # Check if model exists and retrain is not forced
        if not retrain and os.path.exists(model_path) and os.path.exists(scaler_path):
            self.load_model()
            return {
                'status': 'loaded_existing',
                'message': 'Existing model loaded successfully',
                'model_version': self.MODEL_VERSION
            }
        
        try:
            # Prepare training data
            training_data = self._prepare_training_data()
            
            if training_data.empty:
                return {
                    'status': 'error',
                    'message': 'Insufficient data for training. Need at least 30 days of sales history.',
                    'data_points': 0
                }
            
            # Split features and target
            X = training_data[self.feature_columns]
            y = training_data['actual_demand']
            
            # Split into train and test sets
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            
            metrics = {
                'mae': mean_absolute_error(y_test, y_pred),
                'mse': mean_squared_error(y_test, y_pred),
                'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                'r2': r2_score(y_test, y_pred),
                'training_samples': len(X_train),
                'test_samples': len(X_test)
            }
            
            # Save model and scaler
            with open(model_path, 'wb') as f:
                pickle.dump(self.model, f)
            
            with open(scaler_path, 'wb') as f:
                pickle.dump(self.scaler, f)
            
            # Save feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.model.feature_importances_
            ))
            
            return {
                'status': 'success',
                'message': 'Model trained successfully',
                'model_version': self.MODEL_VERSION,
                'metrics': metrics,
                'feature_importance': feature_importance,
                'data_points': len(training_data)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Training failed: {str(e)}',
                'model_version': self.MODEL_VERSION
            }
    
    def load_model(self) -> bool:
        """
        Load trained model and scaler from disk
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            model_path = os.path.join(self.MODEL_DIR, self.MODEL_FILE)
            scaler_path = os.path.join(self.MODEL_DIR, self.SCALER_FILE)
            
            if not os.path.exists(model_path) or not os.path.exists(scaler_path):
                return False
            
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)
            
            return True
            
        except Exception:
            return False
    
    def predict_demand(self, product_id: int, period: str = 'weekly') -> Optional[Dict]:
        """
        Predict demand for a specific product
        
        Args:
            product_id: ID of the product
            period: Prediction period ('weekly', 'monthly', 'quarterly')
            
        Returns:
            Dictionary with prediction results or None if failed
        """
        if not self.model or not self.scaler:
            if not self.load_model():
                # Try to train model if not available
                training_result = self.train_model()
                if training_result['status'] != 'success':
                    return None
        
        try:
            product = Product.query.get(product_id)
            if not product:
                return None
            
            # Prepare features for prediction
            features = self._prepare_prediction_features(product_id)
            if features is None:
                return None
            
            # Scale features
            feature_array = np.array([features[col] for col in self.feature_columns]).reshape(1, -1)
            scaled_features = self.scaler.transform(feature_array)
            
            # Make prediction
            predicted_demand = max(0, int(self.model.predict(scaled_features)[0]))
            
            # Calculate confidence score based on feature quality and model certainty
            confidence_score = self._calculate_confidence_score(features, predicted_demand)
            
            # Adjust prediction based on period
            period_multiplier = {
                'weekly': 1,
                'monthly': 4.33,  # Average weeks per month
                'quarterly': 13   # Average weeks per quarter
            }
            
            adjusted_demand = int(predicted_demand * period_multiplier.get(period, 1))
            
            # Calculate seasonal and trend factors
            seasonal_factor = features.get('seasonal_factor', 1.0)
            trend_factor = self._calculate_trend_factor(features)
            
            # Store prediction in database
            prediction = AIPrediction(
                product_id=product_id,
                predicted_demand=adjusted_demand,
                confidence_score=confidence_score,
                prediction_period=period,
                model_version=self.MODEL_VERSION,
                features_used=json.dumps(features),
                seasonal_factor=seasonal_factor,
                trend_factor=trend_factor
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            return {
                'product_id': product_id,
                'product_name': product.name,
                'predicted_demand': adjusted_demand,
                'confidence_score': float(confidence_score),
                'prediction_period': period,
                'seasonal_factor': seasonal_factor,
                'trend_factor': trend_factor,
                'current_stock': product.quantity,
                'prediction_id': prediction.id,
                'features_used': features
            }
            
        except Exception as e:
            print(f"Prediction error for product {product_id}: {str(e)}")
            return None
    
    def generate_restock_suggestions(self, min_confidence: float = 0.6) -> List[Dict]:
        """
        Generate restocking suggestions for all products
        
        Args:
            min_confidence: Minimum confidence threshold for suggestions
            
        Returns:
            List of restock suggestions
        """
        suggestions = []
        
        # Get all active products
        products = Product.query.filter(Product.quantity >= 0).all()
        
        for product in products:
            # Get latest prediction for this product
            latest_prediction = AIPrediction.query.filter_by(
                product_id=product.id
            ).order_by(AIPrediction.prediction_date.desc()).first()
            
            # Generate new prediction if none exists or is old
            if not latest_prediction or self._is_prediction_stale(latest_prediction):
                prediction_result = self.predict_demand(product.id, 'monthly')
                if not prediction_result:
                    continue
                latest_prediction = AIPrediction.query.get(prediction_result['prediction_id'])
            
            # Only suggest if confidence is high enough
            if latest_prediction.confidence_score < min_confidence:
                continue
            
            # Calculate restock suggestion
            suggestion = self._calculate_restock_suggestion(product, latest_prediction)
            if suggestion:
                suggestions.append(suggestion)
        
        # Sort by urgency (low stock first, then by predicted demand)
        suggestions.sort(key=lambda x: (x['urgency_score'], -x['suggested_quantity']))
        
        return suggestions
    
    def analyze_seasonal_trends(self, product_id: int) -> Dict:
        """
        Analyze seasonal trends for a specific product
        
        Args:
            product_id: ID of the product
            
        Returns:
            Dictionary with seasonal trend analysis
        """
        product = Product.query.get(product_id)
        if not product:
            return {}
        
        # Get sales data for the last year
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        sales = Sale.query.filter(
            Sale.product_id == product_id,
            Sale.sale_date >= start_date
        ).order_by(Sale.sale_date).all()
        
        if not sales:
            return {
                'product_id': product_id,
                'product_name': product.name,
                'seasonal_patterns': {},
                'trend_analysis': 'insufficient_data',
                'recommendations': []
            }
        
        # Group sales by month
        monthly_sales = {}
        for sale in sales:
            month_key = sale.sale_date.strftime('%Y-%m')
            if month_key not in monthly_sales:
                monthly_sales[month_key] = 0
            monthly_sales[month_key] += sale.quantity
        
        # Calculate seasonal factors
        seasonal_factors = self._calculate_seasonal_factors(monthly_sales)
        
        # Identify peak and low seasons
        peak_months = [month for month, factor in seasonal_factors.items() if factor > 1.2]
        low_months = [month for month, factor in seasonal_factors.items() if factor < 0.8]
        
        # Generate recommendations
        recommendations = self._generate_seasonal_recommendations(
            product, seasonal_factors, peak_months, low_months
        )
        
        return {
            'product_id': product_id,
            'product_name': product.name,
            'seasonal_factors': seasonal_factors,
            'peak_months': peak_months,
            'low_months': low_months,
            'trend_analysis': self._analyze_overall_trend(monthly_sales),
            'recommendations': recommendations,
            'data_period': f"{start_date.strftime('%Y-%m')} to {end_date.strftime('%Y-%m')}"
        }
    
    def get_model_performance_stats(self) -> Dict:
        """
        Get performance statistics for the AI model
        
        Returns:
            Dictionary with model performance metrics
        """
        # Get predictions with actual results
        validated_predictions = AIPrediction.query.filter(
            AIPrediction.actual_demand.isnot(None)
        ).all()
        
        if not validated_predictions:
            return {
                'status': 'no_validation_data',
                'message': 'No validated predictions available for performance analysis'
            }
        
        # Calculate performance metrics
        accuracies = [p.accuracy_score for p in validated_predictions if p.accuracy_score is not None]
        confidences = [p.confidence_score for p in validated_predictions]
        errors = [abs(p.predicted_demand - p.actual_demand) for p in validated_predictions]
        
        # Group by confidence levels
        high_confidence = [p for p in validated_predictions if p.confidence_score >= 0.8]
        medium_confidence = [p for p in validated_predictions if 0.6 <= p.confidence_score < 0.8]
        low_confidence = [p for p in validated_predictions if p.confidence_score < 0.6]
        
        return {
            'total_predictions': len(validated_predictions),
            'average_accuracy': np.mean(accuracies) if accuracies else 0,
            'average_confidence': np.mean(confidences) if confidences else 0,
            'average_error': np.mean(errors) if errors else 0,
            'confidence_breakdown': {
                'high_confidence': {
                    'count': len(high_confidence),
                    'avg_accuracy': np.mean([p.accuracy_score for p in high_confidence if p.accuracy_score]) if high_confidence else 0
                },
                'medium_confidence': {
                    'count': len(medium_confidence),
                    'avg_accuracy': np.mean([p.accuracy_score for p in medium_confidence if p.accuracy_score]) if medium_confidence else 0
                },
                'low_confidence': {
                    'count': len(low_confidence),
                    'avg_accuracy': np.mean([p.accuracy_score for p in low_confidence if p.accuracy_score]) if low_confidence else 0
                }
            },
            'model_version': self.MODEL_VERSION
        }
    
    # Private helper methods
    
    def _prepare_training_data(self) -> pd.DataFrame:
        """Prepare training data from historical sales"""
        # Get sales data from the last year
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        sales = Sale.query.filter(Sale.sale_date >= start_date).all()
        
        if not sales:
            return pd.DataFrame()
        
        # Group sales by product and week
        training_records = []
        products = Product.query.all()
        
        for product in products:
            product_sales = [s for s in sales if s.product_id == product.id]
            
            if len(product_sales) < 5:  # Need minimum sales history
                continue
            
            # Create weekly training samples
            current_date = start_date
            while current_date < end_date - timedelta(days=7):
                week_end = current_date + timedelta(days=7)
                
                # Calculate actual demand for this week
                week_sales = [s for s in product_sales if current_date <= s.sale_date < week_end]
                actual_demand = sum(s.quantity for s in week_sales)
                
                # Calculate features for this time point
                features = self._calculate_historical_features(product.id, current_date, sales)
                
                if features:
                    features['actual_demand'] = actual_demand
                    features['product_id'] = product.id
                    training_records.append(features)
                
                current_date = week_end
        
        return pd.DataFrame(training_records)
    
    def _prepare_prediction_features(self, product_id: int) -> Optional[Dict]:
        """Prepare features for prediction"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return None
            
            # Get recent sales data
            recent_sales = Sale.query.filter(
                Sale.product_id == product_id,
                Sale.sale_date >= datetime.utcnow() - timedelta(days=90)
            ).order_by(Sale.sale_date.desc()).all()
            
            if not recent_sales:
                # Return default features for products with no sales history
                return self._get_default_features(product)
            
            return self._calculate_current_features(product, recent_sales)
            
        except Exception:
            return None
    
    def _calculate_historical_features(self, product_id: int, reference_date: datetime, all_sales: List) -> Optional[Dict]:
        """Calculate features for a historical time point"""
        product = Product.query.get(product_id)
        if not product:
            return None
        
        # Filter sales up to reference date
        historical_sales = [s for s in all_sales if s.product_id == product_id and s.sale_date <= reference_date]
        
        if not historical_sales:
            return self._get_default_features(product)
        
        return self._calculate_features_from_sales(product, historical_sales, reference_date)
    
    def _calculate_current_features(self, product: Product, recent_sales: List) -> Dict:
        """Calculate current features for prediction"""
        return self._calculate_features_from_sales(product, recent_sales, datetime.utcnow())
    
    def _calculate_features_from_sales(self, product: Product, sales: List, reference_date: datetime) -> Dict:
        """Calculate features from sales data"""
        # Sort sales by date
        sales.sort(key=lambda x: x.sale_date)
        
        # Calculate time-based metrics
        sales_7d = [s for s in sales if s.sale_date >= reference_date - timedelta(days=7)]
        sales_30d = [s for s in sales if s.sale_date >= reference_date - timedelta(days=30)]
        
        # Average daily sales
        avg_daily_sales_7d = sum(s.quantity for s in sales_7d) / 7 if sales_7d else 0
        avg_daily_sales_30d = sum(s.quantity for s in sales_30d) / 30 if sales_30d else 0
        
        # Trend calculation
        trend_7d = self._calculate_sales_trend(sales_7d)
        trend_30d = self._calculate_sales_trend(sales_30d)
        
        # Seasonal factor (month-based)
        seasonal_factor = self._get_seasonal_factor(reference_date.month)
        
        # Days since last sale
        last_sale_date = max(s.sale_date for s in sales) if sales else reference_date - timedelta(days=365)
        days_since_last_sale = (reference_date - last_sale_date).days
        
        # Price ratio (selling price / cost price)
        price_ratio = float(product.selling_price / product.cost_price) if product.cost_price > 0 else 1.0
        
        # Category performance (average sales for products in same category)
        category_performance = self._get_category_performance_factor(product.category, reference_date)
        
        return {
            'avg_daily_sales_7d': avg_daily_sales_7d,
            'avg_daily_sales_30d': avg_daily_sales_30d,
            'trend_7d': trend_7d,
            'trend_30d': trend_30d,
            'seasonal_factor': seasonal_factor,
            'days_since_last_sale': min(days_since_last_sale, 365),  # Cap at 365 days
            'current_stock': product.quantity,
            'price_ratio': price_ratio,
            'category_performance': category_performance
        }
    
    def _get_default_features(self, product: Product) -> Dict:
        """Get default features for products with no sales history"""
        return {
            'avg_daily_sales_7d': 0.1,  # Small default value
            'avg_daily_sales_30d': 0.1,
            'trend_7d': 0.0,
            'trend_30d': 0.0,
            'seasonal_factor': 1.0,
            'days_since_last_sale': 365,
            'current_stock': product.quantity,
            'price_ratio': float(product.selling_price / product.cost_price) if product.cost_price > 0 else 1.0,
            'category_performance': 1.0
        }
    
    def _calculate_sales_trend(self, sales: List) -> float:
        """Calculate sales trend from sales data"""
        if len(sales) < 2:
            return 0.0
        
        # Simple linear trend calculation
        dates = [(s.sale_date - sales[0].sale_date).days for s in sales]
        quantities = [s.quantity for s in sales]
        
        if len(set(dates)) < 2:
            return 0.0
        
        # Calculate correlation coefficient as trend indicator
        try:
            correlation = np.corrcoef(dates, quantities)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0
        except:
            return 0.0
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal factor for a given month"""
        # Simple seasonal factors (can be improved with actual data analysis)
        seasonal_factors = {
            1: 0.9,   # January - post-holiday low
            2: 0.95,  # February
            3: 1.0,   # March
            4: 1.05,  # April
            5: 1.1,   # May
            6: 1.15,  # June - summer high
            7: 1.2,   # July - peak summer
            8: 1.15,  # August
            9: 1.05,  # September
            10: 1.0,  # October
            11: 1.1,  # November - pre-holiday
            12: 1.3   # December - holiday peak
        }
        return seasonal_factors.get(month, 1.0)
    
    def _get_category_performance_factor(self, category: str, reference_date: datetime) -> float:
        """Get category performance factor"""
        # Get recent sales for products in the same category
        category_products = Product.query.filter_by(category=category).all()
        
        if not category_products:
            return 1.0
        
        total_sales = 0
        for product in category_products:
            recent_sales = Sale.query.filter(
                Sale.product_id == product.id,
                Sale.sale_date >= reference_date - timedelta(days=30)
            ).all()
            total_sales += sum(s.quantity for s in recent_sales)
        
        # Normalize by number of products in category
        avg_category_sales = total_sales / len(category_products) if category_products else 0
        
        # Return factor relative to overall average (1.0 = average performance)
        return min(max(avg_category_sales / 10, 0.1), 3.0)  # Cap between 0.1 and 3.0
    
    def _calculate_confidence_score(self, features: Dict, predicted_demand: int) -> float:
        """Calculate confidence score for prediction"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on sales history
        if features['avg_daily_sales_30d'] > 0:
            confidence += 0.2
        
        if features['avg_daily_sales_7d'] > 0:
            confidence += 0.1
        
        # Adjust based on trend consistency
        if abs(features['trend_7d'] - features['trend_30d']) < 0.3:
            confidence += 0.1
        
        # Reduce confidence for very recent sales
        if features['days_since_last_sale'] > 30:
            confidence -= 0.1
        
        # Adjust based on prediction magnitude
        if predicted_demand > 0:
            confidence += 0.1
        
        return max(0.1, min(1.0, confidence))
    
    def _calculate_trend_factor(self, features: Dict) -> float:
        """Calculate trend factor from features"""
        return (features['trend_7d'] + features['trend_30d']) / 2
    
    def _is_prediction_stale(self, prediction: AIPrediction) -> bool:
        """Check if prediction is stale and needs updating"""
        age_threshold = {
            'weekly': 3,    # 3 days
            'monthly': 7,   # 1 week
            'quarterly': 14 # 2 weeks
        }
        
        days_old = (datetime.utcnow() - prediction.prediction_date).days
        threshold = age_threshold.get(prediction.prediction_period, 7)
        
        return days_old > threshold
    
    def _calculate_restock_suggestion(self, product: Product, prediction: AIPrediction) -> Optional[Dict]:
        """Calculate restock suggestion for a product"""
        current_stock = product.quantity
        predicted_demand = prediction.predicted_demand
        confidence = float(prediction.confidence_score)
        
        # Calculate safety stock based on confidence and variability
        safety_factor = 1.5 - (confidence * 0.5)  # Lower confidence = higher safety stock
        safety_stock = int(predicted_demand * safety_factor * 0.2)  # 20% of adjusted demand
        
        # Calculate suggested restock quantity
        total_needed = predicted_demand + safety_stock
        restock_needed = max(0, total_needed - current_stock)
        
        # Only suggest if restock is needed
        if restock_needed <= 0:
            return None
        
        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(product, prediction)
        
        return {
            'product_id': product.id,
            'product_name': product.name,
            'category': product.category,
            'current_stock': current_stock,
            'predicted_demand': predicted_demand,
            'suggested_quantity': restock_needed,
            'safety_stock': safety_stock,
            'confidence_score': confidence,
            'urgency_score': urgency_score,
            'urgency_level': self._get_urgency_level(urgency_score),
            'prediction_period': prediction.prediction_period,
            'reasoning': f"Predicted {predicted_demand} units needed, current stock: {current_stock}, safety buffer: {safety_stock}",
            'cost_estimate': float(restock_needed * product.cost_price),
            'revenue_potential': float(predicted_demand * product.selling_price)
        }
    
    def _calculate_urgency_score(self, product: Product, prediction: AIPrediction) -> float:
        """Calculate urgency score for restocking"""
        score = 0.0
        
        # Stock level factor (lower stock = higher urgency)
        if product.quantity == 0:
            score += 1.0
        elif product.quantity <= product.low_stock_threshold:
            score += 0.7
        elif product.quantity <= product.low_stock_threshold * 2:
            score += 0.3
        
        # Demand factor (higher predicted demand = higher urgency)
        if prediction.predicted_demand > product.quantity * 2:
            score += 0.5
        elif prediction.predicted_demand > product.quantity:
            score += 0.3
        
        # Confidence factor (higher confidence = higher urgency)
        score += float(prediction.confidence_score) * 0.3
        
        return min(score, 2.0)  # Cap at 2.0
    
    def _get_urgency_level(self, urgency_score: float) -> str:
        """Get urgency level from score"""
        if urgency_score >= 1.5:
            return 'critical'
        elif urgency_score >= 1.0:
            return 'high'
        elif urgency_score >= 0.5:
            return 'medium'
        else:
            return 'low'
    
    def _calculate_seasonal_factors(self, monthly_sales: Dict) -> Dict:
        """Calculate seasonal factors from monthly sales data"""
        if not monthly_sales:
            return {}
        
        # Calculate average monthly sales
        avg_monthly_sales = sum(monthly_sales.values()) / len(monthly_sales)
        
        if avg_monthly_sales == 0:
            return {}
        
        # Calculate seasonal factors (ratio to average)
        seasonal_factors = {}
        for month, sales in monthly_sales.items():
            month_num = int(month.split('-')[1])
            seasonal_factors[month_num] = sales / avg_monthly_sales
        
        return seasonal_factors
    
    def _analyze_overall_trend(self, monthly_sales: Dict) -> str:
        """Analyze overall trend from monthly sales"""
        if len(monthly_sales) < 3:
            return 'insufficient_data'
        
        # Sort by month
        sorted_months = sorted(monthly_sales.items())
        sales_values = [sales for _, sales in sorted_months]
        
        # Calculate trend using linear regression
        x = np.arange(len(sales_values))
        y = np.array(sales_values)
        
        if len(x) < 2:
            return 'stable'
        
        try:
            slope = np.polyfit(x, y, 1)[0]
            
            if slope > 0.1:
                return 'increasing'
            elif slope < -0.1:
                return 'decreasing'
            else:
                return 'stable'
        except:
            return 'stable'
    
    def _generate_seasonal_recommendations(self, product: Product, seasonal_factors: Dict, 
                                         peak_months: List, low_months: List) -> List[str]:
        """Generate seasonal recommendations"""
        recommendations = []
        
        if peak_months:
            recommendations.append(
                f"Increase stock before peak months: {', '.join(map(str, peak_months))}"
            )
        
        if low_months:
            recommendations.append(
                f"Reduce stock during low-demand months: {', '.join(map(str, low_months))}"
            )
        
        # Current month recommendation
        current_month = datetime.now().month
        current_factor = seasonal_factors.get(current_month, 1.0)
        
        if current_factor > 1.2:
            recommendations.append("Current month shows high seasonal demand - consider increasing stock")
        elif current_factor < 0.8:
            recommendations.append("Current month shows low seasonal demand - avoid overstocking")
        
        return recommendations