#!/usr/bin/env python3
"""Hot-leg 1429 SUPPLEMENT — deferred feed shape-checks + missed leg4 targets.
Bounded ~200s. Read-only except hot-leg-seen.json (own file) + own run file."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1429-supplement"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-12 14:29 WIB supplement", "started_wib": now_wib}

def curl(url, timeout=10, data=None):
    cmd = ["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout + 5).stdout
    except Exception:
        return b""

def curl_json(url, timeout=10):
    try:
        return json.loads(curl(url, timeout).decode(errors="replace"))
    except Exception:
        return None

FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeamount", "free_supply", "freeslots", "free_slots",
              "freeminted", "freemint", "freesupply"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def shape_check(a):
    abi_j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 6)
    abi = None
    if isinstance(abi_j, dict):
        abi = abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
    if not abi:
        return {"status": "shape-check-failed", "note": "ABI unfetchable (404 or error)"}
    names = set()
    for fn in abi:
        if isinstance(fn, dict) and fn.get("type") in ("function", None):
            names.add((fn.get("name") or "").lower())
    has_mint = any("mint" in n for n in names)
    has_quote = any(("quote" in n or n in ("cost", "price", "mintprice", "getprice")) for n in names)
    free_views = sorted(n for n in names if n in FREE_VIEWS or "free" in n)
    agent = any(("agent" in n and ("registry" in n or "gate" in n or "id" in n)) or n in
                ("agentregistry", "agentgate", "agent_id_registry", "registry") for n in names)
    src = json.dumps(abi).lower()
    agent = agent or ("agent_id_registry" in src) or ("agentgate" in src) or (REGISTRY[2:].lower() in src)
    is_token = any(n in names for n in ("name", "symbol", "decimals", "totalsupply"))
    has_mintfree = "mintfree" in names
    s1 = has_mint and has_quote and bool(free_views) and agent
    s2 = is_token and has_mintfree and bool(free_views) and agent
    return {"status": "checked", "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free_views, "agent": agent, "n_fns": len(names)}

# ---- Deferred feed shape-checks (8) ----
seen = json.load(open(BASE + "hot-leg-seen.json"))
deferred = ["0xB87ebc35b58f6237cA8921Ef66f5635Ac52385db",
            "0x028Dd48C8AC32aaC79ECC06f0263e9e83b8bac21",
            "0x200C3E42d4d46d80379202E823837972C66058ae",
            "0x887293486fDAD6e4d1de334F11384fe016572137",
            "0x9B8b27CBFde73289F1E65065Df4712E91241588F",
            "0x15FDb41946aD61aE54408da904A9e39170Bb43ED",
            "0xC7EeFd0302a52e6C535C7D17Ad3595ABe0F0f001",
            "0x5515Ec89047E91eD6f639F23FdDf784293CDFcB5"]
shapes = {}
for a in deferred:
    if time.time() > T0 + 60:
        shapes[a] = {"status": "shape-check-deferred", "note": "supplement deadline, retry next run"}
        continue
    shapes[a] = shape_check(a)
    time.sleep(0.1)
out["deferred_shape"] = {a: {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
                         for a, s in shapes.items()}
for a, s in shapes.items():
    if isinstance(seen.get(a), dict):
        seen[a]["status"] = s.get("status", "checked")
        seen[a]["note"] = (f"SUPPLEMENT {now_wib}: S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} "
                          f"quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}")
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Missed leg4 targets (8, promotion-relevant first) ----
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
LEG4_DEADLINE = T0 + 190
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
    ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"),
    ("AGCR", "0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc"),
    ("SEVEN", "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96"),
    ("WFPASS", "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C"),
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
changes = []
try:
    prev = json.load(open(BASE + "run-2026-11-12-1419-verify2.json"))["reads"]
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
out["leg4_changes_vs_1419"] = changes

# ---- Stampooor site retry (pages.dev flipped 200->000 this run) ----
def site_check(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "8", "-w", "%{http_code} %{size_download}",
                            url], capture_output=True, timeout=12)
        return r.stdout.decode(errors="replace").strip()
    except Exception: return "000 0"
out["stampooor_site_retry"] = {"root_com": site_check("https://stampooor.com/"),
                               "pages_dev_packs": site_check("https://stampooor.pages.dev/packs/")}

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
