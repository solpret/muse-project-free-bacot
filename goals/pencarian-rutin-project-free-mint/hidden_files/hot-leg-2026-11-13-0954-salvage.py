#!/usr/bin/env python3
"""Hot-leg run 2026-11-13 09:54 WIB — SALVAGE (sequential re-read).
Main batch leg failed (leg34_ok 0); this retries per-contract sequential
race() eth_calls for the key active items, plus retries Sourcify shape-check
for the 3 feed-new addresses and Boltbook EN/ZH via curl.
Read-only. Writes only hot-leg-run-2026-11-13-0954-salvage.json."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def call(addr, data):
    try:
        r = race("eth_call", [{"to": addr, "data": data}, "latest"])
        if not r or r in ("0x", None):
            return None
        h = r[2:]
        return int(h[-64:], 16) if len(h) >= 64 else None
    except Exception:
        return None

def read_contract(addr, noarg, userarg):
    out = {}
    for fn in noarg:
        out[fn] = call(addr, sel(fn + "()"))
    for fn in userarg:
        out[fn + "_user"] = call(addr, sel(fn + "(address)") + USER_PAD)
    return out

def curl(url, timeout=25):
    try:
        p = subprocess.run(["curl", "-sS", "-m", str(timeout),
                            "-A", "Mozilla/5.0",
                            url], capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

def shape_check(addr):
    body = curl(f"https://sourcify.dev/server/v2/contracts/56/{addr}", 25)
    if not body:
        return {"status": "shape-check-failed", "reason": "sourcify-fetch-failed"}
    try:
        meta = json.loads(body)
        abi = meta["stdJson"]["output"]["abi"]
    except Exception:
        return {"status": "shape-check-failed", "reason": "no-abi-in-sourcify"}
    fns = {e.get("name") for e in abi if e.get("type") == "function"}
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
    from datetime import datetime, timezone, timedelta
    wib = timezone(timedelta(hours=7))
    out = {"run": "hot-leg 0954 salvage (sequential re-read)",
           "started_wib": datetime.now(wib).strftime("%Y-%m-%dT%H:%M:%S+07:00")}
    # Boltbook retry via curl
    bb = {}
    for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
        body = curl(url, 25)
        if body:
            addrs = sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))
            bb[lang] = {"bytes": len(body), "addrs": addrs}
        else:
            bb[lang] = {"error": "fetch-failed"}
    out["boltbook_retry"] = bb
    # Sourcify shape-check retry for the 3 feed-new addresses
    sc = {}
    for a in ("0x7535181f3b2208a560F90B6A1F6c473D0fDafefa",
              "0xf96c66a8730df490037B7cd1cc2Ca1a17a544444",
              "0xb31De539a79A5B5d9Bf6A6071f38240E19Fc2D7b"):
        sc[a] = shape_check(a)
    out["shapecheck_retry"] = sc

    reads = {}
    reads["OBFG"] = read_contract("0x5314071bba19943f58347ba5dec423e5032a6818",
        ["totalMinted", "freeMinted", "FREE_SUPPLY", "saleStart", "saleOpen"],
        ["freeAvailable", "balanceOf"])
    reads["JNTM"] = read_contract("0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
        ["freeClaimed", "freeLeft", "FREE_LOTS_CAP", "totalMinted", "paidMinted", "mintStart", "opened", "saleOpen", "mintOpen", "launched"],
        ["freeAvailable", "balanceOf"])
    reads["Agentx"] = read_contract("0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
        ["freeMinted", "FREE_CAP", "mintOpen", "totalMinted", "mintOpensAt"],
        ["freeClaimed", "balanceOf"])
    reads["BC1B"] = read_contract("0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
        ["freeCount", "FREE_CAP", "totalSupply", "saleStart", "refundOpen"],
        ["freeMinted", "balanceOf"])
    reads["Pickgrid"] = read_contract("0x7f541bcc33abed0e64455565da723e949c6f76f0",
        ["totalSupply", "freeMinted", "FREE_CAP"], ["balanceOf"])
    reads["MECHA"] = read_contract("0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
        ["totalMinted", "freeClaimed", "FREE_SUPPLY"], ["freeAvailable", "balanceOf"])
    reads["NOTV"] = read_contract("0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
        ["totalMinted", "FREE_SHARES", "freeStart"], ["balanceOf"])
    reads["SEVEN"] = read_contract("0xFf65cf70a15fA0B06Bf8D8ED020Cf9F917C80f96",
        ["totalMinted", "freeMinted", "FREE_CAP"], [])
    reads["WFPASS"] = read_contract("0xD52A86AC936c4C3d46aF0d49e8D44F3C698BEe7C",
        ["totalMinted", "freeMinted", "FREE_SUPPLY"], [])
    reads["RunicKey"] = read_contract("0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4",
        ["totalMinted", "freeMinted", "FREE_SUPPLY"], [])
    out["reads"] = reads
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(f"{HF}/hot-leg-run-2026-11-13-0954-salvage.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
