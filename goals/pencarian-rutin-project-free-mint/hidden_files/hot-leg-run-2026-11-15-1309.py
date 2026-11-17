#!/usr/bin/env python3
"""free-mint-hot-leg run 2026-11-15 13:09 WIB — fresh implementation of the job body.
Legs: (1) Sourcify recently-verified feed limit 20; (2) Boltbook front page
en+zh (boltbook.fun); (3) shape-check S1/S2 for new contracts + bounded retry
(20) of shape-check-failed pool; (4) re-read main-job snapshot focus set
(47 items, baseline run-2026-11-15-1304-reread.json) read-only via batch
eth_call; bridge scan-bridge.json read-only.
Writes ONLY run-2026-11-15-1309*.json/.html + hot-leg-seen.json updates.
Never writes the main snapshot / main seen files. No preview, no mint, no signing.
View signatures are resolved per contract from the Sourcify ABI when available,
falling back to a standard-signature table built into this script.
"""
import json, re, subprocess, time, urllib.request, urllib.error, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-1309"
PREV_TAG = "2026-11-15-1304"
NOW = time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time() + 7 * 3600))
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
t0 = time.time()
out = {"run": "free-mint-hot-leg " + NOW, "started_wib": NOW}

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/1309"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

seen = json.load(open(BASE + "hot-leg-seen.json"))
seen_n_prev = len(seen)
def seen_status(v):
    return v.get("status") if isinstance(v, dict) else "legacy-string"
seen_lower = {k.lower() for k in seen}

# --- (1) Sourcify feed ---
try:
    feed = json.loads(get("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25).decode())
    json.dump(feed, open(BASE + "run-" + TAG + "-sourcify.json", "w"))
    results = feed.get("results", [])
except Exception as e:
    results = []
    out["sourcify_feed_error"] = f"{type(e).__name__}: {str(e)[:200]}"
feed_addrs = [r["address"] for r in results]
new_feed = [a for a in feed_addrs if a.lower() not in seen_lower]
out["sourcify_feed"] = {"total": len(results), "new": len(new_feed),
                        "new_contracts": new_feed,
                        "top": feed_addrs[0] if feed_addrs else None,
                        "top_verifiedAt": results[0].get("verifiedAt") if results else None}

# --- (2) Boltbook en+zh ---
ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")
boltbook_new = []
for lang, url in (("en", "https://boltbook.fun/?lang=en"), ("zh", "https://boltbook.fun/?lang=zh")):
    try:
        html = get(url, timeout=25).decode("utf-8", "replace")
        open(BASE + "run-" + TAG + f"-boltbook-{lang}.html", "w").write(html)
        addrs = sorted(set(ADDR_RE.findall(html)))
        newb = [a for a in addrs if a.lower() not in seen_lower]
        boltbook_new.extend(a for a in newb if a not in boltbook_new)
        out["boltbook_" + lang] = {"bytes": len(html), "full_address_contracts": len(addrs),
                                   "new": len(newb), "new_contracts": newb}
    except Exception as e:
        out["boltbook_" + lang] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- (3) shape-check new + bounded retry of failed pool ---
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

failed_pool = [a for a, v in seen.items() if seen_status(v) == "shape-check-failed"]
out["shape_retry_pool"] = len(failed_pool)
retry = []
try:
    prev_run = json.load(open(BASE + "hot-leg-run-" + PREV_TAG + ".json"))
    prev_retried = {a.lower() for a in prev_run.get("shape_retry", [])}
except Exception:
    prev_retried = set()
for a in failed_pool:
    if a.lower() not in prev_retried:
        retry.append(a)
    if len(retry) >= 20:
        break
out["shape_retry"] = retry

to_shape = list(dict.fromkeys(new_feed + boltbook_new + retry))
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
                     "same_owner_discarded": sum(1 for c in cons.values() if isinstance(c, dict) and c.get("same_owner_discarded")),
                     "not_in_snapshot": len(not_in_snap),
                     "not_in_snapshot_list": not_in_snap[:10]}
except Exception as e:
    out["bridge"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# --- (4) re-read focus set (baseline: 1304 reread JSON, data only) ---
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def enc_str(s):
    b = s.encode()
    # dynamic string: offset 0x20, length, data padded
    data = format(32, "064x") + format(len(b), "064x") + b.hex().ljust(((len(b) + 31) // 32) * 64, "0")
    return data
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

# fallback signature table (name -> (signature, args)) used when no ABI is found
NOARG = {"totalSupply", "totalMinted", "freeMinted", "freeRemaining", "freeLeft",
         "freeSharesLeft", "FREE_POOL", "FREE_MAX", "FREE_SUPPLY", "FREE_CAP",
         "FREE_MINT_CAP", "MAX_SUPPLY", "mintOpen", "saleActive", "mintStart", "mintEnd",
         "mintStartTime", "paused", "launched", "failed", "isRefundPhase", "totalShares",
         "remainingSupply", "standardRemaining", "legendaryRemaining", "freeCount",
         "mintsLeft", "freeMintsLeft", "PRICE", "TOKEN_PRICE", "maxSupply", "AGENT_ID",
         "owner", "currentCommit", "genesisOpen", "genesisStart", "currentCycle",
         "currentExperiment", "totalSnippets", "totalRemnants", "totalSpecimens",
         "claimOpen", "mintActive", "mintOpenTimestamp", "mintPaused", "price",
         "openedAt", "freeBlock", "freeClaimed"}
ADDR1 = {"freeClaimed", "balanceOf", "mintedBy", "mintsBy", "freeUsed", "freeLeft",
         "hasAgentId", "holdsAgentId", "isEligible", "mintedPerWallet", "freeMintedPerWallet",
         "mintedByWallet", "mintCountOf", "hasFreeClaimed", "tokenClaimed", "freeBooked"}
ADDR_TYPES = {"address"}

def fetch_abi(addr):
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20).decode())
        abi = meta.get("abi", [])
        return {e["name"]: e for e in abi if e.get("type") == "function"}
    except Exception:
        return None

def parse_key(key):
    """Split a reread view key into (fn_name, [literal args]).
    Suffixes: _user -> USER address; _1 -> uint 1; _masgayut_ai/_masgayut -> string."""
    parts = key.split("_")
    fn = parts[0]
    args = []
    i = 1
    while i < len(parts):
        p = parts[i]
        if p == "user":
            args.append(("address", USER)); i += 1
        elif p == "masgayut":
            if i + 1 < len(parts) and parts[i + 1] == "ai":
                args.append(("string", "masgayut.ai")); i += 2
            else:
                args.append(("string", "masgayut")); i += 1
        elif p.isdigit():
            args.append(("uint256", int(p))); i += 1
        else:
            args.append(("literal", p)); i += 1
    return fn, args

def resolve_sig(addr, key, abi_map):
    fn, args = parse_key(key)
    if abi_map and fn in abi_map:
        e = abi_map[fn]
        ins = e.get("inputs", [])
        if len(ins) == len(args):
            sig = fn + "(" + ",".join(x.get("type", "") for x in ins) + ")"
            vals = []
            ok = True
            for (kind, val), inp in zip(args, ins):
                t = inp.get("type", "")
                if t == "address" and kind == "address":
                    vals.append(("address", val))
                elif t in ("uint256", "uint", "uint8", "uint64") and kind == "uint256":
                    vals.append(("uint256", val))
                elif t == "string" and kind == "string":
                    vals.append(("string", val))
                else:
                    ok = False
            if ok:
                return sig, vals, "abi"
        # ABI takes exactly one more input than the key supplies and it is an
        # address: assume the user address (e.g. bare key for freeClaimed(address)).
        # Find the address input whose removal leaves the remaining types
        # matching the key's literal args in order.
        if len(ins) == len(args) + 1:
            def type_ok(kind, t):
                return (t == "address" and kind == "address") or \
                       (t in ("uint256", "uint", "uint8", "uint64") and kind == "uint256") or \
                       (t == "string" and kind == "string")
            for j, inp in enumerate(ins):
                if inp.get("type") != "address":
                    continue
                rest = ins[:j] + ins[j + 1:]
                if len(rest) != len(args):
                    continue
                if all(type_ok(kind, x.get("type", "")) for (kind, _), x in zip(args, rest)):
                    sig = fn + "(" + ",".join(x.get("type", "") for x in ins) + ")"
                    vals = []
                    arg_i = 0
                    for k2, inp2 in enumerate(ins):
                        if k2 == j:
                            vals.append(("address", USER))
                        else:
                            kind, val = args[arg_i]
                            vals.append((kind, val))
                            arg_i += 1
                    return sig, vals, "abi+user"
    # fallback table
    if not args and fn in NOARG:
        return fn + "()", [], "fallback-noarg"
    if len(args) == 1 and args[0][0] == "address" and fn in ADDR1:
        return fn + "(address)", [("address", USER)], "fallback-addr1"
    if len(args) == 2 and args[0][0] == "address" and args[1][0] == "uint256":
        return fn + "(address,uint256)", [("address", USER), ("uint256", args[1][1])], "fallback-addr-uint"
    if len(args) == 2 and args[0][0] == "uint256" and args[1][0] == "address":
        return fn + "(uint256,address)", [("uint256", args[0][1]), ("address", USER)], "fallback-uint-addr"
    if len(args) == 1 and args[0][0] == "uint256":
        return fn + "(uint256)", [("uint256", args[0][1])], "fallback-uint1"
    if len(args) == 1 and args[0][0] == "string":
        return fn + "(string)", [("string", args[0][1])], "fallback-string"
    return None, None, "unresolved"

def build_data(sig, vals):
    d = sel(sig)
    for kind, val in vals:
        if kind == "address":
            d += enc_addr(val)
        elif kind == "uint256":
            d += enc_u(int(val))
        elif kind == "string":
            d += enc_str(val)
    return d

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
def post_rpc(ep, payload, timeout=150):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(r)

prev_main = json.load(open(BASE + "run-" + PREV_TAG + "-reread.json"))
prev_reads = prev_main.get("reads", {})
ITEMS = {}
for name, v in prev_reads.items():
    views = v.get("views")
    if isinstance(views, dict):
        ITEMS[name] = (v.get("address"), list(views.keys()))

# fetch ABIs for all focus contracts (threaded) to resolve signatures
abi_cache = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(fetch_abi, addr): name for name, (addr, _) in ITEMS.items()}
    for f in concurrent.futures.as_completed(futs):
        abi_cache[futs[f]] = f.result()

sig_report = {}
calls, meta = [], []
for name, (addr, keys) in ITEMS.items():
    abi_map = abi_cache.get(name)
    for key in keys:
        sig, vals, how = resolve_sig(addr, key, abi_map)
        if sig is None:
            sig_report.setdefault(name, {})[key] = {"error": "unresolved signature"}
            continue
        calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, vals)}, "latest"]})
        meta.append((name, key, sig, how))
        sig_report.setdefault(name, {})[key] = {"sig": sig, "via": how}

def decode_value(key, result):
    if not result or result == "0x":
        return None
    # Same decoding as prior runs (first 32-byte word as int) so change
    # detection vs the 1304 baseline stays comparable, including address
    # views (owner / AGENT_ID) which the baseline stores as ints.
    return to_int(result[:66]) if len(result) >= 66 else result

def read_all_batched():
    """Batch eth_call in 60-call chunks across endpoints; fall back to 3-contract chunks."""
    results = [None] * len(calls)
    CH = 60
    for ci in range(0, len(calls), CH):
        chunk = calls[ci:ci + CH]
        done = False
        for ep in EPS:
            try:
                res = post_rpc(ep, chunk, timeout=120)
                if isinstance(res, list) and len(res) == len(chunk):
                    for j, it in enumerate(res):
                        if isinstance(it, dict) and "error" not in it and it.get("result") not in (None, "0x"):
                            results[ci + j] = it["result"]
                        else:
                            results[ci + j] = None
                    done = True
                    break
            except Exception:
                continue
        if not done:
            print(f"batch chunk {ci//CH+1} FAILED all endpoints", flush=True)
    return results

raw = read_all_batched()
full_reads = {}
for name, (addr, keys) in ITEMS.items():
    full_reads[name] = {"address": addr, "views": {}}
for (name, key, sig, how), r in zip(meta, raw):
    full_reads[name]["views"][key] = decode_value(key, r)
for name, (addr, keys) in ITEMS.items():
    for key in keys:
        if key not in full_reads[name]["views"]:
            full_reads[name]["views"][key] = None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

blk = block_number()
reads_ok = sum(1 for name in ITEMS if full_reads[name]["views"] and
               any(v is not None for v in full_reads[name]["views"].values()))
reread = {"started_wib": NOW, "reads": full_reads, "reads_ok": reads_ok,
          "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1),
          "method": "60-call-batches", "sig_report": sig_report}
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)
out["reread"] = {"reads_ok": reads_ok, "reads_total": len(ITEMS), "block": blk,
                 "elapsed_s": reread["elapsed_s"], "method": "60-call-batches"}
out["reread_items"] = len(ITEMS)
out["reread_focus_source"] = "run-" + PREV_TAG + "-reread.json (baseline data)"

changes = []
for name, cur in full_reads.items():
    pv = (prev_reads.get(name) or {}).get("views") or {}
    cv = cur.get("views") or {}
    for k, v in cv.items():
        if pv.get(k) != v:
            changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})
out["reread_changes_vs_" + PREV_TAG] = changes
out["reread_prev_block"] = prev_main.get("block")

# --- update seen with new contracts (only genuinely new ones; retries keep status) ---
added = 0
retry_updated = 0
shape_by_addr = {s.get("address"): s for s in shapes}
for a in to_shape:
    if a.lower() not in seen_lower:
        s = shape_by_addr.get(a)
        st = "SALE-SHAPE" if s and (s.get("S1") or s.get("S2")) else \
             ("checked-not-sale-shape" if s and "error" not in s else "shape-check-failed")
        seen[a] = {"first_seen_wib": NOW,
                   "source": "sourcify-feed" if a in new_feed else "boltbook-en+zh",
                   "status": st, "note": str(s)[:300] if s else ""}
        seen_lower.add(a.lower())
        added += 1
    elif a in retry:
        s = shape_by_addr.get(a)
        if s and "error" not in s:
            seen[a] = {"first_seen_wib": seen[a].get("first_seen_wib", NOW) if isinstance(seen[a], dict) else NOW,
                       "source": "sourcify-feed-retry", "status": "checked-not-sale-shape",
                       "note": str(s)[:300]}
            retry_updated += 1
if added or retry_updated:
    json.dump(seen, open(BASE + "hot-leg-seen.json", "w"))
out["seen_added"] = added
out["seen_retry_updated"] = retry_updated
out["seen_n"] = len(seen)
out["seen_n_prev"] = seen_n_prev
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps(out, indent=1))
