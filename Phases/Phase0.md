<!-- SPDX-License-Identifier: MIT -->

# CosmoSys — Phase 0 (TTT‑0.x)

**Goal:** lock in a fast, repeatable dev loop + basic CI + security guardrails before touching real kernel code.

---

## Objectives

* One command to build/run tests (`tools/dev.py`).
* Pytest green on a tiny smoke test.
* CI green on clean clone.
* Security gates: banned C APIs + secrets scan (deny by default mindset from day 0).

> Tip: Phase 0 is *tiny, total, testable*. Don’t overbuild—just enough to make everything after this smooth.

---

## Prereqs (Arch)

```bash
sudo pacman -S --needed qemu-full clang lld make nasm python python-virtualenv git ripgrep
python -m venv .venv && source .venv/bin/activate && pip install pytest
```

---

## TTT‑0.1 — Repo + Dev Loop

**Scope:** repo skeleton, `tools/dev.py` prints `DEV OK`.

**Files**

```
cosmosys/
├─ tools/dev.py
├─ tests/ttt_00_smoke.py
└─ docs/ttt-00.md
```

**tools/dev.py**

```python
#!/usr/bin/env python3
import os, sys
print("DEV OK")
sys.exit(0)
```

**tests/ttt\_00\_smoke.py**

```python
import subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]

def test_dev_ok():
    cp = subprocess.run([str(ROOT/"tools"/"dev.py")], capture_output=True, text=True)
    assert cp.returncode == 0
    assert "DEV OK" in cp.stdout
```

**docs/ttt-00.md**

```md
# TTT-0.1 Repo + Dev Loop
Goal: Single command confirms env works.
Pass: `tools/dev.py` prints DEV OK (pytest sees it).
```

**Run:** `pytest -q` → **PASS**

---

## TTT‑0.2 — CI Smoke (GitHub Actions)

**Scope:** CI that runs the smoke test on push/PR.

**.github/workflows/ci.yml**

```yaml
name: ci
on: [push, pull_request]
jobs:
  smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: |
          python -m venv .venv
          source .venv/bin/activate
          pip install pytest
          pytest -q
```

**Pass:** CI green on a clean clone.

---

## TTT‑0.3 — Licensing

**Scope:** pick licenses and commit files.

* **Kernel:** `LICENSE.kernel` = GPL‑2.0‑only.
* **Tools/scripts/docs:** `LICENSE.tools` = MIT OR Apache‑2.0.

**Pass:** Licenses present; headers added to new source files going forward.

---

## Security TTTs (Phase 0)

### S‑0.1 — Banned C APIs gate

**Scope:** add a CI step that fails on dangerous APIs.

**banned\_apis.txt**

```
strcpy
strcat
sprintf
gets(
strncpy(\s*[^,]*,\s*[^,]*,\s*[^)]{0,5}\)
scanf(\s*"%s")
memcpy\s*\(\s*[^,]+\s*,\s*[^,]+\s*,\s*0x?[0-9a-fA-F]{1,2}\s*\)
```

**Add to CI**

```yaml
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "Scanning for banned C APIs";
          if rg -n -f banned_apis.txt --glob '!**/third_party/**' --glob '!**/*.md' || true; then
            # rg exits 0 if matches found; flip to failure if any real C/C++ files matched
            MATCHES=$(rg -n -f banned_apis.txt --glob '!**/third_party/**' --glob '!**/*.md' | wc -l);
            [ "$MATCHES" -eq 0 ] || (echo "Banned APIs found" && exit 1);
          fi
```

**Pass:** CI fails if any banned patterns appear in repo.

> We’ll refine as code arrives (allow safe wrappers, etc.).

### S‑0.2 — Basic secrets scan

**Scope:** regex checks for common secrets/keys in CI.

**Add to CI**

```yaml
  secrets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "Secrets scan";
          rg -n --hidden --no-ignore -e 'BEGIN (RSA|EC|PRIVATE) KEY' -e '(password|token|secret)\s*=' -e '[A-Za-z0-9_\.-]+@[A-Za-z0-9_-]+\.[A-Za-z\.-]+' || true
          COUNT=$(rg -n --hidden --no-ignore -e 'BEGIN (RSA|EC|PRIVATE) KEY' -e '(password|token|secret)\s*=' | wc -l);
          [ "$COUNT" -eq 0 ] || (echo "Potential secrets found" && exit 1)
```

**Pass:** CI fails if key material or obvious secrets are committed.

---

## What’s next

* When TTT‑0.x and S‑0.x are green, jump to **Phase 1** (already in the other canvas): Limine boot + serial + panic tests.
* Keep Phase 0 CI blocks around as we grow; they’ll guard every PR.

---

## Definition of Done (Phase 0)

* `pytest` passes locally.
* CI is green on smoke + lint + secrets.
* Licenses committed.
* You can type **one command** and get a deterministic PASS.

