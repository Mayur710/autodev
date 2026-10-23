"""Path glue for the held-out oracle suite.

solution.py is written to the repo ROOT either by the executor (during an
agent run) or by the grader in benchmarks.py / validate_oracle.py. These
tests import from it, so ROOT must be importable no matter where pytest is
invoked from.

This file intentionally imports NOTHING from solution.py — conftest is loaded
during collection, before any solution file is guaranteed to exist.
"""
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
