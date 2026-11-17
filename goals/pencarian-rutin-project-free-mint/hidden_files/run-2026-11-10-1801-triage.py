#!/usr/bin/env python3
"""Triage run 1801: shape-check new Boltbook/feed contracts.
Read-only. Writes run-2026-11-10-1801-triage.json"""
import json, time, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
TARGETS = {
 "ACORE": "0xf4bacf30fb8f69373f63d99c657f53dd7774af1d",
 "NIGHTFORGE": "0x22f43ba09fd4beb9417d4484c60370354b220186",
 "insert.coin": "0x0d03cb2149094910fc7a46f05529c561090ddaaf",
 "Tiny Worlds": "0x04c310b283030c056110abef004fc784a4cb6568",
 "Mixtape & Co.": "0xbb164c4e54cdcc6fa0a262e22f1452a67b44674b",
 "DICE.EXE": "0x9af8ebbc01556421bd4ff603f989fd109b9407d0",
 "Wise Owl Society": "0x1cf9e60218493149ace7dc953497c07175aa625e",
 "EMBERANVIL": "0x7673c596a6702d32f844266dc2ca7b1fd6d7df21",
 "POTION SHOP": "0x7f92593905facb51d9566520b4e6fa8c2997ab0c",
 "ONI-new": "0x852f80b92112f94342c4687f30fde2d849961daa",
 "SAKURA-mint": "0xf2705a84602369069782624279837a08bdbbf6d6",
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
    # costOf(user,1) — "costOf first-free" template: first mint free iff 0
    try:
        data = sel("costOf(address,uint256)") + enc(USER) + "0"*63 + "1"
        for ep in EPS:
            try:
                r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
                res = r.get("result")
                if res and res != "0x":
                    d["costOf_user_1"] = to_int(res); break
            except Exception:
                continue
        else:
            d["costOf_user_1"] = None
    except Exception as e:
        d["costOf_user_1"] = f"ERR {e}"
    d["contractURI"] = str_call(addr, "contractURI()")
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
          "| costOf1:", d.get("costOf_user_1"), "| contractURI:", (d.get("contractURI") or "")[:80], "| sourcify:", d["sourcify"], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-10-1801-triage.json", "w"), indent=1)
print("TRIAGE DONE")
