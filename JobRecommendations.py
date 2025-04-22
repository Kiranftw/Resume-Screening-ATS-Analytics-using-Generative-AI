import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import os
from dotenv import load_dotenv, find_dotenv
from ResumeAnalytics import ResumeAnalytics
from functools import wraps
import logging
from bs4 import BeautifulSoup
import requests
import transformers
import json
import re
from typing import List, Dict, Any, Optional
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@staticmethod
def ExceptionHandeler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as E:
            print(f"An error occurred: {E}")
    return wrapper

class JobRecommendation(object):
    def __init__(self, modelname: str = 'models/gemini-2.0-flash', chatmodel = "models/gemma-3-27b-it") ->None:
        load_dotenv(find_dotenv())
        self.__API = os.getenv("GOOGLE_API_KEY")
        if not self.__API:
            raise ValueError("API key not found. Please set the GEMINIAPI environment variable.")
        genai.configure(api_key = self.__API)
        self.outputsFOLDER = "outputs"
        self.model: genai.GenerativeModel = None
        self.chatmodel: ChatGoogleGenerativeAI = None
        for model in genai.list_models():
            if model.name == modelname:
                self.model: genai.GenerativeModel = genai.GenerativeModel(
                    model_name=modelname,
                    generation_config ={"response_mime_type":"application/json"},
                    safety_settings={},
                    tools = None,
                    system_instruction = "You are an expert resume screening assistant. Always return JSON. Be concise."
                )
            elif model.name == chatmodel:
                self.chatmodel: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
                    model = chatmodel,
                    temperature = 0.7,
                )
                break
        logger.info("CHAT/TEXT GENERATION MODELS initialized successfully.")
        if self.model is None or self.chatmodel is None:
            raise ValueError(f"Error in initlizing the models") 
        self.LINKDIN_URL = """
"""
    
    def getJObDescription(s)
   
if __name__ == "__main__":
    JobRecommendation()