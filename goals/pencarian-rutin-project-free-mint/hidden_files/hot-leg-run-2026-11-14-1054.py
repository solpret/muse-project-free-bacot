#!/usr/bin/env python3
"""Hot-leg run 2026-11-14 10:54 WIB.
Legs: (1) Sourcify recently-verified feed poll limit 20; (2) Boltbook EN+ZH
front pages; (3) shape-check new addresses (S1/S2); (4) batch re-read of
active snapshot items (read-only, fast_rpc batch); (5) scan-bridge check.
Writes ONLY hot-leg-run-2026-11-14-1054.json + hot-leg-seen.json (own files).
Never writes main snapshot / main seen files."""
import json, re, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import call_many, race
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
EXCLUDED = {"0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
            "0x8b47354e7b76b1970a0d06365c8244a810d37493"}
NOW_WIB = "2026-11-14T11:05+07:00"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        return None, str(e)

def get_json(url, timeout=20):
    body = fetch(url, timeout)
    if body is None or isinstance(body, tuple):
        return None
    try:
        return json.loads(body)
    except Exception:
        return None

ADDR_RE = re.compile(r"0x[0-9a-fA-F]{40}")

NOARG = ["totalSupply", "totalMinted", "freeMinted", "freeClaimed", "freeRemaining",
         "FREE_SUPPLY", "FREE_CAP", "FREE_SHARES", "FREE_LOTS_CAP", "mintOpen",
         "isFreeOpen", "saleOpen", "saleStart", "mintOpensAt", "mintStart",
         "freeStart", "freeEnd", "freeClaimedTotal", "launched", "finalized",
         "refunding", "paidMinted", "freeCount", "freeLeft", "refundOpen",
         "totalSnippets", "currentCommit", "genesisOpen", "genesisStart",
         "totalRemnants", "currentCycle", "mintStartTime", "standardRemaining",
         "legendaryRemaining", "MAX_SUPPLY", "remainingSupply", "saleActive",
         "mintEnd", "failed", "isRefundPhase", "totalShares", "AGENT_ID",
         "owner", "paused", "totalSpecimens", "currentExperiment",
         "FREE_MAX", "FREE_POOL", "freeMintedPerWallet", "mintedPerWallet",
         "TOKEN_PRICE", "price", "genesisStart"]
USERARG = ["balanceOf", "freeClaimed", "freeMinted", "mintedLots", "freeAvailable",
           "freeUsed", "priceFor", "holdsAgentId", "hasAgentId", "isEligible",
           "mintedBy", "freeClaimedByWallet", "freeMintedPerWallet",
           "mintedPerWallet", "mintedByWallet", "tokenClaimed",
           "freeSharesClaimed", "snippetsOf", "mintsBy"]

# (name, address, extra calls: list of (label, calldata))
TARGETS = {
 "WoozCode": "0xfF172b79d040faefA1Bf34B47151edc87130246E",
 "MORFO": "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
 "NOISE": "0xBA5352A3A05Ec637394810D791a412E78A349247",
 "DragonAgents": "0xad0D8ac3D61fC8ab397B7136C69fcBf1281a4998",
 "AngelEye-77D9": "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
 "AngelEye-07bD": "0x07bD6DbbEf508ad83BA2C557ED979732488894A1",
 "NovaRemnants": "0x38C1695eb72B7522c8d6452a4CE27122532A0d69",
 "RaceAgents": "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",
 "AbsurdAgentNFT": "0x72c14121681F1133545947B0735563835CC07B67",
 "B77D": "0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe",
 "Zero": "0x89B340435e4fD27e00442f7F1b3a3b3244b4E647",
 "HIVE": "0x1458b0C132Fb51BDC65B1Ca7a3BE484BCd9A2f77",
 "AgentZENITH": "0x699b6397986cc6c444069efe692023b1253dc26d",
 "AgentNOVA": "0x43462d7f269fde4914b03e1e07067a61b62b9540",
 "SPARKS": "0xd52fd117c4b47d03e4e16e778871f09faa5a024b",
 "AgentBubble": "0x0d72970046c056db90888351b739246f468bff0b",
 "BinanceAI-mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
 "WANGCAI": "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd",
 "YUANBAO": "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E",
 "NOTV": "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
 "PX24": "0xe712510fcb27935e657e41ebb97982d6b123136c",
 "Zephyra": "0x00a9791be6317d6e3a6c60f75a706c870d882048",
 "LumenFindings": "0x4158B701EaA30E8FaDBaA526F70780A38318c1C4",
 "Pengu": "0x5AEc03C90656743475810926B2B2bd443D5c26a4",
 "SKRR": "0x9081f02876c173d0c69f042959cfd0d61c668b17",
 "ACARD": "0xf1d544cc495a05320f36cd02d12e8ef9d9fbff69",
 "Boltbook-8d292d": "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",
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

def shape_check(addr):
    meta = get_json(f"https://sourcify.dev/server/v2/contracts/56/{addr}", timeout=20)
    if meta is None:
        return {"status": "shape-check-failed", "reason": "sourcify-fetch-failed"}
    try:
        abi = meta["stdJson"]["output"]["abi"]
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
            "n_fns": len(fns), "functions": sorted(fns),
            "status": "checked"}

def main():
    t0 = time.time()
    out = {"run": "free-mint-hot-leg 2026-11-14 10:54 WIB",
           "started_wib": NOW_WIB}

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
                                "top_verifiedAt": feed_meta.get(feed_addrs[0]) if feed_addrs else None,
                                "new_contracts": []}
    else:
        out["sourcify_feed"] = {"total": 0, "error": "feed-fetch-failed", "new_contracts": []}

    # --- leg 2: Boltbook EN + ZH ---
    seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    out["seen_n"] = len(seen)
    bb = {}
    for lang, url in (("en", "https://boltbook.fun/"),
                      ("zh", "https://boltbook.fun/?lang=zh")):
        body = fetch(url, timeout=25)
        if isinstance(body, tuple) or body is None:
            bb[lang] = {"bytes": 0, "full_address_contracts": 0, "new": 0, "new_contracts": [], "error": "fetch-failed"}
            continue
        addrs = sorted(set(ADDR_RE.findall(body)))
        new = [a for a in addrs if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]
        bb[lang] = {"bytes": len(body), "full_address_contracts": len(addrs),
                    "new": len(new), "new_contracts": new}
    out["boltbook_en"] = bb["en"]
    out["boltbook_zh"] = bb["zh"]
    out["boltbook_new_total"] = bb["en"]["new"] + bb["zh"]["new"]

    # --- leg 3: shape-check new addresses ---
    seen_keys = {k.lower() for k in seen}
    new_addrs = [a for a in feed_addrs if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
    new_addrs += [a for a in bb["en"]["new_contracts"] + bb["zh"]["new_contracts"]
                  if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
    out["sourcify_feed"]["new"] = len([a for a in feed_addrs if a.lower() not in seen_keys and a.lower() not in EXCLUDED])
    out["sourcify_feed"]["new_contracts"] = [a for a in feed_addrs if a.lower() not in seen_keys and a.lower() not in EXCLUDED]
    sc = []
    for a in sorted(set(new_addrs)):
        r = shape_check(a)
        r["address"] = a
        r["verifiedAt"] = feed_meta.get(a)
        sc.append(r)
        seen[a] = {"first_seen_wib": NOW_WIB, "source": "sourcify-feed" if a in feed_addrs else "boltbook",
                   "status": "checked" if r.get("status") == "checked" else r.get("status"),
                   "note": f"S1={r.get('S1')} S2={r.get('S2')} mint={r.get('mint')} quote={r.get('quote')} free={r.get('free')} agent={r.get('agent')}"}
    out["shape_check"] = sc
    out["s1_pass"] = [s["address"] for s in sc if s.get("S1")]
    out["s2_pass"] = [s["address"] for s in sc if s.get("S2")]

    # --- leg 4: batch re-read active snapshot items ---
    try:
        blk = race("eth_blockNumber", [])
        block = int(blk, 16) if blk else None
    except Exception:
        block = None
    calls, keys = [], []
    for name, addr in TARGETS.items():
        for fn in NOARG:
            calls.append((addr, sel(fn + "()")))
            keys.append((name, fn))
        for fn in USERARG:
            calls.append((addr, sel(fn + "(address)") + USER_PAD))
            keys.append((name, fn + "_user"))
        # two-arg variants seen in prior runs
        calls.append((addr, sel("commitEnd(uint256)") + "0" * 63 + "1"))
        keys.append((name, "commitEnd_1"))
        calls.append((addr, sel("snippetsOf(address,uint256)") + USER_PAD + "0" * 63 + "1"))
        keys.append((name, "snippetsOf_1_user"))
        calls.append((addr, sel("priceFor(address,uint256)") + USER_PAD + "0" * 63 + "1"))
        keys.append((name, "priceFor_user_1"))
        calls.append((addr, sel("quote(address,uint256)") + USER_PAD + "0" * 63 + "1"))
        keys.append((name, "quote_user_1"))
    results = {}
    CH = 150
    for i in range(0, len(calls), CH):
        chunk = calls[i:i + CH]
        try:
            res = call_many(chunk)
        except Exception as e:
            print(f"chunk {i} failed: {e}")
            res = [None] * len(chunk)
        for (name, fn), r in zip(keys[i:i + CH], res):
            results.setdefault(name, {})[fn] = decode(r)
    out["block"] = block
    out["reads"] = {n: {"address": TARGETS[n], "views": results.get(n, {})} for n in TARGETS}
    out["reads_ok"] = sum(1 for n in TARGETS if any(v is not None for v in results.get(n, {}).values()))
    out["reads_total"] = len(TARGETS)
    out["elapsed_s"] = round(time.time() - t0, 1)

    # --- bridge leg (read-only) ---
    try:
        bridge = json.load(open(f"{HF}/scan-bridge.json"))
        snap = json.load(open(f"{HF}/onchain-snapshot.json"))
        snap_addrs = set()
        for sec in ("contracts", "track_c"):
            for v in snap.get(sec, {}).values():
                if isinstance(v, dict):
                    for k in ("address", "sale", "token"):
                        if v.get(k):
                            snap_addrs.add(v[k].lower())
        bcontracts = bridge.get("contracts", {})
        not_in_snap = [a for a in bcontracts if a.lower() not in snap_addrs]
        out["bridge"] = {"n": len(bcontracts), "not_in_snapshot": len(not_in_snap),
                         "same_owner_discarded": sum(1 for v in bcontracts.values() if v.get("same_owner_discarded")),
                         "note": "unchanged vs 10:49 run (116/0/7) unless counts differ"}
    except Exception as e:
        out["bridge"] = {"error": str(e)}

    json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-1054.json", "w"), indent=1)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"))
    print(json.dumps({"feed_new": out["sourcify_feed"].get("new_contracts"),
                      "boltbook_new": out["boltbook_new_total"],
                      "s1_pass": out["s1_pass"], "s2_pass": out["s2_pass"],
                      "reads_ok": out["reads_ok"], "block": block,
                      "elapsed_s": out["elapsed_s"]}, indent=1))
    for n in TARGETS:
        print(n, json.dumps(results.get(n, {})))

if __name__ == "__main__":
    main()
