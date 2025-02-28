from flask import Blueprint
from .gyms import gym_routes
from .dining import dining_routes
from .library import library_routes

# Create the main API blueprint
api = Blueprint("api", __name__)

# Register sub-blueprints
api.register_blueprint(gym_routes)
api.register_blueprint(dining_routes)
api.register_blueprint(library_routes) 