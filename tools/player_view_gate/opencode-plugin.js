// OpenCode plugin: runs the player view gate before each shell command.
// The gate exits 2 and writes the reason to stderr when the command starts a model run with no approved player view.
// See tools/player_view_gate/README.md.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";

export const PlayerViewGate = async ({ worktree, directory }) => {
  const script = path.join(worktree || directory, "tools/player_view_gate/player_view_gate.py");
  return {
    "tool.execute.before": async (input, output) => {
      const command = output.args?.command;
      if (input.tool !== "bash" || typeof command !== "string" || !existsSync(script)) return;
      const payload = JSON.stringify({ tool_name: "Bash", cwd: output.args?.workdir || directory, tool_input: { command } });
      const result = spawnSync("python3", [script, "check"], { input: payload, encoding: "utf8", timeout: 10000 });
      if (result.status === 2) throw new Error(result.stderr.trim());
    },
  };
};
