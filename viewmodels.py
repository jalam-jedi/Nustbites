from extensions import *
from models import *



from models import Role  # ✅ Make sure your Role Enum is imported correctly


class UserModelView(ModelView):
    can_create = True
    can_delete = False

    # ✅ Fields to show in admin table view
    column_list = ('id', 'username', 'email', 'whatsapp_no', 'role')

    # ✅ Fields to show in form view (create/edit)
    form_columns = ('username', 'email', 'password', 'whatsapp_no', 'role')

    # ✅ Override field types
    form_overrides = {
        'password': PasswordField,
        'role': SelectField
    }

    form_args = {
    'password': {
        'label': 'New Password',
    },
    'role': {
        'label': 'Role',
        'choices': [(role.name, role.name) for role in Role]
    }
 }

    # ✅ Automatically hash password before saving
    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.password = generate_password_hash(form.password.data)
        super().on_model_change(form, model, is_created)

    # ✅ Only admins can access this model view
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    # ✅ Redirect unauthorized users
    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page!", "danger")
        return redirect(url_for('routes.login'))  # adjust this if your login route is different

class RestaurantModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True

    # Columns to show in the admin list view
    column_list = ('id', 'name', 'code', 'total_orders')

    # Fields to show in the create/edit form
    form_columns = ('name', 'code')

    # Optional: Add search capability
    column_searchable_list = ['name', 'code']

    # Optional: Access control
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('routes.login'))
    


class MenuModelView(ModelView):
    column_list = ('id', 'name', 'category', 'price', 'is_available', 'restaurant_id','image_url','description')  # Columns to display
    column_searchable_list = ['name', 'category']
    column_filters = ['is_available', 'category', 'restaurant_id']
    form_excluded_columns = []  
    # You can exclude fields here if needed
    column_labels = {
        'restaurant_id': 'Restaurant',
        'is_available': 'Available',
        'image_url': 'Image',
        'description': 'Description',
    }
    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.role.name == 'ADMIN'  # Or use Role.ADMIN if enum

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('routes.login', next=request.url))

class RiderModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True

    column_list = ('id', 'name', 'contact')
    form_columns = ('name', 'contact')
    column_searchable_list = ['name', 'contact']
    column_labels = {
        'contact': 'Contact Number'
    }

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('routes.login'))

class LocationModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True

    column_list = ('id', 'name')
    form_columns = ('name',)
    column_searchable_list = ['name']

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('routes.login'))

class ExtraChargesModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True

    column_list = ('charge_name', 'value')
    form_columns = ('charge_name', 'value')
    column_searchable_list = ['charge_name']
    column_labels = {
        'charge_name': 'Charge Type',
        'value': 'Amount (Rs.)'
    }

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('routes.login'))

class PaymentModelView(ModelView):
    can_create = False
    can_edit = True
    can_delete = False

    column_list = ('id', 'order_id', 'user_id', 'amount', 'status', 'created_at')
    form_columns = ('status',)
    column_searchable_list = ['order_id', 'user_id']
    column_filters = ['status']
    column_labels = {
        'order_id': 'Order',
        'user_id': 'User',
        'created_at': 'Payment Date'
    }

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('routes.login'))


class PromoCodeModelView(ModelView):
    can_create = True
    can_edit = True
    can_delete = True

    column_list = ('id', 'restaurant_id', 'code', 'discount_percentage', 'type', 'is_available', 'time_limit')
    form_columns = ('restaurant_id', 'code', 'discount_percentage', 'type', 'is_available', 'time_limit')
    column_searchable_list = ['code', 'restaurant_id']
    column_filters = ['type', 'is_available', 'restaurant_id']
    column_labels = {
        'restaurant_id': 'Restaurant',
        'discount_percentage': 'Discount (%)',
        'time_limit': 'Expiry Date'
    }

    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('routes.login'))



