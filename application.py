import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from models.lutypetable import LuTypeTable
from models.config import Config
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_connection(autocommit: bool = True) -> MySQLConnection:
    config = Config()
    db_conf = {
        "host": config.tidb_host,
        "port": config.tidb_port,
        "user": config.tidb_user,
        "password": config.tidb_password,
        "database": config.tidb_db_name,
        "autocommit": autocommit,
        "use_pure": True,  # Use the pure Python implementation
    }

    if config.ca_path:
        db_conf["ssl_verify_cert"] = True
        db_conf["ssl_verify_identity"] = True
        db_conf["ssl_ca"] = config.ca_path

    try:
        connection = mysql.connector.connect(**db_conf)
        return connection
    except mysql.connector.Error as e:
        logging.error("Error connecting to MySQL Platform: %s", e)
        return None

def get_count(cursor: MySQLCursor, tableName: str) -> int:
    try:
        cursor.execute(f"SELECT count(*) FROM {tableName}")
        count = cursor.fetchone()[0]
        return count
    except mysql.connector.Error as e:
        logging.error("Error fetching count: %s", e)
        return None

def get_lu_type_table_row_by_id(cursor: MySQLCursor, typeID: int, tableName: str) -> LuTypeTable:
    try:
        cursor.execute(f"SELECT * FROM {tableName} WHERE TypeID = %s", (typeID,))
        row = cursor.fetchone()
        if row:
            lu_type = LuTypeTable(
                TypeID=row[0], 
                TypeName=row[1],
                TypeNameVector=row[2],
                Description=row[3],
                DescriptionVector=row[4],
                create_by=row[5],
                create_dt=row[6],
                modified_by=row[7],
                modified_dt=row[8],
                active_flg=row[9]
            )
            return lu_type
        else:
            logging.warning(f"No record found for ID {typeID}")
            return None
    except mysql.connector.Error as e:
        logging.error("Error fetching record: %s", e)
        return None

if __name__ == "__main__":
    typeID = 1
    tableName = 'lu_emotion_type'
    connection = get_connection()
    cursor = connection.cursor()
    lu_type = get_lu_type_table_row_by_id(cursor, typeID, tableName)
    print(lu_type.to_dict())
    cursor.close()
    connection.close()
