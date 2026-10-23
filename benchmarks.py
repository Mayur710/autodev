"""Run benchmark tasks, then grade the agent's code against hand-written oracle tests."""
import time
import csv
import os
import sys
import pathlib
import subprocess
from main import app, AgentState

ROOT = pathlib.Path(__file__).resolve().parent
SOLUTION = ROOT / "solution.py"
SNAP_DIR = ROOT / "snapshots"
SNAP_DIR.mkdir(exist_ok=True)

# (task_id, prompt, difficulty). task_id -> tests/oracle/test_<task_id>.py
BENCHMARK_TASKS = [
    ("is_prime", "Write a function is_prime(n: int) -> bool in solution.py that returns True only if n is a prime number. 0, 1 and negative numbers are not prime.", "easy"),
    ("reverse_string", "Write a function reverse_string(s: str) -> str in solution.py that returns the string reversed.", "easy"),
    ("factorial", "Write a function factorial(n: int) -> int in solution.py that returns n!. Raise ValueError for negative input.", "easy"),
    ("count_vowels", "Write a function count_vowels(s: str) -> int in solution.py that counts the vowels (a, e, i, o, u), case-insensitive.", "easy"),
    ("max_in_list", "Write a function max_in_list(nums: list) -> int in solution.py that returns the maximum value. Raise ValueError if the list is empty.", "easy"),
    ("is_palindrome", "Write a function is_palindrome(s: str) -> bool in solution.py that checks if a string is a palindrome, ignoring case and spaces.", "easy"),

    ("fibonacci", "Write a function fibonacci(n: int) -> int in solution.py that returns the nth Fibonacci number (fibonacci(0)=0, fibonacci(1)=1, n >= 0) using memoization.", "medium"),
    ("merge_sorted", "Write a function merge_sorted(a: list, b: list) -> list in solution.py that merges two sorted lists into one sorted list. Do not modify the input lists.", "medium"),
    ("word_frequency", "Write a function word_frequency(text: str) -> dict in solution.py that counts how often each word appears, case-insensitive and ignoring punctuation.", "medium"),
    ("is_valid_email", "Write a function is_valid_email(s: str) -> bool in solution.py that returns True if s has exactly one '@', at least one '.' after the '@', and no spaces.", "medium"),
    ("two_sum", "Write a function two_sum(nums: list, target: int) -> list in solution.py. Assume no duplicate values. Return a list of [a, b] value pairs that sum to target, each pair once, with a appearing before b in nums. Do not modify nums.", "medium"),
    ("flatten", "Write a function flatten(lst: list) -> list in solution.py that flattens a nested list of arbitrary depth.", "medium"),
    ("dedupe_chars", "Write a function dedupe_chars(s: str) -> str in solution.py that removes duplicate characters, keeping the first occurrence of each and preserving order.", "medium"),

    ("binary_search", "Write a function binary_search(arr: list, target: int) -> int in solution.py that returns the index of target in a sorted list, or -1 if absent.", "hard"),
    ("has_cycle", "In solution.py define a class Node with __init__(self, val, next=None), and a function has_cycle(head) -> bool that returns True if the linked list has a cycle.", "hard"),
    ("clean_csv", "Write a function clean_csv(path: str) -> pd.DataFrame in solution.py. Read the CSV at path with pandas, remove duplicate rows, coerce invalid salary entries to NaN, print a summary, and return the cleaned DataFrame.", "hard"),
    ("flag_ages", "Write a function flag_ages(path: str) -> pd.DataFrame in solution.py. Read the CSV at path, add a boolean column age_valid that is False for ages outside 0-120, remove NO rows, print a summary, and return the DataFrame.", "hard"),
    ("lcs", "Write a function lcs(s1: str, s2: str) -> int in solution.py that returns the length of the longest common subsequence of two strings.", "hard"),
]


def grade_with_oracle(task_id, code):
    """Write code to solution.py, run the hidden oracle tests, return True/False.
    Result is NEVER shown to the agent."""
    if not code or not code.strip():
        return False
    SOLUTION.write_text(code, encoding="utf-8")
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", f"tests/oracle/test_{task_id}.py",
             "-q", "--tb=no", "-p", "no:cacheprovider"],
            cwd=ROOT, capture_output=True, text=True, timeout=90, env=env,
        )
        return proc.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    finally:
        SOLUTION.unlink(missing_ok=True)


def run_benchmarks():
    results = []
    for i, (task_id, prompt, difficulty) in enumerate(BENCHMARK_TASKS, start=1):
        print(f"\n [{i}/{len(BENCHMARK_TASKS)}] {task_id} (Difficulty: {difficulty})")
        initial_state: AgentState = {
            "task": prompt, "plan": "", "code": "", "tests": "", "output": "",
            "error": "", "error_history": [], "success": False,
            "retry_count": 0, "try_limit": 3,
        }
        first_code, final_state = "", dict(initial_state)
        start_time = time.time()
        try:
            for state in app.stream(initial_state, stream_mode="values"):
                final_state = state
                if not first_code and state.get("code"):
                    first_code = state["code"]      # attempt-1 snapshot
        except Exception as e:
            final_state = {**final_state, "success": False, "error": str(e), "retry_count": -1}
        elapsed = time.time() - start_time

        final_code = final_state.get("code", "")
        (SNAP_DIR / f"{task_id}_attempt1.py").write_text(first_code or "", encoding="utf-8")
        (SNAP_DIR / f"{task_id}_final.py").write_text(final_code or "", encoding="utf-8")

        # Grading happens AFTER the agent is done, so no leakage into error_history
        oracle_pass1 = grade_with_oracle(task_id, first_code)
        oracle_final = grade_with_oracle(task_id, final_code)

        results.append({
            "task_id": task_id,
            "difficulty": difficulty,
            "self_success": final_state.get("success", False),
            "retries": final_state.get("retry_count", -1),
            "oracle_pass1": oracle_pass1,
            "oracle_final": oracle_final,
            "time_seconds": round(elapsed, 2),
        })
        print(f"  → self-tests: {final_state.get('success')} | oracle pass@1: {oracle_pass1} "
              f"| oracle final: {oracle_final} | retries: {final_state.get('retry_count')}")
    return results


def print_summary(results):
    total = len(results)
    def rate(key, rs=results):
        return f"{sum(1 for r in rs if r[key])}/{len(rs)}"
    valid = [r["retries"] for r in results if r["retries"] >= 0]
    print("\nBENCHMARK SUMMARY")
    print("=" * 30)
    print(f"Self-test success:   {rate('self_success')}")
    print(f"Oracle pass@1:       {rate('oracle_pass1')}")
    print(f"Oracle final (≤3):   {rate('oracle_final')}")
    print(f"Avg retries:         {sum(valid)/max(len(valid),1):.2f}")
    print(f"Avg time per task:   {sum(r['time_seconds'] for r in results)/total:.2f}s")
    for tier in ["easy", "medium", "hard"]:
        tr = [r for r in results if r["difficulty"] == tier]
        print(f"  {tier.capitalize():7} pass@1 {rate('oracle_pass1', tr)} | final {rate('oracle_final', tr)}")


def save_results_csv(results, filename="benchmark_results.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to {filename}")


if __name__ == "__main__":
    results = run_benchmarks()
    print_summary(results)
    save_results_csv(results)