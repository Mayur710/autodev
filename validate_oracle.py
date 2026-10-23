"""Validate the held-out oracle suite WITHOUT any LLM calls.

Two checks, for every benchmark task:

  1. REFERENCE SOLUTIONS (must PASS):
     Drop the human-written reference solution into solution.py and run the
     oracle tests against it. All green => the oracle is satisfiable, i.e.
     it tests the SPEC, not one particular implementation style.

  2. MUTATIONS (must FAIL):
     Drop a known-bad implementation into solution.py and run the oracle
     tests. Red => the suite has teeth against the silent bug classes this
     project is about (pandas copy-on-write no-op, over-aggressive filtering).

Run:  python validate_oracle.py          (exit code 0 = suite is healthy)

This is the "prove your tests have teeth" harness. Run it once before an
official benchmark run and paste the output into the README.
"""
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SOLUTION = ROOT / "solution.py"
REF_DIR = ROOT / "reference" / "solutions"
MUT_DIR = ROOT / "reference" / "mutations"

# Must match BENCHMARK_TASKS ids in benchmarks.py exactly.
TASK_IDS = [
    "is_prime", "reverse_string", "factorial", "count_vowels",
    "max_in_list", "is_palindrome", "fibonacci", "merge_sorted",
    "word_frequency", "is_valid_email", "two_sum", "flatten",
    "dedupe_chars", "binary_search", "has_cycle", "clean_csv",
    "flag_ages", "lcs",
]


def run_oracle(task_id):
    """Write the staged implementation to solution.py, run its oracle tests,
    return (passed, pytest_output). solution.py is removed afterwards."""
    try:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", f"tests/oracle/test_{task_id}.py",
             "-q", "--tb=line", "-p", "no:cacheprovider"],
            cwd=ROOT, capture_output=True, text=True, timeout=120,
        )
        return proc.returncode == 0, proc.stdout + proc.stderr
    finally:
        SOLUTION.unlink(missing_ok=True)


def stage_and_run(src, task_id):
    shutil.copyfile(src, SOLUTION)
    return run_oracle(task_id)


def main():
    problems = []

    # --- structural checks -------------------------------------------------
    missing_tests = [t for t in TASK_IDS
                     if not (ROOT / "tests" / "oracle" / f"test_{t}.py").exists()]
    missing_refs = [t for t in TASK_IDS if not (REF_DIR / f"{t}.py").exists()]
    if missing_tests:
        problems.append(f"missing oracle test files: {missing_tests}")
    if missing_refs:
        problems.append(f"missing reference solutions: {missing_refs}")

    # --- 1. references must PASS ------------------------------------------
    print("=" * 60)
    print("1) REFERENCE SOLUTIONS (must all PASS)")
    print("=" * 60)
    for task_id in TASK_IDS:
        ref = REF_DIR / f"{task_id}.py"
        if not ref.exists():
            print(f"  SKIPPED  {task_id} (no reference file)")
            continue
        ok, out = stage_and_run(ref, task_id)
        print(f"  {'PASS' if ok else 'FAIL'}  {task_id}")
        if not ok:
            problems.append(f"reference failed on {task_id}")
            print("        " + "\n        ".join(out.strip().splitlines()[-8:]))

    # --- 2. mutations must FAIL -------------------------------------------
    print()
    print("=" * 60)
    print("2) KNOWN-BAD MUTATIONS (must all be CAUGHT)")
    print("=" * 60)
    for mut in sorted(MUT_DIR.glob("*.py")):
        task_id = mut.stem.split("__")[0]
        ok, out = stage_and_run(mut, task_id)
        caught = not ok
        print(f"  {'CAUGHT' if caught else 'MISSED'}  {mut.name}")
        if not caught:
            problems.append(f"mutation not caught: {mut.name}")

    # --- verdict -----------------------------------------------------------
    print()
    print("=" * 60)
    if problems:
        print("ORACLE SUITE IS UNHEALTHY:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    print(f"ORACLE SUITE HEALTHY: {len(TASK_IDS)} reference solutions pass, "
          f"{len(list(MUT_DIR.glob('*.py')))} mutations caught.")
    print("No LLM was used at any point in this validation.")


if __name__ == "__main__":
    main()
