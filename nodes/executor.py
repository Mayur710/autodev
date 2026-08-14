"""This node of the graph is responsible for executing the code written by the llm and register if an error occured or not

in phase 3 we will run the code in a docker container to avoid any security issues and also avoid dependency issues , we will not
run the code in our local machine"""
import subprocess
import os 
import uuid

code_filename = "generated_code.py"
DOCKER_IMAGE_NAME = "autodev-sandbox"
timeout_secs = 10

def executor(state):
    #save code to file 
    with open(code_filename, "w") as f:
        f.write(state["code"])

    #building full path to mount on docker 
    host_path = os.path.abspath(code_filename)
    container_name = f"autodev-run-{uuid.uuid4().hex[:8]}"  # Generate a unique container name
    try:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "--name", container_name,
                "--network", "none",
                "--memory", "512m",
                "--cpus", "1",
                "-v", f"{host_path}:/app/code.py",
                DOCKER_IMAGE_NAME,
            ],
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
        #if container is still running after timeout , kill it 
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        state["success"] = False
        state["output"] = ""
        state["error"] = f"Execution timed out after {timeout_secs} seconds."

    return state