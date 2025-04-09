from extensions import *
from models import *
from forms import *


routes_bp= Blueprint('routes',__name__)

@routes_bp.route('/', methods=['POST', 'GET'])
@login_required
def home():
    return render_template('home.html')

# Log In Page
@routes_bp.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            if user.role == "admin":  # Assuming role-based access
                return redirect(url_for('admin.index'))
            return redirect(url_for('routes.home')) 
        else: return 'Invalid username or password'
    return render_template('login.html', form=form)

# Register Page
@routes_bp.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            whatsapp_no=form.whatsappno.data,
            role=Role.USER  # Change to Enum if using Enum(UserRole)
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('routes.login'))

    return render_template('register.html', form=form)