class LuTypeTable:
    def __init__(self, TypeID, TypeName, TypeNameVector, Description, DescriptionVector, create_by, create_dt, modified_by, modified_dt, active_flg):
        self.TypeID = TypeID
        self.TypeName = TypeName
        self.TypeNameVector = TypeNameVector
        self.Description = Description
        self.DescriptionVector = DescriptionVector
        self.create_by = create_by
        self.create_dt = create_dt
        self.modified_by = modified_by
        self.modified_dt = modified_dt
        self.active_flg = active_flg

    def to_dict(self):
        return {
            'TypeID': self.TypeID,
            'TypeName': self.TypeName,
            'TypeNameVector': self.TypeNameVector,
            'Description': self.Description,
            'DescriptionVector': self.DescriptionVector,
            'create_by': self.create_by,
            'create_dt': self.create_dt,
            'modified_by': self.modified_by,
            'modified_dt': self.modified_dt,
            'active_flg': self.active_flg
        }