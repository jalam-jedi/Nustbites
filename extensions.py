from flask import Flask,Blueprint, url_for, redirect, request, render_template, jsonify,flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DecimalField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, InputRequired, IPAddress, ValidationError
from flask_bcrypt import Bcrypt
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import json
from flask_admin.form import Select2Field
from werkzeug.security import generate_password_hash

# Create Flask app
app = Flask(__name__)

# Database URI for MySQL (update accordingly)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:60029032.comQ@localhost/Nustbites'  # Update your credentials and database name

# Other configurations
app.config['SECRET_KEY'] = '60029032.comQWERTY'

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
admin = Admin()



