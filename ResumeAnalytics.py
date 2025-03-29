import google.generativeai as genai
import os
from typing import Any
from DataProcessing import DocumentProcessing
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from functools import wraps
class Response(BaseModel):
    pass

class ResumeAnalytics(DocumentProcessing):
    def __init__(self, model = "models/gemini-2.0-flash") -> None:
        load_dotenv(find_dotenv())
        self.__API = os.getenv("GEMINIAPI")
        genai.configure(api_key=self.__API)
        # for model in genai.list_models():
        #     print(model.name)
        self.MODEL: genai.GenerativeModel = genai.GenerativeModel(
            model_name=model,
            generation_config={},
            safety_settings={},
            tools=None,
            system_instruction=None,
        )
    
    @staticmethod
    def ExceptionHandelling(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
        return wrapper
    
    @ExceptionHandelling
    @classmethod
    def generateResponse(self, prompt: str) -> str:
        response: str = self.MODEL.generate_content(prompt)
        return response.text

if __name__ == "__main__":
    resume_analytics = ResumeAnalytics()
    data = resume_analytics.generateResponse("What is the name of the person in the resume?")
    print(type(data))