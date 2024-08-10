import uuid
def generate_guid():
    return str(uuid.uuid4())




if __name__ == "__main__":
    print("Generated GUID:")
    print(generate_guid())


