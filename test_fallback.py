# test_fallback.py — temporary, isolated test
from nodes.executor import run_without_docker, DOCKER_INSTALLED

print("Docker available:", DOCKER_INSTALLED)

# Manually create solution + test files, no LLM involved
with open("solution.py", "w") as f:
    f.write("def add(a, b):\n    return a + b\n")

with open("test_solution.py", "w") as f:
    f.write(
        "from solution import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n"
    )

result, err = run_without_docker()
if err:
    print("TIMEOUT:", err)
else:
    print("RETURN CODE:", result.returncode)
    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)