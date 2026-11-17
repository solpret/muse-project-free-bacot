#!/usr/bin/env python3
"""One retry pass for missing meta fields in run 5 (not aggressive)."""
import json, sys, time
from pathlib import Path
from Crypto.Hash import keccak
sys.path.insert(0, str(Path.home() / "workspace/fast_exec"))
import fast_rpc
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def decode_str(hexdata):
    try:
        b = bytes.fromhex(hexdata[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        s = b[off+32:off+32+ln].decode(errors="replace")
        return s if s != "ERROR" else None
    except Exception:
        return None
d = json.load(open("/tmp/tracked-scan-run5-detail.json"))
meta = d["meta"]
targets = {
 "0x1591f1ed9f3dbec3a922dc63f5782daf17eeba1e": ["name()", "owner()"],
 "0x1cf9e60218493149ace7dc953497c07175aa625e": ["owner()"],
 "0xacf150d9ec909e3d339bf4c6d090b18495674e66": ["name()", "symbol()"],
 "0xd8e24465f2f5a8fb9b3b24e3042f26a4b10c020f": ["name()", "symbol()"],
}
for c, fns in targets.items():
    for fn in fns:
        key = "name" if fn == "name()" else "symbol" if fn == "symbol()" else "owner"
        val = None
        for attempt in range(2):
            try:
                r = fast_rpc.race("eth_call", [{"to": c, "data": sel(fn)}, "latest"])
                if fn == "owner()":
                    val = ("0x" + r[-40:]) if r and len(r) >= 42 else None
                else:
                    val = decode_str(r) if r else None
                break
            except Exception as e:
                print(c, fn, "attempt", attempt, "ERROR", str(e)[:150], flush=True)
                time.sleep(10)
        if val: meta[c][key] = val
        print(c, key, "->", val, flush=True)
        time.sleep(8)
json.dump(d, open("/tmp/tracked-scan-run5-detail.json", "w"), indent=1)
print("saved", flush=True)
