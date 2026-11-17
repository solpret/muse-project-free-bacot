#!/usr/bin/env python3
"""free-mint-hot-leg 0944 recovery pass (ONE bounded attempt, not a loop).
Recovers legs degraded by Sourcify IncompleteRead/RemoteDisconnected flakiness
in the main 0944 run: (a) shape-check the 2 new feed contracts whose ABI fetch
failed, (b) one Boltbook en+zh fetch, (c) re-fetch ABIs for the 42 reread focus
items + one batch eth_call pass. Updates run-2026-11-15-0944.json,
run-2026-11-15-0944-reread.json and hot-leg-seen.json (own state only).
Never touches the main snapshot. No preview/mint/signing.
"""
import json, re, subprocess, time, urllib.request, concurrent.futures, http.client
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-0944"
PREV_TAG = "2026-11-15-0934"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()
rec = {"recovery_pass": True, "started_wib": time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time() + 7 * 3600))}

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/0944-recovery"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def get_resilient(url, timeout=25):
    # urllib raises IncompleteRead when the server closes early; http.client
    # lets us read whatever arrived and retry once.
    for attempt in range(2):
        try:
            return get(url, timeout=timeout)
        except Exception as e:
            if attempt == 0 and ("IncompleteRead" in type(e).__name__ or "RemoteDisconnected" in type(e).__name__):
                time.sleep(2)
                continue
            raise

FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeCardsRemaining"}
def shape(addr):
    try:
        meta = json.loads(get_resilient(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi").decode())
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
        return {"address": addr, "S1": s1, "S2": s2, "n_fns": len(names), "status": "checked"}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:150]}"}

# (a) the 2 new feed contracts whose shape-check failed in the main run
new_failed = ["0xFd0B35D8f1b114266FCDAF65f7044B2181b825Ae",
              "0xBF179db5dA977D5283742346199Cba63aedFF9f1"]
shapes = list(concurrent.futures.ThreadPoolExecutor(max_workers=2).map(shape, new_failed))
rec["shape_retry_new"] = shapes
rec["shape_hits_recovery"] = [s["address"] for s in shapes if s.get("S1") or s.get("S2")]

# (b) one Boltbook en+zh fetch
seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_lower = {k.lower() for k in seen}
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
boltbook_new = []
for lang, url in (("en", "https://boltbook.fun/?lang=en"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = get_resilient(url).decode("utf-8", "replace")
        open(BASE + "run-" + TAG + f"-boltbook-{lang}.html", "w").write(html)
        addrs = sorted(set(ADDR_RE.findall(html)))
        newb = [a for a in addrs if a.lower() not in seen_lower]
        boltbook_new.extend(a for a in newb if a not in boltbook_new)
        rec["boltbook_" + lang] = {"bytes": len(html), "full_address_contracts": len(addrs),
                                   "new": len(newb), "new_contracts": newb}
    except Exception as e:
        rec["boltbook_" + lang] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
if boltbook_new:
    bshapes = list(concurrent.futures.ThreadPoolExecutor(max_workers=5).map(shape, boltbook_new))
    rec["shape_check_boltbook"] = bshapes
    rec["shape_hits_recovery"] += [s["address"] for s in bshapes if s.get("S1") or s.get("S2")]
    for a, s in zip(boltbook_new, bshapes):
        if a.lower() not in seen_lower:
            st = "SALE-SHAPE" if (s.get("S1") or s.get("S2")) else \
                 ("checked-not-sale-shape" if "error" not in s else "shape-check-failed")
            seen[a] = {"first_seen_wib": rec["started_wib"], "source": "boltbook-en+zh-recovery",
                       "status": st, "note": str(s)[:300]}
            seen_lower.add(a.lower())
# update seen status for the 2 new feed contracts if now checkable
for s in shapes:
    a = s["address"]
    if "error" not in s and isinstance(seen.get(a), dict) and seen[a].get("status") == "shape-check-failed":
        seen[a] = {"first_seen_wib": seen[a].get("first_seen_wib", rec["started_wib"]),
                   "source": "sourcify-feed", "status": "SALE-SHAPE" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape",
                   "note": str(s)[:300]}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
rec["seen_n"] = len(seen)

# (c) reread: re-fetch ABIs for the 42 focus items, rebuild calls from 0934 labels
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
        meta = json.loads(get_resilient(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi").decode())
        return {e["name"]: e for e in meta.get("abi", []) if e.get("type") == "function"}
    except Exception:
        return {}
def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return None

prev = json.load(open(BASE + "run-" + PREV_TAG + "-reread.json"))
prev_reads = prev.get("reads", {})
items = [(name, d["address"], list((d.get("views") or {}).keys()))
         for name, d in prev_reads.items() if d.get("address")]
abis = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
    for (name, addr, _), ab in zip(items, ex.map(fetch_abi, [a for _, a, _ in items])):
        abis[name] = ab
rec["reread_abi_ok"] = sum(1 for ab in abis.values() if ab)
rec["reread_abi_total"] = len(abis)
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
        print(f"recovery reread chunk {ci//CH + 1} FAIL", flush=True)
        continue
    for it, (name, label) in zip(got, chunk_meta):
        if isinstance(it, dict) and "error" not in it and it.get("result") not in (None, "0x"):
            r = it["result"]
            v = to_int(r[:66]) if len(r) >= 66 else r
            reads.setdefault(name, {})[label] = v
            ok_n += 1
        else:
            reads.setdefault(name, {})[label] = None
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
# merge with the main run's partial reads (main run's 12 reads stand unless recovery re-read them)
main_rr = json.load(open(BASE + "run-" + TAG + "-reread.json"))
full_reads = {}
for name, addr, labels in items:
    merged = dict((main_rr.get("reads", {}).get(name) or {}).get("views", {}))
    merged.update(reads.get(name, {}))
    full_reads[name] = {"address": addr, "views": merged}
reread = {"started_wib": main_rr.get("started_wib"), "recovery_wib": rec["started_wib"],
          "reads": full_reads, "reads_ok": ok_n + main_rr.get("reads_ok", 0),
          "reads_total": len(calls), "block": blk or main_rr.get("block"),
          "elapsed_s": round(time.time() - t0, 1)}
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)
changes = []
for name, cur in full_reads.items():
    pv = (prev_reads.get(name) or {}).get("views") or {}
    cv = cur.get("views") or {}
    for k, v in cv.items():
        if pv.get(k) != v:
            changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})
rec["reread"] = {"reads_ok": reread["reads_ok"], "reads_total": len(calls), "block": reread["block"]}
rec["reread_changes_vs_" + PREV_TAG] = changes
rec["elapsed_s"] = round(time.time() - t0, 1)

# patch the main run JSON with recovery results + assessment
run = json.load(open(BASE + "hot-leg-run-" + TAG + ".json"))
run["recovery"] = rec
run["reread"] = {"reads_ok": reread["reads_ok"], "reads_total": len(calls),
                 "block": reread["block"], "elapsed_s": reread["elapsed_s"]}
run["reread_changes_vs_" + PREV_TAG] = changes
run["seen_n"] = len(seen)
json.dump(run, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps(rec, indent=1))
