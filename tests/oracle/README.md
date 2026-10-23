# Held-out oracle test suite

Human-written grading tests for the 18 benchmark tasks. **The agent never
sees these files, and their results are never fed back into its retry
loop.** This exists to break the circular-validation problem: the agent's
LLM-written `test_solution.py` drives *self-correction*, while `pass@1` /
`final pass` for the benchmark are decided here.

## Grading protocol (in `benchmarks.py`)

1. The agent runs to completion (self-written tests drive its retries).
2. `solution.py` from **attempt 1** is snapshotted to `snapshots/<task>_attempt1.py`.
3. The final `solution.py` is snapshotted to `snapshots/<task>_final.py`.
4. Each snapshot is dropped into `solution.py` and graded by
   `tests/oracle/test_<task_id>.py` in a subprocess — **after** the agent is
   done, so oracle failures can never leak into `error_history`.
5. `solution.py` is deleted between grades so nothing bleeds across tasks.

Reported metrics:
- `self_success` — did the agent's own tests pass?
- `oracle_pass1` — did attempt 1 pass the held-out tests? (true pass@1)
- `oracle_final` — did the final attempt pass? (pass@≤3 with retries)

## Test categories used

parametrized nominal cases · boundary/edge cases · contract tests
(`pytest.raises`) · input-purity tests (no input mutation) · property &
metamorphic tests · determinism checks · perf smoke tests · two
purpose-built silent-bug detectors (`test_clean_csv_cow_trap`,
`test_flag_ages_removes_no_rows`).

## Validation

`python validate_oracle.py` — no LLM involved:
- every task's **reference solution** (`reference/solutions/`) must PASS
  (the suite tests the spec, not one implementation style);
- every known-bad **mutation** (`reference/mutations/`) must FAIL
  (the suite actually catches the pandas copy-on-write no-op and the
  row-dropping filter bug this project wrote up).

Commit the suite **before** an official benchmark run so the timestamps
prove the tests predate the results.
