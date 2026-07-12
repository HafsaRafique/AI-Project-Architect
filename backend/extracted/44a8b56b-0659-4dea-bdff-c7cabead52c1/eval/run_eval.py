#!/usr/bin/env python3
"""
Evaluation harness for the narration LLM layer.

Chess moves are a nice, small domain for a structured-generation eval:
inputs are fully deterministic (a fixed set of move-shapes), the expected
output *shape* is fully known (short sentence + one of ten enum values),
and correctness of the enum choice can be judged with a cheap heuristic
instead of a second LLM call. That makes it possible to measure a real
model's reliability without hand-labeling anything.

This script runs a battery of synthetic move scenarios through the
*actual configured provider* (whatever LLM_PROVIDER/.env you have set) and
reports:

  - schema validity rate    — did the raw output parse and pass
                              NarrationResponse validation?
  - fallback rate           — how often did get_narration() have to give
                              up and use canned narration?
  - effect-mood agreement   — a cheap heuristic check that e.g. checkmate
                              moves tend to get a "heavy" effect
                              (explosion/dark/holy) rather than "sparkle"
  - latency (mean / p50 / p95)

Usage:
    python eval/run_eval.py                    # uses your .env / current provider
    python eval/run_eval.py --repeats 5
    python eval/run_eval.py --persona whimsical
    python eval/run_eval.py --out results.json

Requires a reachable LLM (Ollama running locally, or HF_TOKEN set) to
produce a *meaningful* report — if the provider is unreachable every
scenario will simply exercise (and pass, by design) the fallback path,
which the summary will call out explicitly.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import llm_client as lc  # noqa: E402

# "Heavy" effects we'd expect a good model to reach for on dramatic moments.
HEAVY_EFFECTS = {"explosion", "dark", "holy", "lightning"}
LIGHT_EFFECTS = {"sparkle", "wind", "heal"}

SCENARIOS: list[dict] = [
    {
        "name": "quiet_pawn_push",
        "move_info": {
            "san": "e4", "mover": "white", "piece": "p", "captured": None,
            "castle": False, "en_passant": False, "check": False,
            "checkmate": False, "stalemate": False, "promotion": False,
            "to_square": "e4",
        },
        "expect_mood": "light",
    },
    {
        "name": "knight_capture",
        "move_info": {
            "san": "Nxe5", "mover": "black", "piece": "n", "captured": "p",
            "castle": False, "en_passant": False, "check": False,
            "checkmate": False, "stalemate": False, "promotion": False,
            "to_square": "e5",
        },
        "expect_mood": "heavy",
    },
    {
        "name": "check",
        "move_info": {
            "san": "Qh5+", "mover": "white", "piece": "q", "captured": None,
            "castle": False, "en_passant": False, "check": True,
            "checkmate": False, "stalemate": False, "promotion": False,
            "to_square": "h5",
        },
        "expect_mood": "heavy",
    },
    {
        "name": "checkmate",
        "move_info": {
            "san": "Qxf7#", "mover": "white", "piece": "q", "captured": "p",
            "castle": False, "en_passant": False, "check": True,
            "checkmate": True, "stalemate": False, "promotion": False,
            "to_square": "f7",
        },
        "expect_mood": "heavy",
    },
    {
        "name": "castle",
        "move_info": {
            "san": "O-O", "mover": "black", "piece": "k", "captured": None,
            "castle": True, "en_passant": False, "check": False,
            "checkmate": False, "stalemate": False, "promotion": False,
            "to_square": "g8",
        },
        "expect_mood": None,
    },
    {
        "name": "promotion",
        "move_info": {
            "san": "e8=Q", "mover": "white", "piece": "p", "captured": None,
            "castle": False, "en_passant": False, "check": False,
            "checkmate": False, "stalemate": False, "promotion": True,
            "to_square": "e8",
        },
        "expect_mood": None,
    },
    {
        "name": "stalemate",
        "move_info": {
            "san": "Kb6", "mover": "black", "piece": "k", "captured": None,
            "castle": False, "en_passant": False, "check": False,
            "checkmate": False, "stalemate": True, "promotion": False,
            "to_square": "b6",
        },
        "expect_mood": None,
    },
]


def run(repeats: int, persona: str) -> dict:
    records = []
    for scenario in SCENARIOS:
        for _ in range(repeats):
            result = lc.get_narration(scenario["move_info"], persona=persona)
            records.append({"scenario": scenario["name"], "expect_mood": scenario["expect_mood"], **result})

    total = len(records)
    fallback = [r for r in records if r["source"] == "fallback"]
    non_fallback = [r for r in records if r["source"] != "fallback"]
    latencies = [r["latency_ms"] for r in records]

    mood_checked = [r for r in non_fallback if r["expect_mood"]]
    mood_correct = [
        r for r in mood_checked
        if (r["expect_mood"] == "heavy" and r["effect"] in HEAVY_EFFECTS)
        or (r["expect_mood"] == "light" and r["effect"] in LIGHT_EFFECTS)
    ]

    summary = {
        "provider": lc.LLM_PROVIDER,
        "persona": persona,
        "total_runs": total,
        "fallback_rate": round(len(fallback) / total, 3) if total else None,
        "schema_valid_rate": round(len(non_fallback) / total, 3) if total else None,
        "mood_agreement_rate": (
            round(len(mood_correct) / len(mood_checked), 3) if mood_checked else None
        ),
        "latency_ms": {
            "mean": round(statistics.mean(latencies), 1) if latencies else None,
            "p50": round(statistics.median(latencies), 1) if latencies else None,
            "p95": round(sorted(latencies)[int(len(latencies) * 0.95) - 1], 1) if latencies else None,
        },
        "records": records,
    }
    return summary


def print_report(summary: dict) -> None:
    print(f"\n=== Narration eval report ({summary['provider']}, persona={summary['persona']}) ===")
    print(f"Total runs:            {summary['total_runs']}")
    print(f"Fallback rate:         {summary['fallback_rate']}"
          + ("  (provider unreachable? every run hit canned narration)" if summary['fallback_rate'] == 1.0 else ""))
    print(f"Schema-valid rate:     {summary['schema_valid_rate']}")
    print(f"Mood agreement rate:   {summary['mood_agreement_rate']}  "
          "(does effect choice match the drama of the move — heuristic, not ground truth)")
    lm = summary["latency_ms"]
    print(f"Latency ms (mean/p50/p95): {lm['mean']} / {lm['p50']} / {lm['p95']}")
    print()
    print("Sample outputs:")
    seen = set()
    for r in summary["records"]:
        if r["scenario"] in seen:
            continue
        seen.add(r["scenario"])
        print(f"  [{r['scenario']:>16}] ({r['source']:>9}, {r['effect']:>9}) {r['narration']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repeats", type=int, default=3, help="Repeats per scenario (default: 3)")
    parser.add_argument("--persona", default=lc.DEFAULT_PERSONA, choices=list(lc.NARRATOR_PERSONAS))
    parser.add_argument("--out", type=Path, default=None, help="Optional path to write full JSON report")
    args = parser.parse_args()

    summary = run(args.repeats, args.persona)
    print_report(summary)

    if args.out:
        args.out.write_text(json.dumps(summary, indent=2))
        print(f"\nFull report written to {args.out}")


if __name__ == "__main__":
    main()
