"""to run benchmarks tasks and return a result report"""
import time 
import csv 
from main import app , AgentState

BENCHMARK_TASKS = [
    ("Write a function that checks if a number is prime.", "easy"),
    ("Write a function that reverses a string.", "easy"),
    ("Write a function that returns the factorial of a non-negative integer; raise a ValueError for negative input.", "easy"),
    ("Write a function that counts vowels (a, e, i, o, u, case-insensitive) in a string.", "easy"),
    ("Write a function that returns the maximum value in a list of numbers; raise a ValueError if the list is empty.", "easy"),
    ("Write a function that checks if a string is a palindrome, ignoring case and spaces.", "easy"),

    ("Write a function that returns the nth Fibonacci number using memoization.", "medium"),
    ("Write a function that merges two sorted lists into one sorted list.", "medium"),
    ("Write a function that counts the frequency of each word in a given text, case-insensitive and ignoring punctuation.", "medium"),
    ("Write a function that validates whether a string is a plausible email: exactly one '@', at least one '.' after the '@', and no spaces.", "medium"),
    ("Write a function that finds all pairs of values in a list (assume no duplicate values) that sum to a target, returning a list of value pairs.", "medium"),
    ("Write a function that flattens a nested list of arbitrary depth.", "medium"),
    ("Write a function that removes all duplicate characters from a string while preserving order.", "medium"),

    ("Write a function that implements binary search on a sorted list.", "hard"),
    ("Write a function that detects if a linked list has a cycle. Define a simple Node class first.", "hard"),
    ("Read sample_data.csv with pandas, remove duplicates, coerce invalid salary entries to NaN, and print a summary.", "hard"),
    ("Read sample_data.csv, add an age_valid boolean column flagging ages outside 0-120 without removing rows, and print a summary.", "hard"),
    ("Write a function that finds the longest common subsequence between two strings.", "hard"),
]

def run_benchmarks():
    results = []
    for i, (tasks, difficulty) in enumerate(BENCHMARK_TASKS, start=1):
        print(f"\n [{i}/{len(BENCHMARK_TASKS)}] Running: {tasks[:60]}.. (Difficulty: {difficulty})")
        initial_state: AgentState = {
            "task": tasks,
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
        start_time = time.time()
        try:
            result = app.invoke(initial_state)
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "retry_count": -1
            }
        elapsed = time.time() - start_time

        results.append({
            "task": tasks,
            "difficulty": difficulty,
            "success": result["success"],
            "retries": result["retry_count"],
            "time_seconds": round(elapsed, 2),
        })
        
        status = "PASSED" if result["success"] else "FAILED"
        print(f"  → {status} | retries: {result['retry_count']} | time: {elapsed:.2f}s")

    return results

def print_summary(results):
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    avg_retries = sum(r["retries"] for r in results if r["retries"] >= 0) / total
    avg_time = sum(r["time_seconds"] for r in results) / total
    print("BENCHMARK SUMMARY")
    print("=" * 10)
    print(f"Success rate: {passed}/{total} ({passed/total*100:.1f}%)")
    print(f"Average retries per task: {avg_retries:.2f}")
    print(f"Average time per task: {avg_time:.2f}s")

    for tier in ["easy", "medium", "hard"]:
        tier_results = [r for r in results if r["difficulty"] == tier]
        tier_passed = sum(1 for r in tier_results if r["success"])
        print(f"  {tier.capitalize()}: {tier_passed}/{len(tier_results)} passed")


def save_results_csv(results, filename="benchmark_results.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["task", "difficulty", "success", "retries", "time_seconds"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\nResults saved to {filename}")


if __name__ == "__main__":
    results = run_benchmarks()
    print_summary(results)
    save_results_csv(results)