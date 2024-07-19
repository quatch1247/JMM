import requests
from openai import OpenAI
from config import get_settings
import time

settings = get_settings()

def get_all_vectorstore_ids():
    settings = get_settings() 
    client = OpenAI(api_key=settings.openai_api_key)
    vector_stores = client.beta.vector_stores.list()
    vectorstore_ids = [store.id for store in vector_stores.data]
    print(vectorstore_ids)
    return vectorstore_ids

def delete_vector_store(vector_store_id: str):
    settings = get_settings() 
    api_key = settings.openai_api_key
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Beta": "assistants=v2"
    }
    
    response = requests.delete(f"https://api.openai.com/v1/vector_stores/{vector_store_id}", headers=headers)
    
    if response.status_code == 200:
        print(f"Successfully deleted vector store ID: {vector_store_id}")
        return response.json()
    else:
        print(f"Failed to delete vector store ID: {vector_store_id}. Status code: {response.status_code}, Response: {response.text}")
        return None

if __name__ == "__main__":
    while True:
        vectorstore_ids = get_all_vectorstore_ids()
        
        if not vectorstore_ids:
            print("No more vector stores to delete.")
            break
        
        for vector_store_id in vectorstore_ids:
            delete_vector_store(vector_store_id)

        time.sleep(1)