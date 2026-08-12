from llm import llm , MODEL_NAME
import re

system_prompt = f"""You are an expert Python software engineer.

You will be given a task and a plan. You may also be given code you 
wrote previously along with a history of errors it has produced across 
attempts — if so, use that history to avoid repeating past mistakes 
and fix the code.

Write the complete, runnable Python code to solve the task.
The script must actually execute the solution and print visible output 
when run directly — do not just define functions without calling them, 
and do not comment out any code that should run.
Do not include any explanation — return only the code.

Return your response in this exact format:

CODE:
```python
<your complete code>
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
            f"\n\n Please fix the code taking into account the full error history so you don't return a previously solved bug and return the complete runnable code in the format specified in the system prompt"
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
def parse_code(output:str) -> str:
    """will parse the code from output"""
    match = re.search(r"```(?:\w+)?\s*(.*?)```", output, re.DOTALL)
    code = match.group(1) if match else output.strip()
    return code

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
    code = parse_code(output)
    state["code"] = code
    return state