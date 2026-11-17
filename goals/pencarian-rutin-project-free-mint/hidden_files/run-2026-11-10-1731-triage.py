#!/usr/bin/env python3
"""Triage run 1731: shape-check new Boltbook/feed contracts.
Read-only. Writes run-2026-11-10-1731-triage.json"""
import json, time, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
TARGETS = {
 "POTION SHOP": "0x7f92593905facb51d9566520b4e6fa8c2997ab0c",
 "ONI-new": "0x852f80b92112f94342c4687f30fde2d849961daa",
 "JagentMintV2": "0x3643A907f875fA9B740e1C0747E91b5aA5222aB8",
 "JAGENT token": "0x8e6442663A4F8C50b6132c68d42A30E7DFE4Ae15",
 "feed-f1b9": "0xf1b9D0b2Fac297AAD0A9eA858Dea805A49a0140a",
}
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            outd = {}
            for item, key in zip(res, keys):
                outd[key] = None if (isinstance(item, dict) and "error" in item) else (to_int(item.get("result")) if isinstance(item, dict) else None)
            return outd
        except Exception:
            continue
    return None
def str_call(addr, sig):
    # string-returning view (name/symbol) via eth_call, decode utf8 tail
    data = sel(sig)
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            res = r.get("result")
            if res and len(res) > 130:
                b = bytes.fromhex(res[2:])
                ln = int.from_bytes(b[32:64], "big")
                return b[64:64+ln].decode("utf-8", "ignore")
        except Exception:
            continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "mintPrice()", "price()",
         "balanceOf(address)", "freeClaimed(address)", "freeMintedBy(address)",
         "agentId()", "agentRegistry()", "REGISTRY()", "registry()",
         "freeSharesRemaining()", "freeAvailable(address)", "freeLeft()",
         "freeUsed()", "canClaimFree(address)", "saleStart()", "mintStart()",
         "START_TIME()", "startTime()", "quote(uint256)", "tokensPerShare()",
         "freeSupply()", "freeAllocation()", "decimals()"]
out = {}
for name, addr in TARGETS.items():
    d = {"address": addr}
    got = raw_batch(addr, VIEWS)
    d.update(got if got else {k.split("(")[0] + ("_user" if "(address)" in k else ""): None for k in VIEWS})
    d["name"] = str_call(addr, "name()")
    d["symbol"] = str_call(addr, "symbol()")
    # Sourcify
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contract/56/{addr}",
            headers={"User-Agent": "free-bacot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            sj = json.loads(r.read().decode())
        d["sourcify"] = {"match": sj.get("stdJson", {}).get("match") or sj.get("match"),
                         "has_abi": bool(sj.get("abi"))}
        abi = sj.get("abi") or []
        fnames = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"]
        d["abi_functions"] = fnames
        src = json.dumps(sj)
        d["registry_in_source"] = REG.lower() in src.lower()
        json.dump(sj, open(f"{BASE}/abi-1731-{addr[2:6].lower()}.json", "w"))
    except Exception as e:
        d["sourcify"] = {"error": f"{type(e).__name__}: {str(e)[:100]}"}
    out[name] = d
    print(name, addr, "| name:", d["name"], "| sym:", d["symbol"],
          "| ts:", d.get("totalSupply"), "| tm:", d.get("totalMinted"),
          "| freeMinted:", d.get("freeMinted"), "| FREE_SUPPLY:", d.get("FREE_SUPPLY"),
          "| agentId:", d.get("agentId"), "| registry:", d.get("agentRegistry") or d.get("REGISTRY"),
          "| sourcify:", d["sourcify"], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-10-1731-triage.json", "w"), indent=1)
print("TRIAGE DONE")
