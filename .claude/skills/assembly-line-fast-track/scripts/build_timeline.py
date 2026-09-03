#!/usr/bin/env python3
"""Build the edited timeline in DaVinci Resolve from an approved cutlist.

Usage:
    python3 build_timeline.py <cutlist.json> [--project NAME] [--timeline NAME]

Reads the frame-accurate segments produced by cutpoints.py and assembles them
in order on a fresh timeline in DaVinci Resolve (free edition, via the bridge).
Flagged segments get a red REVIEW marker on the timeline so the rough spots
are visible right where you will scrub them.

Requires: DaVinci Resolve open, a project open, and the bridge running
(Workspace > Scripts > resolve_bridge). `doctor.py` checks all of that.
"""

import argparse
import json
import os
import sys
from pathlib import Path

HOME = Path.home()
CONFIG = HOME / ".showrunner-os/fast-track.json"


def fail(msg: str) -> None:
    print(f"\nPROBLEM: {msg}", file=sys.stderr)
    sys.exit(1)


def mcp_home() -> Path:
    if CONFIG.exists():
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        return Path(cfg.get("mcp_home", HOME / ".showrunner-os/davinci-resolve-mcp"))
    return HOME / ".showrunner-os/davinci-resolve-mcp"


def connect_bridge():
    """Connect to Resolve through the free-edition bridge, re-running this
    script under the MCP server's own Python when needed."""
    home = mcp_home()
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
    except Exception as exc:  # noqa: BLE001 - one clear message for students
        fail("could not reach DaVinci Resolve. Is Resolve open, with your "
             "project open, and did you run Workspace > Scripts > "
             f"resolve_bridge this session? (detail: {exc})")


def find_existing_clip(media_pool, file_path: str):
    """Look for the clip in the media pool root so reruns do not duplicate it."""
    try:
        for clip in media_pool.GetRootFolder().GetClipList() or []:
            if clip.GetClipProperty("File Path") == file_path:
                return clip
    except Exception:  # noqa: BLE001 - a fresh import is a fine fallback
        pass
    return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cutlist")
    parser.add_argument("--project", default=None,
                        help="Resolve project to use (default: the open one)")
    parser.add_argument("--timeline", default="Fast Track Cut")
    args = parser.parse_args()

    cutlist_path = Path(args.cutlist).expanduser()
    if not cutlist_path.exists():
        fail(f"file not found: {cutlist_path}")
    cutlist = json.loads(cutlist_path.read_text(encoding="utf-8"))
    media_file = cutlist["media"]
    segments = cutlist["segments"]
    fps = cutlist["fps"]
    if not segments:
        fail("the cutlist has no segments")
    if not Path(media_file).exists():
        fail(f"the source recording is missing: {media_file}")

    resolve = connect_bridge()
    print(f"Connected to {resolve.GetProductName()} {resolve.GetVersionString()}",
          flush=True)

    pm = resolve.GetProjectManager()
    project = pm.GetCurrentProject()
    if args.project:
        loaded = pm.LoadProject(args.project)
        project = loaded or project
    if not project:
        fail("no project is open in Resolve. Open one (or create one) first.")
    print(f"Project: {project.GetName()}", flush=True)

    # The timeline must run at the footage's frame rate, and the setting only
    # takes effect when set before the timeline is created.
    fps_str = str(int(round(fps)) if float(fps).is_integer() else fps)
    project.SetSetting("timelineFrameRate", fps_str)

    # The playback frame rate does NOT follow the timeline frame rate when the
    # project is driven through the API, and the API cannot change it (verified
    # read-only on Resolve 21 free). Left at its default (24), a 60fps cut
    # plays in slow motion. Detect it and hand the human the exact fix.
    playback = project.GetSetting("timelinePlaybackFrameRate")
    if playback and float(playback) != float(fps):
        print(f"""
NOTE: this project's playback frame rate is {playback}, but the footage is
{fps_str} fps, so the preview will play in slow motion until you fix it
(one time per project, in Resolve):

    Project Settings (gear icon, bottom right) > Master Settings >
    Playback frame rate -> {fps_str} > Save

The timeline itself and the final render are unaffected.
""", flush=True)

    media_pool = project.GetMediaPool()
    clip = find_existing_clip(media_pool, media_file)
    if clip is None:
        print("Importing the recording into the media pool...", flush=True)
        imported = media_pool.ImportMedia([media_file])
        if not imported:
            fail("Resolve could not import the recording. Check the file plays "
                 "in Resolve when dropped in by hand.")
        clip = imported[0]

    name = args.timeline
    timeline = media_pool.CreateEmptyTimeline(name)
    version = 2
    while timeline is None and version < 20:
        name = f"{args.timeline} v{version}"
        timeline = media_pool.CreateEmptyTimeline(name)
        version += 1
    if timeline is None:
        fail("could not create a timeline")
    print(f"Timeline: {name}", flush=True)

    print(f"Assembling {len(segments)} segments...", flush=True)
    batch = [{"mediaPoolItem": clip,
              "startFrame": s["startFrame"],
              "endFrame": s["endFrame"]} for s in segments]
    appended = []
    for i in range(0, len(batch), 25):
        chunk = batch[i:i + 25]
        result = media_pool.AppendToTimeline(chunk)
        if not result or len([r for r in result if r]) != len(chunk):
            fail(f"Resolve rejected segments {i + 1}-{i + len(chunk)}. "
                 "Nothing after that point was added; the timeline so far is "
                 "kept. Re-run after checking those ranges in the cutlist.")
        appended.extend(result)
        print(f"  {min(i + 25, len(batch))}/{len(batch)}", flush=True)

    # Red REVIEW markers where the cut-safety pass flagged a boundary.
    offset = 0
    marked = 0
    for seg in segments:
        length = seg["endFrame"] - seg["startFrame"]
        if seg.get("flags"):
            timeline.AddMarker(max(0, offset), "Red", "REVIEW",
                               "; ".join(seg["flags"]), 1)
            marked += 1
        offset += length

    pm.SaveProject()
    kept_min = cutlist.get("keptDuration", 0) / 60
    print(f"\nDone. {len(segments)} segments on '{name}' "
          f"({kept_min:.1f} min), {marked} red REVIEW markers.")
    print("Open the Edit page in Resolve and scrub the cut. Ask for any fix "
          "in plain language, or make it by hand.")


if __name__ == "__main__":
    main()
