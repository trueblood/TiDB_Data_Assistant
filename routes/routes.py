from controllers.default_controller import DefaultController
from controllers.data_controller import DataController
from helpers.wrappers import Wrappers

def initialize_routes(app, default_controller, data_controller):
    # Health Check Route
    app.add_url_rule("/api/health", 
                     view_func=Wrappers.require_api_key(default_controller.health_check),
                     methods=['GET'])

    # Get Count Route
    app.add_url_rule("/api/get_count", 
                     view_func=Wrappers.require_api_key(data_controller.get_count),
                     methods=['GET'])

    # Vectorize Database Records Route
    app.add_url_rule("/api/vectorize_database_records", 
                     view_func=Wrappers.require_api_key(data_controller.vectorize_database_records),
                     methods=['POST'])