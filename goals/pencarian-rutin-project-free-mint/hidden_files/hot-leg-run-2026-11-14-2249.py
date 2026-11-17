#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-14 22:49 WIB (fresh implementation for this run).
Legs: (1) Sourcify feed (already fetched to run-2026-11-14-2249-sourcify.json),
(2) Boltbook en+zh (already fetched), (3) shape-check new feed contracts,
(4) re-read snapshot focus set from run-2026-11-14-2244-reread.json via batch
eth_call (ABI-driven calldata), bridge read-only.
Writes ONLY run-2026-11-14-2249*.json + hot-leg-seen.json updates.
Never writes main snapshot / main seen files. No preview, no mint, no signing.
"""
import json, re, subprocess, time, urllib.request, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-14-2249"
NOW = time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time() + 7 * 3600))
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
out = {"run": "free-mint-hot-leg " + NOW, "started_wib": NOW}

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/2249"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_n_prev = len(seen)
seen_lower = {k.lower() for k in seen}

# --- (1) feed (pre-fetched) ---
feed = json.load(open(BASE + "run-" + TAG + "-sourcify.json"))
results = feed.get("results", [])
feed_addrs = [r["address"] for r in results]
new_feed = [a for a in feed_addrs if a.lower() not in seen_lower]
out["sourcify_feed"] = {"total": len(results), "new": len(new_feed),
                        "new_contracts": new_feed,
                        "top": feed_addrs[0] if feed_addrs else None,
                        "top_verifiedAt": results[0].get("verifiedAt") if results else None}

# --- (2) boltbook (pre-fetched) ---
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
boltbook_new = []
for lang in ("en", "zh"):
    html = open(BASE + "run-" + TAG + f"-boltbook-{lang}.html").read()
    addrs = sorted(set(ADDR_RE.findall(html)))
    newb = [a for a in addrs if a.lower() not in seen_lower]
    boltbook_new.extend(a for a in newb if a not in boltbook_new)
    out["boltbook_" + lang] = {"bytes": len(html), "full_address_contracts": len(addrs),
                               "new": len(newb), "new_contracts": newb}

# --- (3) shape-check new contracts ---
FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeCardsRemaining"}
def shape(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        meta = json.loads(get(url, timeout=20).decode())
        abi = meta.get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate"})
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in names
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and \
             bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "has_mint": has_mint,
                "has_quote": has_quote, "free_views": free_views, "agent_ref": agent_ref,
                "is_token": is_token, "n_fns": len(names), "status": "checked"}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

to_shape = list(dict.fromkeys(new_feed + boltbook_new))
shapes = []
if to_shape:
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        shapes = list(ex.map(shape, to_shape))
va = {r["address"]: r.get("verifiedAt") for r in results}
for s in shapes:
    s["verifiedAt"] = va.get(s["address"])
out["shape_check_targets"] = to_shape
out["shape_check"] = shapes
out["shape_hits"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]

# --- bridge (read-only) ---
def collect_addrs(obj, acc):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", k):
                acc.add(k.lower())
            collect_addrs(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_addrs(v, acc)
    elif isinstance(obj, str) and re.fullmatch(r"0x[0-9a-fA-F]{40}", obj):
        acc.add(obj.lower())

try:
    bridge = json.load(open(BASE + "scan-bridge.json"))
    cons = bridge.get("contracts", {})
    snap = set()
    snapj = json.load(open(BASE + "onchain-snapshot.json"))
    collect_addrs(snapj, snap)
    not_in_snap = [a for a in cons if a.lower() not in snap]
    out["bridge"] = {"contracts": len(cons),
                     "same_owner_discarded": sum(1 for c in cons.values() if c.get("same_owner_discarded")),
                     "not_in_snapshot": len(not_in_snap),
                     "not_in_snapshot_list": not_in_snap[:10]}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- (4) re-read focus set (ABI-driven calldata) ---
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def post_rpc(ep, payload, timeout=120):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(r)

def fetch_abi(addr):
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                              timeout=20).decode())
        return {e["name"]: e for e in meta.get("abi", []) if e.get("type") == "function"}
    except Exception:
        return {}

def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

prev = json.load(open(BASE + "run-2026-11-14-2244-reread.json"))
prev_reads = prev.get("reads", {})
items = [(name, d["address"], list((d.get("views") or {}).keys()))
         for name, d in prev_reads.items() if d.get("address")]
out["reread_items"] = len(items)

abis = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for (name, addr, _), ab in zip(items, ex.map(fetch_abi, [a for _, a, _ in items])):
        abis[name] = ab

calls, meta = [], []
for name, addr, labels in items:
    ab = abis.get(name, {})
    for label in labels:
        fn = ab.get(label)
        if not fn:
            continue
        inputs = fn.get("inputs", [])
        sig = label + "(" + ",".join(i.get("type", "") for i in inputs) + ")"
        data = sel(sig)
        ok = True
        for i in inputs:
            t = i.get("type", "")
            if t == "address":
                data += USER[2:].lower().rjust(64, "0")
            elif t.startswith("uint") or t.startswith("int"):
                data += format(0, "064x")
            else:
                ok = False
        if not ok:
            continue
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        meta.append((name, label))

reads, ok_n = {}, 0
CH = 60
for ci in range(0, len(calls), CH):
    chunk = calls[ci:ci + CH]
    chunk_meta = meta[ci:ci + CH]
    got = None
    for ep in EPS:
        try:
            res = post_rpc(ep, chunk, timeout=120)
            if isinstance(res, list) and len(res) == len(chunk):
                got = res
                break
        except Exception:
            continue
    if got is None:
        print(f"reread chunk {ci//CH + 1} FAIL", flush=True)
        continue
    for it, (name, label) in zip(got, chunk_meta):
        if isinstance(it, dict) and "error" not in it and it.get("result") not in (None, "0x"):
            r = it["result"]
            v = to_int(r[:66]) if len(r) >= 66 else r
            reads.setdefault(name, {})[label] = v
            ok_n += 1
        else:
            reads.setdefault(name, {})[label] = None
    print(f"reread chunk {ci//CH + 1} ok ({time.time()-t0:.0f}s)", flush=True)
    time.sleep(1)

blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
        if isinstance(r, dict) and r.get("result"):
            blk = int(r["result"], 16)
            break
    except Exception:
        continue

full_reads = {}
for name, addr, labels in items:
    full_reads[name] = {"address": addr, "views": reads.get(name, {})}
reread = {"started_wib": NOW, "reads": full_reads, "reads_ok": ok_n,
          "reads_total": len(calls), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)
out["reread"] = {"reads_ok": ok_n, "reads_total": len(calls), "block": blk,
                 "elapsed_s": reread["elapsed_s"]}

changes = []
for name, cur in full_reads.items():
    pv = (prev_reads.get(name) or {}).get("views") or {}
    cv = cur.get("views") or {}
    for k, v in cv.items():
        if pv.get(k) != v:
            changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})
out["reread_changes_vs_2244"] = changes
out["reread_prev_block"] = prev.get("block")

# --- update seen with new contracts ---
added = 0
for a in to_shape:
    if a.lower() not in seen_lower:
        s = next((x for x in shapes if x.get("address") == a), None)
        st = "SALE-SHAPE" if s and (s.get("S1") or s.get("S2")) else \
             ("checked-not-sale-shape" if s and "error" not in s else "shape-check-failed")
        seen[a] = {"first_seen_wib": NOW,
                   "source": "sourcify-feed" if a in new_feed else "boltbook-en+zh",
                   "status": st, "note": str(s)[:300] if s else ""}
        seen_lower.add(a.lower())
        added += 1
if added:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
out["seen_added"] = added
out["seen_n"] = len(seen)
out["seen_n_prev"] = seen_n_prev
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps(out, indent=1))
