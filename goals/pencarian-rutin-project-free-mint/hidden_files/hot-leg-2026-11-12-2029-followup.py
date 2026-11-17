#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 20:29 WIB - follow-up leg4-lite (bounded ~170s).
Re-reads the 24 leg4 targets skipped on deadline in the main run, priority order.
Read-only except own run file. Never writes main snapshot / main seen files."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-2029"
T0 = time.time()
DEADLINE = T0 + 170
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"followup": "free-mint-hot-leg 2026-11-12 20:29 WIB leg4-lite", "started_wib": now_wib}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=2) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    res = post_rpc_race(calls, timeout=12)
    if res is None:
        return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "mintStart()",
         "freeLeft()", "freeAvailable(address)", "saleStart()", "saleEnd()", "PRICE()",
         "price()", "launched()", "freeSharesLeft()", "openedAt()", "freeSharesRemaining()",
         "freeClaimedByWallet(address)", "currentState()", "finalized()", "refunding()",
         "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]
TARGETS = [
    ("OliverAgents", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("POCKET", "0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102"),
    ("Pathwyrm", "0xf100c608913dc07ed268bea865fca10004f04657"),
    ("Kitebots", "0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0"),
    ("DACIT", "0x90ddd762f407b3edf43f732cd5a68a9e4695a6bd"),
    ("0x7Eb9", "0x7Eb92041aa3037e39baA88154F279e3D9F85c593"),
    ("Snailings", "0x5d8f22549fdba6a437c40564d2a65664e714034b"),
    ("RAMRAIDERS", "0x98dcfdeb5e015bbb3c9aca2a90ba0ee80e35315b"),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"),
    ("NOVA2", "0xdbbc87ae7734e4a16958426f204e6f79ce92e630"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("0x016b9CE7", "0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7"),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
    ("AgenticGangster", "0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("Ronin", "0xF62FA2ee1490708D51DeF7212493D5c7878Fa110"),
    ("DragonAgent", "0xaa87b6B3eCDD3202A80d109A91e88783ffFb0BE6"),
    ("Kongtou-AirdropCnNFT", "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"),
]
try:
    r = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}], timeout=10)
    out["block"] = int(r[0]["result"], 16) if isinstance(r, list) and r else None
except Exception:
    out["block"] = None

reads = {}
for name, addr in TARGETS:
    if time.time() > DEADLINE:
        reads[name] = {"address": addr, "error": "deadline-hit-skipped"}; continue
    v = raw_batch(addr, VIEWS)
    reads[name] = {"address": addr, "views": v}
    if v: reads[name]["summary"] = {k: x for k, x in v.items() if x is not None}
out["reads"] = reads

# Compare vs 2019 + 2029 main baselines
changes = []
try:
    prev = {}
    for f in ("hot-leg-run-2026-11-12-2019.json", "run-2026-11-12-2019-verify2.json",
              "hot-leg-2026-11-12-2019-followup.json",
              "hot-leg-run-2026-11-12-2029.json", "run-2026-11-12-2029-verify2.json",
              "hot-leg-run-2026-11-12-1959.json", "run-2026-11-12-1959-verify2.json",
              "hot-leg-2026-11-12-1959-followup.json"):
        try:
            d = json.load(open(BASE + f))
            for _n, _e in (d.get("leg4_reads") or d.get("reads") or {}).items():
                if _n in prev: continue
                _v = _e.get("views") if isinstance(_e, dict) else None
                if _v: prev[_n] = _e
        except Exception:
            pass
    for name, e in reads.items():
        if "views" not in e or not e["views"]: continue
        pv = (prev.get(name, {}) or {}).get("views") or {}
        for k, v in e["views"].items():
            if v is None: continue
            if k in pv and pv[k] is not None and pv[k] != v:
                changes.append(f"{name}.{k}: {pv[k]} -> {v}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["changes"] = changes
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-{TAG}-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
