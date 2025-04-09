from extensions import *
  # Importing User model from your database

#----------------------------------------------------------------------
# Register Form
class RegisterForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=20)], 
                           render_kw={"placeholder": "Username"})
    
    email = StringField('Email', 
                        validators=[DataRequired(), Email(), Length(max=40)], 
                        render_kw={"placeholder": "Email"})
    
    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=8, max=20)], 
                             render_kw={"placeholder": "Password"})

    Whatsapp = StringField('Whatsapp',
                           validators=[DataRequired(), Length(min=10, max=20)],
                           render_kw={"placeholder": "Whatsapp"})
    
    role = SelectField('Role', 
                       choices=[("User", "User")],  # Managers/Admins will be assigned manually
                       default="User")

    submit = SubmitField("Register")

    def validate_username(self, username):
        from models import User
        existing_username = User.query.filter_by(username=username.data).first()
        if existing_username:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_email(self, email):
        from models import User
        existing_email = User.query.filter_by(email=email.data).first()
        if existing_email:
            raise ValidationError('Email already exists. Please choose a different one.')

#----------------------------------------------------------------------
# Login Form
class LoginForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=4, max=20)], 
                           render_kw={"placeholder": "Username"})

    password = PasswordField('Password', 
                             validators=[DataRequired(), Length(min=7, max=20)], 
                             render_kw={"placeholder": "Password"})

    submit = SubmitField("Log In")
