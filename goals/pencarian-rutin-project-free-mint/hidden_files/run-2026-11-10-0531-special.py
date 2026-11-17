#!/usr/bin/env python3
"""Run 0531 special checks (read-only): binanceai.fun track-B state,
SAKURA + Golden Agents contractURI/tokenURI (methods H/I), THYRK re-read.
Curl transport via dataseed (25s), like the 0431 reread script.
Writes run-2026-11-10-0531-special.json (never touches snapshot/state)."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
OUT = f"{BASE}/run-2026-11-10-0531-special.json"
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_hex(addr, data):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "result" in r and r["result"] not in (None, "0x"):
                return r["result"]
            if isinstance(r, dict) and "error" in r:
                continue
        except Exception:
            continue
    return None

def raw_int(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    return to_int(raw_hex(addr, data))

def decode_string(hexv):
    """Decode an ABI-encoded string return (0x + offset + len + data)."""
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 96: return None
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"<decode-error {e}>"

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

out = {"block": get_block(), "started_wib": "2026-11-10 05:31 WIB", "binanceai": {}, "sakura": {}, "golden": {}, "thyrk": {}}
print("BLOCK", out["block"], flush=True)

# --- binanceai.fun ---
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN = "0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
for sig in ["launched()", "failed()", "isRefundPhase()", "totalShares()"]:
    out["binanceai"][sig[:-2]] = raw_int(MINT, sig)
out["binanceai"]["tokenClaimed_user"] = raw_int(MINT, "tokenClaimed(address)", USER)
out["binanceai"]["tokenBalance_user"] = raw_int(TOKEN, "balanceOf(address)", USER)
print("BINANCEAI", out["binanceai"], flush=True)

# --- SAKURA: contractURI + tokenURI(1) ---
SAK = "0xF2705A84602369069782624279837A08bdbBf6D6"
for fn in ["contractURI()", "tokenURI(uint256)"]:
    sig = fn
    data = sel(sig) + (enc("1").replace("0"*63+"1", "0"*63+"1") if "uint256" in sig else "")
    if "uint256" in sig:
        data = sel(sig) + "0"*63 + "1"
    hx = raw_hex(SAK, data)
    out["sakura"][fn] = decode_string(hx) if hx else None
    print("SAKURA", fn, "->", str(out["sakura"][fn])[:200], flush=True)
out["sakura"]["totalSupply"] = raw_int(SAK, "totalSupply()")
out["sakura"]["freeClaimed_user"] = raw_int(SAK, "freeClaimed(address)", USER)
out["sakura"]["balanceOf_user"] = raw_int(SAK, "balanceOf(address)", USER)

# --- Golden Agents: contractURI + tokenURI(1) ---
GLD = "0x4233C62919CC03168a361C547117c1553C375bfC"
for fn in ["contractURI()", "tokenURI(uint256)"]:
    data = sel(fn) + ("0"*63 + "1" if "uint256" in fn else "")
    hx = raw_hex(GLD, data)
    out["golden"][fn] = decode_string(hx) if hx else None
    print("GOLDEN", fn, "->", str(out["golden"][fn])[:200], flush=True)
out["golden"]["totalSupply"] = raw_int(GLD, "totalSupply()")
out["golden"]["balanceOf_user"] = raw_int(GLD, "balanceOf(address)", USER)
out["golden"]["freeClaimed_user"] = raw_int(GLD, "freeClaimed(address)", USER)

# --- THYRK (hot-leg 0524 early lead, not yet in snapshot) ---
THY = "0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e"
for sig in ["totalSupply()", "freeMinted()", "mintActive()"]:
    out["thyrk"][sig[:-2]] = raw_int(THY, sig)
out["thyrk"]["balanceOf_user"] = raw_int(THY, "balanceOf(address)", USER)
out["thyrk"]["freeClaimed_user"] = raw_int(THY, "freeClaimed(address)", USER)
hx = raw_hex(THY, sel("contractURI()"))
out["thyrk"]["contractURI()"] = decode_string(hx) if hx else None
print("THYRK", out["thyrk"], flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
with open(OUT, "w") as f: json.dump(out, f, indent=1)
print("SPECIAL DONE in", out["elapsed_s"], "s ->", OUT, flush=True)
