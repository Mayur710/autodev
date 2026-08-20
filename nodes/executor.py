"""This node of the graph is responsible for executing the code written by the llm and register if an error occured or not

in phase 3 we will run the code in a docker container to avoid any security issues and also avoid dependency issues , we will not
run the code in our local machine

for streamlit deployment we will need to check if docker is installed and running on the machine , if not we will need to throw an error """
import subprocess
import os 
import uuid

SOLUTION_FILENAME = "solution.py"
TESTS_FILENAME = "test_solution.py"
DOCKER_IMAGE_NAME = "autodev-sandbox"
DATA_FILENAME = "sample_data.csv"
timeout_secs = 15

def is_docker_installed():
    try:
        result = subprocess.run(
            ["docker", "version"],
            capture_output=True, 
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

DOCKER_INSTALLED = is_docker_installed()

def run_in_docker(solution_host_path, tests_host_path, data_host_path):
    container_name = f"autodev-run-{uuid.uuid4().hex[:8]}"  # Generate a unique container name
    docker_args = [
        "docker",
        "run",
        "--rm",
        "--name", container_name,
        "--network", "none",
        "--memory", "512m",
        "--cpus", "1",
        "-v", f"{solution_host_path}:/app/solution.py",
        "-v", f"{tests_host_path}:/app/test_solution.py",
    ]
    if os.path.exists(data_host_path):
        docker_args += ["-v", f"{data_host_path}:/app/{DATA_FILENAME}"]

    docker_args.append(DOCKER_IMAGE_NAME)
    try:
        result = subprocess.run(
            docker_args,
            capture_output=True,
            text=True,
            timeout=timeout_secs
        )
        return result, None
    except subprocess.TimeoutExpired:
        subprocess.run(["docker", "stop", container_name], capture_output=True)
        return None , f"Execution timed out after {timeout_secs} seconds."

def run_without_docker():
    """Fallback running test without docker if docker is not installed we run test directly on host machine"""
    try:
        result = subprocess.run(
            ["pytest", "-v", TESTS_FILENAME],
            capture_output=True,
            text=True,
            timeout=timeout_secs
        )
        return result, None
    except subprocess.TimeoutExpired:
        return None, f"Execution timed out after {timeout_secs} seconds."

def executor(state):
    #save code to file 
    with open(SOLUTION_FILENAME, "w", encoding="utf-8") as f:
        f.write(state["code"])

    with open(TESTS_FILENAME, "w", encoding="utf-8") as f:
        f.write(state["tests"])

    #building full path to mount on docker 
    solution_host_path = os.path.abspath(SOLUTION_FILENAME)
    tests_host_path = os.path.abspath(TESTS_FILENAME)
    data_host_path = os.path.abspath(DATA_FILENAME)
    if DOCKER_INSTALLED:
        result, timeout_error = run_in_docker(solution_host_path, tests_host_path, data_host_path)
    else:
        result, timeout_error = run_without_docker()

    if timeout_error:
        state["success"] = False
        state["output"] = ""
        state["error"] = timeout_error
        return state

    if result.returncode == 0:
        state["success"] = True
        state["output"] = result.stdout
        state["error"] = ""

    else:
        state["success"] = False
        state["error"] = result.stdout + result.stderr
        state["output"] = ""

    return state