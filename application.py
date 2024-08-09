import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor

from config import Config

def get_connection(autocommit: bool = True) -> MySQLConnection:
    config = Config()
    db_conf = {
        "host": config.tidb_host,
        "port": config.tidb_port,
        "user": config.tidb_user,
        "password": config.tidb_password,
        "database": config.tidb_db_name,
        "autocommit": autocommit,
        # mysql-connector-python will use C extension by default,
        # to make this example work on all platforms more easily,
        # we choose to use pure python implementation.
        "use_pure": True,
    }

    if config.ca_path:
        db_conf["ssl_verify_cert"] = True
        db_conf["ssl_verify_identity"] = True
        db_conf["ssl_ca"] = config.ca_path
    return mysql.connector.connect(**db_conf)

def get_count(cursor: MySQLCursor, tableName) -> int:
    cursor.execute(f"SELECT count(*) FROM {tableName}")
    return cursor.fetchone()["count(*)"]

def get_lu_type_table_row_by_id(cursor: MySQLCursor, id: int, tableName) -> dict:
    cursor.execute(f"SELECT id, TypeID FROM {tableName} WHERE id = %s", (id,))

      TypeID INT AUTO_INCREMENT PRIMARY KEY,
  TypeName VARCHAR(255),
  TypeNameVector VECTOR(512),
  Description VARCHAR(255),
  DescriptionVector VECTOR(512),
  create_by VARCHAR(255),
  create_dt DATETIME DEFAULT CURRENT_TIMESTAMP,
  modified_by VARCHAR(255),
  modified_dt DATETIME,
  active_flg BOOL DEFAULT TRUE


    return cursor.fetchone()

if __name__ == "__main__":
    tableName = 'lu_emotion_type'
    recreate_table()
    simple_example()
    trade_example()
