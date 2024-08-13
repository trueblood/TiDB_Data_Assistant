import mysql.connector
from mysql.connector.cursor import MySQLCursor
from models.lutypetable import LuTypeTable
import logging
from mysql.connector import MySQLConnection, Error as MySQLError
import json
from models.exercise import Exercise
from datetime import datetime

class DataService:
    def __init__(self, db_service):
        self.db_service = db_service

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
            print("table name is ", tableName)
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
        
    def update_vectors_luTypeTable_record(connection: MySQLConnection, typeID: int, tableName: str, luTypeTable):
        print("in update_vectors_luTypeTable_record")
        if not luTypeTable:
            logging.error(f"No data provided for update in table {tableName} for TypeID {typeID}")
            return False

        cursor = connection.cursor()
        try:
            # Convert list vectors to JSON strings for storage
            typeNameVector_str = json.dumps(luTypeTable.TypeNameVector)
            descriptionVector_str = json.dumps(luTypeTable.DescriptionVector)
            # Use a parameterized query to safely insert values and prevent SQL injection
            update_query = f"""
                UPDATE {tableName}
                SET TypeNameVector = %s, DescriptionVector = %s, modified_by = %s, modified_dt = %s
                WHERE TypeID = %s
            """
            cursor.execute(update_query, (typeNameVector_str, descriptionVector_str, luTypeTable.modified_by, luTypeTable.modified_dt, luTypeTable.TypeID))
            connection.commit()  # Commit the transaction
            logging.info(f"Record successfully updated in database for TypeID {typeID} in TableName {tableName}")
            return True
        except MySQLError as err:
            connection.rollback()  # Rollback in case of any error
            logging.error(f"Failed to update TypeID {typeID} in TableName {tableName}. Error: {err}")
            return False
        finally:
            cursor.close()

    def insert_exercise_record(connection: MySQLConnection, exercise: Exercise):
        #print("in insert_exercise_record")
        #print("exercise_id is ", exercise.exercise_id)
        if not exercise:
            logging.error("No data provided for insertion")
            return None  # Return None to indicate failure

        cursor = connection.cursor()
        try:
            # Use a parameterized query to safely insert values and prevent SQL injection
            insert_query = """
                INSERT INTO exercise (
                    exercise_id,
                    exercise_name, 
                    exercise_vector, 
                    exercise_location, 
                    exercise_type, 
                    exercise_description, 
                    description_vector, 
                    exercise_parent_child_type_id, 
                    create_by, 
                    create_dt,
                    active_flg
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (
                exercise.exercise_id,
                exercise.exercise_name,
                json.dumps(exercise.exercise_vector),  # Assuming vector needs to be stored as JSON
                exercise.exercise_location,
                exercise.exercise_type,
                exercise.exercise_description,
                json.dumps(exercise.description_vector),  # Assuming vector needs to be stored as JSON
                exercise.exercise_parent_child_type_id,
                exercise.create_by,
                exercise.create_dt,
                exercise.active_flg
            ))
            connection.commit()  # Commit the transaction
            logging.info("New exercise record successfully inserted into the database with ID: %s", exercise.exercise_id)
            return exercise.exercise_id  # Return the ID of the newly created record
        except mysql.connector.Error as err:
            connection.rollback()  # Rollback in case of any error
            logging.error(f"Failed to insert new exercise record. Error: {err}")
            return None  # Return None to indicate failure
        finally:
            cursor.close()
 
    def update_exercise_record_with_vector(connection: MySQLConnection, exercise: Exercise):
        print("in update_exercise_record_with_vector")
        tableName = "exercise"
        cursor = connection.cursor()
        try:
            # Convert list vectors to JSON strings for storage
            descriptionVector_str = json.dumps(exercise.description_vector)
            # Use a parameterized query to safely insert values and prevent SQL injection
            update_query = f"""
                UPDATE {tableName}
                SET description_vector = %s, modified_by = %s, modified_dt = %s
                WHERE exercise_id = %s
            """
            cursor.execute(update_query, (descriptionVector_str, exercise.modified_by, exercise.modified_dt, exercise.exercise_id))
            connection.commit()  # Commit the transaction
            logging.info(f"Record successfully updated in database for exercise.exercise_id {exercise.exercise_id} in TableName {tableName}")
            return True
        except MySQLError as err:
            connection.rollback()  # Rollback in case of any error
            logging.error(f"Failed to update exercise.exercise_id {exercise.exercise_id} in TableName {tableName}. Error: {err}")
            return False
        finally:
            cursor.close()

    def get_count(self, cursor: MySQLCursor, tableName: str) -> int:
        try:
            cursor.execute(f"SELECT count(*) FROM {tableName}")
            count = cursor.fetchone()[0]
            return count
        except mysql.connector.Error as e:
            logging.error("Error fetching count: %s", e)
            return None
        
    def get_max_exercise(cursor: MySQLCursor, tableName: str) -> Exercise:
        try:
            print("table name is ", tableName)
            cursor.execute(f"SELECT * FROM {tableName} WHERE exercise_id = (SELECT MAX(exercise_id) FROM {tableName})")
            row = cursor.fetchone()
            if row:
                exercise = Exercise(
                    exercise_id=row[0],
                    exercise_name=row[1],
                    exercise_vector=json.loads(row[2]),  # Converting JSON string back to list
                    exercise_location=row[3],
                    exercise_type=row[4],
                    exercise_description=row[5],
                    description_vector=json.loads(row[6]),  # Converting JSON string back to list
                    exercise_parent_child_type_id=row[7],
                    create_by=row[8],
                    create_dt=row[9],
                    modified_by=row[10],
                    modified_dt=row[11],
                    active_flg=row[12]
                )
                return exercise
            else:
                logging.warning("No max records found in the exercise table.")
                return None
        except mysql.connector.Error as e:
            logging.error("Error fetching record: %s", e)
            return None
        
    def get_max_lu_type(cursor: MySQLCursor, tableName: str) -> LuTypeTable:
        try:
            print("table name is ", tableName)
            cursor.execute(f"SELECT * FROM {tableName} WHERE TypeID = (SELECT MAX(TypeID) FROM {tableName})")
            row = cursor.fetchone()
            if row:
                luTypeTable = LuTypeTable(
                    TypeID = row[0],
                    TypeName = row[1],
                    TypeNameVector = row[2],
                    Description = row[3],
                    DescriptionVector = row[4],
                    create_by = row[5],
                    create_dt = row[6],
                    modified_by = row[7],
                    modified_dt = row[8],
                    active_flg = row[9]
                )
                return luTypeTable
            else:
                logging.warning("No max records found in the exercise table.")
                return None
        except mysql.connector.Error as e:
            logging.error("Error fetching record: %s", e)
            return None
        
    def insert_lu_type_record(connection: MySQLConnection, lu_type_table: LuTypeTable, tableName: str):
        if not lu_type_table:
            logging.error("No data provided for insertion")
            return None  # Return None to indicate failure

        cursor = connection.cursor()
        try:
            # Use a parameterized query to safely insert values and prevent SQL injection
            insert_query = f"""
                INSERT INTO {tableName} (
                    TypeID,
                    TypeName, 
                    Description, 
                    create_by, 
                    create_dt, 
                    active_flg,
                    DescriptionVector,
                    TypeNameVector
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                lu_type_table.TypeID,
                lu_type_table.TypeName,
                lu_type_table.Description,
                lu_type_table.create_by,
                lu_type_table.create_dt,
                lu_type_table.active_flg,
                json.dumps(lu_type_table.DescriptionVector),
                json.dumps(lu_type_table.TypeNameVector)
            ))
            connection.commit()  # Commit the transaction
            logging.info(f"New LU type record successfully inserted into the table {tableName} with ID: {lu_type_table.TypeID}")
            return lu_type_table.TypeID  # Return the ID of the newly created record
        except mysql.connector.Error as err:
            connection.rollback()  # Rollback in case of any error
            logging.error(f"Failed to insert new LU type record. Error: {err}")
            return None  # Return None to indicate failure
        finally:
            cursor.close()
 
    def update_lu_type_table_record_with_vector(connection: MySQLConnection, lu_type_table: LuTypeTable, tableName: str):
        print("in update_lu_type_table_record_with_vector")
        cursor = connection.cursor()
        try:
            # Convert list vectors to JSON strings for storage
            descriptionVector_str = json.dumps(lu_type_table.DescriptionVector.vector)
            typeNameVector_str = json.dumps(lu_type_table.TypeNameVector.vector)
            # Use a parameterized query to safely insert values and prevent SQL injection
            update_query = f"""
                UPDATE {tableName}
                SET TypeNameVector = %s, DescriptionVector = %s, modified_by = %s, modified_dt = %s
                WHERE TypeID = %s
            """
            cursor.execute(update_query, (typeNameVector_str, descriptionVector_str, "vectorize_database_records", datetime.now(), lu_type_table.TypeID))
            connection.commit()  # Commit the transaction
            logging.info(f"Record successfully updated in database for lu_type_table.TypeID {lu_type_table.TypeID} in TableName {tableName}")
            return True
        except MySQLError as err:
            connection.rollback()  # Rollback in case of any error
            logging.error(f"Failed to update exercise.exercise_id {lu_type_table.TypeID} in TableName {tableName}. Error: {err}")
            return False
        finally:
            cursor.close()