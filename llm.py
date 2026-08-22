"""This file has the base llm model that will be used"""
from dotenv import load_dotenv
from openai import OpenAI
import os 
import streamlit as st

def get_api_key():
    try:
        return st.secrets["MY_API_KEY"]
    except (FileNotFoundError, KeyError):
        return os.getenv("MY_API_KEY")
load_dotenv()
llm = OpenAI(base_url="https://openrouter.ai/api/v1", 
             api_key=get_api_key())

MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"