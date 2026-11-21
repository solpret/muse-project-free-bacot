#!/usr/bin/env python3
"""Main run free-mint-search 2026-11-20 11:31 WIB. Read-only except run outputs.
Re-reads the 49 contracts from run-2026-11-20-1101-reread.json (same view lists),
plus totalMinted() for totalSupply-revert contracts; pre-flight Ankr (fast-fail);
Sourcify recently-verified feed; Boltbook EN+ZH; bridge diff. No mint/preview/claim.
Writes run-2026-11-20-1131-reread.json + run-2026-11-20-1131-interim.json. Snapshot merge
is done by the parent afterwards (merge step reads the interim file)."""
import json, subprocess, time, sys, re
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-1131"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
NOW = datetime.now(timezone(timedelta(hours=7)))  # WIB langsung, bukan UTC sistem
NOW_WIB = NOW.strftime("%Y-%m-%d %H:%M WIB")
START = time.time()
out = {"run": "free-mint-search 2026-11-20 11:31 WIB", "started_wib": NOW_WIB}

def sel(sig):
    return keccak(sig.encode())[:4].hex()
def enc_addr(a):
    return "0" * 24 + a[2:].lower()
def encode(sig, arg=None):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    elif arg == "one":
        data += "%064x" % 1
    elif arg == "user1":
        data += enc_addr(USER) + "%064x" % 1
    return data

SIG = {
    "totalSupply": ("totalSupply()", None),
    "totalMinted": ("totalMinted()", None),
    "freeClaimed": ("freeClaimed()", None),
    "freeClaimed_user": ("freeClaimed(address)", "user"),
    "FREE_SUPPLY": ("FREE_SUPPLY()", None),
    "freeSupply": ("freeSupply()", None),
    "freeLeft": ("freeLeft()", None),
    "balanceOf_user": ("balanceOf(address)", "user"),
    "mintedBy_user": ("mintedBy(address)", "user"),
    "freeMintedByWallet_user": ("freeMintedByWallet(address)", "user"),
    "quote_user_1": ("quote(address,uint256)", "user1"),
    "mintOpen": ("mintOpen()", None),
    "name": ("name()", None),
    "symbol": ("symbol()", None),
    "contractURI": ("contractURI()", None),
    "owner": ("owner()", None),
    "launched": ("launched()", None),
    "failed": ("failed()", None),
    "isRefundPhase": ("isRefundPhase()", None),
    "totalShares": ("totalShares()", None),
    "tokenClaimed_user": ("tokenClaimed(address)", "user"),
    "refundClaimed_user": ("refundClaimed(address)", "user"),
    "freeMinted": ("freeMinted()", None),
}
STRING_VIEWS = {"name", "symbol", "contractURI"}
ADDR_VIEWS = {"owner"}

def decode_str(hexstr):
    try:
        b = bytes.fromhex(hexstr[2:])
        if len(b) < 64:
            return None
        ln = int.from_bytes(b[32:64], "big")
        raw = b[64:64 + ln]
        return raw.decode("utf-8", "replace")
    except Exception:
        return None

# ---- (0) pre-flight Ankr: one small getLogs, must succeed in <60s ----
try:
    p = subprocess.run(["python3", BASE + "preflight-160316.py"],
                       capture_output=True, text=True, timeout=70, cwd=BASE)
    out["preflight"] = {"exit": p.returncode, "stdout": p.stdout.strip()[-300:],
                        "stderr": p.stderr.strip()[-300:]}
except subprocess.TimeoutExpired:
    out["preflight"] = {"exit": "TIMEOUT", "note": "pre-flight >70s -> FAST-FAIL scan leg"}
except Exception as e:
    out["preflight"] = {"exit": "ERR", "note": f"{type(e).__name__}: {e}"}

# ---- (1) re-read watchlist ----
prev = json.load(open(BASE + "run-2026-11-20-1101-reread.json"))
prev_reads = prev["reads"]
prev_block = prev["block"]
prev_started = prev.get("started_wib", "")
TOTALMINTED_EXTRA = {"DRAGON", "Foundry Faces", "B77D-0xB77D", "Zephyra", "Pengu",
                     "CPASS", "RAVE", "AGCLUB", "BNB Genesis", "ARKYN",
                     "Everything Is Mine (EIM)", "ADRAW", "Stromboat", "AgentMintPass",
                     "AGATE-Pass", "AgentDrop", "AgentForge Hero", "DGF-CARD"}
calls, labels = [], []
for name, entry in prev_reads.items():
    addr = entry["address"]
    viewkeys = list(entry["views"].keys())
    for vk in viewkeys:
        if vk not in SIG:
            continue
        sig, arg = SIG[vk]
        calls.append({"to": addr, "data": encode(sig, arg)})
        labels.append((name, vk))
    if name in TOTALMINTED_EXTRA:
        calls.append({"to": addr, "data": encode("totalMinted()", None)})
        labels.append((name, "totalMinted"))

def curl_batch(payload):
    o = subprocess.run(["curl", "-sL", "--max-time", "60", "-X", "POST", RPC,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return json.loads(o.stdout)

results = [None] * len(calls)
n_calls = 0
t0 = time.time()
CHUNK = 20
for i in range(0, len(calls), CHUNK):
    chunk = calls[i:i + CHUNK]
    payload = [{"jsonrpc": "2.0", "id": j + 1, "method": "eth_call",
                "params": [{"to": c["to"], "data": c["data"]}, "latest"]}
               for j, c in enumerate(chunk)]
    try:
        resp = curl_batch(payload)
        by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(chunk)):
            it = by_id.get(j + 1, {})
            if "result" in it and it["result"] not in (None, "0x"):
                results[i + j] = it["result"]
            elif "error" in it:
                results[i + j] = {"error": str(it["error"])[:160]}
            else:
                results[i + j] = None
        n_calls += len(chunk)
    except Exception as e:
        for j in range(len(chunk)):
            results[i + j] = {"error": f"transport {type(e).__name__}: {str(e)[:100]}"}
    time.sleep(1)
elapsed = round(time.time() - t0, 1)
try:
    blk = curl_batch([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])
    block = int(blk[0]["result"], 16)
except Exception as e:
    block = f"ERR {type(e).__name__}"

reads = {}
for (name, vk), v in zip(labels, results):
    entry = reads.setdefault(name, {"address": prev_reads[name]["address"], "views": {}})
    if isinstance(v, dict):
        entry["views"][vk] = v
    elif isinstance(v, str):
        if vk in STRING_VIEWS:
            entry["views"][vk] = decode_str(v)
        elif vk in ADDR_VIEWS:
            entry["views"][vk] = "0x" + v[-40:] if len(v) >= 42 else v
        else:
            try:
                entry["views"][vk] = int(v, 16)
            except Exception:
                entry["views"][vk] = v
    else:
        entry["views"][vk] = v

reread = {"started_wib": NOW_WIB, "block": block, "method": "curl-batch " + RPC + " (chunks of 20)",
          "elapsed_s": elapsed, "n_calls": n_calls, "n_contracts": len(reads),
          "prev_block": prev_block, "prev_started_wib": prev_started,
          "reads": reads, "errors": [l for l, v in zip(labels, results) if isinstance(v, dict)]}
json.dump(reread, open(BASE + f"run-{RUN}-reread.json", "w"), indent=1)
out["reread"] = {"block": block, "n_contracts": len(reads), "n_calls": n_calls,
                 "elapsed_s": elapsed, "errors": len(reread["errors"])}

# velocity + free% vs 0601 baseline
try:
    fmt = "%Y-%m-%d %H:%M"
    t_prev = datetime.strptime(prev_started[:16], fmt)
    t_now = datetime.strptime(NOW_WIB[:16], fmt)
    minutes = max((t_now - t_prev).total_seconds() / 60.0, 1.0)
except Exception:
    minutes = 30.0
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_contracts = snap.get("contracts", {})
by_addr = {}
for k, v in snap_contracts.items():
    if isinstance(v, dict) and isinstance(v.get("address"), str):
        by_addr[v["address"].lower()] = (k, v)
vel = {}
for name, entry in reads.items():
    pv = prev_reads[name]["views"]
    cv = entry["views"]
    def num(d, k):
        x = d.get(k)
        return x if isinstance(x, int) else None
    old_sup = num(pv, "totalSupply") if num(pv, "totalSupply") is not None else num(pv, "totalMinted")
    new_sup = num(cv, "totalSupply") if num(cv, "totalSupply") is not None else num(cv, "totalMinted")
    sup_view = "totalSupply" if num(cv, "totalSupply") is not None else ("totalMinted" if num(cv, "totalMinted") is not None else None)
    delta = (new_sup - old_sup) if (old_sup is not None and new_sup is not None) else None
    rate = (delta / minutes) if delta is not None else None
    sk, sv = by_addr.get(entry["address"].lower(), (None, {}))
    prev_rate = sv.get("currentRatePerMin") if isinstance(sv, dict) else None
    ratio = (rate / prev_rate) if (rate is not None and isinstance(prev_rate, (int, float)) and prev_rate > 0) else None
    vpass = bool(delta is not None and delta >= 20 and ratio is not None and ratio >= 1.5)
    fc = num(cv, "freeClaimed")
    fs = num(cv, "freeSupply") if num(cv, "freeSupply") is not None else num(cv, "FREE_SUPPLY")
    fl = num(cv, "freeLeft")
    if fc is not None and fs:
        freepct = round(100 * fc / fs, 1)
    elif fl is not None and fs:
        freepct = round(100 * (fs - fl) / fs, 1)
    else:
        freepct = None
    vel[name] = {"address": entry["address"], "snapshot_key": sk, "supply_view": sup_view,
                 "old_supply": old_sup, "new_supply": new_sup, "delta": delta,
                 "minutes": round(minutes, 1), "rate_per_min": round(rate, 4) if rate is not None else None,
                 "prev_rate_per_min": prev_rate,
                 "ratio": round(ratio, 2) if ratio is not None else None,
                 "velocity_pass": vpass, "free_pct": freepct,
                 "freeClaimed": fc, "FREE_SUPPLY": fs, "freeLeft": fl,
                 "mintOpen": cv.get("mintOpen"), "balanceOf_user": cv.get("balanceOf_user"),
                 "quote_user_1": cv.get("quote_user_1"),
                 "freeMintedByWallet_user": cv.get("freeMintedByWallet_user")}
out["velocity"] = vel
out["velocity_pass_list"] = [k for k, v in vel.items() if v["velocity_pass"]]
out["delta_ge_20"] = {k: v["delta"] for k, v in vel.items() if v["delta"] is not None and v["delta"] >= 20}
out["free_ge_70"] = {k: v["free_pct"] for k, v in vel.items() if v["free_pct"] is not None and v["free_pct"] > 70}

# ---- (2) Sourcify recently-verified feed ----
def shape_check(addr):
    try:
        o = subprocess.run(["curl", "-sL", "--max-time", "20",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True).stdout
        meta = json.loads(o)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function":
                fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        FREE_VIEWS = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
                      "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
                      "freeMinted", "freeCardsRemaining"}
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
        free_views = sorted(names & FREE_VIEWS)
        agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                                  "agentGate", "AgentGate", "AGENT_ID", "AGENT_ID_REGISTRY",
                                  "agentIdOf", "hasAgentId"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed", "freeMinted"}) and \
            bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "is_nft": bool(names & {"ownerOf", "tokenURI"}),
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
    except Exception as e:
        return {"address": addr, "error": f"{type(e).__name__}: {str(e)[:120]}"}

try:
    o = subprocess.run(["curl", "-sL", "--max-time", "30",
                        "https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc"],
                       capture_output=True, text=True).stdout
    feed = json.loads(o)
    items = feed if isinstance(feed, list) else feed.get("results", feed.get("contracts", []))
    addrs, top_at = [], None
    for it in items:
        a = it.get("address") or it.get("contractAddress")
        if a:
            addrs.append(a)
        if top_at is None:
            top_at = it.get("verifiedAt") or it.get("creationMatch", {}).get("verifiedAt")
    out["sourcify_feed"] = {"total": len(addrs), "top_verifiedAt": top_at, "all": addrs}
    seen = json.load(open(BASE + "hot-leg-seen.json"))
    seen_lower = {k.lower() for k in seen}
    snap_addrs = {v["address"].lower() for v in snap_contracts.values()
                  if isinstance(v, dict) and isinstance(v.get("address"), str)}
    new_feed = [a for a in addrs if a.lower() not in seen_lower
                and a.lower() not in snap_addrs
                and a.lower() != REGISTRY and a not in EXCLUDED]
    out["sourcify_new"] = new_feed
    out["sourcify_shapes"] = [shape_check(a) for a in new_feed]
    out["sourcify_shape_hits"] = [s["address"] for s in out["sourcify_shapes"]
                                  if s.get("S1") or s.get("S2")]
except Exception as e:
    out["sourcify_feed"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# ---- (3) Boltbook EN + ZH ----
try:
    seen = json.load(open(BASE + "hot-leg-seen.json"))
    seen_lower = {k.lower() for k in seen}
    snap_addrs = {v["address"].lower() for v in snap_contracts.values()
                  if isinstance(v, dict) and isinstance(v.get("address"), str)}
    bb = {}
    for lang, url in (("en", "https://boltbook.fun/"),
                      ("zh", "https://boltbook.fun/?lang=zh")):
        o = subprocess.run(["curl", "-sL", "--max-time", "30", url],
                           capture_output=True, text=True)
        html = o.stdout
        found = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", html)))
        newfound = [a for a in found if a.lower() not in seen_lower
                    and a.lower() not in snap_addrs
                    and a.lower() != REGISTRY and a not in EXCLUDED]
        bb[lang] = {"bytes": len(html), "full_address_contracts": len(found),
                    "addresses": found, "new": len(newfound), "new_contracts": newfound}
    out["boltbook"] = bb
    new_all = sorted(set(bb["en"]["new_contracts"] + bb["zh"]["new_contracts"]))
    out["boltbook_shapes"] = [shape_check(a) for a in new_all]
    out["boltbook_shape_hits"] = [s["address"] for s in out["boltbook_shapes"]
                                  if s.get("S1") or s.get("S2")]
except Exception as e:
    out["boltbook"] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}

# ---- bridge diff (read-only) ----
try:
    b = json.load(open(BASE + "scan-bridge.json"))
    bc = b.get("contracts", {})
    snap_addrs = set()
    for coll in ("contracts", "track_c"):
        for v in snap.get(coll, {}).values():
            if isinstance(v, dict):
                for k in ("address", "sale", "token"):
                    val = v.get(k)
                    if isinstance(val, str):
                        snap_addrs.add(val.lower())
    for v in snap.get("pending_claims", {}).values():
        if isinstance(v, dict):
            for k in ("mint", "token"):
                val = v.get(k)
                if isinstance(val, str):
                    snap_addrs.add(val.lower())
    not_in = [a for a in bc if isinstance(a, str) and a.lower() not in snap_addrs]
    discarded = [a for a, v in bc.items() if isinstance(v, dict) and v.get("same_owner_discarded")]
    out["bridge_scan"] = {"total": len(bc), "not_in_snapshot": len(not_in),
                          "not_in_snapshot_list": not_in,
                          "same_owner_discarded": len(discarded)}
except Exception as e:
    out["bridge_scan"] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}

out["elapsed_s"] = round(time.time() - START, 1)
out["executions"] = "none - no preview, no mint, no claim (read-only run)"
json.dump(out, open(BASE + f"run-{RUN}-interim.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:12000])
print("ELAPSED", out["elapsed_s"])
