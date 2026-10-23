# AutoDev — Self-Correcting Code Agent

A LangGraph-based autonomous agent that takes a coding or data-cleaning task in plain English, plans its approach, writes code, tests it, executes it in a sandboxed Docker container, and automatically retries with a fixed version of the code if it fails — repeating until the task passes or a retry limit is hit.

**Live demo:** [autodev-knwajj37cvn5ggktt6yifv.streamlit.app](https://autodev-knwajj37cvn5ggktt6yifv.streamlit.app/)

---

## What it does

Give it a task like *"write a function that checks if a number is prime"* or *"clean this CSV file and print a summary of the issues found,"* and it will:

1. **Plan** — break the task into a short strategy before writing any code
2. **Code** — write a complete solution, plus a matching pytest test suite
3. **Execute** — run the solution against its own tests inside an isolated, resource-capped Docker container
4. **Evaluate** — check whether the tests passed
5. **Self-correct** — if they didn't, feed the full history of past errors back into the Coder and try again, up to a configurable retry limit

This loop — plan, act, observe, correct — is what separates an agent from a single LLM call that writes code once.

---

## Architecture

```
START → Planner → Coder → Executor ──success──→ Output → END
                     ↑                  │
                     │               failure
                     │                  ↓
                     └──────coder──  Error ──limit reached──→ Failure → END
                        (retry)
```

- **Planner** — runs once, produces a high-level strategy for the task
- **Coder** — writes a complete solution *and* a pytest test suite; on retries, receives the full error history to avoid reintroducing previously-fixed bugs
- **Executor** — mounts the generated code into a sandboxed Docker container (`--network none`, memory/CPU caps, `--rm` cleanup) and runs the test suite; falls back to running pytest directly on the host if Docker isn't available (e.g. on the hosted demo)
- **Error** — logs the failure and increments the retry counter
- **Output / Failure** — terminal nodes reporting a successful result or a clear failure message after retries are exhausted

State is tracked through a single `AgentState` object (task, plan, code, tests, output, error, error history, retry count) that flows through every node — no node calls another directly; the graph's conditional edges decide what runs next based on state alone.

---

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python |
| Agent orchestration | LangGraph |
| LLM | OpenRouter — `nvidia/nemotron-3.5-lightning:free` (OpenAI-compatible API) |
| Sandboxed execution | Docker, with a host-subprocess fallback |
| Testing / evaluation | pytest |
| Front-end | Streamlit |
| Deployment | Streamlit Community Cloud |
| Version control | Git + GitHub |

---

## Benchmark results

18 tasks (6 easy, 7 medium, 5 hard), from single-function algorithms to multi-step CSV cleaning, with function signatures and edge-case behavior pinned in each prompt.

**How grading works.** The agent still self-corrects against the tests it writes itself — that loop is the architecture. But benchmark pass/fail is decided by a **held-out, human-written oracle suite** (`tests/oracle/`) the model never sees: grading runs *after* the agent finishes, so oracle failures are never fed back into its retry loop. Attempt-1 code is snapshotted separately, which makes true pass@1 measurable. The oracle itself is validated by `validate_oracle.py` (no LLM, no API quota): all 18 reference solutions pass it, and both planted bugs — a pandas copy-on-write no-op and a row-dropping filter — are caught.

| Metric | Result |
|---|---|
| **Oracle pass@1** — attempt-1 code vs held-out tests | **18/18** |
| **Oracle final** — final code vs held-out tests | **18/18** |
| Agent's own self-tests green | 15/18 |
| Average retries per task | 0.50 (9 retries on 3 tasks) |
| Average time per task | ~58s |

| Difficulty | Oracle pass@1 | Oracle final |
|---|---|---|
| Easy | 6/6 | 6/6 |
| Medium | 7/7 | 7/7 |
| Hard | 5/5 | 5/5 |

**The interesting number is the disagreement: 3/18 (17%).** On `word_frequency`, `two_sum` and `clean_csv`, the agent exhausted all 3 retries against *its own* tests while attempt-1 code already passed the held-out oracle — in each case the self-written test was wrong, not the code (verified by replaying the snapshots against the oracle). Self-grading has now been observed failing in **both directions**: agreeing with wrong code (the `flag_ages` case below) and rejecting correct code (this run). That disagreement is the measured cost of self-graded evaluation, and it's why the benchmark grades externally.

*Model: `nvidia/nemotron-3.5-lightning:free` via OpenRouter, temperature 0. Originally `nvidia/nemotron-3-super-120b-a12b:free`, until Nvidia's free endpoint began returning provider-side 404s mid-project — switching was a one-line change in `llm.py`. Free-tier daily request caps (50/day) still bound how often a full run can be repeated.*

---

## Key findings

Building this surfaced several concrete, non-obvious engineering problems — these were more valuable to work through than a clean run would have been.

### LLM output is not reliably well-formatted
The Coder model would occasionally skip code fences, use the wrong language tag, or omit them entirely. Solved with a fence-optional regex and a fallback parsing path, rather than assuming the model would always comply with the requested format.

### "Complete and runnable" isn't a strong enough instruction
The model once wrote fully correct code but left the actual function call commented out — technically a successful run (exit code 0) that produced no output. The prompt had to explicitly require the script to self-execute and print output, not just define reusable functions.

### A subprocess timeout doesn't kill the underlying Docker container
`subprocess.run(timeout=...)` only stops *waiting* on the Python side — the container it spawned can keep running in the background indefinitely. Fixed by explicitly naming each container and issuing `docker stop` inside the timeout handler. Left unfixed, this would have caused container leaks during the benchmark run.

### Exit-code-only evaluation is a weak correctness signal
Code can run cleanly and still be wrong. A recurring pandas bug — `df[col].fillna(value, inplace=True)` silently failing to update the dataframe due to copy-on-write — produced a "successful" run with unchanged data multiple times. Only pytest-based assertions, which check actual data state rather than just completion, caught this.

### Self-graded tests can encode contradictory requirements
When the Coder writes its own tests, ambiguous task phrasing can produce a solution and a test that disagree with each other. One task asked the agent to *"flag"* out-of-range ages; the Coder correctly kept the rows and flagged them, but its own test then asserted no invalid ages could remain — a contradiction that exhausted all retries, because the problem was in the specification, not the code. Rephrasing the task removed the ambiguity and it passed on the very next attempt. **This finding is what motivated the held-out oracle suite that now grades the benchmark (see below).**

### Self-grading and held-out grading disagree — measured
The first oracle-graded benchmark made the circular-validation problem *measurable*: on 3 of 18 tasks the agent exhausted all retries against its own tests while attempt-1 code already passed the human-written oracle (`word_frequency`, `two_sum`, `clean_csv` — all replayed and confirmed by hand). That's a 17% false-alarm rate: 9 wasted retries and ~9.5 minutes of wall-clock chasing correct code. Combined with the `flag_ages` case above — self-test agreeing with *wrong* code — self-graded evaluation has now been observed failing in both directions. Reporting both graders side by side (`self_success` vs `oracle_pass1`) is the fix.

### The architecture genuinely generalizes
Pointing the exact same graph — same five nodes, same routing logic, same retry mechanism — at a structurally different domain (CSV data cleaning instead of algorithmic coding tasks) required only two changes: adding `pandas` to the sandbox's dependencies, and conditionally mounting an input data file in the Executor. No changes to the state schema, the graph wiring, or any node's core logic.

---

## Project structure

```
autodev/
├── app.py                   # Streamlit front-end
├── main.py                  # Graph definition, routing, entry point
├── state.py                 # AgentState schema
├── llm.py                   # LLM client (OpenRouter), env/secrets handling
├── benchmarks.py            # Runs the 18-task benchmark, grades results via the oracle suite
├── validate_oracle.py       # LLM-free oracle sanity check (refs pass, planted bugs caught)
├── nodes/
│   ├── planner.py
│   ├── coder.py
│   ├── executor.py
│   └── error.py
├── tests/
│   └── oracle/              # Human-written held-out grading tests + shared CSV fixture
├── reference/
│   ├── solutions/           # Reference implementations used to validate the oracle
│   └── mutations/           # Known-bad implementations the oracle must catch
├── Dockerfile                # Sandbox image definition
├── docker-requirements.txt   # Dependencies installed inside the sandbox
└── requirements.txt          # Dependencies for the app / deployment
```

---

## Running it locally

**Prerequisites:** Python 3.11+, Docker Desktop (optional — the agent falls back to direct execution if unavailable), an OpenRouter API key (free tier available, no card required).

```bash
git clone https://github.com/Mayur710/autodev.git
cd autodev
python -m venv myvenv
myvenv\Scripts\activate        # Windows
pip install -r requirements.txt
docker build -t autodev-sandbox .   # optional, enables sandboxed execution
```

Create a `.env` file:
```
MY_API_KEY=your_openrouter_api_key
```

Run the CLI version:
```bash
python main.py
```

Run the web UI:
```bash
streamlit run app.py
```

Run the benchmark suite (agent run + held-out oracle grading):
```bash
python benchmarks.py
```

Sanity-check the oracle suite itself — no LLM calls, no API quota:
```bash
python validate_oracle.py
```

---

## Future improvements

- **Snapshot self-tests alongside code** — code attempts are snapshotted per run, but the agent's self-written test files aren't; preserving them would keep the full evidence when the two graders disagree
- **CI/CD** — a GitHub Actions workflow to run `validate_oracle.py` on every push and the benchmark on a schedule
- **Streaming UI** — show each node's output live as it happens, rather than only after the full run completes
- **Multi-language support** — extend the Executor's sandbox to compile/run languages beyond Python
- **Sandboxed hosted demo** — the Community Cloud deployment can't run Docker and uses the host-subprocess fallback; a remote ephemeral sandbox would close that gap

---

## Why this project

Built to demonstrate the core skills behind agentic AI systems — planning, tool use, state management, self-correction, and evaluation — using LangGraph as the orchestration layer, with a working self-correction loop, real sandboxing, and honest, tested benchmark results rather than a single hand-picked demo.
