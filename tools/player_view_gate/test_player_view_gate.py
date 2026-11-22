import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import player_view_gate as gate  # noqa: E402

SCRIPT = Path(gate.__file__).resolve()
CONFIG = {
    "views_dir": "views",
    "register": "approvals.json",
    "launchers": [r"(^|/)gpu/run_[^/]*\.sh$", r"(^|/)private-runs/[^ ]+\.py$", r"^-m src\.orchestrator$"],
    "markers": [r"chat/completions"],
    "not_launch": [r"runner\.py summary"],
}


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        (self.root / gate.CONFIG).write_text(json.dumps(CONFIG))
        (self.root / "gpu").mkdir()
        (self.root / "gpu/run_games.sh").write_text("echo start\n")
        (self.root / "gpu/runner.py").write_text("URL = 'http://localhost:8000/v1/chat/completions'\n")
        (self.root / "gpu/score.py").write_text("print('auroc')\n")
        (self.root / "gpu/test_runner.py").write_text("FAKE = '/v1/chat/completions'\n")
        (self.root / "request.json").write_text(json.dumps(
            {"max_tokens": 1024, "messages": [{"role": "system", "content": "You are Wei."},
                                             {"role": "user", "content": "Give your orders."}]}))

    def tearDown(self):
        self.tmp.cleanup()

    def blocked(self, command):
        return gate.check(command, self.root, self.root)

    def quiet(self, function, *args):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return function(*args)

    def make(self, run="run-1"):
        self.quiet(gate.make, self.root, gate.load_config(self.root), run, [self.root / "request.json"])

    def approve(self, run="run-1"):
        self.quiet(gate.approve, self.root, gate.load_config(self.root), run, "Read it. Go.")

    def test_commands_that_start_no_run_pass(self):
        for command in ("ls -la", "grep -n vllm gpu/run_games.sh", "cat gpu/runner.py", "git add gpu/run_games.sh",
                        "git commit -m 'bash gpu/run_games.sh'", "echo 'bash gpu/run_games.sh'",
                        "python3 gpu/score.py", "python3 -m unittest gpu.test_runner",
                        "python3 gpu/test_runner.py", "python3 gpu/runner.py stage --out x",
                        "python3 gpu/runner.py --help", "python3 gpu/runner.py summary",
                        "bash gpu/run_games.sh --dry-run"):
            self.assertIsNone(self.blocked(command), command)

    def test_a_run_with_no_view_named_is_blocked(self):
        for command in ("bash gpu/run_games.sh",
                        "cd gpu && bash run_games.sh",
                        "nohup bash gpu/run_games.sh > log 2>&1 &",
                        "caffeinate -i uv run python gpu/runner.py run --seeds 5",
                        "./gpu/run_games.sh",
                        "ls && python3 gpu/runner.py run",
                        "bash -lc 'python3 gpu/runner.py run'",
                        "python3 private-runs/issue-63/run.py run",
                        "python3 -m src.orchestrator init --campaign x",
                        "ssh -p 1000 root@host 'cd /workspace && bash gpu/run_games.sh'",
                        "tmux new -d 'bash gpu/run_games.sh'",
                        "python3 -c \"import requests; requests.post(u + '/v1/chat/completions')\""):
            problem = self.blocked(command)
            self.assertIsNotNone(problem, command)
            self.assertIn("names no player view", problem)

    def test_a_script_is_found_by_what_it_contains(self):
        (self.root / "new_idea.py").write_text("post(base + '/v1/chat/completions', json=body)\n")
        self.assertIsNotNone(self.blocked("python3 new_idea.py"))

    def test_a_named_view_must_exist_and_be_approved(self):
        command = "PLAYER_VIEW=run-1 bash gpu/run_games.sh"
        self.assertIn("no player view named", self.blocked(command))
        self.make()
        self.assertIn("has not approved", self.blocked(command))
        self.approve()
        self.assertIsNone(self.blocked(command))
        self.assertIsNone(self.blocked("export PLAYER_VIEW=run-1; nohup bash gpu/run_games.sh &"))
        self.assertIn("no player view named", self.blocked("PLAYER_VIEW=other bash gpu/run_games.sh"))

    def test_a_view_changed_after_approval_is_blocked(self):
        self.make()
        self.approve()
        view = self.root / "views/run-1/view.txt"
        view.write_text(view.read_text() + "one more line\n")
        self.assertIn("changed after it was made", self.blocked("PLAYER_VIEW=run-1 bash gpu/run_games.sh"))

    def test_making_the_view_again_removes_the_approval(self):
        self.make()
        self.approve()
        (self.root / "request.json").write_text(json.dumps([{"role": "user", "content": "New request."}]))
        self.make()
        self.assertIn("has not approved", self.blocked("PLAYER_VIEW=run-1 bash gpu/run_games.sh"))

    def test_approve_needs_a_view_and_the_owners_words(self):
        cfg = gate.load_config(self.root)
        with self.assertRaises(SystemExit):
            gate.approve(self.root, cfg, "run-1", "Go.")
        self.make()
        with self.assertRaises(SystemExit):
            gate.approve(self.root, cfg, "run-1", "  ")

    def test_the_view_shows_each_message_and_the_settings(self):
        self.make()
        view = (self.root / "views/run-1/view.txt").read_text()
        for expected in ("Player view: run-1", "--- system (12 characters) ---", "You are Wei.",
                         "--- user (17 characters) ---", "Give your orders.", '"max_tokens": 1024'):
            self.assertIn(expected, view)

    def test_token_ids_are_refused(self):
        (self.root / "ids.json").write_text("[1, 2, 3]")
        with self.assertRaises(SystemExit):
            gate.render(self.root / "ids.json")

    def hook(self, payload, root=None):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root or self.root), "check"],
                              input=payload, capture_output=True, text=True)

    def test_the_hook_exits_2_with_the_reason_on_stderr(self):
        payload = json.dumps({"tool_name": "Bash", "cwd": str(self.root),
                              "tool_input": {"command": "bash gpu/run_games.sh"}})
        result = self.hook(payload)
        self.assertEqual(result.returncode, 2)
        self.assertIn("names no player view", result.stderr)
        self.make()
        self.approve()
        payload = payload.replace("bash gpu", "PLAYER_VIEW=run-1 bash gpu")
        self.assertEqual(self.hook(payload).returncode, 0)

    def test_the_hook_passes_input_it_cannot_read(self):
        self.assertEqual(self.hook("not json").returncode, 0)
        self.assertEqual(self.hook(json.dumps({"tool_input": {"file_path": "x"}})).returncode, 0)

    def test_without_a_config_file_the_gate_does_nothing(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertIsNone(gate.find_root(empty))


if __name__ == "__main__":
    unittest.main()
