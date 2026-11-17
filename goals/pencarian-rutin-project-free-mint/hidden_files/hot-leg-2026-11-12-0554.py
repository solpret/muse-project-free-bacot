#!/usr/bin/env python3
"""Hot-leg 2026-11-12 05:54 WIB — legs 1+2+4 in one fast script.
Leg 1: Sourcify feed limit 20, shape-check new vs hot-leg-seen.json.
Leg 2: Boltbook EN+ZH front pages, extract addresses.
Leg 4: prio re-read via 5-call batched eth_call (18 items, 0519 set).
Bridge: read-only counts.
Stampooor site: root + /packs/ reachability.
Read-only except hot-leg-seen.json (own file) + own run files."""
import json, re, subprocess, time
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-12-0554"
T0 = time.time()
now_wib = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%dT%H:%M:%S+07:00")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
out = {"run": "free-mint-hot-leg 2026-11-12 05:54 WIB", "started_wib": now_wib}

def curl(url, timeout=12, data=None, headers=None):
    cmd = ["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["-d", data]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""

def curl_json(url, timeout=12):
    raw = curl(url, timeout)
    try:
        return json.loads(raw.decode(errors="replace"))
    except Exception:
        return None

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lc = {k.lower(): k for k in seen}

# ---- Leg 1: Sourcify feed ----
feed = curl_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", 12)
feed_addrs, feed_meta = [], {}
if isinstance(feed, dict):
    items = feed.get("results") or feed.get("contracts") or []
    for it in items:
        a = (it.get("address") or "").strip()
        if a:
            feed_addrs.append(a)
            feed_meta[a] = it.get("verifiedAt") or ""
elif isinstance(feed, list):
    for it in feed:
        a = (it.get("address") or "").strip()
        if a:
            feed_addrs.append(a)
            feed_meta[a] = it.get("verifiedAt") or ""
out["feed"] = {"n": len(feed_addrs),
               "newest_verifiedAt": max(feed_meta.values()) if feed_meta else None,
               "oldest_verifiedAt": min(feed_meta.values()) if feed_meta else None}
json.dump({"addrs": feed_addrs, "meta": feed_meta}, open(BASE + f"run-2026-11-12-0554-feed.json", "w"), indent=1)

FREE_VIEWS = {"freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freesharesclaimed",
              "freeamount", "free_supply", "freeslots", "free_slots",
              "freeminted", "freemint", "freesupply"}
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}

def shape_check(a):
    al = a.lower()
    if al in EXCLUDED or al == REGISTRY:
        return {"status": "excluded-or-registry"}
    abi_j = curl_json(f"https://sourcify.dev/server/v2/contract/56/{a}?fields=abi", 8)
    abi = None
    if isinstance(abi_j, dict):
        abi = abi_j.get("abi") or (abi_j.get("stdJson") or {}).get("abi")
    if not abi:
        return {"status": "shape-check-failed", "note": "ABI unfetchable"}
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

new = [a for a in feed_addrs if a.lower() not in seen_lc]
out["feed_new"] = new
shapes = {}
for a in new:
    shapes[a] = shape_check(a)
    time.sleep(0.15)
out["feed_shape"] = {"s1_pass": [a for a, s in shapes.items() if s.get("S1")],
                     "s2_pass": [a for a, s in shapes.items() if s.get("S2")],
                     "early_shape": [],
                     "shapes": [{"address": a, "S1": bool(s.get("S1")), "S2": bool(s.get("S2")),
                                 "early_shape": False, "has_mint": bool(s.get("mint")),
                                 "has_quote": bool(s.get("quote")), "free_views": s.get("free", []),
                                 "agent_ref": bool(s.get("agent")), "is_token": None,
                                 "is_nft": None, "fn_count": s.get("n_fns")}
                                for a, s in shapes.items()]}
seen_added = 0
for a in new:
    key = seen_lc.get(a.lower())
    if key is None:
        s = shapes.get(a, {})
        seen[a] = {"first_seen_wib": now_wib, "source": "sourcify-feed",
                   "status": s.get("status", "checked"),
                   "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('mint')} quote={s.get('quote')} free={s.get('free')} agent={s.get('agent')}"}
        seen_lc[a.lower()] = a
        seen_added += 1
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_added"] = seen_added

# ---- Leg 2: Boltbook EN + ZH ----
def boltbook(lang):
    url = "https://boltbook.fun/" + ("?lang=zh" if lang == "zh" else "")
    raw = curl(url, 12)
    open(BASE + f"hot-leg-{TAG}-boltbook-{lang}.html", "wb").write(raw)
    return raw.decode(errors="replace")

addrs = set()
for lang in ("en", "zh"):
    html = boltbook(lang)
    found = set(re.findall(r"0x[a-fA-F0-9]{40}", html))
    addrs |= found
    out[f"boltbook_{lang}"] = {"bytes": len(html),
                               "error": None if len(html) > 1000 else "urllib+curl failed",
                               "addrs": sorted(found)}
    time.sleep(0.3)
bb_new = sorted(a for a in addrs if a.lower() not in seen_lc)
out["boltbook_new"] = bb_new
out["boltbook_new_shapecheck"] = {}
for a in bb_new:
    if a.lower() not in seen_lc:
        seen[a] = {"first_seen_wib": now_wib, "source": "boltbook",
                   "status": "boltbook-mention-unchecked", "note": "Boltbook mention run 0554, shape-check pending"}
        seen_lc[a.lower()] = a
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)

# ---- Leg 4: prio re-read, 5-call batches ----
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
U = enc_addr(USER)

ITEMS = {
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459",
   ["freeMinted()", "freeAvailable(address)", "balanceOf(address)", "mintOpen()",
    "totalMinted()", "FREE_SUPPLY()", "freeClaimed(address)"]),
 "Eco": ("0xd31b168F7b6f3dB39BEd89433124595aaa91cfF3",
   ["freeMinted()", "totalMinted()", "FREE_WALLETS()", "freeWalletsLeft()", "freeWalletCount()",
    "MAX_SUPPLY()", "mintOpen()", "mintOpensAt()", "FREE_PER_WALLET()", "balanceOf(address)",
    "freeCountBy(address)", "mintsBy(address)", "holdsAgentId(address)"]),
 "Moonfang": ("0x79b0CE8b39c3Ed230487172751612b4F631398Bc",
   ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)", "mintedBy(address)"]),
 "AGCR": ("0x5491f2341a178d35c7bbb82bd1ed37330f3d01cc",
   ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
    "freeAvailable(address)", "balanceOf(address)", "freeClaimed(address)", "mintOpen()"]),
 "MECHA": ("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
   ["totalSupply()", "totalMinted()", "freeClaimed()", "FREE_SUPPLY()", "MAX_SUPPLY()",
    "freeAvailable(address)", "balanceOf(address)"]),
 "WFPASS": ("0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
   ["mintOpen()", "freeMinted()", "totalMinted()", "totalSupply()", "balanceOf(address)"]),
 "CRTSAINTS": ("0x2A3dFcBf3b4c881d571598e926bE694f919FDa0F",
   ["totalSupply()", "firstFreeUsed()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "paidMinted()",
    "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)"]),
 "BUCKET": ("0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
   ["totalSupply()", "totalFreeCount()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "mintOpenedAt()",
    "balanceOf(address)", "freeUsed(address)"]),
 "MOONDRILL": ("0x87b354E2014D2e418927A1105dD219A2e7b063b0",
   ["totalSupply()", "firstFreeUsed()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "paidMinted()",
    "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)", "freeMinted()"]),
 "0x2e50": ("0x2e508C6510d9550031932f0D6Fe691DCe38E66E3",
   ["totalSupply()", "firstFreeUsed()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "paidMinted()",
    "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)", "freeMinted()"]),
 "ORIGAMIX": ("0x43CAb600E87B0F96e7a310049774797FC3DF5756",
   ["totalSupply()", "firstFreeUsed()", "FIRST_FREE_CAP()", "X_FREE_CAP()", "paidMinted()",
    "mintOpen()", "balanceOf(address)", "firstFreeByWallet(address)", "freeMinted()"]),
 "CAP7-Obrigado": ("0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd",
   ["totalSupply()", "freeMinted()", "phase()", "sharesMinted()", "soldOut()",
    "balanceOf(address)", "freeClaimed(address)"]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb",
   ["totalSupply()", "totalMinted()", "freeMinted()", "FREE_CAP()", "balanceOf(address)"]),
 "RIGFORGE": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
   ["freeSharesLeft()", "openedAt()", "freeClaimed()"]),
 "BINANCEAI": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
   ["launched()"]),
 "SEVEN": ("0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
   ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)"]),
 "Pickgrid": ("0x7f541bcc33abed0e64455565da723e949c6f76f0",
   ["totalSupply()", "freeMinted()", "FREE_CAP()", "mintOpen()", "balanceOf(address)"]),
 "SUDOSAINTS": ("0x869d330bb48e7ab32da16745ef9a36a69d34f12f",
   ["totalSupply()", "freeMinted()", "FREE_CAP()", "FREE_SUPPLY()", "mintOpen()", "balanceOf(address)"]),
}
# field name mapping: fn -> key used in 0519 json
def fname(sig):
    n = sig.split("(")[0]
    if n == "balanceOf": return "balanceOf_user"
    if n in ("freeAvailable", "freeClaimed", "freeCountBy", "mintsBy", "holdsAgentId",
             "mintedBy", "freeUsed", "firstFreeByWallet"): return n + "_user"
    return n

CALLS = []
for name, (addr, sigs) in ITEMS.items():
    for sig in sigs:
        args = U if "(address)" in sig else ""
        CALLS.append((f"{name}.{fname(sig)}", addr, sig, args))

EPS = ("https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.defibit.io/",
       "https://bsc.nodereal.io/")
block = None
for ep in EPS:
    try:
        r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                            "-d", json.dumps({"jsonrpc": "2.0", "id": 0, "method": "eth_blockNumber", "params": []}), ep],
                           capture_output=True, timeout=15)
        j = json.loads(r.stdout.decode(errors="replace"))
        if j.get("result"):
            block = int(j["result"], 16)
            out["leg4_block"] = block
            break
    except Exception:
        continue

results = {}
notes = []
CHUNK = 5
for ci in range(0, len(CALLS), CHUNK):
    chunk = CALLS[ci:ci + CHUNK]
    batch = [{"jsonrpc": "2.0", "id": i, "method": "eth_call",
              "params": [{"to": addr, "data": sel(sig) + args}, "latest"]}
             for i, (key, addr, sig, args) in enumerate(chunk)]
    done = False
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", "20", "-H", "Content-Type: application/json",
                                "-d", json.dumps(batch), ep],
                               capture_output=True, timeout=25)
            arr = json.loads(r.stdout.decode(errors="replace"))
            if isinstance(arr, list) and arr and all("result" in it or "error" in it for it in arr):
                for item in arr:
                    i = item.get("id")
                    if i is None or i >= len(chunk):
                        continue
                    key = chunk[i][0]
                    if "error" in item:
                        results[key] = None
                    else:
                        res = item.get("result")
                        if res in (None, "0x"):
                            results[key] = None
                        elif len(res) >= 66:
                            try:
                                results[key] = int(res[2:66], 16)
                            except Exception:
                                results[key] = None
                        else:
                            results[key] = None
                done = True
                break
        except Exception:
            continue
    if not done:
        for key, _, _, _ in chunk:
            results[key] = None
        notes.append(f"chunk@{ci} failed all endpoints")
    time.sleep(0.4)

# restructure into per-item dicts like 0519
reread = {}
for name, (addr, sigs) in ITEMS.items():
    d = {"address": addr}
    all_null = True
    for sig in sigs:
        key = f"{name}.{fname(sig)}"
        v = results.get(key)
        d[fname(sig)] = v
        if v is not None:
            all_null = False
    if all_null:
        d["read_failure_all_null"] = True
    reread[name] = d
out["leg4_reread"] = reread
out["leg4_notes"] = notes

# ---- Stampooor site check ----
def site_check(url):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-m", "10", "-w", "%{http_code} %{size_download}",
                            url], capture_output=True, timeout=15)
        return r.stdout.decode(errors="replace").strip()
    except Exception:
        return "000 0"
out["stampooor_site"] = {"root": site_check("https://stampooor.com/"),
                         "packs": site_check("https://stampooor.com/packs/")}

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
