#!/usr/bin/env python3
"""Hot-leg run 2026-11-12 12:54 WIB — supplement: (a) shape-check the 5 feed
contracts deferred at the T0+70 shape deadline (they are already in seen.json
with status shape-check-deferred, so the next run's retry leg — which only
retries shape-check-failed — would never pick them up); (b) re-read the 13
leg-4 targets whose batches returned None after the T0+195 leg-4 deadline.
Read-only except hot-leg-seen.json status/note updates for (a). Bounded 120s."""
import json, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-1254"
T0 = time.time()
DEADLINE = T0 + 120
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-12 12:54 WIB supplement", "started_wib": now_wib}

def curl(url, timeout=8):
    try:
        r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""

def curl_json(url, timeout=8):
    try:
        return json.loads(curl(url, timeout).decode(errors="replace"))
    except Exception:
        return None

seen = json.load(open(BASE + "hot-leg-seen.json"))
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
    is_token = all(n in names for n in ("name", "symbol", "decimals", "totalsupply"))
    has_mintfree = "mintfree" in names
    s1 = has_mint and has_quote and bool(free_views) and agent
    s2 = is_token and has_mintfree and bool(free_views) and agent
    return {"status": "checked", "S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free_views, "agent": agent, "n_fns": len(names)}

# (a) deferred shape-checks
DEFERRED = ["0x4AaF642c225143b32608FdBbe222457E68745c5e",
            "0xC07Edb0d2C998267fB8472CB48A2398ee7ACC183",
            "0x3Bf11e4a03f33c79d1F8b644209A7957a3A36b8B",
            "0x9a46A988cE4c7Fb982E87cF7cfb64088b5C09afc",
            "0x4d68A7Aa5DE2862924c94e0ED0433e94023FCa5d"]
out["deferred_shape"] = {}
for a in DEFERRED:
    if time.time() > DEADLINE:
        out["deferred_shape"][a] = {"status": "still-deferred", "note": "supplement deadline"}
        continue
    s = shape_check(a)
    out["deferred_shape"][a] = {k: s.get(k) for k in ("S1", "S2", "mint", "quote", "free", "agent", "status")}
    if isinstance(seen.get(a), dict):
        if s.get("status") == "checked":
            seen[a]["status"] = "checked"
            seen[a]["note"] = (f"SUPPLEMENT {now_wib}: ABI now fetchable — S1={s.get('S1')} S2={s.get('S2')} "
                               f"mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}")
        else:
            seen[a]["note"] = (seen[a].get("note", "") + f" | supplement {now_wib}: still 404").strip()[:400]
    time.sleep(0.1)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# (b) leg-4 tail re-read
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def post_rpc(ep, payload, timeout=12):
    outb = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                           "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                          capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(outb)
def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=12)
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
        if time.time() > DEADLINE: return None
        try:
            res = post_rpc(ep, calls, timeout=12)
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
    if time.time() > DEADLINE:
        reads[name] = {"address": addr, "error": "deadline-hit-skipped"}; continue
    r = raw_batch(addr, VIEWS)
    reads[name] = {"address": addr, "views": r}
    if r: reads[name]["summary"] = {k: v for k, v in r.items() if v is not None}
out["leg4_tail_block"] = block
out["leg4_tail_reads"] = reads
json.dump({"started_wib": now_wib, "block": block, "reads": reads,
           "elapsed_s": round(time.time() - T0, 1)},
          open(BASE + f"run-{TAG}-verify2-supplement.json", "w"), indent=1)

# compare tail vs 1249 reads
changes = []
try:
    prev = json.load(open(BASE + "run-2026-11-12-1249-verify2.json"))["reads"]
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
out["leg4_tail_changes_vs_1249"] = changes
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + f"hot-leg-run-{TAG}-supplement.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
