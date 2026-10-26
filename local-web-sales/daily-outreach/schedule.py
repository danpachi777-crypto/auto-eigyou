#!/usr/bin/env python3
"""Install or inspect the nightly macOS launchd job. Installation never sends now."""

import argparse
import json
import os
import plistlib
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LABEL = "jp.designdan.auto-eigyou.nightly"
PLIST = Path.home() / "Library" / "LaunchAgents" / (LABEL + ".plist")


def definition(hour=21):
    return {
        "Label": LABEL,
        "ProgramArguments": [str(Path(sys.executable).resolve()), str(ROOT / "nightly.py")],
        "WorkingDirectory": str(ROOT.parents[1]),
        "EnvironmentVariables": {"PATH": os.pathsep.join([
            str(Path.home() / ".local" / "bin"), "/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"]),
            "TZ": "Asia/Tokyo"},
        "StartCalendarInterval": {"Hour": hour, "Minute": 0},
        "RunAtLoad": False,
        "ProcessType": "Background",
        "StandardOutPath": str(ROOT / "runs" / "nightly.log"),
        "StandardErrorPath": str(ROOT / "runs" / "nightly-error.log"),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("install", "status", "uninstall", "preview"))
    parser.add_argument("--hour", type=int, choices=range(24), default=21)
    args = parser.parse_args()
    domain = f"gui/{os.getuid()}"
    service = f"{domain}/{LABEL}"
    if args.command == "preview":
        print(plistlib.dumps(definition(args.hour)).decode())
        return
    if args.command == "status":
        result = subprocess.run(["launchctl", "print", service])
        raise SystemExit(result.returncode)
    if args.command == "uninstall":
        subprocess.run(["launchctl", "bootout", service], capture_output=True)
        if PLIST.exists():
            PLIST.unlink()
        print("Nightly outreach disabled.")
        return
    if not (Path.home() / ".local" / "bin" / "codex").is_file():
        raise SystemExit("Codex CLI is not installed at ~/.local/bin/codex")
    readiness = ROOT / "runs" / "preflight.json"
    if not readiness.exists():
        raise SystemExit("Run nightly.py --preflight first; it never sends mail")
    check = json.loads(readiness.read_text())
    if not check.get("ready") or datetime.now().astimezone() - datetime.fromisoformat(check["checked_at"]) > timedelta(days=1):
        raise SystemExit("Nightly connector readiness is not verified; run nightly.py --preflight")
    # launchd uses the system calendar timezone, not the child process TZ.
    if Path("/etc/localtime").resolve().name != "Tokyo":
        raise SystemExit("Set the Mac system timezone to Asia/Tokyo before installing")
    (ROOT / "runs").mkdir(exist_ok=True)
    PLIST.parent.mkdir(parents=True, exist_ok=True)
    running = subprocess.run(["launchctl", "print", service], capture_output=True, text=True)
    if running.returncode == 0 and any(line.strip().startswith("pid =") for line in running.stdout.splitlines()):
        raise SystemExit("A job is running; do not interrupt a possible delivery")
    if PLIST.exists():
        shutil.copy2(PLIST, ROOT / "runs" / "previous-nightly.plist")
        subprocess.run(["launchctl", "bootout", service], capture_output=True)
    with PLIST.open("wb") as stream:
        plistlib.dump(definition(args.hour), stream)
    subprocess.run(["launchctl", "bootstrap", domain, str(PLIST)], check=True)
    subprocess.run(["launchctl", "print", service], check=True)
    print(f"Installed for {args.hour:02}:00 Asia/Tokyo; no job started now.")


if __name__ == "__main__":
    main()
