#!/usr/bin/env python3
"""Run the TPC-DS queries and record status/time in a CSV.

Usage: ./run_queries.py [--runs 2] [--timeout 600] [--queries 1 2 3 ...] [--out results/results.csv]
Env:   CLICKHOUSE_CLIENT  client command (default: clickhouse-client)
"""
import argparse
import csv
import os
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def first_error(stderr: str) -> str:
    m = re.search(r"Code: \d+\.[^(]*(\([A-Z_]+\))?", stderr)
    msg = m.group(0) if m else stderr.strip()
    return " ".join(msg.split())[:200]


def run_query(client, n, timeout, out_dir):
    sql = (ROOT / "queries" / f"query_{n}.sql").read_bytes()
    start = time.monotonic()
    p = subprocess.run(
        client + ["-mn", f"--max_execution_time={timeout}", "--format=TSV"],
        input=sql, capture_output=True,
    )
    seconds = time.monotonic() - start
    (out_dir / f"query_{n}.out").write_bytes(p.stdout)
    (out_dir / f"query_{n}.err").write_bytes(p.stderr)
    rows = p.stdout.count(b"\n")
    ok = p.returncode == 0
    err = "" if ok else first_error(p.stderr.decode(errors="replace"))
    return ok, seconds, rows, err


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs", type=int, default=2, help="runs per query")
    ap.add_argument("--timeout", type=int, default=600, help="per-query timeout, seconds")
    ap.add_argument("--queries", type=int, nargs="*", default=list(range(1, 100)))
    ap.add_argument("--out", default="results/results.csv", help="CSV path, relative to the repo root")
    args = ap.parse_args()

    client = shlex.split(os.environ.get("CLICKHOUSE_CLIENT", "clickhouse-client"))
    out_csv = ROOT / args.out
    out_dir = out_csv.parent
    out_dir.mkdir(exist_ok=True)

    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["query", "run", "status", "seconds", "rows", "error"])
        for n in args.queries:
            for r in range(1, args.runs + 1):
                ok, seconds, rows, err = run_query(client, n, args.timeout, out_dir)
                row = [n, r, "OK" if ok else "FAIL", f"{seconds:.3f}", rows, err]
                w.writerow(row)
                f.flush()
                print(",".join(map(str, row)), flush=True)
                if not ok:
                    break  # no point repeating a failure


if __name__ == "__main__":
    sys.exit(main())
