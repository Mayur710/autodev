"""This node of the graph is responsible for executing the code written by the llm and register if an error occured or not"""
import subprocess

code_filename = "generated_code.py"
timeout_secs = 10

def executor(state):
    #save code to file 
    with open(code_filename, "w") as f:
        f.write(state["code"])
    try:
        result = subprocess.run(
            ['python', code_filename],
            capture_output=True,
            text=True,
            timeout=timeout_secs
        )
        if(result.returncode == 0):
            state["success"] = True
            state["output"] = result.stdout
            state["error"] = ""

        else:
            state["success"] = False
            state["error"] = result.stderr
            state["output"] = ""

    except subprocess.TimeoutExpired:
        state["success"] = False
        state["output"] = ""
        state["error"] = f"Execution timed out after {timeout_secs} seconds."

    return state