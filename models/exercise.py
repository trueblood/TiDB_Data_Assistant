class Exercise:
    def __init__(self, exercise_id, exercise_name, exercise_vector, exercise_location, exercise_type, 
                 exercise_description, description_vector, exercise_parent_child_type_id, 
                 create_by, modified_by=None, modified_dt=None, active_flg=True):
        self.exercise_id = exercise_id
        self.exercise_name = exercise_name
        self.exercise_vector = exercise_vector
        self.exercise_location = exercise_location
        self.exercise_type = exercise_type
        self.exercise_description = exercise_description
        self.description_vector = description_vector
        self.exercise_parent_child_type_id = exercise_parent_child_type_id
        self.create_by = create_by
        self.create_dt = None  # Will be set to current datetime in the database
        self.modified_by = modified_by
        self.modified_dt = modified_dt
        self.active_flg = active_flg

    def to_dict(self):
        return {
            "exercise_id": self.exercise_id,
            "exercise_name": self.exercise_name,
            "exercise_vector": self.exercise_vector,
            "exercise_location": self.exercise_location,
            "exercise_type": self.exercise_type,
            "exercise_description": self.exercise_description,
            "description_vector": self.description_vector,
            "exercise_parent_child_type_id": self.exercise_parent_child_type_id,
            "create_by": self.create_by,
            "create_dt": self.create_dt,  # Although it's set in the DB, it can be included if set in Python
            "modified_by": self.modified_by,
            "modified_dt": self.modified_dt,
            "active_flg": self.active_flg
        }
