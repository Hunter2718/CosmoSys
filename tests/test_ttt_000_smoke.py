#!/bin/env python3
# SPDX-License-Identifier: MIT

import subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_dev_ok():
    cp = subprocess.run([str(ROOT/"tools"/"dev.py")], capture_output=True, text=True)
    assert cp.returncode == 0
    assert "DEV OK" in cp.stdout
