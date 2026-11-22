# Player view gate

A hook for AI coding assistants. It blocks a command that starts a model run until the project owner has read what the model receives.

## Why

I used AI assistants to run an experiment on broken promises between AI players. Two weeks in, after the final test, I checked 965 requests for orders. None of them contained the messages the player had sent. A player that broke a promise was never shown that promise.

Reading one request on day one would have shown me. The assistants wrote the code that built the requests, and I never read a request.

The gate makes that reading a step the assistant cannot skip.

## How it works

1. The assistant writes one real request of each kind the run sends, as text, without calling the model.
2. `make` puts those requests in one file, the player view, and prints it.
3. The assistant shows the text to the owner. The owner reads it and answers.
4. `approve` records the owner's words and the date beside the sha256 of the view.
5. The run starts with `PLAYER_VIEW=<run>` in front of the command.

The hook reads each shell command before it runs. If the command starts a model run, the hook looks for the named view. It blocks the command when no view is named, when the view is missing, when the view file changed after `make`, or when the owner has not approved it. The assistant gets the reason and the five steps.

```
python3 tools/player_view_gate/player_view_gate.py make order-replay requests/orders.json requests/messages.json
python3 tools/player_view_gate/player_view_gate.py approve order-replay --quote "Read both. The orders request has no sent messages, add them."
PLAYER_VIEW=order-replay bash gpu/run_games.sh
```

A request file is one of these:

- a text file with the prompt
- a JSON list of chat messages
- a JSON request body with `messages` or `prompt`. Other fields, such as `max_tokens`, are printed as settings.

A list of token ids is refused. Decode it to text first.

## What counts as a model run

`player-view.json` at the repo root holds the rules. Without that file the gate does nothing.

| Key | Meaning |
|---|---|
| `launchers` | Patterns for the script path, or for `-m module`. A match is a run. |
| `markers` | Patterns for the script's text. A script that contains one is a run. This finds new scripts that no pattern names. |
| `staging_args` | Arguments that mean no model is called: `stage`, `--dry-run`, `--help`, `-h`. |
| `not_launch` | Patterns for the whole command. A match is not a run. Use it for a script that contains a marker and does not call the model. |
| `views_dir` | Where views are saved. Requests can hold private data, so keep this folder out of git. |
| `register` | The approvals file. Keep it in git. It holds hashes, dates and the owner's words, and no request text. |

The hook finds the script in commands such as `bash x.sh`, `./x.sh`, `python -m pkg.mod`, `uv run python x.py`, `nohup ... &`, `cd dir && ...`, `bash -c '...'`, `ssh host '...'` and `tmux new '...'`. Files named `test_*` pass.

## Install

Copy this folder to `tools/player_view_gate/` in your repo. Copy `player-view.example.json` to `player-view.json` at the repo root and edit the patterns. The script needs Python 3.9 or later and no packages.

Claude Code, in `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/tools/player_view_gate/player_view_gate.py\" check",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Codex, in `.codex/hooks.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$(git rev-parse --show-toplevel)/tools/player_view_gate/player_view_gate.py\" check",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

The hook exits with code 2 and writes the reason to stderr. Both assistants treat that as a blocked command.

Run the tests:

```
python3 -m unittest discover -s tools/player_view_gate -p 'test_*.py'
```

## Limits

- **The assistant records the approval.** The gate does not prove that the owner read the view. The register is in git, so the owner's quoted words are there to check.
- **The view is as real as the files given to `make`.** The gate cannot tell a real request from an invented one. Build the view with the same code that builds the run's requests.
- **It shows text, not tokens.** The chat template can add text that the request file does not show.
- **A changed prompt needs a new view.** The gate compares the view file with its hash. It does not notice that the code that builds the requests changed after approval.
- **It reads shell commands.** A run started another way, such as from a notebook, is not seen.
- **A project hook covers sessions started in that repo.** A session started in another folder does not load it.
