"""This is the main entry point of application , this has the graph information and main loop"""
from langgraph.graph import StateGraph , START, END
from nodes.planner import planner
from nodes.error import error
from nodes.coder import coder
from nodes.executor import executor
from nodes.output import output
from state import AgentState #python looks for state.py and imports the AgentState class from it

"""this function tells the route of graph after executor"""
def route_after_executor(state: AgentState) -> str:
    #if agent does the job perfectly then it will return the output else through error node 
    if state["success"]:
        return 'output'
    else:
        return 'error'

"""if agent fails to write the correct code after max retries then it will go to a failure node and return a failure message"""
def failure(state: AgentState) -> AgentState:
    state["output"] = (f"Failed to solve the task after {state['try_limit']} retries.\n"
                       f"Last error encountered: \n {state['error']}")
    return state

"""this function tells the route of graph after error node"""
def route_after_error(state: AgentState) -> str:
    if state["retry_count"] >= state["try_limit"]:
        return 'failure'
    else:
        return 'coder'
    
"""defining the graph structure and adding nodes and edges to it"""
graph = StateGraph(AgentState)

graph.add_node('planner', planner)
graph.add_node('coder', coder)
graph.add_node('executor', executor)
graph.add_node('output', output)
graph.add_node('error', error)
graph.add_node('failure', failure)

graph.add_edge(START, 'planner')
graph.add_edge('planner', 'coder')
graph.add_edge('coder', 'executor')
graph.add_conditional_edges('executor', route_after_executor, {'output': 'output', 'error': 'error'})
graph.add_conditional_edges('error', route_after_error,{'coder': 'coder', 'failure': 'failure'})
graph.add_edge('failure', END)
graph.add_edge('output', END)

app = graph.compile() 
if __name__ == "__main__":
    """Inital state of graph """
    initial_state: AgentState = {
        "task": input("Enter your task: "),
        "plan": "",
        "code": "",
        "tests": "",
        "output": "",
        "error": "",
        "error_history": [],
        "success": False,
        "retry_count": 0,
        "try_limit": 3
    }
    result = app.invoke(initial_state)
    print("PLAN: \n", result["plan"])
    print("\nERROR HISTORY: \n", "\n".join(result["error_history"]))
    print("\nOUTPUT: \n", result["output"])