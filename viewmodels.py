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
    column_list = ('id', 'name')

    # Fields to show in the create/edit form
    form_columns = ('name',)

    # Optional: Add search capability
    column_searchable_list = ['name']

    # Optional: Access control
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'role', None) == Role.ADMIN

    def inaccessible_callback(self, name, **kwargs):
        flash("You are not authorized to access this page.", "danger")
        return redirect(url_for('routes.login'))