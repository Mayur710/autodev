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
| LLM | OpenRouter (free-tier models, OpenAI-compatible API) |
| Sandboxed execution | Docker, with a host-subprocess fallback |
| Testing / evaluation | pytest |
| Front-end | Streamlit |
| Deployment | Streamlit Community Cloud |
| Version control | Git + GitHub |

---

## Benchmark results

Ran 18 tasks (6 easy, 7 medium, 5 hard) through the full agent pipeline, from single-function algorithms to multi-step CSV cleaning.

- **16/16 attempted tasks passed (100%)**
- **2 tasks not attempted** — blocked by OpenRouter's free-tier daily rate limit (50 requests/day) partway through the run
- **Average retries per task:** 0.39
- **Average time per task:** ~28s

| Difficulty | Result |
|---|---|
| Easy | 6/6 passed |
| Medium | 7/7 passed |
| Hard | 3/5 passed (2 unattempted due to rate limit — 0 genuine failures) |

**Known limitation:** free-tier LLM APIs impose daily request caps that a full benchmark run can exhaust mid-way. This is a real constraint of building on free infrastructure, documented here rather than hidden. In a paid deployment this ceiling disappears.

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
When the Coder writes its own tests, ambiguous task phrasing can produce a solution and a test that disagree with each other. One task asked the agent to *"flag"* out-of-range ages; the Coder correctly kept the rows and flagged them, but its own test then asserted no invalid ages could remain — a contradiction that exhausted all retries, because the problem was in the specification, not the code. Rephrasing the task removed the ambiguity and it passed on the very next attempt. This is a concrete case for externally-supplied test cases over self-graded ones in a stronger, production version of this system.

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
├── benchmark.py              # Runs the full benchmark suite, logs results
├── nodes/
│   ├── planner.py
│   ├── coder.py
│   ├── executor.py
│   └── error.py
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

Run the benchmark suite:
```bash
python benchmark.py
```

---

## Future improvements

- **Externally-supplied test cases** for the benchmark suite, rather than LLM-self-graded tests, to remove the self-contradiction failure mode found in Phase 4
- **CI/CD** — a GitHub Actions workflow to run the benchmark suite automatically on push
- **Streaming UI** — show each node's output live as it happens, rather than only after the full run completes
- **Multi-language support** — extend the Executor's sandbox to compile/run languages beyond Python

---

## Why this project

Built to demonstrate the core skills behind agentic AI systems — planning, tool use, state management, self-correction, and evaluation — using LangGraph as the orchestration layer, with a working self-correction loop, real sandboxing, and honest, tested benchmark results rather than a single hand-picked demo.
