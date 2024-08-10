from flask import jsonify
from services.health_check_service import HealthCheckService

class DefaultController:
    def __init__(self, db_service):
        self.db_service = db_service

    def health_check(self):
        service = HealthCheckService()
        api_status = service.check_api_status()
        db_status = service.check_database_status()
        return jsonify({"api_status": api_status, "db_status": db_status})