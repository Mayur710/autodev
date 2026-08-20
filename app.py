"""app.py — Streamlit front-end for AutoDev"""
import streamlit as st
from main import app  

st.set_page_config(page_title="AutoDev")
st.title("AutoDev — Self-Correcting Code Agent")
st.caption("Describe a coding task. Watch the agent plan, code, test, and fix itself.")

task = st.text_area("What should the agent build?", placeholder="e.g. Write a function that checks if a number is prime.")

if st.button("Run Agent", type="primary"):
    if not task.strip():
        st.warning("Please enter a task.")
    else:
        with st.spinner("Agent is working..."):
            initial_state = {
                "task": task,
                "plan": "", "code": "", "tests": "",
                "output": "", "error": "", "error_history": [],
                "success": False, "retry_count": 0, "try_limit": 3
            }
            result = app.invoke(initial_state)

        st.subheader("Plan")
        st.write(result["plan"])

        st.subheader("Result")
        if result["success"]:
            st.success(f"Succeeded after {result['retry_count']} retr{'y' if result['retry_count']==1 else 'ies'}.")
        else:
            st.error(f"Failed after {result['retry_count']} retries.")

        st.subheader("Final Code")
        st.code(result["code"], language="python")

        if result["tests"]:
            st.subheader("Tests")
            st.code(result["tests"], language="python")

        st.subheader("Output")
        st.text(result["output"])

        if result["error_history"]:
            with st.expander(f"Error history ({len(result['error_history'])} attempts)"):
                for i, err in enumerate(result["error_history"], 1):
                    st.text(f"Attempt {i}:\n{err}")