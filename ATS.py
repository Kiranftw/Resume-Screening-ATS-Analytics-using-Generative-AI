from ResumeAnalytice import ResumeAnalytics
import os
from dotenv import load_dotenv, find_dotenv
from functools import wraps

def ExceptionHandelling(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as E:
            print(f"An error occurred: {E}")
            return None
    return wrapper

class ATS:
    def __init__(self, object: ResumeAnalytics) -> None:
        self.model = object.getMODEL
        self.chatmodel = object.chatmodel

    load_dotenv(find_dotenv())
    #TODO- CURRENTLY WE ARE BULDING ATS SYSTEM USING JOB DESCRIPTION LATER WE DEVELOP AUTONONOMOUS ATS SYSTEM
    def getATS(self, resume: str, jobdescription: str) -> None:
        if not os.__file__.startswith()   

if __name__ == "__main__":
    object = ATS(ResumeAnalytics())
    
