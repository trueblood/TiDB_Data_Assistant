class HealthCheckService:

    def check_api_status(self):
        # Implement the logic to check API status
        # For simplicity, returning "up"
        return "up"

    def check_database_status(self):
        # Implement the logic to check MongoDB database server status
        # This could involve a simple query or ping to the database
        # For simplicity, returning "up"
        return "up"