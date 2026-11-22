#!/usr/bin/env python3
"""Player view gate: a model run does not start until the owner has read what the model receives.

  make <run> <request file>...   write and print the player view for a run
  approve <run> --quote "..."    record the owner's answer after they have read the view
  check                          hook mode: read a tool call on stdin, exit 2 to block it

Settings are in player-view.json at the repo root. Without that file the gate does nothing.
See README.md beside this file.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shlex
import sys
from pathlib import Path

CONFIG = "player-view.json"
DEFAULTS = {
    "views_dir": ".player-views",
    "register": "player-view-approvals.json",
    "launchers": [],
    "markers": [],
    "staging_args": ["stage", "--dry-run", "--help", "-h"],
    "not_launch": [],
}
ABOUT = ("Which runs the owner has approved after reading what the model receives. `make` adds a run with the "
         "sha256 of its view. `approve` adds the owner's words and the date. A run starts only when its view "
         "file still has the recorded sha256 and the entry has an approval.")
RUN_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
NAMED = re.compile(r"\bPLAYER_VIEW=[\"']?([A-Za-z0-9._-]+)")
ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
DURATION = re.compile(r"^\d+[smhd]?$")
SHELL = re.compile(r"^(ba|z|da|k)?sh$")
PYTHON = re.compile(r"^python[\d.]*$")
SHELL_INLINE = re.compile(r"^-[A-Za-z]*c$")
WRAPPERS = {"nohup", "time", "exec", "command", "env", "caffeinate", "nice", "stdbuf", "sudo", "setsid",
            "timeout", "uv", "run", "export"}
CARRIERS = {"tmux", "screen", "eval", "xargs", "watch"}
SSH_VALUE_FLAGS = set("bcDEeFIiJLlmOopQRSWw")
PUNCTUATION = ";|&()"


def find_root(start=None):
    start = Path(start or __file__).resolve()
    for folder in [start, *start.parents]:
        if (folder / CONFIG).is_file():
            return folder
    return None


def load_config(root):
    return {**DEFAULTS, **json.loads((root / CONFIG).read_text())}


def views_dir(root, cfg):
    folder = Path(os.path.expanduser(cfg["views_dir"]))
    return folder if folder.is_absolute() else root / folder


def read_register(root, cfg):
    path = root / cfg["register"]
    return json.loads(path.read_text()) if path.is_file() else {"about": ABOUT, "runs": {}}


def write_register(root, cfg, register):
    path = root / cfg["register"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(register, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- the view

def content_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(part.get("text", json.dumps(part)) if isinstance(part, dict) else str(part) for part in content)
    return json.dumps(content, ensure_ascii=False)


def render(source):
    """One request file as the text the model receives."""
    raw = source.read_text()
    if source.suffix.lower() != ".json":
        return raw.rstrip("\n")
    data = json.loads(raw)
    lines = []
    if isinstance(data, dict) and isinstance(data.get("messages"), list):
        settings = {k: v for k, v in data.items() if k != "messages"}
        if settings:
            lines.append("[settings] " + json.dumps(settings, ensure_ascii=False, sort_keys=True))
        data = data["messages"]
    elif isinstance(data, dict) and isinstance(data.get("prompt"), str):
        data = data["prompt"]
    if isinstance(data, str):
        return "\n".join(lines + [data.rstrip("\n")])
    if isinstance(data, list) and data and all(isinstance(m, dict) and "role" in m for m in data):
        for message in data:
            text = content_text(message.get("content", ""))
            lines += [f"--- {message['role']} ({len(text):,} characters) ---", text.rstrip("\n")]
        return "\n".join(lines)
    if isinstance(data, list) and data and all(isinstance(x, int) for x in data):
        raise SystemExit(f"{source}: this is a list of token ids. Decode it to text with the run's tokenizer first.")
    raise SystemExit(f"{source}: give one request per file: text, a list of chat messages, "
                     "or a request body with `messages` or `prompt`.")


def make(root, cfg, run, sources):
    if not RUN_NAME.match(run):
        raise SystemExit(f"Run name {run!r}: use letters, digits, dot, hyphen and underscore.")
    today = datetime.date.today().isoformat()
    parts = [f"Player view: {run}", f"Made {today}. Requests: {len(sources)}.", ""]
    for number, source in enumerate(sources, 1):
        parts += [f"===== Request {number} of {len(sources)}: {source.name} =====", render(source), ""]
    folder = views_dir(root, cfg) / run
    folder.mkdir(parents=True, exist_ok=True)
    view = folder / "view.txt"
    view.write_text("\n".join(parts))
    register = read_register(root, cfg)
    register["runs"][run] = {"made": today, "requests": len(sources), "view_sha256": sha256(view)}
    write_register(root, cfg, register)
    print(view.read_text())
    print(f"Saved to {view}\n"
          f"Next: paste the text above into your reply to the owner, in full, and wait for their answer.\n"
          f"Then record it: {script_name(root)} approve {run} --quote \"<their words>\"", file=sys.stderr)


def approve(root, cfg, run, quote):
    register = read_register(root, cfg)
    problem = view_problem(root, cfg, register, run)
    if problem:
        raise SystemExit(problem)
    if not quote.strip():
        raise SystemExit("--quote needs the owner's own words.")
    register["runs"][run]["approved"] = {"quote": quote.strip(), "date": datetime.date.today().isoformat()}
    write_register(root, cfg, register)
    print(f"Recorded. Start the run with PLAYER_VIEW={run} in front of the command.")


def view_problem(root, cfg, register, run):
    entry = register["runs"].get(run)
    view = views_dir(root, cfg) / run / "view.txt"
    if not entry or not view.is_file():
        return f"There is no player view named {run!r}."
    if sha256(view) != entry.get("view_sha256"):
        return f"The view file for {run!r} changed after it was made. Run `make` again and show the new text."
    return None


def approval_problem(root, cfg, register, run):
    problem = view_problem(root, cfg, register, run)
    if problem:
        return problem
    approved = register["runs"][run].get("approved") or {}
    if not (approved.get("quote") and approved.get("date")):
        return f"The owner has not approved the player view {run!r}."
    return None


# ---------------------------------------------------------------- reading a command

def simple_commands(command):
    text = command.replace("\n", " ; ")
    try:
        lexer = shlex.shlex(text, posix=True, punctuation_chars=PUNCTUATION)
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        tokens = re.findall(r"[;|&()]+|[^\s;|&()]+", text)
    words = []
    for token in tokens:
        if token and all(c in PUNCTUATION for c in token):
            if words:
                yield words
            words = []
        else:
            words.append(token)
    if words:
        yield words


def script_of(rest, shell):
    """What an interpreter was told to run: ('file' | 'inline' | 'module' | None, value, remaining args)."""
    i = 0
    while i < len(rest):
        word = rest[i]
        if i + 1 < len(rest):
            if (shell and SHELL_INLINE.match(word)) or (not shell and word == "-c"):
                return "inline", rest[i + 1], rest[i + 2:]
            if not shell and word == "-m":
                return "module", rest[i + 1], rest[i + 2:]
        if not shell and word in ("-X", "-W"):
            i += 2
        elif word.startswith("-"):
            i += 1
        else:
            return "file", word, rest[i + 1:]
    return None, None, []


def ssh_command(rest):
    i = 0
    while i < len(rest) and rest[i].startswith("-"):
        i += 2 if len(rest[i]) == 2 and rest[i][1] in SSH_VALUE_FLAGS else 1
    return " ".join(rest[i + 1:])


def resolve(target, cwd):
    path = Path(os.path.expanduser(target))
    return path if path.is_absolute() else cwd / path


def calls_model(names, file, cfg):
    if any(re.search(pattern, name) for pattern in cfg["launchers"] for name in names):
        return True
    try:
        if file and file.is_file() and file.stat().st_size < 2_000_000:
            text = file.read_text(errors="ignore")
            return any(re.search(pattern, text) for pattern in cfg["markers"])
    except OSError:
        pass
    return False


def launches(command, cwd, cfg, depth=0):
    """The parts of a shell command that start a model run."""
    found = []
    if depth > 3:
        return found
    for words in simple_commands(command):
        while words and (ASSIGN.match(words[0]) or words[0] in WRAPPERS or words[0].startswith("-")
                         or DURATION.match(words[0])):
            words.pop(0)
        if not words:
            continue
        head, rest = os.path.basename(words[0]), words[1:]
        if head == "cd":
            if rest:
                cwd = resolve(rest[0], cwd)
            continue
        if head == "ssh":
            found += launches(ssh_command(rest), cwd, cfg, depth + 1)
            continue
        if head in CARRIERS:
            for word in rest:
                found += launches(word, cwd, cfg, depth + 1)
            continue
        shell = bool(SHELL.match(head)) or head in ("source", ".")
        if shell or PYTHON.match(head):
            kind, value, args = script_of(rest, shell)
        elif "/" in words[0] or words[0].endswith((".sh", ".py")):
            kind, value, args = "file", words[0], rest
        else:
            continue
        if kind == "inline" and shell:
            found += launches(value, cwd, cfg, depth + 1)
            continue
        if kind == "inline":
            if any(re.search(pattern, value) for pattern in cfg["markers"]):
                found.append("python -c")
            continue
        if kind is None:
            continue
        if kind == "module":
            names, file = [f"-m {value}"], cwd / (value.replace(".", "/") + ".py")
        else:
            file = resolve(value, cwd)
            names = [value, str(file)]
        if os.path.basename(value).startswith("test_"):
            continue
        if any(arg in cfg["staging_args"] for arg in args):
            continue
        if any(re.search(pattern, " ".join(words)) for pattern in cfg["not_launch"]):
            continue
        if calls_model(names, file, cfg):
            found.append(names[0])
    return found


def script_name(root):
    here = Path(__file__).resolve()
    try:
        return f"python3 {here.relative_to(root)}"
    except ValueError:
        return f"python3 {here}"


def steps(root):
    tool = script_name(root)
    return ("Before a run, the owner reads what the model receives:\n"
            "1. Write one real request of each kind the run sends, as text, without calling the model "
            "(the runner's `stage` or `--dry-run` step).\n"
            f"2. {tool} make <run> <request file>...\n"
            "3. Paste the printed text into your reply to the owner, in full. Wait for their answer.\n"
            f"4. {tool} approve <run> --quote \"<their words>\"\n"
            "5. Start the run with PLAYER_VIEW=<run> in front of the command.\n"
            f"If this command does not call the model, add a pattern for it to `not_launch` in {CONFIG}.")


def check(command, cwd, root):
    """Why a command may not run yet, or None."""
    cfg = load_config(root)
    found = launches(command, Path(cwd), cfg)
    if not found:
        return None
    what = ", ".join(dict.fromkeys(found))
    runs = list(dict.fromkeys(NAMED.findall(command)))
    if not runs:
        return f"Blocked: this command starts a model run ({what}) and names no player view.\n" + steps(root)
    register = read_register(root, cfg)
    problems = [p for p in (approval_problem(root, cfg, register, run) for run in runs) if p]
    if problems:
        return f"Blocked: this command starts a model run ({what}). " + " ".join(problems) + "\n" + steps(root)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, help="repo root (default: the nearest folder above this file with player-view.json)")
    sub = parser.add_subparsers(dest="action", required=True)
    making = sub.add_parser("make")
    making.add_argument("run")
    making.add_argument("sources", type=Path, nargs="+")
    approving = sub.add_parser("approve")
    approving.add_argument("run")
    approving.add_argument("--quote", required=True)
    sub.add_parser("check")
    args = parser.parse_args(argv)
    root = args.root.resolve() if args.root else find_root()
    if args.action == "check":
        try:
            payload = json.load(sys.stdin)
            command = payload["tool_input"]["command"]
        except (ValueError, KeyError, TypeError):
            return 0
        if root is None or not (root / CONFIG).is_file() or not isinstance(command, str):
            return 0
        problem = check(command, payload.get("cwd") or os.getcwd(), root)
        if problem:
            print(problem, file=sys.stderr)
            return 2
        return 0
    if root is None:
        raise SystemExit(f"No {CONFIG} found above {Path(__file__).resolve().parent}.")
    cfg = load_config(root)
    if args.action == "make":
        make(root, cfg, args.run, args.sources)
    else:
        approve(root, cfg, args.run, args.quote)
    return 0


if __name__ == "__main__":
    sys.exit(main())
