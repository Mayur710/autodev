"""This file has the base llm model that will be used"""
from dotenv import load_dotenv
from openai import OpenAI
import os 

load_dotenv()
llm = OpenAI(base_url="https://openrouter.ai/api/v1", 
             api_key=os.getenv("MY_API_KEY"))

MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"