from ResumeAnalytics import ResumeAnalytics
from DataProcessing import DocumentProcessing
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai
import os

class ATS():
    def __init__(self) -> None:
        load_dotenv(find_dotenv())
        object = ResumeAnalytics()
        self.model: genai.GenerativeModel = object._MODEL
    
    def getATS(self, resume: str):
