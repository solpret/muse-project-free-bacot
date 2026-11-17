#!/usr/bin/env python3
"""Hot-leg 0644 recovery part 2: Boltbook EN+ZH (curl), bridge (read-only),
binanceai launched() + RigForge re-check. Bounded ~90s.
Writes run-2026-11-12-0644-legs2.json."""
import json, re, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
t0 = time.time()
out = {"started_wib": "2026-11-12 06:44 WIB (recovery)"}

ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
    html = None
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "30", url], capture_output=True, text=True, timeout=35)
        if r.stdout and len(r.stdout) > 1000:
            html = r.stdout
    except Exception as e:
        print(f"BOLTBOOK {lang}: curl fail {e}", flush=True)
    if html:
        addrs = sorted(set(a for a in ADDR_RE.findall(html)))
        out[f"boltbook_{lang}"] = {"bytes": len(html), "addrs": addrs, "n": len(addrs)}
        open(BASE + f"run-2026-11-12-0644-boltbook-{lang}.html", "w").write(html)
        print(f"BOLTBOOK {lang}: {len(html)} bytes, {len(addrs)} addrs", flush=True)
    else:
        out[f"boltbook_{lang}"] = {"bytes": 0, "error": "curl failed", "addrs": []}
        print(f"BOLTBOOK {lang}: FAIL", flush=True)

seen = set()
try:
    hl = json.load(open(BASE + "hot-leg-seen.json"))
    seen |= {k.lower() for k in hl.keys()}
except Exception:
    pass
try:
    snap = json.load(open(BASE + "onchain-snapshot.json"))
    snap_addrs = {str((v or {}).get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    snap_addrs |= {str((v or {}).get("address") or (v or {}).get("sale") or "").lower() for v in snap.get("track_c", {}).values() if isinstance(v, dict)}
except Exception:
    snap = {}
    snap_addrs = set()
bb_new = []
for lang in ("en", "zh"):
    for a in out.get(f"boltbook_{lang}", {}).get("addrs", []):
        if a.lower() not in seen and a.lower() not in snap_addrs and a not in bb_new:
            bb_new.append(a)
out["boltbook_new"] = bb_new
print("BOLTBOOK NEW:", bb_new, flush=True)

try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    bcontracts = bridge.get("contracts", {})
    snap_addrs_l = {str((v or {}).get("address", "")).lower() for v in snap.get("contracts", {}).values() if isinstance(v, dict)}
    not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs_l]
    discarded = [a for a in bcontracts if bcontracts[a].get("same_owner_discarded")]
    out["bridge"] = {"total": len(bcontracts), "not_in_snapshot": not_in_snap,
                     "same_owner_discarded": discarded}
    print("BRIDGE total", len(bcontracts), "not_in_snapshot", len(not_in_snap), "discarded", len(discarded), flush=True)
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    print("BRIDGE FAIL", e, flush=True)

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT = "masgayut.ai"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def eth_call(to, data):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": to, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "20", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=25)
            res = json.loads(r.stdout)
            if "result" in res:
                return res["result"]
        except Exception:
            continue
    return None
def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

BIN_MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
val = eth_call(BIN_MINT, sel("launched()"))
out["binanceai"] = {"launched_raw": val, "launched": (to_int(val) == 1) if val else None}
print("BINANCEAI launched:", out["binanceai"], flush=True)

RIG_SALE = "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d"
rig = {}
rig["freeSharesLeft"] = to_int(eth_call(RIG_SALE, sel("freeSharesLeft()")))
rig["openedAt"] = to_int(eth_call(RIG_SALE, sel("openedAt()")))
rig["freeClaimed"] = to_int(eth_call(RIG_SALE, sel("freeClaimed()")))
def enc_dyn_string(s):
    b = s.encode()
    pad = (32 - len(b) % 32) % 32
    return (32).to_bytes(32, "big").hex() + len(b).to_bytes(32, "big").hex() + b.hex() + "00" * pad
rig["freeTaken_agentId"] = to_int(eth_call(RIG_SALE, sel("freeTaken(string)") + enc_dyn_string(AGENT)))
rig["freeBooked_user"] = to_int(eth_call(RIG_SALE, sel("freeBooked(address)") + enc(USER)))
rig["sharesLeftFor_agentId"] = to_int(eth_call(RIG_SALE, sel("sharesLeftFor(string)") + enc_dyn_string(AGENT)))
out["rigforge"] = rig
print("RIGFORGE:", rig, flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-12-0644-legs2.json", "w"), indent=1)
print("LEGS2 DONE in", out["elapsed_s"], "s", flush=True)
