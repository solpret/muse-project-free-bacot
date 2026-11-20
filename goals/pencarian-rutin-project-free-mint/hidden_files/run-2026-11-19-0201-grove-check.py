#!/usr/bin/env python3
"""Grove-watch run 2026-11-19 02:01 WIB. Read-only: freeOpen() + freeClaimed(user)."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import call_many, race

GROVE = "0x8b710e45D38fD55E2D198d2295c0a0D24EBfd64c"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

t0 = time.time()
out = {"route": None, "block": None, "freeOpen": None, "freeClaimed_user": None}

# Route 1: fast_rpc batch
try:
    blk = int(race("eth_blockNumber", []), 16)
    out["block"] = blk
    fo, fc = call_many([(GROVE, sel("freeOpen()")), (GROVE, sel("freeClaimed(address)") + enc(USER))], timeout=15)
    if to_int(fo) is not None and to_int(fc) is not None:
        out.update(route="fast_rpc", freeOpen=to_int(fo), freeClaimed_user=bool(to_int(fc)))
        print("GROVE", json.dumps(out), flush=True)
        print("DONE", round(time.time() - t0, 1), flush=True)
        sys.exit(0)
    print("GROVE fast_rpc returned None(s)", flush=True)
except Exception as e:
    print("GROVE fast_rpc FAIL", type(e).__name__, str(e)[:120], flush=True)

# Route 2: QuickNode fallback (helper CLI)
qn = "/home/hatch/workspace/custom-connectors/custom.quicknode/bin/quicknode.py"
try:
    for name, data in [("freeOpen", sel("freeOpen()")), ("freeClaimed", sel("freeClaimed(address)") + enc(USER))]:
        params = json.dumps([{"to": GROVE, "data": data}, "latest"])
        r = subprocess.run([sys.executable, qn, "rpc", "--method", "eth_call", "--params", params], capture_output=True, text=True, timeout=90)
        m = re.findall(r"0x[0-9a-fA-F]+", r.stdout or "")
        val = to_int(m[-1]) if m else None
        if val is None:
            print(f"GROVE quicknode {name} FAIL rc={r.returncode} out={r.stdout[:100]!r} err={r.stderr[:100]!r}", flush=True)
            raise RuntimeError(f"quicknode {name} no value")
        out["freeClaimed_user" if name == "freeClaimed" else "freeOpen"] = bool(val) if name == "freeClaimed" else val
    if out["block"] is None:
        try:
            r = subprocess.run([sys.executable, qn, "block"], capture_output=True, text=True, timeout=60)
            m = re.findall(r"0x[0-9a-fA-F]+", r.stdout or "")
            out["block"] = int(m[-1], 16) if m else None
        except Exception:
            pass
    out["route"] = "quicknode"
    print("GROVE", json.dumps(out), flush=True)
    print("DONE", round(time.time() - t0, 1), flush=True)
    sys.exit(0)
except Exception as e:
    out["error"] = str(e)[:150]
    print("GROVE quicknode FAIL", str(e)[:150], flush=True)

print("GROVE-ALL-FAIL", json.dumps(out), flush=True)
sys.exit(1)
