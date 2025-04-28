from flask import Flask
from extensions import *
from routes import routes_bp
from viewmodels import *
from models import *
from api_routes import api_bp
def create_app():
    app = Flask(__name__)

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:60029032.comQ@localhost/Nustbites'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = '60029032.comQWERTY'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    admin = Admin(app, name="Admin Panel", template_mode="bootstrap4")  # Change to bootstrap4 or bootstrap5
    admin.add_view(UserModelView(User, db.session))
    admin.add_view(RestaurantModelView(Restaurant, db.session))
    admin.add_view(MenuModelView(Menu, db.session, name='Menu Items'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(routes_bp)
    app.register_blueprint(api_bp)
    # Import routes (to avoid circular imports)
    with app.app_context():
        import models
        db.create_all()

    return app
