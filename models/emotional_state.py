from datetime import datetime

class EmotionalState:
    def __init__(self, state_id, user_id, emotion_vector, location_vector, create_dt, create_by, modified_dt, modified_by, active_flg):
        self.state_id = state_id
        self.user_id = user_id
        self.emotion_vector = emotion_vector
        self.location_vector = location_vector
        self.create_dt = create_dt
        self.create_by = create_by
        self.modified_dt = modified_dt
        self.modified_by = modified_by
        self.active_flg = active_flg

    def to_dict(self):
        return {
            "state_id": self.state_id,
            "user_id": self.user_id,
            "emotion_vector": self.emotion_vector,
            "location_vector": self.location_vector,
            "create_dt": self.create_dt,  # Convert datetime back to string
            "create_by": self.create_by,
            "modified_dt": self.modified_dt,  # Convert datetime back to string
            "modified_by": self.modified_by,
            "active_flg": self.active_flg
        }