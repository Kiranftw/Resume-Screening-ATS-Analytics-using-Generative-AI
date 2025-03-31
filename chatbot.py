import os
import google.generativeai as genai
from ResumeAnalytics import ResumeAnalytics
from typing import Optional, Any

class chatbot(object):
    def __init__(self, modelname = "models/gemma-3-27b-it") -> None:
        object = ResumeAnalytics()
        genai.configure(api_key=object.getAPI)
        self.__MODEL: Optional[genai.GenerativeModel] = None
        
        if modelname not in object.models:
            raise ValueError(f"{modelname} not found! Please check the model name.")
        else:
            self.__MODEL: genai.GenerativeModel = genai.GenerativeModel(
                model_name=modelname,
                generation_config={},
                safety_settings={},
                tools=None,
                system_instruction=None,
            )
        
if __name__ == "__main__":
    chatbot()
