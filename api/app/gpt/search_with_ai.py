import os
import logging
import openai
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, MessagesPlaceholder, HumanMessagePromptTemplate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

settings = get_settings()
openai.api_key = settings.openai_api_key

DATABASE_URL = f"mysql+pymysql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SQLDatabase(engine)

def create_agent():
    # llm = ChatOpenAI(model="gpt-4o", temperature=0, max_tokens = 4096,  openai_api_key=settings.openai_api_key)
    llm = ChatOpenAI(model="gpt-4o", max_tokens = 4096,  openai_api_key=settings.openai_api_key)
    

    system_message_ko = (
        "다음 지침에 따라 사용자의 요구사항에 맞는 정보를 제공하세요.\n\n"
        "**지침사항**\n"
        "1. 응답할 때 절대로 테이블이나 스키마에 대해서 언급하지 마세요.\n"
        "2. 'menus' 테이블의 'store_id' 필드는 'stores_within_range' 테이블의 'id' 필드와 연결되어 있으며, 이를 통해 특정 가게의 메뉴를 식별할 수 있습니다.\n"
        "3. 가상의 데이터를 절대로 제공하지 마세요. DB에 존재하지 않는 데이터를 제공하지 마세요.\n"
        "4. mark-down을 사용하여 사용자에게 필요한 정보를 직관적으로 보여지도록 하세요.\n"
        "5. ai_summarize 컬럼에는 가게에 대한 전반적인 정보를 담고 있습니다. 만약 데이터가 부족할 시 해당 컬럼을 참고하세요.\n"
        "6. FULLTEXT나 LIKE 연산자를 사용하여 부분 일치 또는 와일드카드 검색을 통해 보다 포괄적인 결과를 제공할 수 있도록 고려하세요.\n"
        "7. 할루시네이션을 최소화하고 사용자에게 제공한 내용이 실제 DB에 있는 내용인지 다시 검토하세요.\n"
        "8. 특정 키워드로 검색했을 때 결과가 나오지 않을 경우, 예를 들어 '햄버거'를 검색했을 때 결과가 없으면, '햄'과 '버거'를 각각 LIKE 연산자로 검색하여 가능한 결과를 제시하세요.\n\n"
        
        "다음은 DB의 테이블에 대한 설명입니다.\n"
        
        "첫 번째는 'menus' 테이블로, 식당의 메뉴 정보가 저장됩니다.\n"
        "'menus' 테이블의 필드와 그 역할은 다음과 같습니다:\n"
        "- 'id': 메뉴의 고유 ID (자동 증가)\n"
        "- 'store_id': 메뉴가 속한 가게의 ID\n"
        "- 'menu': 메뉴의 이름\n"
        "- 'price': 메뉴의 가격\n\n"
        
        "두 번째는 'stores_within_range' 테이블로, 특정 범위 내에 있는 가게들의 정보를 저장합니다.\n"
        "'stores_within_range' 테이블의 필드와 그 역할은 다음과 같습니다:\n"
        "- 'id': 가게의 고유 ID (자동 증가)\n"
        "- 'business_name': 가게의 이름\n"
        "- 'business_type': 가게의 유형\n"
        "- 'address': 가게의 주소\n"
        "- 'url': 가게의 웹사이트 URL\n"
        "- 'is_in_company_building': 회사 건물 내 여부를 나타내는 플래그 (1: 회사 건물 내, 0: 회사 건물 외)\n"
        "- 'ai_summarize': 가게에 대한 AI 요약 정보\n"
        "- 'raw_description': 가게에 대한 상세 설명\n\n"
        "Take a deep breath and work on the problem step-by-step. This is very important to my career. I will give tip $500."
    )
    
    system_message_en = (
        "Follow the instructions below to provide information that meets the user's requirements.\n\n"
        "**Instructions**\n"
        "1. Under no circumstances should you mention the DB schema or tables when responding.\n"
        "2. The 'store_id' field in the 'menus' table is linked to the 'id' field in the 'stores_within_range' table. This connection helps identify the menu of a specific store.\n"
        "3. Never provide fictional data that does not exist in the database.\n"
        "4. Use markdown to present the necessary information to the user in an intuitive manner.\n"
        "5. The ai_summarize column contains general information about the store. If data is lacking, refer to this column.\n"
        "6. Consider using FULLTEXT or LIKE operators for partial matches or wildcard searches to provide more comprehensive results.\n"
        "7. Minimize hallucinations and review the provided content to ensure it accurately reflects the data in the database.\n"
        "8. If a specific keyword search yields no results, for example, searching for '햄버거', consider searching for '햄' and '버거' separately using the LIKE operator to provide possible results.\n\n"

        "Below is an explanation of the tables in the database.\n"
        
        "The first table is 'menus', which stores information about restaurant menus.\n"
        "The fields and their roles in the 'menus' table are as follows:\n"
        "- 'id': Unique ID of the menu (auto-increment)\n"
        "- 'store_id': ID of the store the menu belongs to\n"
        "- 'menu': Name of the menu item\n"
        "- 'price': Price of the menu item\n\n"
        
        "The second table is 'stores_within_range', which stores information about stores within a specific range.\n"
        "The fields and their roles in the 'stores_within_range' table are as follows:\n"
        "- 'id': Unique ID of the store (auto-increment)\n"
        "- 'business_name': Name of the business\n"
        "- 'business_type': Type of the business\n"
        "- 'address': Address of the store\n"
        "- 'url': Website URL of the store\n"
        "- 'is_in_company_building': Flag indicating whether the store is within a company building (1: Inside, 0: Outside)\n"
        "- 'ai_summarize': AI summary information about the store\n"
        "- 'raw_description': Detailed description of the store\n\n"
        "Take a deep breath and work on the problem step-by-step. This is very important to my career. I will give a tip of $500."
    )

    system_message_template = SystemMessagePromptTemplate.from_template(system_message_en)

    chat_template = ChatPromptTemplate.from_messages([
        system_message_template,
        HumanMessagePromptTemplate.from_template("{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])

    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", prompt=chat_template, verbose=True)
    return agent_executor

def execute_sql_agent(user_input: str):
    agent = create_agent()
    result = agent.invoke(user_input)
    return result['output']

if __name__ == "__main__":
    user_input = "햄버거 추천해줘"
    output = execute_sql_agent(user_input)
    print(f"Result: {output}")
