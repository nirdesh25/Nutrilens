"""
AI routes for Smart Inventory Management System
Provides API endpoints for AI predictions and restocking suggestions
"""

from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from services.ai_prediction_service import AIPredictionService
from services.restocking_service import RestockingService
from utils.route_protection import api_admin_required, admin_required
from models.product import Product
from models.ai_prediction import AIPrediction

# Create blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/admin/ai')


@ai_bp.route('/suggestions', methods=['GET'])
@login_required
@admin_required
def get_restock_suggestions():
    """
    Get AI-powered restocking suggestions
    
    Query Parameters:
        min_confidence (float): Minimum confidence threshold (default: 0.6)
        include_seasonal (bool): Include seasonal analysis (default: true)
        budget_limit (float): Optional budget constraint
    
    Returns:
        JSON response with restocking suggestions
    """
    try:
        min_confidence = request.args.get('min_confidence', 0.6, type=float)
        include_seasonal = request.args.get('include_seasonal', 'true').lower() == 'true'
        budget_limit = request.args.get('budget_limit', type=float)
        
        # Validate parameters
        if min_confidence < 0.1 or min_confidence > 1.0:
            return jsonify({
                'error': 'Minimum confidence must be between 0.1 and 1.0'
            }), 400
        
        if budget_limit is not None and budget_limit <= 0:
            return jsonify({
                'error': 'Budget limit must be positive'
            }), 400
        
        restocking_service = RestockingService()
        suggestions = restocking_service.generate_comprehensive_suggestions(
            min_confidence=min_confidence,
            include_seasonal=include_seasonal,
            budget_limit=budget_limit
        )
        
        return jsonify({
            'success': True,
            'data': suggestions
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to generate restocking suggestions: {str(e)}'
        }), 500


@ai_bp.route('/critical-restocks', methods=['GET'])
@login_required
@admin_required
def get_critical_restocks():
    """
    Get products that critically need restocking
    
    Returns:
        JSON response with critical restock items
    """
    try:
        restocking_service = RestockingService()
        critical_items = restocking_service.get_critical_restocks()
        
        return jsonify({
            'success': True,
            'data': {
                'critical_items': critical_items,
                'total_critical': len(critical_items),
                'out_of_stock': len([item for item in critical_items if item['current_stock'] == 0]),
                'urgent_restock_needed': len([item for item in critical_items if item['urgency_score'] > 7])
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get critical restocks: {str(e)}'
        }), 500


@ai_bp.route('/seasonal-analysis', methods=['GET'])
@login_required
@admin_required
def get_seasonal_analysis():
    """
    Get seasonal restocking analysis
    
    Query Parameters:
        months_ahead (int): Number of months to analyze ahead (default: 3)
    
    Returns:
        JSON response with seasonal analysis
    """
    try:
        months_ahead = request.args.get('months_ahead', 3, type=int)
        
        if months_ahead < 1 or months_ahead > 12:
            return jsonify({
                'error': 'Months ahead must be between 1 and 12'
            }), 400
        
        restocking_service = RestockingService()
        seasonal_data = restocking_service.analyze_seasonal_restocking_needs(months_ahead)
        
        return jsonify({
            'success': True,
            'data': seasonal_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get seasonal analysis: {str(e)}'
        }), 500


@ai_bp.route('/predict/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def predict_product_demand(product_id):
    """
    Generate demand prediction for a specific product
    
    Path Parameters:
        product_id (int): ID of the product
    
    JSON Body:
        period (str): Prediction period ('weekly', 'monthly', 'quarterly')
    
    Returns:
        JSON response with prediction results
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'JSON data required'
            }), 400
        
        period = data.get('period', 'monthly')
        
        if period not in ['weekly', 'monthly', 'quarterly']:
            return jsonify({
                'error': 'Period must be weekly, monthly, or quarterly'
            }), 400
        
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'error': 'Product not found'
            }), 404
        
        ai_service = AIPredictionService()
        prediction = ai_service.predict_demand(product_id, period)
        
        if not prediction:
            return jsonify({
                'error': 'Failed to generate prediction for this product'
            }), 500
        
        return jsonify({
            'success': True,
            'data': prediction
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to predict demand: {str(e)}'
        }), 500


@ai_bp.route('/train-model', methods=['POST'])
@login_required
@admin_required
def train_ai_model():
    """
    Train or retrain the AI prediction model
    
    JSON Body:
        retrain (bool): Whether to retrain even if model exists (default: false)
    
    Returns:
        JSON response with training results
    """
    try:
        data = request.get_json() or {}
        retrain = data.get('retrain', False)
        
        ai_service = AIPredictionService()
        training_result = ai_service.train_model(retrain=retrain)
        
        return jsonify({
            'success': True,
            'data': training_result
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to train model: {str(e)}'
        }), 500


@ai_bp.route('/model-performance', methods=['GET'])
@login_required
@admin_required
def get_model_performance():
    """
    Get AI model performance statistics
    
    Returns:
        JSON response with model performance metrics
    """
    try:
        ai_service = AIPredictionService()
        performance_stats = ai_service.get_model_performance_stats()
        
        return jsonify({
            'success': True,
            'data': performance_stats
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get model performance: {str(e)}'
        }), 500


@ai_bp.route('/product/<int:product_id>/seasonal-trends', methods=['GET'])
@login_required
@admin_required
def get_product_seasonal_trends(product_id):
    """
    Get seasonal trend analysis for a specific product
    
    Path Parameters:
        product_id (int): ID of the product
    
    Returns:
        JSON response with seasonal trend analysis
    """
    try:
        # Check if product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({
                'error': 'Product not found'
            }), 404
        
        ai_service = AIPredictionService()
        seasonal_trends = ai_service.analyze_seasonal_trends(product_id)
        
        return jsonify({
            'success': True,
            'data': seasonal_trends
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get seasonal trends: {str(e)}'
        }), 500


@ai_bp.route('/optimal-orders', methods=['POST'])
@login_required
@admin_required
def calculate_optimal_orders():
    """
    Calculate optimal order quantities for specified products
    
    JSON Body:
        product_ids (list): List of product IDs to analyze
        budget_constraint (float): Optional budget limit
    
    Returns:
        JSON response with optimal order calculations
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'JSON data required'
            }), 400
        
        product_ids = data.get('product_ids', [])
        budget_constraint = data.get('budget_constraint')
        
        if not product_ids:
            return jsonify({
                'error': 'Product IDs list is required'
            }), 400
        
        if not isinstance(product_ids, list):
            return jsonify({
                'error': 'Product IDs must be a list'
            }), 400
        
        if budget_constraint is not None and budget_constraint <= 0:
            return jsonify({
                'error': 'Budget constraint must be positive'
            }), 400
        
        restocking_service = RestockingService()
        optimal_orders = restocking_service.calculate_optimal_order_quantities(
            product_ids, budget_constraint
        )
        
        return jsonify({
            'success': True,
            'data': optimal_orders
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to calculate optimal orders: {str(e)}'
        }), 500


@ai_bp.route('/supplier-optimization', methods=['GET'])
@login_required
@admin_required
def get_supplier_optimization():
    """
    Get supplier optimization suggestions
    
    Returns:
        JSON response with supplier optimization insights
    """
    try:
        restocking_service = RestockingService()
        optimization_data = restocking_service.get_supplier_optimization_suggestions()
        
        return jsonify({
            'success': True,
            'data': optimization_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get supplier optimization: {str(e)}'
        }), 500


@ai_bp.route('/predictions/history', methods=['GET'])
@login_required
@admin_required
def get_prediction_history():
    """
    Get historical predictions with accuracy data
    
    Query Parameters:
        product_id (int): Optional product ID filter
        limit (int): Number of predictions to return (default: 50)
        period (str): Optional period filter
    
    Returns:
        JSON response with prediction history
    """
    try:
        product_id = request.args.get('product_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        period = request.args.get('period')
        
        if limit < 1 or limit > 500:
            return jsonify({
                'error': 'Limit must be between 1 and 500'
            }), 400
        
        query = AIPrediction.query
        
        if product_id:
            query = query.filter_by(product_id=product_id)
        
        if period:
            if period not in ['weekly', 'monthly', 'quarterly']:
                return jsonify({
                    'error': 'Period must be weekly, monthly, or quarterly'
                }), 400
            query = query.filter_by(prediction_period=period)
        
        predictions = query.order_by(AIPrediction.prediction_date.desc()).limit(limit).all()
        
        prediction_data = [prediction.to_dict() for prediction in predictions]
        
        return jsonify({
            'success': True,
            'data': {
                'predictions': prediction_data,
                'total_count': len(prediction_data),
                'filters_applied': {
                    'product_id': product_id,
                    'period': period,
                    'limit': limit
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get prediction history: {str(e)}'
        }), 500


@ai_bp.route('/predictions/<int:prediction_id>/validate', methods=['POST'])
@login_required
@admin_required
def validate_prediction(prediction_id):
    """
    Validate a prediction with actual demand data
    
    Path Parameters:
        prediction_id (int): ID of the prediction to validate
    
    JSON Body:
        actual_demand (int): Actual demand that occurred
    
    Returns:
        JSON response with validation results
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'JSON data required'
            }), 400
        
        actual_demand = data.get('actual_demand')
        
        if actual_demand is None:
            return jsonify({
                'error': 'Actual demand is required'
            }), 400
        
        try:
            actual_demand = int(actual_demand)
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Actual demand must be a valid integer'
            }), 400
        
        if actual_demand < 0:
            return jsonify({
                'error': 'Actual demand cannot be negative'
            }), 400
        
        # Get prediction
        prediction = AIPrediction.query.get(prediction_id)
        if not prediction:
            return jsonify({
                'error': 'Prediction not found'
            }), 404
        
        # Update prediction with actual demand
        prediction.update_actual_demand(actual_demand)
        
        from extensions import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'prediction_id': prediction_id,
                'predicted_demand': prediction.predicted_demand,
                'actual_demand': prediction.actual_demand,
                'accuracy_score': float(prediction.accuracy_score) if prediction.accuracy_score else None,
                'error_percentage': prediction.error_percentage,
                'validation_date': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to validate prediction: {str(e)}'
        }), 500


# HTML page routes

@ai_bp.route('/suggestions-page', methods=['GET'])
@login_required
@admin_required
def ai_suggestions_page():
    """
    Render the AI suggestions page
    
    Returns:
        Rendered AI suggestions template
    """
    try:
        # Get initial data for server-side rendering
        restocking_service = RestockingService()
        initial_suggestions = restocking_service.generate_comprehensive_suggestions(min_confidence=0.6)
        critical_items = restocking_service.get_critical_restocks()
        
        ai_service = AIPredictionService()
        model_performance = ai_service.get_model_performance_stats()
        
        return render_template('admin/ai_suggestions.html',
                             initial_suggestions=initial_suggestions,
                             critical_items=critical_items,
                             model_performance=model_performance,
                             current_user=current_user)
        
    except Exception as e:
        return render_template('admin/ai_suggestions.html',
                             error=f'Failed to load AI suggestions: {str(e)}',
                             current_user=current_user)


@ai_bp.route('/model-management', methods=['GET'])
@login_required
@admin_required
def model_management_page():
    """
    Render the AI model management page
    
    Returns:
        Rendered model management template
    """
    try:
        ai_service = AIPredictionService()
        model_performance = ai_service.get_model_performance_stats()
        
        # Get recent predictions for display
        recent_predictions = AIPrediction.query.order_by(
            AIPrediction.prediction_date.desc()
        ).limit(10).all()
        
        return render_template('admin/model_management.html',
                             model_performance=model_performance,
                             recent_predictions=[p.to_dict() for p in recent_predictions],
                             current_user=current_user)
        
    except Exception as e:
        return render_template('admin/model_management.html',
                             error=f'Failed to load model management: {str(e)}',
                             current_user=current_user)


# Utility endpoints

@ai_bp.route('/status', methods=['GET'])
@login_required
@admin_required
def get_ai_status():
    """
    Get AI system status and health check
    
    Returns:
        JSON response with AI system status
    """
    try:
        ai_service = AIPredictionService()
        
        # Check if model is loaded
        model_loaded = ai_service.load_model()
        
        # Get basic statistics
        total_predictions = AIPrediction.query.count()
        recent_predictions = AIPrediction.query.filter(
            AIPrediction.prediction_date >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        status_data = {
            'model_loaded': model_loaded,
            'model_version': ai_service.MODEL_VERSION,
            'total_predictions': total_predictions,
            'recent_predictions_7d': recent_predictions,
            'system_status': 'healthy' if model_loaded else 'model_not_loaded',
            'last_check': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': status_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get AI status: {str(e)}'
        }), 500


@ai_bp.route('/quick-suggestions', methods=['GET'])
@login_required
@admin_required
def get_quick_suggestions():
    """
    Get quick restocking suggestions for dashboard widgets
    
    Query Parameters:
        limit (int): Number of suggestions to return (default: 5)
    
    Returns:
        JSON response with quick suggestions
    """
    try:
        limit = request.args.get('limit', 5, type=int)
        
        if limit < 1 or limit > 20:
            return jsonify({
                'error': 'Limit must be between 1 and 20'
            }), 400
        
        restocking_service = RestockingService()
        suggestions = restocking_service.generate_comprehensive_suggestions(min_confidence=0.7)
        
        # Get top suggestions by urgency
        top_suggestions = sorted(
            suggestions['suggestions'], 
            key=lambda x: x['urgency_score'], 
            reverse=True
        )[:limit]
        
        quick_data = {
            'suggestions': top_suggestions,
            'total_available': len(suggestions['suggestions']),
            'critical_count': len([s for s in suggestions['suggestions'] if s['urgency_level'] == 'critical']),
            'total_investment': sum(s['cost_estimate'] for s in top_suggestions)
        }
        
        return jsonify({
            'success': True,
            'data': quick_data
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get quick suggestions: {str(e)}'
        }), 500