#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload built distributions to PyPI using Twine.

Loads TWINE credentials from a .env file without echoing secrets.
Default env file path: configs/.pypi-token.env
"""

import os
import sys
import glob
import re


def load_env(path: str) -> None:
    if not os.path.isfile(path):
        print(f"ERROR: Env file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"([^=]+)=(.*)", line)
            if m:
                key, val = m.group(1), m.group(2)
                os.environ[key] = val


def main() -> int:
    env_path = os.environ.get("PYPI_ENV_PATH", os.path.join("configs", ".pypi-token.env"))
    load_env(env_path)
    if not os.environ.get("TWINE_USERNAME") or not os.environ.get("TWINE_PASSWORD"):
        print("ERROR: Missing TWINE credentials in env file.", file=sys.stderr)
        return 1
    files = glob.glob(os.path.join("dist", "*"))
    if not files:
        print("ERROR: No distribution files found in dist/", file=sys.stderr)
        return 1

    import subprocess
    cmd = [sys.executable, "-m", "twine", "upload", "--skip-existing"] + files
    result = subprocess.run(cmd, stdout=sys.stdout, stderr=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    rc = main()
    sys.exit(rc)