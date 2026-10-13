"""Compatibility entry point for the five automotive proposal emails."""

import argparse
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sender-name", help="旧オプション。差出人名は共通設定を使用します")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--company", choices=("toun", "toshima", "kyowa", "kimura", "kworks"))
    group.add_argument("--all", action="store_true")
    parser.add_argument("--send", action="store_true")
    args = parser.parse_args()
    tool = Path(__file__).resolve().parents[1] / "local-web-sales" / "cli.py"
    command = [sys.executable, str(tool), "send" if args.send else "check"]
    command += ["--group", "auto"] if args.all else ["--company", args.company]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
