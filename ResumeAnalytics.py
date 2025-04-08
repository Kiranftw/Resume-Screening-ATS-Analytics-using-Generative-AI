import google.generativeai as genai
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.chains import ConversationChain
from IPython.display import display, Markdown
from typing import Any
from DataProcessing import DocumentProcessing
from dotenv import load_dotenv, find_dotenv
from functools import wraps
from typing import Dict, List, Optional, Any
import json
import os
from json import JSONDecodeError

class ResumeAnalytics(DocumentProcessing):
    def __init__(self, modelname: str ='models/gemini-2.0-flash') -> None:
        load_dotenv(find_dotenv())
        self.__API = os.getenv("GOOGLE_API_KEY")
        if not self.__API:
            raise ValueError("API key not found. Please set the GEMINIAPI environment variable.")
        
        genai.configure(api_key=self.__API)
        self.models: list[str] = list(model.name for model in genai.list_models())
        
        if modelname not in self.models:
            raise ValueError(f"{modelname} not found! Please check the model name.")
        
        self.__MODEL: genai.GenerativeModel = genai.GenerativeModel(
            model_name=modelname,
            generation_config ={"response_mime_type":"application/json"},
            safety_settings={},
            tools=None,
            system_instruction=None,
        )
        self._CHATMODEL = None
        for model in genai.list_models():
            if "generateContent" in model.supported_generation_methods:
                if model.name == "models/gemma-3-27b-it":
                    self._CHATMODEL: ChatGoogleGenerativeAI = ChatGoogleGenerativeAI(
                        model = model.name,
                        temperature = 0.7,
                    )
                    break
        if self._CHATMODEL == None:
            raise ValueError("Chat Model not Loaded")
        self.memory = ConversationSummaryBufferMemory(
            llm = self._CHATMODEL,
            max_token_limit=10000,
            return_messages=True
        )
        self.conversation = ConversationChain(
            llm = self._CHATMODEL,
            memory = self.memory,
            verbose = True
        )
        self.corpus = ""
        FOLDER = "./JSON"
        if not os.path.exists(FOLDER):
            os.makedirs(FOLDER)
        self.JSONFOLDER = FOLDER
        
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
    
    @ExceptionHandelling
    def getResponse(self, prompt: str) -> str:
        response = self.__MODEL.generate_content(prompt)
        response.resolve()
        return response.text
    
    @ExceptionHandelling
    def resumeanalytics(self, resumepath: str, jobdescription: str, filename: str = "prompt.txt") -> Optional[Dict[str, Any]]:
        resume = self.FileProcessing(resumepath)
        JobDescription = self.FileProcessing(jobdescription)

        if not os.path.exists(filename):
            raise FileNotFoundError(f"The file {filename} does not exist.")
        with open(filename, "r", encoding="utf-8") as file:
            prompt = file.read()
        Fprompt = f"{prompt}\nResume: {resume}\nJob Description: {JobDescription}"
        try:
            OutputFile = f"{self.JSONFOLDER}/{os.path.basename(resumepath)}.json"
            response = self.getResponse(Fprompt)
            responseJSON = json.loads(response)
            with open(OutputFile, "w", encoding="utf-8") as file:
                json.dump(responseJSON, file, indent=4, ensure_ascii=False)
            print(f"JSON file saved: {OutputFile}")
            
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
    
    @ExceptionHandelling
    def chatbot(self,Document: str, Query: str = None) -> str:
        data: str = self.FileProcessing(Document)
        self.memory.chat_memory.add_user_message(data)
        self.memory.chat_memory.add_ai_message("Document Loaded Successfully")
        if Query:
            print("\n[Bot]: ", end="", flush=True)
            response: str = ""
            messages = self.memory.chat_memory.messages.copy()
            messages.append(HumanMessage(content = Query))
            for chunk in self._CHATMODEL.stream(messages):
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
        
