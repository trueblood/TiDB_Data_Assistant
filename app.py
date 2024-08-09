import MySQLdb

class TiDBConnection:
    def __init__(self, host, port, user, password, dbname, table_name, ssl_ca = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.dbname = dbname
        # self.ssl_ca = ssl_ca
        # self.ssl_ca = ''
        self.table_name = table_name
        self.db = None

    def connect(self):
        try:
            self.db = MySQLdb.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                passwd=self.password,
                db=self.dbname #,
              #  ssl_mode="VERIFY_IDENTITY",
              #  ssl={"ca": self.ssl_ca}
            )
            print("Connection successful!")
        except MySQLdb.Error as e:
            print(f"Error connecting to MySQL Platform: {e}")
            self.db = None

    def check_connection(self):
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute("SELECT 1")
                if cursor.fetchone():
                    print("Database connection is active.")
                    return True
                else:
                    print("Database connection is inactive.")
                    return False
            except MySQLdb.Error as e:
                print(f"Error checking MySQL connection: {e}")
                return False
            finally:
                cursor.close()
        else:
            print("No database connection.")
            return False

    def fetch_data(self):
        try:
            cursor = self.db.cursor()
            query = f"SELECT id, typename, description FROM {self.table_name}"
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        finally:
            cursor.close()

    def update_data(self, typenamevector, id):
        try:
            cursor = self.db.cursor()
            query = f"UPDATE {self.table_name} SET typenamevector = %s WHERE id = %s"
            cursor.execute(query, (typenamevector, id))
            self.db.commit()
            print(f"Data updated for ID {id}")
        except MySQLdb.Error as e:
            self.db.rollback()
            print(f"Error updating MySQL Platform: {e}")
        finally:
            cursor.close()

    def close(self):
        if self.db:
            self.db.close()

# Usage of the class
if __name__ == "__main__":
    db_handler = TiDBConnection(
        host="gateway01.us-east-1.prod.aws.tidbcloud.com",
        port=4000,
        user="EcFsmzHzn16sz32.root",
        password="4UTXzVBKxU10w2Z1",  # Replace with actual password
        dbname="embracepath",
        table_name="lu_thought_type"
    )

    db_handler.connect()

    # Check if connection is successful
    if db_handler.check_connection():
        data = db_handler.fetch_data()
        print(data)

        # Update data example
        for record in data:
            id = record[0]
            typenamevector = "example_vector"  # Assume vector calculation or retrieval
            db_handler.update_data(typenamevector, id)

    db_handler.close()