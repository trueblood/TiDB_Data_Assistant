import mysql.connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from models.lutypetable import LuTypeTable
from models.config import Config
import logging
import services.database_service as DatabaseService
from flask import request, jsonify
from services.data_service import DataService
from services.ai_service import AiService
from datetime import datetime

class DataController:
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_count(self, cursor: MySQLCursor, tableName: str) -> int:
        try:
            cursor.execute(f"SELECT count(*) FROM {tableName}")
            count = cursor.fetchone()[0]
            return count
        except mysql.connector.Error as e:
            logging.error("Error fetching count: %s", e)
            return None

    def vectorize_database_records(self):
        try:
            data = request.get_json()
            tableName = data.get('tableName')
            typeIDs = data.get('typeIDs')
            
            if tableName and typeIDs:
                processedSuccessfully = []
                connection = self.db_service.get_connection()
                cursor = connection.cursor()
                
                for typeID in typeIDs:
                    lu_type = DataService.get_lu_type_table_row_by_id(cursor, typeID, tableName)
                    #print("lu_type is ", lu_type.to_dict())
                    if lu_type:
                        # Vectorize TypeName
                        vectorized_type_name = AiService.call_vectorization_api(lu_type.TypeID, lu_type.TypeName)
                        lu_type.TypeNameVector = vectorized_type_name.vector
                        #print("lu_type.TypeNameVector is : ", lu_type.TypeNameVector)
                        print(f"Received lu_type.TypeNameVector for {lu_type.TypeID} in {lu_type.TypeName}")
                        
                        # Vectorize Description
                        vectorized_description = AiService.call_vectorization_api(lu_type.TypeID, lu_type.Description)
                        lu_type.DescriptionVector = vectorized_description.vector
                        print(f"Received lu_type.DescriptionVector for {lu_type.TypeID} in {lu_type.TypeName}")
                        #print("lu_type.DescriptionVector is : ", lu_type.DescriptionVector)

                        lu_type.modified_by = 'vectorize_database_records'
                        lu_type.modified_dt = datetime.now()

                        # Update record in database
                        DataService.update_vectors_luTypeTable_record(connection=connection, typeID=lu_type.TypeID, tableName=tableName, luTypeTable=lu_type)
                        processedSuccessfully.append(typeID)    
                cursor.close()
                connection.close()

                return jsonify({"tableName": tableName, "processedIDs": processedSuccessfully}), 200
            else:
                return jsonify({"error": "Missing tableName or typeIDs"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 400

    #if __name__ == "__main__":
        # typeID = 1
        # tableName = 'lu_emotion_type'
        # connection = DatabaseService.get_connection()
        # cursor = connection.cursor()
        # lu_type = get_lu_type_table_row_by_id(cursor, typeID, tableName)
        # print(lu_type.to_dict())
        # cursor.close()
        # connection.close()
