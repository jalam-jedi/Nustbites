from extensions import *
from models import *

api_bp = Blueprint('api', __name__, url_prefix='/api')

# API to fetch full menu
@api_bp.route('/menu', methods=['GET'])
@login_required
def get_menu_items():
    restaurant_id = request.args.get('restaurant_id', type=int)

    if not restaurant_id:
        return {"error": "Restaurant ID is required."}, 400

    # Query the database for menu items of that restaurant
    menu_items = Menu.query.filter_by(restaurant_id=restaurant_id, is_available=True).all()

    # Group by category (optional, but useful)
    categories = {}
    for item in menu_items:
        if item.category not in categories:
            categories[item.category] = []
        categories[item.category].append({
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'description': item.description,
            'image_url': item.image_url,
            'is_available': item.is_available
        })

    return jsonify(categories)

@api_bp.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_data = [
        {
            'id': restaurant.id,
            'name': restaurant.name
            # No logo for now
        } 
        for restaurant in restaurants
    ]
    return jsonify(restaurants_data)
