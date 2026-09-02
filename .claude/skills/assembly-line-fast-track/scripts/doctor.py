#!/usr/bin/env python3
"""Health check for the Fast Tracked Assembly Line. Run before every session.

Usage:
    python3 doctor.py

Prints PASS or FAIL for each thing the pipeline needs, with the fix for every
FAIL. Exit code is the number of failures (0 = ready to edit).
"""

import json
import shutil
import socket
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
BASE = HOME / ".showrunner-os"
CONFIG = BASE / "fast-track.json"

failures = 0


def check(name, passed, fix=""):
    global failures
    if passed:
        print(f"  PASS  {name}")
    else:
        failures += 1
        print(f"  FAIL  {name}")
        if fix:
            print(f"        fix: {fix}")


def main() -> None:
    print("Fast Tracked Assembly Line — doctor\n" + "=" * 40)

    cfg = {}
    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    check("setup has been run", bool(cfg),
          "run: python3 .claude/skills/assembly-line-fast-track/scripts/setup.py")

    check("ffmpeg", shutil.which("ffmpeg") is not None,
          "run setup again; on a Mac without Homebrew, install Homebrew from "
          "brew.sh first; on Windows use the gyan.dev/ffmpeg/builds "
          "'release-essentials' zip")

    venv_python = Path(cfg.get("venv_python", BASE / "venv/bin/python"))
    stable_ok = False
    if venv_python.exists():
        r = subprocess.run([str(venv_python), "-c", "import stable_whisper"],
                           capture_output=True)
        stable_ok = r.returncode == 0
    check("transcription environment (stable-ts)", stable_ok, "run setup again")

    mcp_home = Path(cfg.get("mcp_home", BASE / "davinci-resolve-mcp"))
    check("Resolve MCP server installed", (mcp_home / "src/server.py").exists(),
          "run setup again")

    bridge_cfg_path = HOME / ".config/davinci-resolve-mcp/bridge.json"
    check("bridge installed", bridge_cfg_path.exists(), "run setup again")

    bridge_up = False
    if bridge_cfg_path.exists():
        try:
            bridge_cfg = json.loads(bridge_cfg_path.read_text(encoding="utf-8"))
            with socket.create_connection(
                    (bridge_cfg.get("host", "127.0.0.1"),
                     int(bridge_cfg.get("port", 0))), timeout=2):
                bridge_up = True
        except OSError:
            bridge_up = False
    check("bridge is running (Resolve answering)", bridge_up,
          "in DaVinci Resolve: open your project, then "
          "Workspace > Scripts > resolve_bridge")

    print("=" * 40)
    if failures == 0:
        print("All clear. Ready to edit.")
    else:
        print(f"{failures} problem(s) above. Fix them top to bottom, "
              "then run doctor again.")
    sys.exit(failures)


if __name__ == "__main__":
    main()
