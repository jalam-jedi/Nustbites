from extensions import *
from models import *
from forms import *


routes_bp = Blueprint('routes', __name__)

# =====================
# Home Page (After Login)
# =====================
@routes_bp.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)

# =====================
# Login Page
# =====================
@routes_bp.route('/login', methods=[ 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            # Redirect based on role
            if user.role == Role.ADMIN:
                return redirect(url_for('admin.index'))  # hypothetical admin blueprint
            else:
                return redirect(url_for('routes.home'))  # general user home
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

# =====================
# Register Page
# =====================
@routes_bp.route('/register', methods=['POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            whatsapp_no=form.whatsappno.data,
            role=Role.USER  # Default role is USER
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('routes.login'))
    return render_template('register.html', form=form)

# =====================
# Logout
# =====================
@routes_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('routes.login'))



@routes_bp.route('/menu/<int:restaurant_id>')
@login_required
def menu_page(restaurant_id):
    """
    Load the menu.html page dynamically for a given restaurant.
    The restaurant_id will be passed to frontend JS for API fetching.
    """
    return render_template('menu.html', restaurant_id=restaurant_id, user=current_user)




@routes_bp.route('/order_details', methods=['GET', 'POST'])
@login_required
def order_details():
    bucket = session.get('bucket', [])
    print("DEBUG: bucket in session:", bucket)
    for item in bucket:
        print(f"Item: {item}")
    total = sum(item['price'] * item['quantity'] for item in bucket)
    locations = Location.query.all()
    return render_template(
        'order_details.html',
        bucket=bucket,
        total=total,
        user=current_user,
        locations=locations
    )
@routes_bp.route('/checkout', methods=['POST'])
@login_required
def checkout():
    bucket = session.get('bucket', [])
    total = sum(item['price'] * item['quantity'] for item in bucket)
    delivery_type = request.form.get('delivery_type')
    location_id = request.form.get('location_id')
    special_instructions = request.form.get('special_instructions')
    # Optionally, get location name from DB
    location = Location.query.get(location_id)
    return render_template(
        'checkout.html',
        bucket=bucket,
        total=total,
        delivery_type=delivery_type,
        location=location,
        special_instructions=special_instructions,
        user=current_user
    )

@routes_bp.route('/save_bucket', methods=['POST'])
@login_required
def save_bucket():
    bucket = request.json.get('bucket', [])
    session['bucket'] = bucket
    return jsonify({'success': True})


@routes_bp.route('/account')
@login_required
def account():
    user = current_user
    # Query the user's orders, sorted by most recent
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('account.html', user=user, orders=orders)