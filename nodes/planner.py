"""code for the planner node"""
from llm import llm, MODEL_NAME

system_prompt = f"""You are a software engineer planner.
Given a coding task , your job is to briefly explain the approach to solve it.
What steps or logi will be needed. No need to write any code. keep the explanation in 3 to 5 sentences"""

def planner(state):
    response = llm.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role":"system", "content": system_prompt},
            {"role":"user", "content": state["task"]}
        ],
        temperature=0
    )
    state["plan"] = response.choices[0].message.content
    return state    