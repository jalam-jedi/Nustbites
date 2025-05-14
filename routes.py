from extensions import *
from models import *
from forms import *
from flask import jsonify, request



# Maximum file size (2.5MB)
MAX_CONTENT_LENGTH = 2.5 * 1024 * 1024


routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)

# =====================
# Login Page
# =====================
@routes_bp.route('/login', methods=[ 'POST','GET'])
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
@routes_bp.route('/register', methods=['POST', 'GET'])
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
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return render_template('menu.html', restaurant=restaurant)




@routes_bp.route('/order_details', methods=['GET', 'POST'])
@login_required
def order_details():
    bucket = session.get('bucket', [])
    for item in bucket:
        print(f"Item: {item}")
    total = sum(item['price'] * item['quantity'] for item in bucket)
    locations = Location.query.all()
    session['can_access_checkout'] = True  # Allow access to checkout only after visiting order_details

    resp = make_response(render_template(
        'order_details.html',
        bucket=bucket,
        total=total,
        user=current_user,
        locations=locations
    ))
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@routes_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if not session.get('can_access_checkout'):
        bucket = session.get('bucket', [])
        restaurant_id = None
        if bucket and 'restaurant_id' in bucket[0]:
            restaurant_id = bucket[0]['restaurant_id']
        if restaurant_id:
            flash('You must review your order details before checkout.', 'error')
            return redirect(url_for('routes.menu_page', restaurant_id=restaurant_id))
        else:
            flash('You must review your order details before checkout.', 'error')
            return redirect(url_for('routes.home'))
    session.pop('can_access_checkout', None)  # Remove flag after first access
    try:
        bucket = session.get('bucket', [])
        if not bucket or len(bucket) == 0:
            flash('Your bucket is empty!', 'error')
            return redirect(url_for('routes.menu_page', restaurant_id=request.form.get('restaurant_id')))
            
        if request.method == 'POST':
            total = sum(item['price'] * item['quantity'] for item in bucket)
            delivery_type = request.form.get('delivery_type')
            location_id = request.form.get('location_id')
            special_instructions = request.form.get('special_instructions')
            
            # Validate required fields
            if not delivery_type:
                flash('Please select a delivery type', 'error')
                return redirect(url_for('routes.order_details'))
                
            # Optionally, get location name from DB
            location = Location.query.get(location_id) if location_id else None
            
            resp = make_response(render_template(
                'checkout.html',
                bucket=bucket,
                total=total,
                delivery_type=delivery_type,
                location=location,
                special_instructions=special_instructions,
                user=current_user
            ))
            resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        # For GET requests
        resp = make_response(redirect(url_for('routes.menu_page', restaurant_id=request.form.get('restaurant_id'))))
        resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        resp.headers['Pragma'] = 'no-cache'
        resp.headers['Expires'] = '0'
        return resp
    except Exception as e:
        flash('An error occurred while processing your checkout', 'error')
        return redirect(url_for('routes.menu_page', restaurant_id=request.form.get('restaurant_id')))

@routes_bp.route('/get_bucket')
@login_required
def get_bucket():
    try:
        bucket = session.get('bucket', [])
        return jsonify({'bucket': bucket})
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve bucket'}), 500

@routes_bp.route('/save_bucket', methods=['POST'])
@login_required
def save_bucket():
    try:
        bucket = request.json.get('bucket', [])
        if not isinstance(bucket, list):
            return jsonify({'error': 'Invalid bucket format'}), 400
            
        session['bucket'] = bucket
        session.modified = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': 'Failed to save bucket'}), 500


@routes_bp.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    user = current_user
    # Query the user's orders, sorted by most recent
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    return render_template('account.html', user=user, orders=orders)

@routes_bp.route('/create_order', methods=['POST'])
@login_required
def create_order():
    try:
        bucket = session.get('bucket', [])
        if not bucket:
            return redirect(url_for('routes.menu_page', restaurant_id=request.form.get('restaurant_id')))

        restaurant_id = bucket[0].get('restaurant_id')
        if not restaurant_id:
            return redirect(url_for('routes.menu_page', restaurant_id=restaurant_id))

        # Generate order ID and create order
        try:
            order_id = Order.generate_order_id(restaurant_id)
            sequence = int(order_id.split('-')[1])
        except ValueError as e:
            return redirect(url_for('routes.checkout'))

        # Create the order
        new_order = Order(
            id=order_id,
            sequence=sequence,
            user_id=current_user.id,
            restaurant_id=restaurant_id,
            items=json.dumps(bucket),
            special_instructions=request.form.get('special_instructions')
        )

        # Create the payment record
        total = sum(item['price'] * item['quantity'] for item in bucket)
        new_payment = Payment(
            order_id=order_id,
            user_id=current_user.id,
            amount=total
        )

        # Handle payment slip upload
        slip_uploaded = False
        if 'payment_slip' in request.files:
            file = request.files['payment_slip']
            if file and file.filename:
                try:
                    # Check file size
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > MAX_CONTENT_LENGTH:
                        return redirect(url_for('routes.checkout'))
                    
                    # Create temp directory if it doesn't exist
                    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # Secure the filename
                    filename = secure_filename(file.filename)
                    temp_path = os.path.join(temp_dir, filename)
                    file.save(temp_path)
                    
                    # Upload to Google Drive
                    try:
                        drive_file_id = upload_to_drive(temp_path, filename, FOLDER_ID)
                        new_payment.drive_file_id = drive_file_id
                        slip_uploaded = True
                    except Exception as e:
                        pass
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)
                except Exception as e:
                    pass
        if not slip_uploaded:
            flash('No payment slip uploaded', 'error')

        # Save to database
        try:
            db.session.add(new_order)
            db.session.add(new_payment)
            db.session.commit()
            # Only clear the bucket after successful database commit
            session.pop('bucket', None)
            session.modified = True
            return redirect(url_for('routes.account'))
        except Exception as e:
            db.session.rollback()
            flash('Order could not be created. Please try again.', 'error')
            return redirect(url_for('routes.checkout'))

    except Exception as e:
        return redirect(url_for('routes.checkout'))

def upload_to_drive(local_file_path, filename, folder_id):
    try:
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError("Google Drive credentials not found")
        
        if not os.path.exists(local_file_path):
            raise FileNotFoundError("File to upload not found")

        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': filename,
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(local_file_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    except Exception as e:
        raise Exception(f"Failed to upload to Google Drive: {str(e)}")

@routes_bp.route('/order_details/<order_id>')
@login_required
def get_order_details(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        # Ensure user can only view their own orders
        if order.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
            
        return jsonify({
            'id': order.id,
            'created_at': order.created_at.isoformat(),
            'status': order.status.value,
            'items': order.items,
            'special_instructions': order.special_instructions
        })
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve order details'}), 500

@routes_bp.app_context_processor
def inject_restaurants():
    from models import Restaurant
    return {'restaurants': Restaurant.query.all()}

@routes_bp.route('/admin/orderdashboard')
@login_required
def admin_order_dashboard():
    if not getattr(current_user, 'role', None) == Role.ADMIN:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('routes.login'))
    restaurants = Restaurant.query.all()
    orders = Order.query.options(db.joinedload(Order.user), db.joinedload(Order.rider)).all()
    riders = Rider.query.all()
    # Attach menu_items to each order
    for order in orders:
        order.menu_items = []
        try:
            items = json.loads(order.items)
            for item in items:
                menu_item = Menu.query.get(item.get('menu_id'))
                if menu_item:
                    order.menu_items.append({
                        'menu': menu_item,
                        'quantity': item.get('quantity', 1)
                    })
        except Exception:
            order.menu_items = []
    return render_template('orders_dashboard.html', restaurants=restaurants, orders=orders, riders=riders)

@routes_bp.route('/admin/update_order/<order_id>', methods=['POST'])
@login_required
def update_order(order_id):
    if not getattr(current_user, 'role', None) == Role.ADMIN:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Order not found'}), 404
    try:
        # Update order fields
        for field in ['status', 'special_instructions', 'delivery_type', 'promo_code', 'promo_type', 'discount', 'reason', 'order_no', 'cost_price', 'delivery_price']:
            if field in request.form:
                setattr(order, field, request.form[field] if request.form[field] != '' else None)
        # Update location if provided
        if 'location' in request.form:
            location_name = request.form['location']
            if location_name:
                location = Location.query.filter_by(name=location_name).first()
                if location:
                    order.location_id = location.id
        # Update rider assignment
        if 'rider_id' in request.form:
            rider_id = request.form['rider_id']
            order.rider_id = int(rider_id) if rider_id else None
        # Update payment amount if provided
        if 'amount' in request.form and hasattr(order, 'payment') and order.payment:
            order.payment.amount = request.form['amount']
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})