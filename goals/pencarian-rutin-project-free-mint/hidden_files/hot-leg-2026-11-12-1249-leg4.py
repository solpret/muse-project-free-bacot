#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 12:49 WIB — leg4-only continuation (legs 1-2+retry completed
before service restart killed the parent run; seen.json already saved)."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1249"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-12 12:49 WIB leg4-only", "started_wib": now_wib}
# ---- Leg 4: re-read (priority order, RigForge first) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
LEG4_DEADLINE = T0 + 195
def post_rpc(ep, payload, timeout=15):
    outb = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                           "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                          capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(outb)
def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            return int(r["result"], 16)
        except Exception: continue
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
    for ep in EPS:
        if time.time() > LEG4_DEADLINE: return None
        try:
            res = post_rpc(ep, calls, timeout=15)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
        except Exception: continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
         "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
         "freeUsed(address)", "mintedBy(address)", "freeMintedBy(address)", "mintStart()",
         "freeLeft()", "freeAvailable(address)", "saleStart()", "saleEnd()", "PRICE()",
         "price()", "launched()", "freeSharesLeft()", "openedAt()", "freeSharesRemaining()",
         "freeClaimedByWallet(address)", "currentState()", "finalized()", "refunding()",
         "totalFreeMinted()", "FREE_SHARES()", "freeLeftFor(address)"]
TARGETS = [
    ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"),
    ("OliverAgents", "0xad86e4d52e55709d1bda08f922853d4b109e0810"),
    ("Stampooor", "0x467696af8c2206B977B24081445104632dc1D459"),
    ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("0x016b9CE7", "0x016b9CE7508628e4Fb19E4fAF3129Fdc41b150d7"),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("BUCKET", "0x2b0d3b384C341020aed1d49907b5708C423bA6DA"),
    ("MOONDRILL", "0x87b354E2014D2e418927A1105dD219A2e7b063b0"),
    ("CRTSAINTS", "0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F"),
    ("SUDOSAINTS", "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"),
    ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0"),
    ("LuckyCatch", "0xD405C90079c594DA2456F5b37B4158A12f1382e5"),
    ("BinanceLife", "0x4367b86F889014e6fD57fE812B86A581b913C645"),
    ("0x2e50", "0x2e508C6510d9550031932f0D6Fe691DCe38E66E3"),
    ("Kongtou-AirdropCnNFT", "0xb5A132A2Efd8351DA2c04e38E2568dd8DC5b1c1a"),
    ("0x7Eb9", "0x7Eb92041aa3037e39baA88154F279e3D9F85c593"),
    ("NAOMI", "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9"),
    ("AgenticGangster", "0x0a2a07ef09dd7d83e2312476f0588abaa3e34ce3"),
]
block = get_block()
reads = {}
for name, addr in TARGETS:
    if time.time() > LEG4_DEADLINE:
        reads[name] = {"address": addr, "error": "deadline-hit-skipped"}; continue
    r = raw_batch(addr, VIEWS)
    reads[name] = {"address": addr, "views": r}
    if r: reads[name]["summary"] = {k: v for k, v in r.items() if v is not None}
out["leg4_block"] = block
out["leg4_reads"] = reads
json.dump({"started_wib": now_wib, "block": block, "reads": reads,
           "elapsed_s": round(time.time() - T0, 1)},
          open(BASE + f"run-{TAG}-verify2.json", "w"), indent=1)

# ---- Compare vs 1244 leg4 reads ----
changes = []
try:
    prev = json.load(open(BASE + "run-2026-11-12-1244-verify2.json"))["reads"]
    for name, e in reads.items():
        if "views" not in e or not e["views"]: continue
        p = prev.get(name, {})
        pv = p.get("views") or {}
        for k, v in e["views"].items():
            if v is None: continue
            if k in pv and pv[k] is not None and pv[k] != v:
                changes.append(f"{name}.{k}: {pv[k]} -> {v}")
            elif k not in pv or pv.get(k) is None:
                changes.append(f"{name}.{k}: (new read) {v}")
except Exception as ex:
    changes = [f"compare-error: {ex}"]
out["leg4_changes_vs_1244"] = changes

# ---- Stampooor site ----
def site_check(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "8", "-w", "%{http_code} %{size_download}",
                            url], capture_output=True, timeout=12)
        return r.stdout.decode(errors="replace").strip()
    except Exception: return "000 0"
out["stampooor_site"] = {"root": site_check("https://stampooor.com/")}

# ---- Bridge (read-only) ----
try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    contracts = bridge.get("contracts", {})
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = set()
    for sec in ("contracts", "track_c"):
        for v in snap.get(sec, {}).values():
            if isinstance(v, dict) and v.get("address"):
                snap_addrs.add(v["address"].lower())
    not_in = [a for a in contracts if a.lower() not in snap_addrs]
    disc = [a for a, v in contracts.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge"] = {"total": len(contracts), "not_in_snapshot": not_in,
                     "same_owner_discarded": disc}
except Exception as e:
    out["bridge"] = {"error": str(e)[:120]}

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
