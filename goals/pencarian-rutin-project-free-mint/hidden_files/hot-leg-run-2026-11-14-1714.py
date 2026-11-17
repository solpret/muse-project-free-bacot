#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 17:14 WIB (scheduled 17:14:38).
Legs: (1) Sourcify recently-verified feed poll limit 20; (2) Boltbook EN+ZH
front pages via curl; (3) shape-check new addresses (S1/S2); (4) batch
re-read of active snapshot items via curl JSON-RPC batch (fast_rpc was
down in the 1659/1704 runs); (5) scan-bridge check (read-only).
Writes ONLY hot-leg-run-2026-11-14-1714.json + hot-leg-seen.json (own files).
Never writes main snapshot / main seen files."""
import json, re, subprocess, sys, time, urllib.request
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
WIB = timezone(timedelta(hours=7))
NOW_WIB = datetime.now(WIB).strftime("%Y-%m-%dT%H:%M+07:00")
RUN_TAG = "2026-11-14 17:14 WIB"
RPCS = ["https://bsc-dataseed1.bnbchain.org/",
        "https://bsc-rpc.publicnode.com/",
        "https://bsc.drpc.org/",
        "https://bnb.api.onfinality.io/public/",
        "https://bsc-dataseed.binance.org/"]

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        return (None, str(e))

def get_json(url, timeout=20):
    body = fetch(url, timeout)
    if body is None or isinstance(body, tuple):
        return None
    try:
        return json.loads(body)
    except Exception:
        return None

def curl_get(url, timeout=25):
    try:
        p = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else (None, f"curl rc={p.returncode}")
    except Exception as e:
        return (None, str(e))

def rpc_batch(calls, chunk=26):
    """calls: list of (to, data). Returns list of result hex or None."""
    results = [None] * len(calls)
    rpc_i = 0
    for ci in range(0, len(calls), chunk):
        sub = calls[ci:ci + chunk]
        payload = json.dumps([{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}
                              for i, (to, data) in enumerate(sub)])
        ok = False
        for attempt in range(len(RPCS)):
            url = RPCS[(rpc_i + attempt) % len(RPCS)]
            try:
                p = subprocess.run(["curl", "-s", "--max-time", "20", "-X", "POST",
                                    "-H", "Content-Type: application/json",
                                    "--data", payload, url],
                                   capture_output=True, text=True, timeout=25)
                resp = json.loads(p.stdout)
                if isinstance(resp, dict) and "error" in resp:
                    raise ValueError(f"rpc error {resp['error']}")
                if isinstance(resp, list) and len(resp) == len(sub):
                    for j, r in enumerate(resp):
                        results[ci + j] = r.get("result")
                    ok = True
                    rpc_i = (rpc_i + attempt + 1) % len(RPCS)
                    break
            except Exception as e:
                print(f"  chunk@{ci} attempt {url}: {e}", flush=True)
                continue
        if not ok:
            print(f"  chunk@{ci}: ALL endpoints failed", flush=True)
        time.sleep(1)
    return results

def rpc_block():
    for url in RPCS:
        try:
            p = subprocess.run(["curl", "-s", "--max-time", "15", "-X", "POST",
                                "-H", "Content-Type: application/json",
                                "--data", '{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}',
                                url], capture_output=True, text=True, timeout=20)
            r = json.loads(p.stdout)
            if r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

ITEMS = {
 "PIXEL FROGS": ("0x454054e55FA2D7Ba37df7F3ceA269696f19037dF", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("freeLeft","freeLeft()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[]),
    ("freeClaimed_user","freeClaimed(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "WANGCAI": ("0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "YUANBAO": ("0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "B77D-Kryntar": ("0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("standardRemaining","standardRemaining()",[]),
    ("legendaryRemaining","legendaryRemaining()",[]),
    ("hasAgentId_user","hasAgentId(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "RaceAgents": ("0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("FREE_MAX","FREE_MAX()",[]),("mintOpen","mintOpen()",[])]),
 "Pengu": ("0x5AEc03C90656743475810926B2B2bd443D5c26a4", [
    ("freeMinted","freeMinted()",[]),("FREE_CAP","FREE_CAP()",[]),
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("freeClaimed_user","freeClaimed(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "Zephyra": ("0x00a9791be6317d6e3a6c60f75a706c870d882048", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("mintedBy_user","mintedBy(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "DragonAgents": ("0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("mintedBy_user","mintedBy(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "BinanceAI-mint": ("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
    ("launched","launched()",[]),("failed","failed()",[]),
    ("isRefundPhase","isRefundPhase()",[]),("totalShares","totalShares()",[]),
    ("tokenClaimed_user","tokenClaimed(address)",["U"])]),
 "AngelEye-77D9": ("0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_POOL","FREE_POOL()",[]),("saleActive","saleActive()",[]),
    ("mintStart","mintStart()",[]),("mintEnd","mintEnd()",[])]),
 "NOTV": ("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeClaimed","freeClaimed()",[]),("FREE_SHARES","FREE_SHARES()",[]),
    ("freeStart","freeStart()",[]),("balanceOf_user","balanceOf(address)",["U"])]),
 "AbsurdAgentNFT": ("0x72c14121681F1133545947B0735563835CC07B67", [
    ("totalMinted","totalMinted()",[]),("mintOpen","mintOpen()",[]),
    ("mintStartTime","mintStartTime()",[]),("isEligible_user","isEligible(address)",["U"])]),
 "AgentBubble": ("0x0d72970046c056db90888351b739246f468bff0b", [
    ("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",["U"])]),
 "Ledgera": ("0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
    ("freeClaimed","freeClaimed()",[]),("totalSupply","totalSupply()",[]),
    ("mintedBy_user","mintedBy(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "SKRR": ("0x9081f02876c173d0c69f042959cfd0d61c668b17", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "PX24": ("0xe712510fcb27935e657e41ebb97982d6b123136c", [
    ("totalSupply","totalSupply()",[]),("freeClaimed","freeClaimed()",[])]),
 "ZephyrAgent": ("0x010597f2e8723cde9e92d234cbdf23b47cc5504a", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintedBy_user","mintedBy(address)",["U"]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
 "CPASS": ("0x5877d2bb9f226cc3e438f4d656caeb27deafc576", [
    ("totalMinted","totalMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("balanceOf_user","balanceOf(address)",["U"])]),
}

def decode(hexres):
    if not hexres or hexres in ("0x", None):
        return None
    try:
        h = hexres[2:]
        if len(h) < 64:
            return None
        return int(h[-64:], 16)
    except Exception:
        return None

def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if a == "U":
            d += USER_PAD
        else:
            d += format(int(a), "064x")
    return d

def shape_check(addr):
    # Correct endpoint (known-good since 1514 runs): singular /v2/contract/ + ?fields=abi.
    # The plural /v2/contracts/56/{addr} path 404s; repo.sourcify.dev paths 404 too.
    meta = get_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20)
    if meta is None:
        body = curl_get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=20)
        if isinstance(body, tuple):
            return {"status": "shape-check-failed", "reason": "sourcify-fetch-failed"}
        try:
            meta = json.loads(body)
        except Exception:
            return {"status": "shape-check-failed", "reason": "sourcify-parse-failed"}
    try:
        abi = meta["abi"]
    except Exception:
        return {"status": "shape-check-failed", "reason": "no-abi-in-sourcify"}
    fns = set()
    for e in abi:
        if e.get("type") == "function":
            fns.add(e.get("name"))
    mint = any(n in fns for n in ("mint", "mintFree", "claimFree", "mintWithAgentId"))
    quote = any(n in fns for n in ("quote", "cost", "getQuote", "price"))
    free = [n for n in fns if n.startswith("free") or n in ("freeMinted", "freeClaimed", "freeLeft", "freeAvailable", "freeSharesRemaining", "freeFor", "freeUsed", "freeSharePoolExhausted", "freeSharesClaimed")]
    agent = any(n in fns for n in ("agentId", "registry", "AGENT_ID_REGISTRY", "agentRegistry", "agentGate")) or REGISTRY.lower() in json.dumps(abi).lower()
    s1 = bool(mint and quote and free and agent)
    s2 = bool(("name" in fns or "symbol" in fns) and ("mintFree" in fns or "claimFree" in fns) and free and agent)
    return {"S1": s1, "S2": s2, "mint": mint, "quote": quote, "free": free,
            "agent": agent, "is_token": bool({"name", "symbol", "decimals", "totalSupply"} <= fns),
            "n_fns": len(fns), "status": "checked",
            "fn_names": sorted(fns)}

def main():
    t0 = time.time()
    out = {"run": f"free-mint-hot-leg {RUN_TAG}", "started_wib": NOW_WIB}
    seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    out["seen_n_prev"] = len(seen)

    # --- leg 1: Sourcify feed ---
    feed = get_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed_addrs, feed_meta = [], {}
    if feed and isinstance(feed, dict):
        for c in feed.get("results", feed.get("contracts", [])):
            a = c.get("address") or c.get("contractAddress")
            if a:
                feed_addrs.append(a)
                feed_meta[a] = c.get("verifiedAt")
        out["sourcify_feed"] = {"total": len(feed_addrs),
                                "top": feed_addrs[0] if feed_addrs else None,
                                "top_verifiedAt": feed_meta.get(feed_addrs[0]) if feed_addrs else None}
    else:
        out["sourcify_feed"] = {"total": 0, "error": "feed-fetch-failed"}

    # --- leg 2: Boltbook EN + ZH via curl ---
    bb = {}
    for lang, url in (("en", "https://boltbook.fun/"),
                      ("zh", "https://boltbook.fun/?lang=zh")):
        body = curl_get(url, timeout=25)
        if isinstance(body, tuple) or body is None:
            bb[lang] = {"bytes": 0, "full_address_contracts": 0, "new": 0, "new_contracts": [], "error": "fetch-failed"}
            continue
        open(f"{HF}/run-2026-11-14-1714-boltbook-{lang}.html", "w").write(body)
        addrs = sorted(set(ADDR_RE.findall(body)))
        new = [a for a in addrs if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]
        bb[lang] = {"bytes": len(body), "full_address_contracts": len(addrs),
                    "new": len(new), "new_contracts": new}
    out["boltbook_en"] = bb["en"]
    out["boltbook_zh"] = bb["zh"]

    # --- leg 3: shape-check new addresses ---
    seen_keys = {k.lower() for k in seen}
    feed_new = [a for a in feed_addrs if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
    out["sourcify_feed"]["new"] = len(feed_new)
    out["sourcify_feed"]["new_contracts"] = feed_new
    new_addrs = list(feed_new)
    new_addrs += [a for a in bb["en"]["new_contracts"] + bb["zh"]["new_contracts"]
                  if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
    sc = []
    for a in sorted(set(new_addrs)):
        r = shape_check(a)
        r["address"] = a
        r["verifiedAt"] = feed_meta.get(a)
        sc.append(r)
        seen[a] = {"first_seen_wib": NOW_WIB,
                   "source": "sourcify-feed" if a in feed_addrs else "boltbook",
                   "status": "checked" if r.get("status") == "checked" else r.get("status"),
                   "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free')} agent={r.get('agent')}"}
    out["shape_check"] = sc
    out["shape_hits"] = [s["address"] for s in sc if s.get("S1") or s.get("S2")]
    out["seen_n"] = len(seen)

    # --- leg 4: curl batch re-read of active snapshot items ---
    block = rpc_block()
    calls, keys = [], []
    for name, (addr, views) in ITEMS.items():
        for label, sig, args in views:
            calls.append((addr, build_data(sig, args)))
            keys.append((name, label))
    res = rpc_batch(calls)
    results = {}
    for (name, label), r in zip(keys, res):
        results.setdefault(name, {})[label] = decode(r)
    out["reread"] = {"reads": {n: {"address": ITEMS[n][0], "views": results.get(n, {})} for n in ITEMS},
                     "reads_ok": sum(1 for n in ITEMS if any(v is not None for v in results.get(n, {}).values())),
                     "reads_total": len(ITEMS), "block": block}

    # --- leg 5: bridge (read-only) ---
    try:
        import os
        bridge = json.load(open(f"{HF}/scan-bridge.json"))
        snap = json.load(open(f"{HF}/onchain-snapshot.json"))
        snap_addrs = set()
        for sec in ("contracts", "track_c"):
            for v in snap.get(sec, {}).values():
                if isinstance(v, dict):
                    for k in ("address", "sale", "token"):
                        if v.get(k):
                            snap_addrs.add(str(v[k]).lower())
        bcontracts = bridge.get("contracts", {})
        not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
        out["bridge"] = {"contracts": len(bcontracts),
                         "same_owner_discarded": sum(1 for v in bcontracts.values() if isinstance(v, dict) and v.get("same_owner_discarded")),
                         "not_in_snapshot": len(not_in_snap),
                         "not_in_snapshot_contracts": not_in_snap[:10],
                         "mtime": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(f"{HF}/scan-bridge.json")))}
    except Exception as e:
        out["bridge"] = {"error": str(e)}

    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-1714.json", "w"), indent=1)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"))
    print(json.dumps({"feed": out["sourcify_feed"], "bb_en": out["boltbook_en"],
                      "bb_zh": out["boltbook_zh"], "shape_hits": out["shape_hits"],
                      "shape_check": sc, "reads_ok": out["reread"]["reads_ok"],
                      "block": block, "bridge": out["bridge"],
                      "elapsed_s": out["elapsed_s"]}, indent=1))
    for n in ITEMS:
        print(n, json.dumps(results.get(n, {})))

if __name__ == "__main__":
    main()
