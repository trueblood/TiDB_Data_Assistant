from flask import Flask, request
from routes.routes import initialize_routes
from controllers.default_controller import DefaultController
from controllers.data_controller import DataController
from services.database_service import DatabaseService
import os

app = Flask(__name__)

database_service = DatabaseService()
data_controller = DataController(db_service = database_service)
default_controller = DefaultController(db_service=database_service)

initialize_routes(app, data_controller=data_controller, default_controller=default_controller)

if __name__ == '__main__':
    # Dynamically bind to the port provided by Cloud Run
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)