#!/usr/bin/env python3
"""Draws results/comparison.svg: per-query time on ClickHouse 24.1 vs 26.10 (log axis).

Standard library only:  python3 bin/make_chart.py

Reads results/results-24.1.csv and results/results-26.10.csv (best of the runs per query).
Shown: queries that ran on both versions, plus those that timed out on 24.1 (hollow marker at the
600 s limit). Queries that failed with an error on either version, and query 78 (empty result on
both), are left out; the README table lists every query.
"""
import csv
import math
from pathlib import Path

RESULTS = Path(__file__).resolve().parent.parent / "results"
OLD_CSV, NEW_CSV = RESULTS / "results-24.1.csv", RESULTS / "results-26.10.csv"
OUT = RESULTS / "comparison.svg"
TIMEOUT_S = 600
EXCLUDE = {78}

T = dict(surface="#fcfcfb", ink="#0b0b0b", ink2="#52514e", muted="#898781", grid="#e1e0d9",
         base="#c3c2b7", link="#b9b8ae", old="#2a78d6", new="#1baf7a")
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"
W, M, LW, RW = 900, 24, 36, 60
ROW, TOP, AXIS = 15, 100, 30
LO, HI = 0.1, 1000.0
SLOWER = 1.2  # label queries at least this much slower on 26.10


def load(path):
    q = {}
    for r in csv.DictReader(open(path, newline="")):
        n = int(r["query"])
        d = q.setdefault(n, {"ok": True, "t": [], "err": ""})
        if r["status"] == "OK":
            d["t"].append(float(r["seconds"]))
        else:
            d["ok"], d["err"] = False, r["error"]
    return q


def rows():
    old, new = load(OLD_CSV), load(NEW_CSV)
    out = []
    for n in sorted(new):
        if n in EXCLUDE or not new[n]["ok"]:
            continue
        o = old[n]
        if o["ok"]:
            out.append((n, min(o["t"]), min(new[n]["t"]), False))
        elif "Timeout" in o["err"]:
            out.append((n, float(TIMEOUT_S), min(new[n]["t"]), True))
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render(data):
    t = T
    x0, plotw = M + LW + 8, W - 2 * M - LW - 8 - RW
    sx = lambda v: x0 + (math.log10(v) - math.log10(LO)) / (math.log10(HI) - math.log10(LO)) * plotw
    height = TOP + len(data) * ROW + AXIS + 10
    ytop, ybot = TOP, TOP + len(data) * ROW
    title = "ClickHouse 24.1.8.22 vs 26.10.7.24 on TPC-DS SF100, lower is better"
    sub = ("c6id.8xlarge, best of 2 runs, log axis; queries that ran on both versions or timed out on 24.1 "
           f"({len(data)} of 99)")
    faster = sum(1 for _, o, n, _ in data if n < o)
    desc = f"{faster} of {len(data)} queries are faster on 26.10; " + ", ".join(
        f"Q{n}: {o:.2f} s{' (timeout)' if to else ''} to {nw:.2f} s" for n, o, nw, to in data)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height}" width="{W}" height="{height}" '
         f'role="img" aria-labelledby="t d" font-family="{FONT}">',
         f'<title id="t">{esc(title)}</title>', f'<desc id="d">{esc(desc)}.</desc>',
         f'<rect width="{W}" height="{height}" fill="{t["surface"]}"/>',
         f'<text x="{M}" y="34" font-size="17" font-weight="700" fill="{t["ink"]}">{esc(title)}</text>',
         f'<text x="{M}" y="55" font-size="12" fill="{t["ink2"]}">{esc(sub)}</text>']
    # legend
    lx, ly = M, 78
    s.append(f'<path d="M{lx+6},{ly-6} l6,6 l-6,6 l-6,-6 z" fill="{t["old"]}"/>')
    s.append(f'<text x="{lx+18}" y="{ly+4}" font-size="12" fill="{t["ink2"]}">24.1.8.22</text>')
    s.append(f'<circle cx="{lx+120}" cy="{ly}" r="5.5" fill="{t["new"]}"/>')
    s.append(f'<text x="{lx+131}" y="{ly+4}" font-size="12" fill="{t["ink2"]}">26.10.7.24</text>')
    s.append(f'<path d="M{lx+246},{ly-6} l6,6 l-6,6 l-6,-6 z" fill="{t["surface"]}" stroke="{t["old"]}" stroke-width="2"/>')
    s.append(f'<text x="{lx+258}" y="{ly+4}" font-size="12" fill="{t["ink2"]}">24.1 timeout (limit 600 s)</text>')
    # grid + axis
    d = LO
    while d <= HI * 1.0001:
        for m in (1, 2, 5) if d < HI else (1,):
            v = d * m
            if v > HI * 1.0001:
                continue
            major = m == 1
            gx = sx(v)
            s.append(f'<line x1="{gx:.1f}" y1="{ytop}" x2="{gx:.1f}" y2="{ybot}" stroke="{t["grid"]}" '
                     f'stroke-width="1"{"" if major else " stroke-dasharray=\"2 3\""}/>')
            if major:
                lab = f"{v:g} s"
                s.append(f'<text x="{gx:.1f}" y="{ybot + 18}" font-size="11" text-anchor="middle" fill="{t["muted"]}">{lab}</text>')
        d *= 10
    s.append(f'<line x1="{x0}" y1="{ytop}" x2="{x0}" y2="{ybot}" stroke="{t["base"]}" stroke-width="1"/>')
    for i, (n, o, nw, to) in enumerate(data):
        cy = ytop + i * ROW + ROW / 2
        xo, xn = sx(o), sx(nw)
        tip = (f"Q{n}: 24.1 {'timeout (>600 s)' if to else f'{o:.2f} s'}, 26.10 {nw:.2f} s, "
               + (f"{o / nw:.1f}x faster" if nw < o else f"{nw / o:.1f}x slower"))
        s.append(f'<g><title>{esc(tip)}</title>')
        s.append(f'<rect x="{x0}" y="{cy - ROW / 2:.1f}" width="{plotw:.1f}" height="{ROW}" fill="transparent"/>')
        s.append(f'<text x="{M + LW}" y="{cy + 4:.1f}" font-size="11" text-anchor="end" fill="{t["ink2"]}">Q{n}</text>')
        s.append(f'<line x1="{xo:.1f}" y1="{cy:.1f}" x2="{xn:.1f}" y2="{cy:.1f}" stroke="{t["link"]}" stroke-width="1.5"/>')
        fill = t["surface"] if to else t["old"]
        s.append(f'<path d="M{xo:.1f},{cy - 5:.1f} l5,5 l-5,5 l-5,-5 z" fill="{fill}" stroke="{t["old"]}" stroke-width="2"/>')
        s.append(f'<circle cx="{xn:.1f}" cy="{cy:.1f}" r="4.5" fill="{t["new"]}" stroke="{t["surface"]}" stroke-width="2"/>')
        if nw > o * SLOWER:  # the regressions get a direct label
            s.append(f'<text x="{max(xo, xn) + 10:.1f}" y="{cy + 4:.1f}" font-size="11" fill="{t["ink2"]}" '
                     f'stroke="{t["surface"]}" stroke-width="3" paint-order="stroke">{nw / o:.1f}x slower</text>')
        s.append("</g>")
    s.append("</svg>")
    OUT.write_text("\n".join(s) + "\n", encoding="utf-8")
    return OUT


if __name__ == "__main__":
    print(render(rows()))
