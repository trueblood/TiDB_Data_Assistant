class VectorData:
    def __init__(self, vector, id):
        self.vector = vector
        self.id = id

    def to_dict(self):
        return {
            'id': self.id,
            'vector': self.vector
        }