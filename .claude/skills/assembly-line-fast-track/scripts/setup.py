#!/usr/bin/env python3
"""One-time setup for the Fast Tracked Assembly Line. Safe to run again anytime.

Installs everything the editing pipeline needs, all free:
  - a local transcription environment (stable-ts + faster-whisper)
  - the DaVinci Resolve MCP server (community, open source) wired into
    Claude Code and Codex
  - the free-edition bridge script that lets the AI talk to DaVinci Resolve

It does NOT install DaVinci Resolve itself. Download that first (free) from
https://www.blackmagicdesign.com/products/davinciresolve and install it.

Usage:
    python3 setup.py
"""

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
BASE = HOME / ".showrunner-os"
VENV = BASE / "venv"
MCP_HOME = BASE / "davinci-resolve-mcp"
CONFIG = BASE / "fast-track.json"
MCP_REPO = "https://github.com/samuelgursky/davinci-resolve-mcp.git"

IS_MAC = sys.platform == "darwin"
IS_WIN = sys.platform == "win32"

steps_failed = []


def step(n, title):
    print(f"\n[{n}] {title}", flush=True)


def ok(msg):
    print(f"    OK  {msg}", flush=True)


def warn(msg):
    print(f"    !!  {msg}", flush=True)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if IS_WIN else "bin/python")


def pick_python() -> str:
    """Prefer Python 3.10-3.12 when one is installed; they are the least-risk
    range for the audio libraries. Fall back to whatever is running us."""
    for name in ("python3.12", "python3.11", "python3.10"):
        path = shutil.which(name)
        if path:
            return path
    if sys.version_info >= (3, 10):
        return sys.executable
    print("PROBLEM: Python 3.10 or newer is required. Install it from python.org "
          "and run this again.")
    sys.exit(1)


def main() -> None:
    print("Fast Tracked Assembly Line — setup\n" + "=" * 40)
    BASE.mkdir(exist_ok=True)

    # ------------------------------------------------------------------ 1
    step(1, "DaVinci Resolve installed?")
    resolve_present = False
    if IS_MAC:
        resolve_present = any(Path(p).exists() for p in (
            "/Applications/DaVinci Resolve/DaVinci Resolve.app",
            "/Applications/DaVinci Resolve.app"))
    elif IS_WIN:
        resolve_present = any(Path(p).exists() for p in (
            r"C:\Program Files\Blackmagic Design\DaVinci Resolve",
            r"C:\ProgramData\Blackmagic Design\DaVinci Resolve"))
    else:
        resolve_present = Path("/opt/resolve").exists()
    if resolve_present:
        ok("found DaVinci Resolve")
    else:
        warn("DaVinci Resolve not found. Install the FREE version from "
             "blackmagicdesign.com/products/davinciresolve, then run setup again.")
        steps_failed.append("resolve")

    # ------------------------------------------------------------------ 2
    step(2, "ffmpeg (reads and writes video files)")
    if shutil.which("ffmpeg"):
        ok("ffmpeg is installed")
    else:
        installed = False
        if IS_MAC and shutil.which("brew"):
            print("    installing with Homebrew...", flush=True)
            installed = run(["brew", "install", "ffmpeg"]).returncode == 0
        elif IS_WIN and shutil.which("winget"):
            print("    installing with winget...", flush=True)
            installed = run(["winget", "install", "--id", "Gyan.FFmpeg",
                             "-e", "--accept-source-agreements",
                             "--accept-package-agreements"]).returncode == 0
        if installed:
            ok("ffmpeg installed (open a NEW terminal if it is not found later)")
        else:
            if IS_MAC:
                warn("could not install ffmpeg automatically. Install Homebrew "
                     "first (one command, from https://brew.sh), then run setup "
                     "again and it handles the rest.")
            elif IS_WIN:
                warn("could not install ffmpeg automatically. Download the "
                     "'ffmpeg-release-essentials' build from "
                     "https://www.gyan.dev/ffmpeg/builds/ , unzip it, and add its "
                     "bin folder to PATH — or install winget and run setup again.")
            else:
                warn("install ffmpeg with your package manager (e.g. "
                     "sudo apt install ffmpeg) and run setup again.")
            steps_failed.append("ffmpeg")

    # ------------------------------------------------------------------ 3
    step(3, "Local transcription environment (stable-ts + faster-whisper)")
    py = pick_python()
    if not venv_python().exists():
        r = run([py, "-m", "venv", str(VENV)])
        if r.returncode != 0:
            warn(f"could not create the environment: {r.stderr.strip()}")
            steps_failed.append("venv")
    if venv_python().exists():
        r = run([str(venv_python()), "-m", "pip", "install", "--quiet",
                 "--upgrade", "pip"])
        r = run([str(venv_python()), "-m", "pip", "install", "--quiet",
                 "-U", "stable-ts[fw]", "numpy"])
        if r.returncode == 0:
            ok(f"transcription environment ready (using {py})")
        else:
            warn("pip could not install the audio libraries. Error tail:\n    "
                 + r.stderr.strip()[-400:])
            steps_failed.append("stable-ts")

    # ------------------------------------------------------------------ 4
    step(4, "DaVinci Resolve MCP server (free, open source)")
    if not shutil.which("git"):
        warn("git is not installed. Install it (git-scm.com) and run setup again.")
        steps_failed.append("git")
    else:
        if (MCP_HOME / ".git").exists():
            run(["git", "-C", str(MCP_HOME), "pull", "--ff-only"])
            ok("MCP server already present, updated")
        else:
            r = run(["git", "clone", "--depth", "1", MCP_REPO, str(MCP_HOME)])
            if r.returncode != 0:
                warn(f"could not download the MCP server: {r.stderr.strip()[-300:]}")
                steps_failed.append("mcp-clone")
            else:
                ok("MCP server downloaded")
        if (MCP_HOME / "install.py").exists():
            print("    installing its environment (takes a minute)...", flush=True)
            # --clients manual: the pipeline's scripts talk to Resolve through
            # the bridge directly, so nothing needs to be registered into
            # Claude Code or Codex (and no restart is needed).
            r = run([py, "install.py", "--clients", "manual",
                     "--update-policy", "never"], cwd=str(MCP_HOME))
            if r.returncode == 0:
                ok("Resolve control layer installed")
            else:
                warn("its installer reported a problem. Tail of its output:\n    "
                     + (r.stdout + r.stderr).strip()[-400:])
                steps_failed.append("mcp-install")

    # ------------------------------------------------------------------ 5
    step(5, "Free-edition bridge (lets the AI reach Resolve)")
    # Resolve does not create its Scripts folder until something installs into
    # it, and the bridge installer refuses to run without it. Create it first.
    if IS_MAC:
        scripts_dir = (HOME / "Library/Application Support/Blackmagic Design"
                       / "DaVinci Resolve/Fusion/Scripts/Utility")
        scripts_dir.mkdir(parents=True, exist_ok=True)
    elif not IS_WIN:
        (HOME / ".local/share/DaVinciResolve/Fusion/Scripts/Utility").mkdir(
            parents=True, exist_ok=True)
    mcp_venv_py = MCP_HOME / ("venv/Scripts/python.exe" if IS_WIN else "venv/bin/python")
    bridge_installer = MCP_HOME / "scripts/install_resolve_bridge.py"
    if mcp_venv_py.exists() and bridge_installer.exists():
        r = run([str(mcp_venv_py), str(bridge_installer)])
        if r.returncode == 0:
            ok("bridge installed into Resolve's Scripts menu")
        else:
            warn("bridge install failed:\n    " + (r.stdout + r.stderr).strip()[-400:])
            steps_failed.append("bridge")
    else:
        warn("skipped (MCP server install did not finish)")
        steps_failed.append("bridge")

    # ------------------------------------------------------------------ 6
    if IS_MAC:
        step(6, "Can Resolve find Python? (macOS quirk)")
        # Resolve only looks in /usr/local/bin/python3 or $PYTHON3HOME.
        if Path("/usr/local/bin/python3").exists():
            ok("/usr/local/bin/python3 exists, Resolve will find it")
        else:
            base = run([py, "-c", "import sys; print(sys.base_prefix)"])
            prefix = base.stdout.strip()
            r = run(["launchctl", "setenv", "PYTHON3HOME", prefix])
            if r.returncode == 0:
                ok(f"pointed Resolve at Python via PYTHON3HOME={prefix}")
                warn("restart DaVinci Resolve if it was open")
            else:
                warn("could not set PYTHON3HOME. In Terminal run:\n"
                     f'    launchctl setenv PYTHON3HOME "{prefix}"')
                steps_failed.append("python3home")

    # ------------------------------------------------------------------ save
    CONFIG.write_text(json.dumps({
        "venv_python": str(venv_python()),
        "mcp_home": str(MCP_HOME),
        "platform": platform.platform(),
    }, indent=2), encoding="utf-8")

    print("\n" + "=" * 40)
    if steps_failed:
        print(f"Setup finished with {len(steps_failed)} problem(s): "
              f"{', '.join(steps_failed)}")
        print("Fix what is listed above and run setup again. It is safe to rerun.")
        sys.exit(1)
    print("""Setup complete. Before every editing session, do this once:

  1. Open DaVinci Resolve.
  2. Open (or create) your project.
  3. Menu bar: Workspace > Scripts > resolve_bridge   (starts the connection)

That's it — you are ready to edit.""")


if __name__ == "__main__":
    main()
