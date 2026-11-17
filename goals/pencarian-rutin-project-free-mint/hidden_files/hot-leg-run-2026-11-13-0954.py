#!/usr/bin/env python3
"""Hot-leg run 2026-11-13 09:54 WIB.
Legs: (1) Sourcify recently-verified feed poll limit 20; (2) Boltbook EN+ZH
front pages; (3) shape-check new addresses (S1/S2); (4) batch re-read of
active snapshot items (read-only, fast_rpc batch); (5) scan-bridge check.
Writes ONLY hot-leg-run-2026-11-13-0954.json + hot-leg-seen.json (own files).
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
         "refunding", "paidMinted", "freeCount", "freeLeft", "refundOpen"]
USERARG = ["balanceOf", "freeClaimed", "freeMinted", "mintedLots", "freeAvailable", "freeUsed"]

TARGETS = {
 "OBFG": "0x5314071bba19943f58347ba5dec423e5032a6818",
 "Agentx": "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
 "BUCKET": "0x2b0d3b384C341020aed1d49907b5708C423bA6DA",
 "Airdrop-417d": "0x417d04C0a323fC89cDBbEf4D361161fCfA45baF9",
 "SEVEN": "0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
 "NOTV": "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
 "JNTM": "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
 "BC1B": "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
 "BinanceLife": "0x4367b86F889014e6fD57fE812B86A581b913C645",
 "WFPASS": "0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
 "LuckyCatch": "0xD405C90079c594DA2456F5b37B4158A12f1382e5",
 "RunicKey": "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
 "Stampooor": "0x467696af8c2206B977B24081445104632dc1D459",
 "Pickgrid": "0x7f541bcc33abed0e64455565da723e949c6f76f0",
 "MECHA": "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
 "OliverAgents": "0xad86e4d52e55709d1bda08f922853d4b109e0810",
 "RigForge": "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d",
 "binanceai-mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
 "MOONDRILL": "0x87b354E2014D2e418927A1105dD219A2e7b063b0",
 "NAOMI": "0xC7Adf8f0b49a5C1840C31636A96c6D5ed077c7E9",
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
    """Light S1/S2 shape check via Sourcify ABI. Returns dict or failure."""
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
            "agent": agent, "status": "ok" if (s1 or s2) else "not-sale-shape"}

def main():
    t0 = time.time()
    out = {"run": "free-mint-hot-leg 2026-11-13 09:54 WIB",
           "started_wib": "2026-11-13T09:56:00+07:00"}

    # --- leg 1: Sourcify feed ---
    feed = get_json("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=20)
    feed_addrs = []
    if feed and isinstance(feed, dict):
        for c in feed.get("results", feed.get("contracts", [])):
            a = c.get("address") or c.get("contractAddress")
            if a:
                feed_addrs.append(a)
        out["feed"] = {"n": len(feed_addrs),
                       "newest_verifiedAt": (feed.get("results") or [{}])[0].get("verifiedAt") if feed.get("results") else None,
                       "oldest_verifiedAt": (feed.get("results") or [{}])[-1].get("verifiedAt") if feed.get("results") else None}
    else:
        out["feed"] = {"n": 0, "error": "feed-fetch-failed"}

    # --- leg 2: Boltbook EN + ZH ---
    seen = json.load(open(f"{HF}/hot-leg-seen.json"))
    out["seen_total_before"] = len(seen)
    bb = {}
    for lang, url in (("en", "https://boltbook.fun/"),
                      ("zh", "https://boltbook.fun/?lang=zh")):
        body = fetch(url, timeout=25)
        if isinstance(body, tuple) or body is None:
            bb[lang] = {"error": "fetch-failed"}
            continue
        addrs = sorted(set(ADDR_RE.findall(body)))
        bb[lang] = {"bytes": len(body), "addrs": addrs}
    out["boltbook_en"] = bb.get("en", {})
    out["boltbook_zh"] = bb.get("zh", {})
    bb_addrs = sorted(set(bb.get("en", {}).get("addrs", []) + bb.get("zh", {}).get("addrs", [])))
    new_addrs = [a for a in bb_addrs + feed_addrs if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]
    out["feed_new"] = [a for a in feed_addrs if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]
    out["boltbook_new"] = [a for a in bb_addrs if a.lower() not in {k.lower() for k in seen} and a.lower() not in EXCLUDED]

    # --- leg 3: shape-check new addresses ---
    sc = {}
    for a in sorted(set(new_addrs)):
        sc[a] = shape_check(a)
        seen[a] = "2026-11-13T09:56+07:00"
    out["shapecheck"] = sc

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
    out["leg34_reads"] = {n: {"address": TARGETS[n], "views": results.get(n, {})} for n in TARGETS}
    out["leg34_ok"] = sum(1 for n in TARGETS if any(v is not None for v in results.get(n, {}).values()))
    out["seen_total"] = len(seen)
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
        out["bridge"] = {"total": len(bcontracts), "not_in_snapshot": not_in_snap,
                         "same_owner_discarded": [a for a, v in bcontracts.items() if v.get("same_owner_discarded")]}
    except Exception as e:
        out["bridge"] = {"error": str(e)}

    json.dump(out, open(f"{HF}/hot-leg-run-2026-11-13-0954.json", "w"), indent=1)
    json.dump(seen, open(f"{HF}/hot-leg-seen.json", "w"))
    print(json.dumps({k: out[k] for k in ("feed", "feed_new", "boltbook_new", "shapecheck", "leg34_ok", "block", "elapsed_s")}, indent=1))
    for n in TARGETS:
        print(n, json.dumps(results.get(n, {})))

if __name__ == "__main__":
    main()
