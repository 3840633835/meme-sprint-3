#!/bin/sh
# Re-verify determinism and gate limits for meme-sprint-3.
# - main.py (stdlib only): run twice, outputs must be byte-identical.
# - generate.py (needs Pillow): run twice, outputs must be byte-identical.
# - PNG must be 1024x1024 and at most 1 MiB.
set -e
cd "$(dirname "$0")"

rm -rf /tmp/ms3-test1 /tmp/ms3-test2
MAKEFUN_OUTPUT_DIR=/tmp/ms3-test1 python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/ms3-test2 python3 main.py
cmp /tmp/ms3-test1/entry.png /tmp/ms3-test2/entry.png
cmp /tmp/ms3-test1/entry.png entry.png
echo "entrypoint: two runs byte-identical, identical to repo entry.png"

if python3 -c "import PIL" 2>/dev/null; then
  rm -rf /tmp/ms3-gen1 /tmp/ms3-gen2
  mkdir -p /tmp/ms3-gen1 /tmp/ms3-gen2
  MAKEFUN_OUTPUT_DIR=/tmp/ms3-gen1 python3 generate.py
  MAKEFUN_OUTPUT_DIR=/tmp/ms3-gen2 python3 generate.py
  cmp /tmp/ms3-gen1/entry.png /tmp/ms3-gen2/entry.png
  cmp /tmp/ms3-gen1/entry.png entry.png
  echo "generator: two runs byte-identical, identical to repo entry.png"
else
  echo "generator check skipped: Pillow not installed"
fi

python3 - <<'EOF'
import os, struct
p = "entry.png"
data = open(p, "rb").read()
assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
w, h = struct.unpack(">II", data[16:24])
assert (w, h) == (1024, 1024), f"dimensions {w}x{h}, expected 1024x1024"
assert len(data) <= 1048576, f"{len(data)} bytes exceeds 1 MiB"
print(f"gate: PNG {w}x{h}, {len(data)} bytes (<= 1048576) OK")
EOF
echo "ALL CHECKS PASSED"
