import requests
import logging
import os
from models.vectordata import VectorData

class AiService:
    def call_vectorization_api(id, text):
        api_url = "https://universal-sentence-encoderv4-api-it43s2nu4a-uc.a.run.app/vectorize"
        headers = {"X-API-KEY": os.getenv("UNIVERSAL-SENTENCE-ENCODER-V4-API")}
        payload = {
            "id": id,
            "sentence": text
        }
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            vector_data = response.json()
            return vector_data.get('vector'), vector_data.get('id')
        else:
            logging.error(f"Failed to vectorize text: {text} with status code {response.status_code}")
            return None, id
        

    def process_vector_data(vector_response):
        # Assuming vector_response is the tuple (vector_list, id)
        vector_data = VectorData(vector=vector_response[0], id=vector_response[1])
        return vector_data