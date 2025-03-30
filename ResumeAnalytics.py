import google.generativeai as genai
import os
from typing import Any
from DataProcessing import DocumentProcessing
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from functools import wraps
from typing import Dict, List, Optional
import time

class ResumeAnalytics(DocumentProcessing):
    def __init__(self, modelname: str ='models/gemini-2.0-flash') -> None:
        load_dotenv(find_dotenv())
        self.__API = os.getenv("GEMINIAPI")
        if not self.__API:
            raise ValueError("API key not found. Please set the GEMINIAPI environment variable.")
        
        genai.configure(api_key=self.__API)
        models: list[str] = list(model.name for model in genai.list_models())
        
        if modelname not in models:
            raise ValueError(f"{modelname} not found! Please check the model name.")
        self.__MODEL = genai.GenerativeModel(
            model_name=modelname,
            generation_config={},
            safety_settings={},
            tools=None,
            system_instruction=None,
        )
        print(self.__MODEL)
            
    @staticmethod
    def ExceptionHandelling(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
        return wrapper
    
    @ExceptionHandelling
    def makeRequest(self, promptfile: str) -> Any:
        with open(promptfile, "r", encoding = "utf-8") as file:
            promptext = file.read()
        template = PromptTemplate(
            template = "Analyze the following {prompt}"
            input_variables = ["prompt"]
        )
        return template.format(prompt = promptext)

if __name__ == "__main__":
    object = ResumeAnalytics()
