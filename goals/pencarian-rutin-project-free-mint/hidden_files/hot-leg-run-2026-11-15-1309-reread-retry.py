#!/usr/bin/env python3
"""Retry of the 1309 hot-leg re-read leg (leg 4).
The first attempt used 60-call batches, which failed on ALL endpoints
(reads_ok 0/47) — the same failure mode noted in the 1009 run.
This retry uses the proven 3-contract-chunk method (curl timeout 150s).
Also fixes a signature-parser bug from the first attempt: view keys whose
function name itself contains underscores (MAX_SUPPLY, FREE_POOL,
FREE_SUPPLY, FREE_MAX, FREE_CAP, TOKEN_PRICE, AGENT_ID) were split on '_'
and left unresolved. The parser now matches the longest known function-name
prefix first.
Overwrites run-2026-11-15-1309-reread.json and patches
hot-leg-run-2026-11-15-1309.json (reread section + changes). No other files.
"""
import json, re, subprocess, time, urllib.request, concurrent.futures
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "2026-11-15-1309"
PREV_TAG = "2026-11-15-1304"
NOW = time.strftime("%Y-%m-%dT%H:%M+07:00", time.gmtime(time.time() + 7 * 3600))
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
t0 = time.time()

def get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "free-mint-hot-leg/1309-retry"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def enc_str(s):
    b = s.encode()
    return format(32, "064x") + format(len(b), "064x") + b.hex().ljust(((len(b) + 31) // 32) * 64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

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
KNOWN = NOARG | ADDR1 | {"priceFor", "quote", "snippetsOf", "commitEnd", "freeClaimedByAgent",
                         "questionFor", "answerFor"}

def fetch_abi(addr):
    try:
        meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20).decode())
        abi = meta.get("abi", [])
        return {e["name"]: e for e in abi if e.get("type") == "function"}
    except Exception:
        return None

def parse_key(key, abi_map):
    """Return (fn_name, [(kind, value), ...]) with args in key order.
    Function name = longest prefix that is a known/ABI function name."""
    if abi_map and key in abi_map:
        return key, []
    if key in KNOWN:
        return key, []
    # longest known prefix
    best = None
    for cand in list(KNOWN) + (list(abi_map.keys()) if abi_map else []):
        if key.startswith(cand + "_") and (best is None or len(cand) > len(best)):
            best = cand
    if best is None:
        parts = key.split("_")
        return parts[0], []
    rest = key[len(best) + 1:]
    args = []
    for tok in rest.split("_"):
        if tok == "user":
            args.append(("address", USER))
        elif tok == "masgayut":
            args.append(("string", "masgayut"))
        elif tok == "ai" and args and args[-1] == ("string", "masgayut"):
            args[-1] = ("string", "masgayut.ai")
        elif tok.isdigit():
            args.append(("uint256", int(tok)))
        else:
            args.append(("literal", tok))
    return best, args

def resolve_sig(key, abi_map):
    fn, args = parse_key(key, abi_map)
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

abi_cache = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    futs = {ex.submit(fetch_abi, addr): name for name, (addr, _) in ITEMS.items()}
    for f in concurrent.futures.as_completed(futs):
        abi_cache[futs[f]] = f.result()

sig_report = {}
plan = {}  # name -> [(key, sig, vals, how)]
for name, (addr, keys) in ITEMS.items():
    abi_map = abi_cache.get(name)
    plan[name] = []
    for key in keys:
        sig, vals, how = resolve_sig(key, abi_map)
        sig_report.setdefault(name, {})[key] = {"sig": sig, "via": how} if sig else {"error": "unresolved signature"}
        if sig:
            plan[name].append((key, sig, vals, how))

def read_chunk(chunk):
    calls, meta = [], []
    for name, (addr, keys) in chunk:
        for key, sig, vals, how in plan.get(name, []):
            calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                          "params": [{"to": addr, "data": build_data(sig, vals)}, "latest"]})
            meta.append((name, key))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=150)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for it, (name, key) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    outd.setdefault(name, {})[key] = None
                else:
                    r = it["result"]
                    outd.setdefault(name, {})[key] = to_int(r[:66]) if len(r) >= 66 else r
            return outd, ep
        except Exception:
            continue
    return None, None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=60)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

items = list(ITEMS.items())
reads, ok = {}, 0
chunks = [items[i:i + 3] for i in range(0, len(items), 3)]
for ci, ch in enumerate(chunks):
    r, ep = read_chunk(ch)
    names = [n for n, _ in ch]
    if r is None:
        print(f"reread chunk {ci+1}/{len(chunks)} FAIL {names}", flush=True)
        for n in names:
            reads[n] = {"address": ITEMS[n][0], "views": None}
        continue
    ok += sum(1 for n in names if r.get(n) is not None)
    for n in names:
        reads[n] = {"address": ITEMS[n][0], "views": r.get(n)}
    print(f"reread chunk {ci+1}/{len(chunks)} OK via {ep} ({time.time()-t0:.0f}s) {names}", flush=True)
    time.sleep(5)
blk = block_number()

full_reads = {}
for name, (addr, keys) in ITEMS.items():
    views = (reads.get(name, {}) or {}).get("views")
    full_reads[name] = {"address": addr, "views": {k: (views or {}).get(k) for k in keys}}
reread = {"started_wib": NOW, "reads": full_reads, "reads_ok": ok,
          "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1),
          "method": "3-contract-chunks-retry", "sig_report": sig_report,
          "note": "Retry of the 1309 first attempt (60-call batches failed on all endpoints, reads_ok 0/47); parser fixed for underscore function names."}
json.dump(reread, open(BASE + "run-" + TAG + "-reread.json", "w"), indent=1)

changes = []
for name, cur in full_reads.items():
    pv = (prev_reads.get(name) or {}).get("views") or {}
    cv = cur.get("views") or {}
    for k, v in cv.items():
        if pv.get(k) != v:
            changes.append({"contract": name, "view": k, "prev": pv.get(k), "now": v})

run = json.load(open(BASE + "hot-leg-run-" + TAG + ".json"))
run["reread"] = {"reads_ok": ok, "reads_total": len(ITEMS), "block": blk,
                 "elapsed_s": reread["elapsed_s"], "method": "3-contract-chunks-retry"}
run["reread_changes_vs_" + PREV_TAG] = changes
run["reread_prev_block"] = prev_main.get("block")
run["reread_retry"] = {"reason": "first attempt 60-call batches failed on all endpoints (reads_ok 0/47); parser bug on underscore function names fixed",
                       "finished_wib": NOW, "elapsed_s": round(time.time() - t0, 1)}
run["elapsed_s"] = round(run.get("elapsed_s", 0) + time.time() - t0, 1)
json.dump(run, open(BASE + "hot-leg-run-" + TAG + ".json", "w"), indent=1)
print(json.dumps({"reads_ok": ok, "reads_total": len(ITEMS), "block": blk,
                  "changes": len(changes), "elapsed_s": round(time.time() - t0, 1)}, indent=1))
print(json.dumps(changes, indent=1))
