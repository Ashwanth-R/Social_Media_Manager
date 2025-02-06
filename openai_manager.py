import os
from dotenv import load_dotenv
load_dotenv()
# from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

class OpenAIManager:
    def __init__(self, model_name):
        self.model = model_name
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found. Please check your .env file.")
        # self.groq_api_key = os.getenv('GROQ_API_KEY')
        # if not self.groq_api_key:
        #     raise ValueError("GROQ_API_KEY not found. Please check your .env file.")

    def create_llm(self, temperature=0.4):
        return ChatOpenAI(
            temperature=temperature,
            api_key=self.openai_api_key,
            model=self.model
        )
