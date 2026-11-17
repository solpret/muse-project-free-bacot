#!/usr/bin/env python3
"""Hot-leg 2026-11-10 19:29 early-lead probe: re-read today's early leads
(NIGHTFORGE, EMBERANVIL, NIGHTFORGE B, Cosmic Sentinel, Sakura, Cinder
Agents, Arcane Stones, HackouCoinPass) for free-% promotion. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc.nodereal.io/"
T0 = time.time()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
def decode(r):
    if not isinstance(r, str) or not r.startswith("0x"): return None
    try: return int(r, 16)
    except Exception: return None

ITEMS = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
 "EMBERANVIL": ("0x7673c596a6702d32f844266dc2ca7b1fd6d7df21", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
 "NIGHTFORGE B": ("0x051f04ff7b095793613b9caac197cc1051c24e2b", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
 "Cosmic Sentinel": ("0x88731d1eb41c36f3d705fdb58b658244c06afc36", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
 "Sakura": ("0xF2705A84602369069782624279837A08bdbBf6D6", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
 "Cinder Agents": ("0x49966cf050a5a9cedd252184875267c0e93dbc00", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
 "Arcane Stones": ("0x23f3De28E55C392F24A217B2B1602C90e0292f35", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
 "HackouCoinPass": ("0xA96f20BCeD857d3174Bb40e806b0151daeEaa62e", ["totalSupply","freeClaimed","freeMinted","freeLeft","FREE_SUPPLY","FREE_CAP","mintOpen"]),
}
USERF = ["balanceOf","mintedBy","freeClaimed","freeLeft","freeUsed","freeAvailable"]

def run_batch(calls):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-s", "--max-time", "30", "-X", "POST", EP,
                        "-H", "Content-Type: application/json", "--data", payload],
                       capture_output=True, text=True)
    try: return json.loads(p.stdout)
    except Exception: return {"_curl_error": p.stdout[:200] + p.stderr[:200]}

p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST", EP,
                    "-H", "Content-Type: application/json",
                    '--data', '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'],
                   capture_output=True, text=True)
try: block = int(json.loads(p.stdout)["result"], 16)
except Exception: block = None

calls, meta = [], []
for name, (addr, fields) in ITEMS.items():
    for f in fields:
        calls.append((addr, sel(f"{f}()"))); meta.append((name, f))
    for f in USERF:
        calls.append((addr, sel(f"{f}(address)") + enc_addr(USER))); meta.append((name, f + "_user"))
resp_all = []
for i in range(0, len(calls), 25):
    r = run_batch(calls[i:i+25])
    if isinstance(r, dict) and "_curl_error" in r:
        resp_all.extend([{}] * len(calls[i:i+25]))
    else:
        if isinstance(r, dict): r = [r]
        resp_all.extend(r)
resp = resp_all
out = {"block": block, "items": {}, "duration_sec": round(time.time() - T0, 1)}
for j, (name, f) in enumerate(meta):
    it = resp[j] if j < len(resp) else {}
    v = decode(it.get("result")) if isinstance(it, dict) else None
    out["items"].setdefault(name, {})[f] = v
# promotion evaluation
prev = json.load(open(BASE + "hot-leg-2026-11-10-1909-early-probe.json"))
prev_items = prev.get("items", {})
promo = []
for name, row in out["items"].items():
    free = row.get("freeMinted", row.get("freeClaimed"))
    cap = row.get("FREE_SUPPLY", row.get("FREE_CAP"))
    if isinstance(free, int) and isinstance(cap, int) and cap > 0:
        pct = free / cap
        user_open = row.get("freeClaimed_user") in (0, False, None) and row.get("balanceOf_user") == 0
        prev_free = (prev_items.get(name, {}) or {}).get("freeMinted", (prev_items.get(name, {}) or {}).get("freeClaimed"))
        promo.append({"item": name, "free": free, "cap": cap, "pct": round(pct, 4),
                      "prev_free": prev_free, "user_open": user_open,
                      "verdict": "STRONG (>=25% + slot open)" if pct >= 0.25 and user_open else
                                 ("sellout" if free >= cap else "stays early")})
    else:
        prev_free = (prev_items.get(name, {}) or {}).get("freeMinted", (prev_items.get(name, {}) or {}).get("freeClaimed"))
        promo.append({"item": name, "free": free, "cap": cap, "pct": None,
                      "prev_free": prev_free, "user_open": row.get("balanceOf_user") == 0,
                      "verdict": "free % unverified - stays early"})
out["promotion_eval"] = promo
json.dump(out, open(BASE + "hot-leg-2026-11-10-1929-early-probe.json", "w"), indent=1)
print(json.dumps(out, indent=1))
