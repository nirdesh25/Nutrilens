"""
Purchase Request Service for Smart Inventory Management System
Handles business logic for customer purchase request operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from models.purchase_request import PurchaseRequest
from models.product import Product
from models.user import User
from extensions import db


class PurchaseRequestService:
    """Service class for purchase request operations"""
    
    @staticmethod
    def create_purchase_request(customer_id: int, product_id: int, quantity: int) -> PurchaseRequest:
        """
        Create a new purchase request
        
        Args:
            customer_id: ID of the customer making the request
            product_id: ID of the product being requested
            quantity: Quantity requested
            
        Returns:
            PurchaseRequest: The created purchase request
            
        Raises:
            ValueError: If validation fails
        """
        # Validate customer exists and is a customer
        customer = User.query.get(customer_id)
        if not customer or customer.role != 'customer':
            raise ValueError("Invalid customer")
        
        # Validate product exists
        product = Product.query.get(product_id)
        if not product:
            raise ValueError("Product not found")
        
        # Check if product is available
        if product.is_out_of_stock():
            raise ValueError(f"Product '{product.name}' is out of stock")
        
        # Validate quantity
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        if quantity > product.quantity:
            raise ValueError(f"Requested quantity ({quantity}) exceeds available stock ({product.quantity})")
        
        # Create the purchase request
        purchase_request = PurchaseRequest(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity
        )
        
        db.session.add(purchase_request)
        db.session.commit()
        
        return purchase_request
    
    @staticmethod
    def get_customer_requests(customer_id: int, status: Optional[str] = None, 
                            limit: Optional[int] = None, offset: int = 0) -> List[PurchaseRequest]:
        """
        Get purchase requests for a specific customer
        
        Args:
            customer_id: ID of the customer
            status: Optional status filter
            limit: Optional limit for pagination
            offset: Offset for pagination
            
        Returns:
            List[PurchaseRequest]: List of purchase requests
        """
        query = PurchaseRequest.get_customer_requests(customer_id)
        
        if status:
            query = query.filter(PurchaseRequest.status == status)
        
        if offset > 0:
            query = query.offset(offset)
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    @staticmethod
    def get_customer_request_stats(customer_id: int) -> Dict[str, Any]:
        """
        Get statistics for a customer's purchase requests
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            Dict containing request statistics
        """
        # Get counts by status
        pending_count = PurchaseRequest.query.filter_by(
            customer_id=customer_id, 
            status=PurchaseRequest.STATUS_PENDING
        ).count()
        
        approved_count = PurchaseRequest.query.filter_by(
            customer_id=customer_id, 
            status=PurchaseRequest.STATUS_APPROVED
        ).count()
        
        rejected_count = PurchaseRequest.query.filter_by(
            customer_id=customer_id, 
            status=PurchaseRequest.STATUS_REJECTED
        ).count()
        
        total_count = pending_count + approved_count + rejected_count
        
        # Calculate total value of approved requests
        approved_requests = PurchaseRequest.query.filter_by(
            customer_id=customer_id, 
            status=PurchaseRequest.STATUS_APPROVED
        ).all()
        
        total_approved_value = sum(req.total_value for req in approved_requests)
        
        # Calculate approval rate
        approval_rate = (approved_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'total_requests': total_count,
            'pending_requests': pending_count,
            'approved_requests': approved_count,
            'rejected_requests': rejected_count,
            'total_approved_value': float(total_approved_value),
            'approval_rate': round(approval_rate, 2)
        }
    
    @staticmethod
    def check_product_availability(product_id: int, quantity: int) -> Dict[str, Any]:
        """
        Check if a product is available for the requested quantity
        
        Args:
            product_id: ID of the product
            quantity: Requested quantity
            
        Returns:
            Dict containing availability information
        """
        product = Product.query.get(product_id)
        
        if not product:
            return {
                'product_id': product_id,
                'exists': False,
                'error': 'Product not found'
            }
        
        is_available = product.can_fulfill_quantity(quantity)
        
        return {
            'product_id': product_id,
            'product_name': product.name,
            'exists': True,
            'requested_quantity': quantity,
            'available_quantity': product.quantity,
            'is_available': is_available,
            'is_in_stock': not product.is_out_of_stock(),
            'is_low_stock': product.is_low_stock(),
            'unit_price': float(product.selling_price),
            'total_value': float(product.selling_price * quantity) if is_available else None,
            'message': 'Available' if is_available else f'Only {product.quantity} units available'
        }
    
    @staticmethod
    def get_recent_requests(customer_id: int, days: int = 7) -> List[PurchaseRequest]:
        """
        Get recent purchase requests for a customer
        
        Args:
            customer_id: ID of the customer
            days: Number of days to look back
            
        Returns:
            List[PurchaseRequest]: Recent purchase requests
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return PurchaseRequest.query.filter(
            PurchaseRequest.customer_id == customer_id,
            PurchaseRequest.requested_at >= cutoff_date
        ).order_by(PurchaseRequest.requested_at.desc()).all()
    
    @staticmethod
    def get_pending_requests_count(customer_id: int) -> int:
        """
        Get count of pending requests for a customer
        
        Args:
            customer_id: ID of the customer
            
        Returns:
            int: Number of pending requests
        """
        return PurchaseRequest.query.filter_by(
            customer_id=customer_id,
            status=PurchaseRequest.STATUS_PENDING
        ).count()
    
    @staticmethod
    def validate_request_data(product_id: int, quantity: int, customer_id: int) -> Dict[str, Any]:
        """
        Validate purchase request data before creation
        
        Args:
            product_id: ID of the product
            quantity: Requested quantity
            customer_id: ID of the customer
            
        Returns:
            Dict containing validation results
        """
        errors = []
        
        # Validate customer
        customer = User.query.get(customer_id)
        if not customer:
            errors.append("Customer not found")
        elif customer.role != 'customer':
            errors.append("Invalid customer role")
        
        # Validate product
        product = Product.query.get(product_id)
        if not product:
            errors.append("Product not found")
        else:
            if product.is_out_of_stock():
                errors.append(f"Product '{product.name}' is out of stock")
            elif not product.can_fulfill_quantity(quantity):
                errors.append(f"Requested quantity ({quantity}) exceeds available stock ({product.quantity})")
        
        # Validate quantity
        if quantity <= 0:
            errors.append("Quantity must be greater than 0")
        elif quantity > 1000:
            errors.append("Quantity cannot exceed 1000 per request")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'product': product.to_dict() if product else None,
            'customer': customer.to_dict() if customer else None
        }
    
    @staticmethod
    def get_request_by_id(request_id: int, customer_id: Optional[int] = None) -> Optional[PurchaseRequest]:
        """
        Get a purchase request by ID, optionally filtered by customer
        
        Args:
            request_id: ID of the request
            customer_id: Optional customer ID for access control
            
        Returns:
            PurchaseRequest or None if not found/not accessible
        """
        query = PurchaseRequest.query.filter_by(id=request_id)
        
        if customer_id:
            query = query.filter_by(customer_id=customer_id)
        
        return query.first()
    
    @staticmethod
    def can_customer_access_request(request_id: int, customer_id: int) -> bool:
        """
        Check if a customer can access a specific request
        
        Args:
            request_id: ID of the request
            customer_id: ID of the customer
            
        Returns:
            bool: True if customer can access the request
        """
        request = PurchaseRequest.query.get(request_id)
        return request is not None and request.customer_id == customer_id
    
    @staticmethod
    def search_customer_requests(customer_id: int, search_term: Optional[str] = None,
                               status: Optional[str] = None, 
                               date_from: Optional[datetime] = None,
                               date_to: Optional[datetime] = None) -> List[PurchaseRequest]:
        """
        Search customer's purchase requests with various filters
        
        Args:
            customer_id: ID of the customer
            search_term: Optional search term for product name
            status: Optional status filter
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List[PurchaseRequest]: Filtered purchase requests
        """
        query = PurchaseRequest.query.filter_by(customer_id=customer_id)
        
        if search_term:
            query = query.join(Product).filter(
                Product.name.contains(search_term)
            )
        
        if status:
            query = query.filter(PurchaseRequest.status == status)
        
        if date_from:
            query = query.filter(PurchaseRequest.requested_at >= date_from)
        
        if date_to:
            query = query.filter(PurchaseRequest.requested_at <= date_to)
        
        return query.order_by(PurchaseRequest.requested_at.desc()).all()