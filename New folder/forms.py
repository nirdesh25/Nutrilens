"""
WTForms for Smart Inventory Management System
Enhanced with comprehensive validation and error handling
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, IntegerField, TextAreaField, DecimalField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, ValidationError, EqualTo, Regexp
from models.user import User
from models.product import Product
from utils.error_handling import ValidationError as CustomValidationError, SecurityValidator
import re

class LoginForm(FlaskForm):
    """Login form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email is too long')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    """User registration form"""
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email is too long')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=80, message='First name must be between 2 and 80 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=80, message='Last name must be between 2 and 80 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    password_confirm = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ])
    role = SelectField('Account Type', choices=[
        ('customer', 'Customer'),
        ('admin', 'Administrator')
    ], default='customer', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        """Check if email is already registered"""
        # Sanitize input
        field.data = SecurityValidator.sanitize_input(field.data)
        
        if User.get_by_email(field.data):
            raise ValidationError('This email address is already registered')
    
    def validate_password(self, field):
        """Validate password strength"""
        try:
            User.validate_password(field.data)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def validate_first_name(self, field):
        """Validate first name"""
        field.data = SecurityValidator.sanitize_input(field.data)
        try:
            User.validate_name(field.data, "First name")
        except ValueError as e:
            raise ValidationError(str(e))
    
    def validate_last_name(self, field):
        """Validate last name"""
        field.data = SecurityValidator.sanitize_input(field.data)
        try:
            User.validate_name(field.data, "Last name")
        except ValueError as e:
            raise ValidationError(str(e))

class ProductForm(FlaskForm):
    """Product creation/editing form"""
    name = StringField('Product Name', validators=[
        DataRequired(message='Product name is required'),
        Length(min=2, max=200, message='Product name must be between 2 and 200 characters')
    ])
    description = TextAreaField('Description', validators=[
        Length(max=1000, message='Description is too long (maximum 1000 characters)')
    ])
    category = StringField('Category', validators=[
        DataRequired(message='Category is required'),
        Length(min=2, max=100, message='Category must be between 2 and 100 characters')
    ])
    cost_price = DecimalField('Cost Price ($)', validators=[
        DataRequired(message='Cost price is required'),
        NumberRange(min=0, max=999999.99, message='Cost price must be between $0 and $999,999.99')
    ], places=2)
    selling_price = DecimalField('Selling Price ($)', validators=[
        DataRequired(message='Selling price is required'),
        NumberRange(min=0, max=999999.99, message='Selling price must be between $0 and $999,999.99')
    ], places=2)
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=0, max=1000000, message='Quantity must be between 0 and 1,000,000')
    ])
    low_stock_threshold = IntegerField('Low Stock Alert Threshold', validators=[
        NumberRange(min=0, max=1000, message='Threshold must be between 0 and 1,000')
    ], default=10)
    submit = SubmitField('Save Product')
    
    def validate_name(self, field):
        """Validate product name"""
        field.data = SecurityValidator.sanitize_input(field.data)
        try:
            Product.validate_name(field.data)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def validate_category(self, field):
        """Validate product category"""
        field.data = SecurityValidator.sanitize_input(field.data)
        try:
            Product.validate_category(field.data)
        except ValueError as e:
            raise ValidationError(str(e))
    
    def validate_cost_price(self, field):
        """Validate cost price"""
        try:
            Product.validate_price(field.data, "Cost price")
        except ValueError as e:
            raise ValidationError(str(e))
    
    def validate_selling_price(self, field):
        """Validate selling price and ensure it's not less than cost price"""
        try:
            Product.validate_price(field.data, "Selling price")
        except ValueError as e:
            raise ValidationError(str(e))
        
        if self.cost_price.data and field.data and field.data < self.cost_price.data:
            raise ValidationError('Selling price cannot be less than cost price')
    
    def validate_quantity(self, field):
        """Validate quantity"""
        try:
            Product.validate_quantity(field.data)
        except ValueError as e:
            raise ValidationError(str(e))

class PurchaseRequestForm(FlaskForm):
    """Purchase request form"""
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, max=1000, message='Quantity must be between 1 and 1,000')
    ])
    submit = SubmitField('Submit Request')
    
    def validate_product_id(self, field):
        """Validate product ID"""
        try:
            product_id = int(field.data)
            product = Product.query.get(product_id)
            if not product or not product.is_active:
                raise ValidationError('Invalid product selected')
        except (ValueError, TypeError):
            raise ValidationError('Invalid product ID format')
    
    def validate_quantity(self, field):
        """Check if requested quantity is available and valid"""
        # First validate quantity format and range
        try:
            from models.purchase_request import PurchaseRequest
            PurchaseRequest.validate_quantity(field.data)
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Then check product availability
        if self.product_id.data:
            try:
                product = Product.query.get(int(self.product_id.data))
                if product:
                    if product.is_out_of_stock():
                        raise ValidationError(f'Product "{product.name}" is out of stock')
                    elif not product.can_fulfill_quantity(field.data):
                        raise ValidationError(f'Only {product.quantity} units available in stock')
                else:
                    raise ValidationError('Product not found')
            except (ValueError, TypeError):
                raise ValidationError('Invalid product selected')

class QuickPurchaseRequestForm(FlaskForm):
    """Quick purchase request form for product listings"""
    quantity = IntegerField('Qty', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, max=1000, message='Quantity must be between 1 and 1,000')
    ], default=1)

class AdminRequestProcessForm(FlaskForm):
    """Admin form for processing purchase requests"""
    action = SelectField('Action', choices=[
        ('approve', 'Approve'),
        ('reject', 'Reject')
    ], validators=[DataRequired()])
    rejection_reason = TextAreaField('Rejection Reason (if rejecting)', validators=[
        Length(max=500, message='Rejection reason is too long (maximum 500 characters)')
    ])
    submit = SubmitField('Process Request')
    
    def validate_rejection_reason(self, field):
        """Require rejection reason when rejecting"""
        if field.data:
            field.data = SecurityValidator.sanitize_input(field.data)
        
        if self.action.data == 'reject':
            if not field.data or not field.data.strip():
                raise ValidationError('Rejection reason is required when rejecting a request')
            if len(field.data.strip()) < 10:
                raise ValidationError('Rejection reason must be at least 10 characters long')

class ProductSearchForm(FlaskForm):
    """Product search and filter form"""
    search = StringField('Search Products', validators=[
        Length(max=100, message='Search term is too long')
    ])
    category = SelectField('Category', choices=[('', 'All Categories')], default='')
    submit = SubmitField('Search')

class StockUpdateForm(FlaskForm):
    """Form for updating product stock"""
    quantity = IntegerField('New Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=0, max=1000000, message='Quantity must be between 0 and 1,000,000')
    ])
    submit = SubmitField('Update Stock')

class BulkActionForm(FlaskForm):
    """Form for bulk actions on purchase requests"""
    bulk_action = SelectField('Bulk Action', choices=[
        ('', 'Select Action'),
        ('approve', 'Approve Selected'),
        ('reject', 'Reject Selected')
    ], validators=[DataRequired(message='Please select an action')])
    bulk_reason = TextAreaField('Reason (for rejections)', validators=[
        Length(max=500, message='Reason is too long (maximum 500 characters)')
    ])
    submit = SubmitField('Apply to Selected')
    
    def validate_bulk_reason(self, field):
        """Require reason when bulk rejecting"""
        if field.data:
            field.data = SecurityValidator.sanitize_input(field.data)
        
        if self.bulk_action.data == 'reject':
            if not field.data or not field.data.strip():
                raise ValidationError('Reason is required when rejecting requests')
            if len(field.data.strip()) < 10:
                raise ValidationError('Rejection reason must be at least 10 characters long')

class PasswordChangeForm(FlaskForm):
    """Password change form"""
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, max=128, message='Password must be between 8 and 128 characters')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')
    
    def validate_current_password(self, field):
        """Validate current password"""
        from flask_login import current_user
        if current_user.is_authenticated and not current_user.check_password(field.data):
            raise ValidationError('Current password is incorrect')
    
    def validate_new_password(self, field):
        """Validate new password strength"""
        try:
            User.validate_password(field.data)
        except ValueError as e:
            raise ValidationError(str(e))
        
        # Ensure new password is different from current
        from flask_login import current_user
        if current_user.is_authenticated and current_user.check_password(field.data):
            raise ValidationError('New password must be different from current password')

class ProfileUpdateForm(FlaskForm):
    """User profile update form"""
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=80, message='First name must be between 2 and 80 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=80, message='Last name must be between 2 and 80 characters')
    ])
    submit = SubmitField('Update Profile')

class CategoryForm(FlaskForm):
    """Category management form"""
    name = StringField('Category Name', validators=[
        DataRequired(message='Category name is required'),
        Length(min=2, max=100, message='Category name must be between 2 and 100 characters')
    ])
    submit = SubmitField('Save Category')
class EmailValidationForm(FlaskForm):
    """Form for email validation and verification"""
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email is too long')
    ])
    submit = SubmitField('Verify Email')
    
    def validate_email(self, field):
        """Validate email format and sanitize"""
        field.data = SecurityValidator.sanitize_input(field.data)
        try:
            User.validate_email(field.data)
        except ValueError as e:
            raise ValidationError(str(e))


class SearchForm(FlaskForm):
    """Enhanced search form with validation"""
    query = StringField('Search', validators=[
        Length(max=100, message='Search query is too long')
    ])
    category = SelectField('Category', choices=[('', 'All Categories')], default='')
    sort_by = SelectField('Sort By', choices=[
        ('name', 'Name'),
        ('price_asc', 'Price (Low to High)'),
        ('price_desc', 'Price (High to Low)'),
        ('quantity', 'Stock Level'),
        ('created_at', 'Date Added')
    ], default='name')
    submit = SubmitField('Search')
    
    def validate_query(self, field):
        """Validate and sanitize search query"""
        if field.data:
            field.data = SecurityValidator.sanitize_input(field.data)
            # Prevent SQL injection attempts
            dangerous_chars = ['--', ';', '/*', '*/', 'xp_', 'sp_']
            for char in dangerous_chars:
                if char in field.data.lower():
                    raise ValidationError('Invalid characters in search query')


class DateRangeForm(FlaskForm):
    """Form for date range selection with validation"""
    start_date = StringField('Start Date', validators=[
        DataRequired(message='Start date is required'),
        Regexp(r'^\d{4}-\d{2}-\d{2}$', message='Date must be in YYYY-MM-DD format')
    ])
    end_date = StringField('End Date', validators=[
        DataRequired(message='End date is required'),
        Regexp(r'^\d{4}-\d{2}-\d{2}$', message='Date must be in YYYY-MM-DD format')
    ])
    submit = SubmitField('Apply Filter')
    
    def validate_start_date(self, field):
        """Validate start date"""
        try:
            from datetime import datetime
            start_date = datetime.strptime(field.data, '%Y-%m-%d')
            # Don't allow dates too far in the past or future
            min_date = datetime(2020, 1, 1)
            max_date = datetime.now().replace(year=datetime.now().year + 1)
            
            if start_date < min_date:
                raise ValidationError('Start date cannot be before 2020')
            if start_date > max_date:
                raise ValidationError('Start date cannot be more than 1 year in the future')
        except ValueError:
            raise ValidationError('Invalid date format')
    
    def validate_end_date(self, field):
        """Validate end date and ensure it's after start date"""
        try:
            from datetime import datetime
            end_date = datetime.strptime(field.data, '%Y-%m-%d')
            
            if self.start_date.data:
                start_date = datetime.strptime(self.start_date.data, '%Y-%m-%d')
                if end_date < start_date:
                    raise ValidationError('End date must be after start date')
                
                # Don't allow date ranges longer than 1 year
                if (end_date - start_date).days > 365:
                    raise ValidationError('Date range cannot exceed 1 year')
        except ValueError:
            raise ValidationError('Invalid date format')


class QuantityUpdateForm(FlaskForm):
    """Form for updating product quantities with validation"""
    operation = SelectField('Operation', choices=[
        ('set', 'Set to'),
        ('add', 'Add'),
        ('subtract', 'Subtract')
    ], validators=[DataRequired()], default='set')
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=0, max=1000000, message='Quantity must be between 0 and 1,000,000')
    ])
    reason = TextAreaField('Reason for Change', validators=[
        Length(max=500, message='Reason is too long (maximum 500 characters)')
    ])
    submit = SubmitField('Update Stock')
    
    def validate_quantity(self, field):
        """Validate quantity based on operation"""
        try:
            Product.validate_quantity(field.data)
        except ValueError as e:
            raise ValidationError(str(e))
        
        if self.operation.data == 'subtract' and field.data <= 0:
            raise ValidationError('Quantity to subtract must be greater than 0')
        elif self.operation.data == 'add' and field.data <= 0:
            raise ValidationError('Quantity to add must be greater than 0')
    
    def validate_reason(self, field):
        """Validate reason field"""
        if field.data:
            field.data = SecurityValidator.sanitize_input(field.data)


class NotificationPreferenceForm(FlaskForm):
    """Form for managing notification preferences"""
    email_notifications = SelectField('Email Notifications', choices=[
        ('all', 'All Notifications'),
        ('important', 'Important Only'),
        ('none', 'None')
    ], default='important')
    low_stock_alerts = SelectField('Low Stock Alerts', choices=[
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled')
    ], default='enabled')
    purchase_updates = SelectField('Purchase Request Updates', choices=[
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled')
    ], default='enabled')
    submit = SubmitField('Save Preferences')


class ReportGenerationForm(FlaskForm):
    """Form for generating reports with validation"""
    report_type = SelectField('Report Type', choices=[
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('customers', 'Customer Report'),
        ('requests', 'Purchase Requests Report')
    ], validators=[DataRequired()])
    date_range = SelectField('Date Range', choices=[
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('quarter', 'This Quarter'),
        ('year', 'This Year'),
        ('custom', 'Custom Range')
    ], default='month')
    format = SelectField('Format', choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV')
    ], default='pdf')
    include_charts = SelectField('Include Charts', choices=[
        ('yes', 'Yes'),
        ('no', 'No')
    ], default='yes')
    submit = SubmitField('Generate Report')


class SystemSettingsForm(FlaskForm):
    """Form for system settings (admin only)"""
    default_low_stock_threshold = IntegerField('Default Low Stock Threshold', validators=[
        DataRequired(message='Threshold is required'),
        NumberRange(min=1, max=1000, message='Threshold must be between 1 and 1,000')
    ], default=10)
    max_purchase_quantity = IntegerField('Maximum Purchase Quantity', validators=[
        DataRequired(message='Maximum quantity is required'),
        NumberRange(min=1, max=10000, message='Maximum must be between 1 and 10,000')
    ], default=1000)
    auto_approve_threshold = DecimalField('Auto-approve Threshold ($)', validators=[
        NumberRange(min=0, max=10000, message='Threshold must be between $0 and $10,000')
    ], places=2, default=0)
    maintenance_mode = SelectField('Maintenance Mode', choices=[
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled')
    ], default='disabled')
    submit = SubmitField('Save Settings')


class ContactForm(FlaskForm):
    """Contact form with comprehensive validation"""
    name = StringField('Full Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters'),
        Regexp(r"^[a-zA-Z\s\-']+$", message='Name can only contain letters, spaces, hyphens, and apostrophes')
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address'),
        Length(max=120, message='Email is too long')
    ])
    subject = StringField('Subject', validators=[
        DataRequired(message='Subject is required'),
        Length(min=5, max=200, message='Subject must be between 5 and 200 characters')
    ])
    message = TextAreaField('Message', validators=[
        DataRequired(message='Message is required'),
        Length(min=20, max=2000, message='Message must be between 20 and 2,000 characters')
    ])
    submit = SubmitField('Send Message')
    
    def validate_name(self, field):
        """Validate and sanitize name"""
        field.data = SecurityValidator.sanitize_input(field.data)
    
    def validate_email(self, field):
        """Validate and sanitize email"""
        field.data = SecurityValidator.sanitize_input(field.data)
    
    def validate_subject(self, field):
        """Validate and sanitize subject"""
        field.data = SecurityValidator.sanitize_input(field.data)
    
    def validate_message(self, field):
        """Validate and sanitize message"""
        field.data = SecurityValidator.sanitize_input(field.data)
        
        # Check for spam-like content
        spam_indicators = ['click here', 'free money', 'urgent', 'act now', 'limited time']
        message_lower = field.data.lower()
        spam_count = sum(1 for indicator in spam_indicators if indicator in message_lower)
        
        if spam_count >= 2:
            raise ValidationError('Message appears to be spam. Please revise your message.')