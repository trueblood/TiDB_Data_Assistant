from flask import Flask, request
from routes.routes import initialize_routes
from controllers.default_controller import DefaultController
from controllers.data_controller import DataController
from services.database_service import DatabaseService

app = Flask(__name__)

database_service = DatabaseService()
data_controller = DataController(db_service = database_service)
default_controller = DefaultController(db_service=database_service)

initialize_routes(app, data_controller=data_controller, default_controller=default_controller)

if __name__ == "__main__":
    app.run(debug=True, port=9009)