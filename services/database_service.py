# db_service.py
import mysql.connector
from mysql.connector import MySQLConnection
from models.config import Config
import logging

class DatabaseService:
    def __init__(self):
        self.config = Config()
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_connection(self, autocommit: bool = True) -> MySQLConnection:
        db_conf = {
            "host": self.config.tidb_host,
            "port": self.config.tidb_port,
            "user": self.config.tidb_user,
            "password": self.config.tidb_password,
            "database": self.config.tidb_db_name,
            "autocommit": autocommit,
            "use_pure": True,
        }

        if self.config.ca_path:
            db_conf["ssl_verify_cert"] = True
            db_conf["ssl_verify_identity"] = True
            db_conf["ssl_ca"] = self.config.ca_path

        try:
            connection = mysql.connector.connect(**db_conf)
            return connection
        except mysql.connector.Error as e:
            logging.error("Error connecting to MySQL Platform: %s", e)
            return None

