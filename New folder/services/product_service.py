"""
Product Service for Smart Inventory Management System
Enhanced with comprehensive error handling and validation
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from extensions import db
from models.product import Product
from utils.error_handling import ValidationError, BusinessLogicError, ErrorHandler


class ProductService:
    """Service class for product management operations"""
    
    @staticmethod
    def create_product(product_data: Dict[str, Any]) -> Product:
        """
        Create a new product with comprehensive validation
        
        Args:
            product_data: Dictionary containing product information
            
        Returns:
            Product: Created product instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business logic fails
        """
        # Validate required fields
        required_fields = ['name', 'category', 'cost_price', 'selling_price']
        missing_fields = [field for field in required_fields if field not in product_data or product_data[field] is None]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        
        # Validate data types and ranges
        try:
            # Check for duplicate product name
            existing_product = Product.query.filter_by(name=product_data['name'], is_active=True).first()
            if existing_product:
                raise ValidationError(f"Product with name '{product_data['name']}' already exists")
            
            product = Product(
                name=product_data['name'],
                category=product_data['category'],
                cost_price=product_data['cost_price'],
                selling_price=product_data['selling_price'],
                quantity=product_data.get('quantity', 0),
                description=product_data.get('description'),
                low_stock_threshold=product_data.get('low_stock_threshold', 10)
            )
            
            db.session.add(product)
            db.session.commit()
            
            ErrorHandler.log_error(
                Exception(f"Product created: {product.name}"),
                context={'product_id': product.id, 'action': 'create_product'}
            )
            
            return product
            
        except ValidationError:
            db.session.rollback()
            raise
        except ValueError as e:
            db.session.rollback()
            raise ValidationError(str(e))
        except IntegrityError as e:
            db.session.rollback()
            raise BusinessLogicError("Product data violates database constraints")
        except SQLAlchemyError as e:
            db.session.rollback()
            ErrorHandler.log_error(e, context={'action': 'create_product', 'data': product_data})
            raise BusinessLogicError("Database error occurred while creating product")
        except Exception as e:
            db.session.rollback()
            ErrorHandler.log_error(e, context={'action': 'create_product', 'data': product_data})
            raise BusinessLogicError(f"Unexpected error creating product: {str(e)}")
    
    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Product]:
        """
        Get product by ID
        
        Args:
            product_id: Product ID
            
        Returns:
            Product or None if not found
        """
        return Product.query.filter_by(id=product_id, is_active=True).first()
    
    @staticmethod
    def get_all_products(include_inactive: bool = False) -> List[Product]:
        """
        Get all products
        
        Args:
            include_inactive: Whether to include inactive products
            
        Returns:
            List of products
        """
        if include_inactive:
            return Product.query.all()
        return Product.query.filter_by(is_active=True).all()
    
    @staticmethod
    def update_product(product_id: int, update_data: Dict[str, Any]) -> Product:
        """
        Update product information with comprehensive validation
        
        Args:
            product_id: Product ID to update
            update_data: Dictionary containing fields to update
            
        Returns:
            Updated product instance
            
        Raises:
            ValidationError: If validation fails
            BusinessLogicError: If business logic fails
        """
        # Validate product ID
        if not isinstance(product_id, int) or product_id <= 0:
            raise ValidationError("Invalid product ID")
        
        try:
            product = ProductService.get_product_by_id(product_id)
            if not product:
                raise BusinessLogicError(f"Product with ID {product_id} not found")
            
            # Check for name conflicts if name is being updated
            if 'name' in update_data and update_data['name'] != product.name:
                existing_product = Product.query.filter_by(
                    name=update_data['name'], 
                    is_active=True
                ).filter(Product.id != product_id).first()
                
                if existing_product:
                    raise ValidationError(f"Product with name '{update_data['name']}' already exists")
            
            # Store original values for logging
            original_values = {
                'name': product.name,
                'quantity': product.quantity,
                'cost_price': float(product.cost_price),
                'selling_price': float(product.selling_price)
            }
            
            # Update product details
            product.update_details(
                name=update_data.get('name'),
                description=update_data.get('description'),
                category=update_data.get('category'),
                cost_price=update_data.get('cost_price'),
                selling_price=update_data.get('selling_price'),
                low_stock_threshold=update_data.get('low_stock_threshold')
            )
            
            # Update quantity if provided
            if 'quantity' in update_data:
                product.update_stock(update_data['quantity'])
            
            db.session.commit()
            
            # Log the update
            ErrorHandler.log_error(
                Exception(f"Product updated: {product.name}"),
                context={
                    'product_id': product_id,
                    'action': 'update_product',
                    'original_values': original_values,
                    'updated_values': update_data
                }
            )
            
            return product
            
        except (ValidationError, BusinessLogicError):
            db.session.rollback()
            raise
        except ValueError as e:
            db.session.rollback()
            raise ValidationError(str(e))
        except IntegrityError as e:
            db.session.rollback()
            raise BusinessLogicError("Product data violates database constraints")
        except SQLAlchemyError as e:
            db.session.rollback()
            ErrorHandler.log_error(e, context={'action': 'update_product', 'product_id': product_id})
            raise BusinessLogicError("Database error occurred while updating product")
        except Exception as e:
            db.session.rollback()
            ErrorHandler.log_error(e, context={'action': 'update_product', 'product_id': product_id})
            raise BusinessLogicError(f"Unexpected error updating product: {str(e)}")
    
    @staticmethod
    def delete_product(product_id: int, soft_delete: bool = True) -> bool:
        """
        Delete product (soft delete by default)
        
        Args:
            product_id: Product ID to delete
            soft_delete: If True, deactivate product; if False, permanently delete
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If product not found
        """
        try:
            product = Product.query.get(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            
            if soft_delete:
                product.deactivate()
                db.session.commit()
            else:
                # Check if product has related records
                if product.purchase_requests.count() > 0 or product.sales.count() > 0:
                    raise ValueError("Cannot permanently delete product with existing purchase requests or sales")
                
                db.session.delete(product)
                db.session.commit()
            
            return True
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to delete product: {str(e)}")
    
    @staticmethod
    def search_products(search_term: str = None, category: str = None, 
                       in_stock_only: bool = False, low_stock_only: bool = False) -> List[Product]:
        """
        Search and filter products
        
        Args:
            search_term: Search term for name or description
            category: Filter by category
            in_stock_only: Only return products with quantity > 0
            low_stock_only: Only return products with low stock
            
        Returns:
            List of matching products
        """
        query = Product.query.filter_by(is_active=True)
        
        # Apply search term filter
        if search_term:
            search_pattern = f"%{search_term.strip()}%"
            query = query.filter(
                or_(
                    Product.name.ilike(search_pattern),
                    Product.description.ilike(search_pattern),
                    Product.category.ilike(search_pattern)
                )
            )
        
        # Apply category filter
        if category:
            query = query.filter(Product.category == category)
        
        # Apply stock filters
        if in_stock_only:
            query = query.filter(Product.quantity > 0)
        
        if low_stock_only:
            query = query.filter(Product.quantity <= Product.low_stock_threshold)
        
        return query.order_by(Product.name).all()
    
    @staticmethod
    def get_products_by_category(category: str) -> List[Product]:
        """
        Get products by category
        
        Args:
            category: Category name
            
        Returns:
            List of products in the category
        """
        return Product.query.filter_by(category=category, is_active=True).order_by(Product.name).all()
    
    @staticmethod
    def get_categories() -> List[str]:
        """
        Get all unique product categories
        
        Returns:
            List of category names
        """
        categories = db.session.query(Product.category).filter_by(is_active=True).distinct().all()
        return [category[0] for category in categories]
    
    @staticmethod
    def get_low_stock_products() -> List[Product]:
        """
        Get products with low stock levels
        
        Returns:
            List of products with low stock
        """
        return Product.query.filter(
            and_(
                Product.is_active == True,
                Product.quantity <= Product.low_stock_threshold
            )
        ).order_by(Product.quantity.asc()).all()
    
    @staticmethod
    def get_out_of_stock_products() -> List[Product]:
        """
        Get products that are out of stock
        
        Returns:
            List of out-of-stock products
        """
        return Product.query.filter(
            and_(
                Product.is_active == True,
                Product.quantity <= 0
            )
        ).order_by(Product.name).all()
    
    @staticmethod
    def update_stock(product_id: int, quantity_change: int, operation: str = 'set') -> Product:
        """
        Update product stock levels
        
        Args:
            product_id: Product ID
            quantity_change: Quantity to add, subtract, or set
            operation: 'add', 'subtract', or 'set'
            
        Returns:
            Updated product instance
            
        Raises:
            ValueError: If product not found or invalid operation
        """
        try:
            product = ProductService.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            
            if operation == 'add':
                product.increase_stock(quantity_change)
            elif operation == 'subtract':
                product.reduce_stock(quantity_change)
            elif operation == 'set':
                product.update_stock(quantity_change)
            else:
                raise ValueError(f"Invalid operation: {operation}")
            
            db.session.commit()
            return product
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Failed to update stock: {str(e)}")
    
    @staticmethod
    def check_stock_availability(product_id: int, requested_quantity: int) -> Dict[str, Any]:
        """
        Check if requested quantity is available
        
        Args:
            product_id: Product ID
            requested_quantity: Requested quantity
            
        Returns:
            Dictionary with availability information
        """
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return {
                'available': False,
                'reason': 'Product not found',
                'current_stock': 0,
                'requested': requested_quantity
            }
        
        available = product.can_fulfill_quantity(requested_quantity)
        
        return {
            'available': available,
            'reason': 'Insufficient stock' if not available else 'Available',
            'current_stock': product.quantity,
            'requested': requested_quantity,
            'product_name': product.name
        }
    
    @staticmethod
    def get_inventory_summary() -> Dict[str, Any]:
        """
        Get inventory summary statistics
        
        Returns:
            Dictionary with inventory statistics
        """
        active_products = Product.query.filter_by(is_active=True)
        
        total_products = active_products.count()
        total_value = sum(product.total_value for product in active_products.all())
        total_selling_value = sum(product.total_selling_value for product in active_products.all())
        low_stock_count = len(ProductService.get_low_stock_products())
        out_of_stock_count = len(ProductService.get_out_of_stock_products())
        
        return {
            'total_products': total_products,
            'total_inventory_value': float(total_value),
            'total_selling_value': float(total_selling_value),
            'low_stock_products': low_stock_count,
            'out_of_stock_products': out_of_stock_count,
            'categories_count': len(ProductService.get_categories())
        }
    
    @staticmethod
    def bulk_update_stock(updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Bulk update stock levels for multiple products
        
        Args:
            updates: List of dictionaries with product_id, quantity, and operation
            
        Returns:
            Dictionary with update results
        """
        results = {
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        try:
            for update in updates:
                try:
                    ProductService.update_stock(
                        update['product_id'],
                        update['quantity'],
                        update.get('operation', 'set')
                    )
                    results['successful'] += 1
                except Exception as e:
                    results['failed'] += 1
                    results['errors'].append({
                        'product_id': update['product_id'],
                        'error': str(e)
                    })
            
            return results
            
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Bulk update failed: {str(e)}")