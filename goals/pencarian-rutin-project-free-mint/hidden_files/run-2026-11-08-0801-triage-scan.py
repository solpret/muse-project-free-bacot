#!/usr/bin/env python3
"""Run 2026-11-08 0801 triage: HokiPanda 0x4b61...4517 (only first-seen
among 70 enriched). READ-ONLY; writes run-2026-11-08-0801-triage-scan.*
only. Single-call batches (batch reverts if one view reverts).
First-mint check via Ankr getLogs chunked <=1000 blocks; block timestamp
via dataseed eth_getBlockByNumber (Ankr timestamps are FAKE - never use)."""
import sys, json, time, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import batch
from ankr import ankr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0801"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x4b61A7767dA68f18266907b2Eb7C9A1EE3d24517"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

log = open(f"{BASE}/run-{TS}-triage-scan.log", "w")
def p(*a):
    print(*a, flush=True)
    print(*a, file=log, flush=True)

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def single(addr, data):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return res[0]
        except Exception:
            continue
    return None
def view(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    return to_int(single(addr, data))
def addr_view(addr, sig):
    r = single(addr, sel(sig))
    if r is None: return None
    try: return "0x" + r[-40:]
    except Exception: return None

out = {"contract": ADDR, "name": "HokiPanda", "symbol": "HPANDA",
       "scan": {"first_block": 132301457, "mint_count": 43, "distinct_minters": 43,
                "registry_bytes_hit": True, "sourcify": "verified",
                "free_shaped": ["FREE_CAP", "FREE_PER_WALLET", "freeCount", "freeMint", "freeMinted"]}}
d = {}
for sig in ["totalMinted()", "FREE_CAP()", "FREE_PER_WALLET()", "freeMinted()",
            "mintOpen()", "PRICE()", "paidMintedCount()", "paidUnlocked()"]:
    d[sig.split("(")[0]] = view(ADDR, sig)
    time.sleep(0.15)
d["freeCount_user"] = view(ADDR, "freeCount(address)", USER)
d["balanceOf_user"] = view(ADDR, "balanceOf(address)", USER)
d["owner"] = addr_view(ADDR, "owner()")
d["agentIdRegistry"] = addr_view(ADDR, "agentIdRegistry()")
d["treasury"] = addr_view(ADDR, "treasury()")
out["views"] = d
p("views: " + json.dumps(d))

# first-mint check: any Transfer-from-zero to this contract BEFORE window start 132301401?
for (fb, tb) in [(132300401, 132301400), (132299401, 132300400)]:
    try:
        body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(fb),
            "toBlock": hex(tb), "pageSize": 1000, "decodeLogs": False,
            "topics": [TRANSFER, ZERO_TOPIC],
            "address": [ADDR.lower()]}, timeout=30)
        n = len(body.get("result", {}).get("logs", []))
    except Exception as e:
        n = f"ERROR {e}"
    p(f"pre-window mints {fb}-{tb}: {n}")
    out.setdefault("pre_window_mints", {})[f"{fb}-{tb}"] = n

# first mint in-window: earliest Transfer-from-zero at/after 132301401
try:
    body = ankr_post("ankr_getLogs", {"blockchain": "bsc", "fromBlock": hex(132301401),
        "toBlock": hex(132301457), "pageSize": 1000, "decodeLogs": False,
        "topics": [TRANSFER, ZERO_TOPIC], "address": [ADDR.lower()]}, timeout=30)
    logs = body.get("result", {}).get("logs", [])
    p(f"in-window mints 132301401-132301457: {len(logs)}")
    out["first_mint_logs_in_window"] = len(logs)
    if logs:
        out["first_mint_tx"] = logs[0].get("transactionHash")
        out["first_mint_to"] = "0x" + logs[0]["topics"][2][-40:] if len(logs[0].get("topics", [])) > 2 else None
except Exception as e:
    p(f"in-window first-mint check ERROR: {e}")
    out["first_mint_logs_in_window"] = f"ERROR {e}"

# block timestamp for first-mint block via dataseed (never Ankr)
ts = None
for ep in EPS:
    try:
        res = batch([("eth_getBlockByNumber", [hex(132301457), False])], endpoint=ep, timeout=10)
        ts = int(res[0]["timestamp"], 16)
        break
    except Exception:
        continue
out["first_mint_block"] = 132301457
out["first_mint_timestamp_utc"] = ts
if ts:
    wib = datetime.datetime.fromtimestamp(ts, datetime.timezone(datetime.timedelta(hours=7)))
    out["first_mint_wib"] = wib.strftime("%Y-%m-%d %H:%M:%S")
    p(f"first mint block 132301457 ts={ts} WIB={out['first_mint_wib']}")
else:
    p("first mint block timestamp FAILED (all dataseeds)")

# same-owner check vs bridge + known factory group
try:
    bridge = json.load(open(f"{BASE}/scan-bridge.json"))
    disc = bridge.get("same_owner_discarded", {})
    out["bridge_same_owner_discarded_keys"] = list(disc.keys())[:50]
    out["bridge_same_owner_discarded_count"] = len(disc)
    owners = set()
    for k, v in disc.items():
        if isinstance(v, dict):
            o = v.get("owner") or v.get("owner_address")
            if o: owners.add(o.lower())
        elif isinstance(v, str) and v.startswith("0x"):
            owners.add(v.lower())
    out["owner_in_bridge_discarded"] = (d["owner"].lower() in owners) if d.get("owner") else None
    out["owner_is_known_factory_a054"] = (d.get("owner","").lower() == "0xa054275580c6d1c9077543907ac5798f2494ecce")
    p(f"owner={d.get('owner')} in_bridge_discarded={out['owner_in_bridge_discarded']} factory_a054={out['owner_is_known_factory_a054']}")
except Exception as e:
    p(f"bridge check ERROR: {e}")
    out["bridge_error"] = str(e)

# classification
free_cap = d.get("FREE_CAP"); free_minted = d.get("freeMinted")
free_pct = (free_minted / free_cap * 100) if (free_cap and free_minted is not None) else None
out["free_pct_verified"] = free_pct
slot_open = (d.get("freeCount_user") == 0) if d.get("freeCount_user") is not None else None
out["user_slot_open"] = slot_open
p(f"free% verified: {free_pct} (freeMinted={free_minted}/{free_cap}); user freeCount={d.get('freeCount_user')} slot_open={slot_open}; mintOpen={d.get('mintOpen')}; PRICE={d.get('PRICE')} wei; agentIdRegistry={d.get('agentIdRegistry')} (registry={REGISTRY})")
json.dump(out, open(f"{BASE}/run-{TS}-triage-scan.json", "w"), indent=1)
p("triage JSON written")
log.close()
