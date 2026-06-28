#!/usr/bin/env python3
"""
build-release.py - build the clean, player-facing Windows zip for a GitHub Release.

Run from the repo root:   python build-release.py
Output: ../TheOtServer-Client-Windows.zip  (the EXACT asset name download.php serves)

Excludes all dev-only material - above all host_local.lua (the local 127.0.0.1 toggle) -
and ABORTS if that file would ever end up in the zip, so a release can't leak it.
"""
import os, sys, zipfile, fnmatch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(os.path.dirname(HERE), "TheOtServer-Client-Windows.zip")
TOP  = "TheOtServer"   # extracts into a clean TheOtServer/ folder

EXCLUDE_DIRS  = {".git", "_design_handoff", "_skin_backup"}
EXCLUDE_FILES = [
    "host_local.lua", "host_local.example.lua",          # DEV localhost toggle - NEVER ship
    "*.theotbak", "otcv8.zip.bak-*", "otcv8.zip.theotbak",
    "*.log", "*_preview.png", "dlgwin_view.png",
    ".gitignore", ".gitattributes", "build-release.py",
    "otclient_mac", "otclient_linux", "otclientv8.apk",  # Windows-only zip
]
skip = lambda n: any(fnmatch.fnmatch(n, p) for p in EXCLUDE_FILES)

if os.path.exists(OUT):
    os.remove(OUT)
count = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if skip(f):
                continue
            full = os.path.join(root, f)
            z.write(full, os.path.join(TOP, os.path.relpath(full, HERE)))
            count += 1

# Safety gate: the dev/localhost file must never be in a public download.
leaked = [n for n in zipfile.ZipFile(OUT).namelist() if "host_local.lua" in n]
if leaked:
    os.remove(OUT)
    sys.exit("ABORTED: host_local.lua would have shipped -> " + str(leaked))

mb = os.path.getsize(OUT) / 1048576
print(f"Built {OUT}")
print(f"{count} files, {mb:.1f} MB | host_local.lua shipped: NO (verified)")
print("Next: publish a new GitHub Release and attach this file as exactly")
print("      TheOtServer-Client-Windows.zip  (download.php auto-serves the latest release).")
