#!/usr/bin/env python3
"""Render the current timeline out of DaVinci Resolve.

Usage:
    python3 render.py [--out DIR] [--name NAME]

Renders whatever timeline is currently open in Resolve. The output lands in
--out (default: ~/Movies/ShowrunnerOS). Note for the free edition: the bridge
only writes inside your Movies folder, so keep --out under there.

Requires Resolve open with the bridge running (doctor.py checks).
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

HOME = Path.home()
CONFIG = HOME / ".showrunner-os/fast-track.json"
DEFAULT_OUT = HOME / "Movies" / "ShowrunnerOS"


def fail(msg: str) -> None:
    print(f"\nPROBLEM: {msg}", file=sys.stderr)
    sys.exit(1)


def connect_bridge():
    home = HOME / ".showrunner-os/davinci-resolve-mcp"
    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        home = Path(cfg.get("mcp_home", home))
    if not (home / "src/server.py").exists():
        fail("the Resolve MCP server is not installed. Run setup.py first.")
    sys.path.insert(0, str(home))
    os.environ["DAVINCI_RESOLVE_BRIDGE"] = "1"
    try:
        from src.utils import resolve_bridge_client as bc
    except ImportError:
        venv_py = home / ("venv/Scripts/python.exe" if sys.platform == "win32"
                          else "venv/bin/python")
        if venv_py.exists() and Path(sys.executable) != venv_py:
            os.execv(str(venv_py), [str(venv_py)] + sys.argv)
        raise
    try:
        return bc.connect()
    except Exception as exc:  # noqa: BLE001
        fail("could not reach DaVinci Resolve. Is it open with the bridge "
             f"running (Workspace > Scripts > resolve_bridge)? (detail: {exc})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--name", default=None,
                        help="output file name (default: the timeline's name)")
    parser.add_argument("--preset", default="YouTube - 1080p",
                        help="Resolve render preset (default: 'YouTube - 1080p', an "
                             "upload-ready mp4; pass '' to keep the Deliver page's "
                             "current settings)")
    args = parser.parse_args()

    out_dir = Path(args.out).expanduser()
    out_dir.mkdir(parents=True, exist_ok=True)

    resolve = connect_bridge()
    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if not project:
        fail("no project is open in Resolve")
    timeline = project.GetCurrentTimeline()
    if not timeline:
        fail("no timeline is open in Resolve")

    name = args.name or timeline.GetName().replace(" ", "-").lower()
    if args.preset:
        if project.LoadRenderPreset(args.preset):
            print(f"Using render preset: {args.preset}", flush=True)
        else:
            print(f"  (preset {args.preset!r} not found; using the Deliver page's "
                  "current settings)", flush=True)
    print(f"Rendering '{timeline.GetName()}' to {out_dir}/{name} ...", flush=True)

    if not project.SetRenderSettings({"TargetDir": str(out_dir),
                                      "CustomName": name}):
        fail("Resolve rejected the render settings. Is --out inside your "
             "Movies folder? The free-edition bridge only writes there.")
    job = project.AddRenderJob()
    if not job:
        fail("could not queue the render job")
    if not project.StartRendering():
        fail("could not start the render")

    while project.IsRenderingInProgress():
        time.sleep(5)
        print("  ...rendering", flush=True)

    hits = sorted(out_dir.glob(f"{name}*"), key=lambda p: p.stat().st_mtime)
    if not hits:
        fail("the render finished but no output file appeared. Check the "
             "Deliver page in Resolve for the job's status.")
    final = hits[-1]
    print(f"\nDone: {final} ({final.stat().st_size / 1e6:.0f} MB)")


if __name__ == "__main__":
    main()
