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
from models.emotional_state import EmotionalState as EmotionalState

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
                exercise_vector=[0]*384,  # 384-dimensional zero vector
                exercise_location=1,
                exercise_type=28,
                exercise_description=candidatesTexts,
                description_vector=[0]*384,  # 384-dimensional zero vector
                exercise_parent_child_type_id=1,
                create_by="gemini",
                create_dt=datetime.now(),
                modified_by="vectorize_database_records",
                modified_dt=datetime.now(),
                active_flg=True
            )

            with self.db_service.get_connection() as connection:
                exercise.exercise_id = DataService.insert_exercise_record(connection, exercise)
            #    print("exercise_id is :", exercise.exercise_id)
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

    def vectorize_emotion_image_and_location(self):
        try:
            print("in vectorize_emotion_image")
            data = request.get_json()
            location = data.get('location')
            print("location is ", location)
            current_id = data.get('ID')
            connection = self.db_service.get_connection()
            cursor = connection.cursor()

            # Vectorize Location
            print('before vectorized_location_name')
            vectorized_location_name = AiService.call_vectorization_api(current_id, location)

            # call this functo get to max record
            tableName = "user_emotional_state"
            userState = DataService.get_max_user_state(cursor, tableName)
            print("user state id is ", userState.to_dict())
            # save that to the databse
            emotionalState = EmotionalState(
                state_id = int(current_id) + 1,
                user_id = 1,
                emotion_vector = [0]*384,
                location_vector = [0]*384,
                create_dt = datetime.now(),
                create_by = "tidb_data_assistant",
                modified_dt = None,
                modified_by = None,
                active_flg = True
            )
            inserted_record_id = DataService.insert_emotional_state_record(connection, emotionalState)
            print("inserted_record_id is ", inserted_record_id)
            # now we do the api call to call the RL model to wake up
            if vectorized_location_name is not None:
                return jsonify({
                    "message": "emotion image vectorized and inserted into database successfully",
                    "vectorized_location_name": vectorized_location_name.vector,
                    "id": vectorized_location_name.id  # Assuming id is a field in VectorData
                }), 200
            else:
                return jsonify({"error": "Vectorization failed"}), 400

        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def insert_lu_type_table_and_vectorize_into_database(self):
        print("in insert_lu_type_table_and_vectorize_into_database")
        try:
            data = request.get_json()
            typeName = data.get('typeName')
            typeDescription = data.get('typeDescription')
            tableName = data.get('tableName')
            createdBy = data.get('createBy')
            connection = self.db_service.get_connection()
            cursor = connection.cursor()

            # print("typename is ", typeName)
            # print("typeDescription is ", typeDescription)
            # print("tableName is ", tableName)
            # print("createdBy is ", createdBy)


            if not tableName:
                return jsonify({"error": "Missing tableName data"}), 400

            getMostRecentLuTypeRecord = DataService.get_max_lu_type(cursor=cursor, tableName=tableName)

            if getMostRecentLuTypeRecord:
                newTypeID = getMostRecentLuTypeRecord.TypeID + 1
              #  print("newTypeID", newTypeID)
            else:
                newTypeID = 1

          #  print("newTypeID", newTypeID)

            luTypeTable = LuTypeTable(
                TypeID = newTypeID,
                TypeName = typeName,
                TypeNameVector = [0]*384,  # 384-dimensional zero vector
                Description = typeDescription,
                DescriptionVector = [0]*384,  # 384-dimensional zero vector
                create_by = createdBy,
                create_dt = datetime.now(),
                modified_by="vectorize_database_records",
                modified_dt=datetime.now(),
                active_flg = True
            )

            with self.db_service.get_connection() as connection:
                luTypeTable.TypeID = DataService.insert_lu_type_record(connection, luTypeTable, tableName)
             #   print("typeid is :", luTypeTable.TypeID)
                if not luTypeTable.TypeID:
                    return jsonify({"error": "Failed to insert luTypeTable record"}), 500
                
               # print("ready to vectorize data")
                vectorized_description = AiService.call_vectorization_api(luTypeTable.TypeID, luTypeTable.Description)
                vectorized_type_name = AiService.call_vectorization_api(luTypeTable.TypeID, luTypeTable.TypeName)

                if vectorized_description and vectorized_type_name:
                    luTypeTable.DescriptionVector = vectorized_description
                    luTypeTable.TypeNameVector = vectorized_type_name
                  #  print("luTypeTable.DescriptionVector is ", luTypeTable.DescriptionVector.vector)
                 #   print("luTypeTable.TypeNameVector is ", luTypeTable.TypeNameVector.vector)
                    updated = DataService.update_lu_type_table_record_with_vector(connection, luTypeTable, tableName)
                    if not updated:
                        return jsonify({"error": "Failed to update luTypeTable record with vectors"}), 500
            return jsonify({
                "message": "luTypeTable record inserted and vectorized successfully",
                "TypeID": luTypeTable.TypeID,
                "TypeName": luTypeTable.TypeName,
                "Description": luTypeTable.Description,
            }), 200
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
            return jsonify({"error": str(e)}), 500
        
    def insert_emotion_cnn_ai_training(self, data):
        connection = self.db_service.get_connection()
        cursor = connection.cursor()
        try:
            sql = """
            INSERT INTO emotion_cnn_ai_training (
                start_time, end_time, data_split_ratio, training_accuracy, validation_accuracy, test_accuracy, 
                model_architecture, model_name, feature_set, training_status, created_by, active_flg
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['start_time'], data['end_time'], data['data_split_ratio'], data['training_accuracy'],
                data['validation_accuracy'], data['test_accuracy'], data['model_architecture'], data['model_name'],
                data['feature_set'], data['training_status'], data['created_by'], data['active_flg']
            ))
            connection.commit()
            return jsonify({"message": "Record successfully inserted into emotion_cnn_ai_training"}), 200
        except mysql.connector.Error as e:
            logging.error("Error inserting into emotion_cnn_ai_training: %s", e)
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            connection.close()

    def insert_encoding_model_training(self, data):
        connection = self.db_service.get_connection()
        cursor = connection.cursor()
        try:
            sql = """
            INSERT INTO encoding_model_training (
                start_time, end_time, data_split_ratio, training_accuracy, validation_accuracy, test_accuracy, 
                model_architecture, model_name, feature_set, training_status, created_by, active_flg
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['start_time'], data['end_time'], data['data_split_ratio'], data['training_accuracy'],
                data['validation_accuracy'], data['test_accuracy'], data['model_architecture'], data['model_name'],
                data['feature_set'], data['training_status'], data['created_by'], data['active_flg']
            ))
            connection.commit()
            return jsonify({"message": "Record successfully inserted into encoding_model_training"}), 200
        except mysql.connector.Error as e:
            logging.error("Error inserting into encoding_model_training: %s", e)
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            connection.close()

    def insert_rl_training_info(self, data):
        connection = self.db_service.get_connection()
        cursor = connection.cursor()
        try:
            sql = """
            INSERT INTO rl_training_info (
                start_time, end_time, total_episodes, total_steps, average_reward, epsilon, learning_rate, 
                environment_settings, model_architecture, model_name, training_status, created_by, active_flg
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                data['start_time'], data['end_time'], data['total_episodes'], data['total_steps'], data['average_reward'],
                data['epsilon'], data['learning_rate'], data['environment_settings'], data['model_architecture'], 
                data['model_name'], data['training_status'], data['created_by'], data['active_flg']
            ))
            connection.commit()
            return jsonify({"message": "Record successfully inserted into rl_training_info"}), 200
        except mysql.connector.Error as e:
            logging.error("Error inserting into rl_training_info: %s", e)
            return jsonify({"error": str(e)}), 400
        finally:
            cursor.close()
            connection.close()

    def get_rl_training_info(self):
        connection = self.db_service.get_connection()
        cursor = connection.cursor()
        try:
            sql = "SELECT * FROM rl_training_info"
            cursor.execute(sql)
            records = cursor.fetchall()
            # Assume that records contain columns with names corresponding to your table's schema
            # Here, we transform raw database records into a list of dictionaries
            records_list = [{
                "training_id": record[0],
                "start_time": str(record[1]),  # Converting datetime to string for JSON compatibility
                "end_time": str(record[2]),
                "total_episodes": record[3],
                "total_steps": record[4],
                "average_reward": record[5],
                "epsilon": record[6],
                "learning_rate": record[7],
                "environment_settings": record[8],
                "model_architecture": record[9],
                "model_name": record[10],
                "training_status": record[11],
                "ram_usage": record[12],
                "cpu_usage": record[13],
                "num_features": record[14],
                "created_by": record[15],
                "create_dt": str(record[16]),
                "modified_by": record[17],
                "modified_dt": str(record[18]),
                "active_flg": record[19]
            } for record in records]

            return jsonify({
                "message": "rl_training_info records fetched successfully",
                "data": records_list
            }), 200
        except mysql.connector.Error as e:
            logging.error("Error fetching from rl_training_info: %s", e)
            return jsonify({
                "message": "Error fetching from rl_training_info",
                "error": str(e)
            }), 400
        finally:
            cursor.close()
            connection.close()


    def get_feedback_rating_options(self):
        connection = self.db_service.get_connection()
        cursor = connection.cursor()
        try:
            sql = "SELECT * FROM feedback_rating_options WHERE active_flg = TRUE"
            cursor.execute(sql)
            records = cursor.fetchall()
            options_list = [{
                "rating_id": row[0],
                "rating_label": row[1],
                "rating_description": row[2],
                "active_flg": row[3]
            } for row in records]

            return jsonify({
                "message": "Feedback rating options fetched successfully",
                "data": options_list
            }), 200
        except mysql.connector.Error as e:
            logging.error("Error fetching feedback rating options: %s", e)
            return jsonify({
                "message": "Error fetching feedback rating options",
                "error": str(e)
            }), 400
        finally:
            cursor.close()
            connection.close()

    def get_feedback_by_user(self, user_id):
        connection = self.db_service.get_connection()
        cursor = connection.cursor()
        try:
            sql = """
            SELECT user_exercise_feedback_id, user_id, exercise_id, emotion_id, feedback, 
                   create_by, create_dt, modified_by, modified_dt, active_flg 
            FROM user_exercise_feedback 
            WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
            records = cursor.fetchall()
            feedback_list = [{
                "user_exercise_feedback_id": row[0],
                "user_id": row[1],
                "exercise_id": row[2],
                "emotion_id": row[3],
                "feedback": row[4],
                "create_by": row[5],
                "create_dt": str(row[6]),  # Converting datetime to string for JSON compatibility
                "modified_by": row[7],
                "modified_dt": str(row[8]),
                "active_flg": row[9]
            } for row in records]
            
            return jsonify({
                "message": "Feedback records fetched successfully for user",
                "data": feedback_list
            }), 200
        except mysql.connector.Error as e:
            logging.error(f"Error fetching feedback by user_id {user_id}: {e}")
            return jsonify({
                "message": "Error fetching feedback by user_id",
                "error": str(e)
            }), 400
        finally:
            cursor.close()
            connection.close()  
