from llm import llm , MODEL_NAME
import re

system_prompt = f"""You are an expert software engineer.

You will be given a task and a plan. You may also be given code you 
wrote previously along with a history of errors it has produced across 
attempts — if so, use that history to avoid repeating past mistakes 
and fix the code.

Your job is to:
1. Write the complete solution code in a file called solution.py
2. Write pytest test cases for that solution in a file called test_solution.py
   The tests must import from solution.py (e.g., "from solution import function_name")
   and check that the code behaves correctly, including edge cases.

Return your response in this exact format, with no other text:

SOLUTION:
```python
<your complete solution code>
```

TESTS:
```python
<your complete pytest test code>
```

"""

def build_user_prompt(state):
    msg = f"""Task : {state["task"]}\n\nPlan : {state["plan"]}"""
    if state["error_history"]:
        history_text = "\n".join(
            f"Attempt {i+1} error: \n{err}" for i, err in enumerate(state["error_history"])
        )
        msg += (
            f"\n\n Previous code : \n {state['code']}"
            f"\n\n History of all errors:\n {history_text}"
            f"\n\n fix the solution and/ or tests , taking into account the full error history so you don't reintroduce the previously fixed bugs"
        )
    return msg

r"""this function will extract the block of code from the output 
in the LLM response the code wills start from ``` so the function will look for this and know that the code started from here 
\w+ means one or more word characters 
?: means non-capturing group, it groups things together 
? right after means whole group is optional
(?:\w+)? there might be a language tag like python right after the backticks, or there might not be — either is fine
s* - whitespace characters, zero or more
(.*?) - capture group for the code itself, non-greedy match
``` - closing backticks"""

def parse_response(response : str):
    """to extract solution and test code from the LLM response"""
    solution_match= re.search(r"SOLUTION:\s*```(?:\w+)?\s*(.*?)```", response, re.DOTALL)
    tests_match = re.search(r"TESTS:\s*```(?:\w+)?\s*(.*?)```", response, re.DOTALL)

    solution = solution_match.group(1) if solution_match else None
    tests = tests_match.group(1) if tests_match else None
    if not solution or not tests:
        raise ValueError(f"Could not find solution or tests in the response.: \n {response}")
    return solution, tests

"""main coder function that will write the code given the user prompt and system prompt"""
def coder(state):
    user_prompt =  build_user_prompt(state)
    response = llm.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role":"system", "content": system_prompt},
            {"role":"user", "content": user_prompt}
        ],
        temperature=0
    )
    output = response.choices[0].message.content
    try:
        solution, tests = parse_response(output)
        state["code"] = solution
        state["tests"] = tests

    #treating value error as a failure to parse and not a crash 
    except ValueError as e:
        state["code"] = ""
        state["tests"] = ""
    
    return state