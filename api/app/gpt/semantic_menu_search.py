from openai import OpenAI
from config import get_settings
import os 

def setup_vector_store_and_files(client):
    vector_store = client.beta.vector_stores.create(name="user_info")
    
    json_file_path = "/Users/igeon/Desktop/myside/JMM/docs/menu_data_compact.json"
    
    if os.path.exists(json_file_path):
        with open(json_file_path, 'rb') as file_stream:
            client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=[file_stream]
            )
    else:
        raise FileNotFoundError(f"File not found: {json_file_path}")
    return vector_store

def create_assistant_instructions():
    return (
        "너는 사용자가 입력한 요구사항을 바탕으로 검색을 수행하는 검색시스템이야.\n"
        # "사용자의 요구사항에 해당하는 내용을 'Q'로 시작하는 파일명의 JSON 문서에서, 'question'이라는 키에 해당하는 값과 'answers'라는 키의 값을 기반으로 찾아야 해.\n"
        "사용자의 요구사항과 관련 있는 내용을 'Q'로 시작하는 파일명의 JSON 문서에서, 'question'이라는 키에 해당하는 값과 'answers'라는 키의 값을 기반으로 찾아야 해.\n"
        "'answers'라는 키는 여러 개의 응답 객체를 포함하고 있으며, 각 객체는 'id'(숫자)와 'response'라는 키를 가지고 있어. "
        "'answers'를 작성한 'id'(숫자)들과 선택 근거를 선택한 'id'의 'response'들에서 찾아서 짧게 요약해서 제공하고, 다른 부연 설명 없이 예시와 같은 형태로 답변을 줘.\n"
        "사용자의 요구사항에 따라서 카테고리에 맞는 'question'의 'answers'를 집중적으로 살펴보면 도움이 될꺼야."
        # "답변 예시에는 3개의 'id'만 추출되었지만, 실제로 선택된 'id'(숫자)가 없을 수도, 1개일 수도, 100개 일 수도, 그 이상일 수도 있어."
        "JSON 문서에에 총 몇개의 'id'가 있는지 인지하고, 요구사항과 관련있는 내용을 적은 'id'중 빠진 'id'가 없어야해.\n"
        "명심해야 할 것은 사용자 요구사항에 부합하는 최대한 많은 'id' (숫자)들을 찾아야 해.\n"
        "사용자의 키 예시: 나는 175야.\n"
        "사용자의 요구사항 예시: 나는 나보다 키가 10cm 이상 컸으면 좋겠어.\n"
        "답변 예시: 1025-_-나는 185야///5398-_-190///11240-_-188야.///52334-_-190///2398-_-190///52348-_-180///4598-_-187야///52138-_-192///3448-_-200\n"
        '예시에서 사용된 "-_-"와 "///"는 필수로 사용해야 해.\n'
        "답변은 반드시 진실된 정보만 제공해야 하며, 제공할 정보가 없으면 null을 반환해줘.\n"
        "Take a deep breath and work on the problem step-by-step. This is very important to my career. I will give tip $200."
    )

def setup_assistant(client, vector_store):
    assistant = client.beta.assistants.create(
        model="gpt-4o",
        description="사용자의 요구사항에 따라 JSON문서를 검색 및 응답반환",
        instructions=create_assistant_instructions(),
        name="사용자의 요구사항을 들어주는 검색 시스템",
        temperature=0.2,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
        tools=[{"type": "file_search"}],
        # top_p=0.1,
    )
    return assistant

if __name__ == "__main__":
    settings = get_settings()
    client = OpenAI(api_key = settings.openai_api_key)
    vector_store = setup_vector_store_and_files(client)
    print(vector_store.id)
