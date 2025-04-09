from setup import create_app
from routes import routes_bp
from models import *
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
