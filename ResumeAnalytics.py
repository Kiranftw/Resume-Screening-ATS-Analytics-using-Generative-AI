import google.generativeai as genai
import os
from typing import Any
from DataProcessing import DocumentProcessing
from dotenv import load_dotenv, find_dotenv
from pydantic import BaseModel
from functools import wraps
from typing import Dict, List, Optional, Any
from IPython.display import display, Markdown
import json
from json import JSONDecodeError

class ResumeAnalytics(DocumentProcessing):
    def __init__(self, modelname: str ='models/gemini-2.0-flash') -> None:
        load_dotenv(find_dotenv())
        self.__API = os.getenv("GEMINIAPI")
        if not self.__API:
            raise ValueError("API key not found. Please set the GEMINIAPI environment variable.")
        
        genai.configure(api_key=self.__API)
        self.models: list[str] = list(model.name for model in genai.list_models())
        
        if modelname not in self.models:
            raise ValueError(f"{modelname} not found! Please check the model name.")
        self.__MODEL: genai.GenerativeModel = genai.GenerativeModel(
            model_name=modelname,
            generation_config ={
                "response_mime_type":"application/json"
            },
            safety_settings={},
            tools=None,
            system_instruction=None,
        )
        JSONFOLDER = "./JSON"
        if not os.path.exists(JSONFOLDER):
            os.makedirs(JSONFOLDER)
        self.JSONFOLDER = JSONFOLDER
        
    @property
    def getAPI(self) -> Any:
        return self.__API
            
    @staticmethod
    def ExceptionHandelling(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
        return wrapper
    
    def getResponse(self, prompt: str) -> str:
        response = self.__MODEL.generate_content(prompt)
        return response.text
    
    def resumeanalytics(self, resumepath: str, jobdescription: str, filename: str = "prompt.txt") -> Optional[Dict[str, Any]]:
        resume = self.FileProcessing(resumepath)
        jobdescription = self.FileProcessing(jobdescription)

        if not os.path.exists(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")
        with open(filename, "r", encoding="utf-8") as file:
            prompt = file.read()
        Fprompt = f"{prompt}\nResume: {resume}\nJob Description: {jobdescription}"
        try:
            OutputFile = f"{self.JSONFOLDER}/{os.path.basename(resumepath)}.json"
            response = self.getResponse(Fprompt)
            print(response)
            responseJSON = json.loads(response)
            with open(OutputFile, "w", encoding="utf-8") as file:
                json.dump(responseJSON, file, indent=4, ensure_ascii=False)

            print(f"JSON file saved: {OutputFile}")
            return responseJSON

        except (JSONDecodeError, Exception) as e:
            print(f"Error in resumeanalytics: {e}")
            return None
    
    def main(self) -> None:
        resume = r"/home/kiranftw/Resume-Screening-ATS-Analytics-using-Generative-AI/testfiles/ResumePDF.pdf"
        jd = r"testfiles/jobdescription.txt"
        self.resumeanalytics(resume, jd)
        
if __name__ == "__main__":
    ResumeAnalytics().main()