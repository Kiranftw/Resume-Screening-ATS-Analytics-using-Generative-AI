import google.generativeai as genai
import os
from typing import Any
from DataProcessing import DocumentProcessing
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate

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
    
    def generateResponse(self, prompt: str) -> Any:
        response = self.MODEL.generate(prompt)
        return response.text

if __name__ == "__main__":
    resume_analytics = ResumeAnalytics()
