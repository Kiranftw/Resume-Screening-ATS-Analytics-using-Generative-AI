from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyMuPDFLoader, TextLoader, Docx2txtLoader
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.chains import ConversationChain
from IPython.display import Markdown, display
from IPython.display import display, Markdown
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv, find_dotenv
from docx import Document
import pytesseract
from typing import List, Dict
import pytesseract
import os
from functools import wraps
from newspaper import Article
import re
import base64
import json
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from json import JSONDecodeError
import datetime
import logging
pytesseract.pytesseract.tesseract_cmd = r"/usr/bin/tesseract"

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
   
class ResumeAnalytics(object):
    def __init__(self, modelname: str = 'models/gemini-2.0-flash', chatmodel = "models/gemma-3-27b-it") ->None:
        load_dotenv(find_dotenv())
        self.__API = os.getenv("GOOGLE_API_KEY")
        if not self.__API:
            raise ValueError("API key not found. Please set the GEMINIAPI environment variable.")
        genai.configure(api_key = self.__API)
        self.outputsFOLDER = "outputs"
        self.model: genai.GenerativeModel = None
        self.chatmodel: ChatGoogleGenerativeAI = None
        ##Initlizing the google AI models for text generations and chatbot
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
        if self.model is None or self.chatmodel is None:
            raise ValueError(f"Error in initlizing the models")
        
        #Initlizing the memory & conversation chain
        self.memory = ConversationSummaryBufferMemory(
            llm = self.chatmodel,
            max_tokens = 100000,
            return_messages = True,
            memory_key = "history"
        )
        self.conversation = ConversationChain(
            llm = self.chatmodel,
            memory = self.memory,
            verbose = True
        )
    
    @ExceptionHandeler 
    @property
    def getAPI(self) -> Any:
        return self.__API
    
    @ExceptionHandeler
    @property
    def getMODEL(self) -> genai.GenerativeModel:
        return self.model
    
    @ExceptionHandeler
    def getResponse(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        if hasattr(response, 'text'):
            return response.text
        else:
            raise ValueError("Invalid response format from the model.")
    
    @ExceptionHandeler
    def datacleaning(self, textfile: str) -> str:
        if not textfile:
            return ""
        
        text = textfile
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub(r'[^\x00-\x7F]', ' ', text)
        text = re.sub(r'[-–]', ' ', text) 
        text = re.sub(r'(\w)[|](\w)', r'\1, \2', text)
        
        text = text.replace(" - ", "\n- ").replace(":", ":\n")  

        return text.strip()
   
    def documentParser(self, filepath: str) -> Optional[str]:
        if not filepath:
            raise ValueError("No input provided.")

        if os.path.exists(filepath):
            ext = os.path.splitext(filepath)[1].lower()

            if ext in [".pdf", ".docx", ".txt"]:
                if ext == ".pdf":
                    loader = PyMuPDFLoader(filepath)
                elif ext == ".docx":
                    loader = Docx2txtLoader(filepath)
                elif ext == ".txt":
                    loader = TextLoader(filepath)
                else:
                    print("Unsupported document format.")
                    return None

                document = loader.load()
                filecontent: str = " ".join([doc.page_content for doc in document])
                return self.datacleaning(filecontent.strip()) if filecontent else None

            elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
                image = Image.open(filepath)
                if image.mode != "RGB":
                    image = image.convert("RGB")
                filecontent: str = pytesseract.image_to_string(image)
                if not filecontent.strip():
                    raise ValueError("No text found in the image.")
                return self.datacleaning(filecontent)

            else:
                print("Invalid file format.")
                return None
        else:
            return self.datacleaning(filepath)

    @ExceptionHandeler
    def resumeanalytics(self, resumepath: str, jobdescription: str, filename: str = "prompt.txt") -> Optional[Dict[str, Any]]:
        resume = self.documentParser(resumepath)
        JobDescription = self.documentParser(jobdescription)

        if not os.path.exists(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")
        with open(filename, "r", encoding="utf-8") as file:
            prompt = file.read()
        Fprompt = f"{prompt}\nResume: {resume}\nJob Description: {JobDescription}"
        if not os.path.exists(self.outputsFOLDER):
            os.makedirs(self.outputsFOLDER, exist_ok=True)
        filename = os.path.split(os.path.basename(resumepath))[1]
        savePath = f"{os.path.join(self.outputsFOLDER,filename)}.json"
        try:
            response = self.getResponse(Fprompt)
            responseJSON = json.loads(response)
            with open(savePath, "w", encoding="utf-8") as file:
                json.dump(responseJSON, file, indent=4, ensure_ascii=False)
            print(f"JSON file saved: {savePath}")
            
            return responseJSON
        except JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Error in resumeanalytics: {e}")
            return None
            
    @ExceptionHandeler   
    def chatbot(self,Document: str, Query: str = None) -> str:
        data: Optional[str] = self.documentParser(Document)
        if not data or data.strip() == "":
            print("[Bot]: Unable to extract any meaningful content from the file.")
            return "Unable to extract any meaningful content from the file. Please check the document and try again."
        
        self.memory.chat_memory.add_user_message(data)
        self.memory.chat_memory.add_ai_message("Document Loaded Successfully")
        if Query:
            print("\n[Bot]: ", end="", flush=True)
            response: str = ""
            messages = self.memory.chat_memory.messages.copy()
            messages.append(HumanMessage(content = Query))
            for chunk in self.chatmodel.stream(messages):
                if chunk.content:
                    print(chunk.content, end = "", flush = True)
                    response += chunk.content
            print()
            self.memory.chat_memory.add_user_message(Query)
            self.memory.chat_memory.add_ai_message(response)
            Markdown(response)
            return response
        else:
            return "Document Loaded Successfully"
    
    @ExceptionHandeler
    def CoverLetterGeneration(self,fullname: str, position: str, companyname: str, relvantExperience: str):
        prompt = ChatPromptTemplate.from_template(
            """
            Write a professional cover letter for {fullname}, who is applying for the position of {position} at {companyname}.
            The candidate has relevant experience in {relevant_experience}. The tone should be formal, enthusiastic, and concise.
            Today's date is {date}.
            """
        )
        formatted_prompt = prompt.format(
            fullname=fullname,
            position=position,
            companyname=companyname,
            relevant_experience=relvantExperience,
            date=datetime.date.today().strftime("%B %d, %Y")
        )
        response = str(self.chatmodel.invoke(formatted_prompt))
        outputpath = os.path.join(self.outputsFOLDER, "coverletter.txt")
        with open(outputpath, "w", encoding = "utf-8") as file:
            file.write(response)
        print(f"file successfully stored with name coverletter.txt")
        Markdown(response)
        return response