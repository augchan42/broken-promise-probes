"""Check the Wei-Han broken promise against its saved files.

Usage: python verify_example.py

Needs only the Python standard library. It checks that the promise, the order that broke
it, the board before the order, and the saved token trace all agree with case.json.
"""

import hashlib
import json
from pathlib import Path

EXAMPLE = Path(__file__).resolve().parent / "examples/wei-han"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check(condition, message):
    if not condition:
        raise SystemExit("FAILED: " + message)


def main():
    case = load(EXAMPLE / "case.json")
    rd = EXAMPLE / f"round_{case['round']:02d}"
    sender, recipient = case["sender"], case["recipient"]

    earlier = load(rd / "diplomacy/pass_1" / f"{sender}.json")
    promise = load(rd / f"diplomacy/pass_{case['pass']}" / f"{sender}.json")
    check(promise["to"] == recipient and promise["message"] == case["promise"], "The promise text differs")

    order = case["submitted_order"]
    owners = load(rd / "pre_ownership.json")
    orders = load(rd / "orders" / f"{sender}.json")["orders"]
    check(any(all(o.get(k) == v for k, v in order.items()) for o in orders), "The order is not in the saved orders")
    check(order["order"] == "move" and owners[order["target"]] == recipient,
          "The order is not a move into the recipient's territory")
    check(case["resolution"] in (rd / "resolution.txt").read_text(encoding="utf-8"), "The resolution differs")

    rows = [json.loads(line) for line in (EXAMPLE / "trace.jsonl").read_text(encoding="utf-8").splitlines()]
    thinking, = [r for r in rows if r["stage"] == "thinking"]
    answer, = [r for r in rows if r["stage"] == "answer"]
    cutoffs = case["cutoff_token_counts"]
    check(len(thinking["prompt_token_ids"]) == cutoffs["prompt_end"], "The prompt length differs")
    prefix = answer["prompt_token_ids"]
    check(len(prefix) == cutoffs["reasoning_end"], "The reasoning end differs")
    check(prefix[:cutoffs["prompt_end"]] == thinking["prompt_token_ids"], "The answer does not continue the prompt")
    digest = hashlib.sha256(json.dumps(prefix, separators=(",", ":")).encode()).hexdigest()
    check(digest == case["prefix_token_ids_sha256"], "The token prefix hash differs")
    reasoning = (rd / "reasoning_before_promise.txt").read_text(encoding="utf-8")
    check(hashlib.sha256(reasoning.encode()).hexdigest() == case["reasoning_sha256"], "The reasoning text differs")
    check(reasoning.strip() in thinking["text"], "The reasoning text is not in the trace")

    print(f"Round {case['round']}. {sender.title()} told {earlier['to'].title()} in pass 1:")
    print(f"  {earlier['message']}")
    print(f"{sender.title()} then told {recipient.title()} in pass {case['pass']}:")
    print(f"  {promise['message']}")
    print(f"{sender.title()} ordered: {order['unit']} {order['order']} {order['target']} "
          f"({order['target']} belonged to {owners[order['target']].title()}).")
    print(f"Result: {case['resolution']}.")
    print(f"Label: {case['label']}.")
    print(f"The probe reads the model at token {cutoffs['reasoning_end']}, the last token of its reasoning, "
          "before it writes the promise.")
    print("All checks passed.")


if __name__ == "__main__":
    main()
