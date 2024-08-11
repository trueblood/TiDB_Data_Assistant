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
from models.exercise import Exercise
import uuid
import numpy as np

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

    def vectorize_database_records_for_lu_type_table(self):
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
        
    def insert_exercise_and_vectorize_into_database(self):
        try:
            data = request.get_json()
            candidatesTexts = data.get('candidates_texts')
            connection = self.db_service.get_connection()
            cursor = connection.cursor()

            if not candidatesTexts:
                return jsonify({"error": "Missing candidates_texts data"}), 400

            getMostRecentExerciseRecord = DataService.get_max_exercise(cursor=cursor, tableName='exercise')
            if getMostRecentExerciseRecord:
                newExerciseID = getMostRecentExerciseRecord.exercise_id + 1
            else:
                newExerciseID = 1
                print("exercise id= newExerciseID", newExerciseID)

            exercise = Exercise(
                exercise_id=newExerciseID,
                exercise_name=str(uuid.uuid4()),  # Random GUID
                exercise_vector=[0]*512,  # 512-dimensional zero vector
                exercise_location=1,
                exercise_type=1,
                exercise_description=candidatesTexts,
                description_vector=[0]*512,  # 512-dimensional zero vector
                exercise_parent_child_type_id=1,
                create_by="gemini",
                create_dt=datetime.now(),
                modified_by="vectorize_database_records",
                modified_dt=datetime.now(),
                active_flg=True
            )

            with self.db_service.get_connection() as connection:
                exercise.exercise_id = DataService.insert_exercise_record(connection, exercise)
                print("exercise_id is :", exercise.exercise_id)
                if not exercise.exercise_id:
                    return jsonify({"error": "Failed to insert exercise record"}), 500
                vectorized_description =  AiService.call_vectorization_api(exercise.exercise_id, exercise.exercise_description)
                if vectorized_description:
                    exercise.description_vector = vectorized_description.vector
                    print("exercise.description_vector is ", exercise.description_vector)
                    print("")
                    updated = DataService.update_exercise_record_with_vector(connection, exercise)
                    if not updated:
                        return jsonify({"error": "Failed to update exercise record with vector"}), 500
            return jsonify({
                "message": "Exercise record inserted and vectorized successfully",
                "exercise_id": exercise.exercise_id,
                "Description": exercise.exercise_description
            }), 200
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
    # def insert_exercise_and_vectorize_into_database():
    #     try:
    #         data = request.get_json()
    #         candidatesTexts = data.get('candidates_texts')
    #         if candidatesTexts:
    #             exercise = Exercise(
    #                 exercise_name=None,
    #                 exercise_vector= None,
    #                 exercise_location=1,
    #                 exercise_type=1,
    #                 exercise_description="A series of stretching exercises aimed at increasing flexibility.",
    #                 description_vector=None,
    #                 exercise_parent_child_type_id=1,
    #                 create_by="gemini",
    #                 create_dt=datetime.now() 
    #             )
    #             if exercise:
    #                 connection = self.db_service.get_connection()
    #                 exercise.exercise_id =  DatabaseService.insert_exercise_record(connection, exercise)

    #                 vectorized_description = AiService.call_vectorization_api(exercise.exercise_id, exercise.exercise_description)
    #                 exercise.description_vector = vectorized_description

    #                 # Update record in database

    #                 #DataService.update_vectors_luTypeTable_record(connection=connection, typeID=lu_type.TypeID, tableName=tableName, luTypeTable=lu_type)
    #             cursor.close()
    #             connection.close()

    #             return jsonify({"exerise record inserted and vectorized successfully": exercise.exercise_id , "Description": exercise.exercise_description}), 200
    #         else:
    #             return jsonify({"error": "Missing tableName or typeIDs"}), 400
    #     except Exception as e:
    #         return jsonify({"error": str(e)}), 400
        
    

    #if __name__ == "__main__":
        # typeID = 1
        # tableName = 'lu_emotion_type'
        # connection = DatabaseService.get_connection()
        # cursor = connection.cursor()
        # lu_type = get_lu_type_table_row_by_id(cursor, typeID, tableName)
        # print(lu_type.to_dict())
        # cursor.close()
        # connection.close()
