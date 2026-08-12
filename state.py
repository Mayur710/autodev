"""This file has the states that will be used in the graph """
from typing import TypedDict
class AgentState(TypedDict):
    task : str #user input 
    plan : str
    code : str
    output : str
    error : str
    error_history : list[str]
    success : bool  #whether the task was successful or not
    retry_count : int  #current count of retries
    try_limit : int #max limit of retries 