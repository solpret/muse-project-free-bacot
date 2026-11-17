#!/usr/bin/env python3
"""Run 1731 triage: Motor Agent (strong-lead promotion check), Osiris Guardians
(age deep-dive + strong-lead check), Frost Agent (new, Boltbook 17:29),
Marbleworks (early-lead re-read), ORDIagent/Pacture/NIBULL/NUSA (track-C),
binanceai (track-B). Read-only; writes run-2026-11-09-1731-triage.json."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
REG = "60b9262456de011f7d15a54CdD8c48bAaa8B022F".lower()

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
            res = post_rpc(ep, calls)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {key: (None if (isinstance(it, dict) and "error" in it)
                          else (to_int(it.get("result")) if isinstance(it, dict) else None))
                    for it, key in zip(res, keys)}
        except Exception:
            continue
    return None

def raw_call(addr, data):
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]})
            if isinstance(res, dict) and "result" in res and res["result"] not in (None, "0x"):
                return res["result"]
        except Exception:
            continue
    return None

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=25)
            if isinstance(r, dict) and r.get("result"): return r["result"]
        except Exception: continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception: continue
    return None

def sourcify(addr):
    try:
        req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{addr}",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r: data = json.load(r)
        return {"match": data.get("match"), "creation": data.get("creationMatch"),
                "runtime": data.get("runtimeMatch"),
                "sources": list((data.get("stdJson", {}) or {}).get("sources", {}).keys())[:10]}
    except Exception as e:
        return {"error": str(e)[:200]}

GENERIC = ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()",
           "FREE_SUPPLY()", "MAX_SUPPLY()", "paidMinted()", "mintStart()", "mintEnd()",
           "mintOpen()", "balanceOf(address)", "freeClaimed(address)",
           "freeUsed(address)", "owner()", "contractURI()"]
targets = {
    "Motor Agent": "0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5",
    "Osiris Guardians": "0xd6fcf9db58a559aafbbf9fd823f4f081e6701311",
    "Frost Agent": "0x09f893bab23d14ad296a17092c6611aac5a0932b",
    "Marbleworks": "0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0",
}
out = {"block": get_block(), "run": "2026-11-09-1731", "items": {}}
for name, addr in targets.items():
    t0 = time.time()
    code = get_code(addr)
    reads = raw_batch(addr, GENERIC)
    # Motor-specific: freeLeft() + freeOf(user)
    extra = {}
    if name == "Motor Agent":
        extra = raw_batch(addr, ["freeLeft()", "freeOf(address)"]) or {}
        # costOf(address,uint256) for 1
        data = sel("costOf(address,uint256)") + enc(USER) + "1".rjust(64, "0")
        rc = raw_call(addr, data)
        extra["costOf_user_1"] = to_int(rc)
    # tokenURI(1) for site pointer (Osiris / Frost / Marbleworks)
    turi = None
    if name in ("Osiris Guardians", "Frost Agent", "Marbleworks"):
        data = sel("tokenURI(uint256)") + "1".rjust(64, "0")
        rc = raw_call(addr, data)
        turi = rc
    out["items"][name] = {"address": addr, "reads": reads, "extra": extra,
                          "code_len": len(code) if code else None,
                          "registry_bytes": (REG in code.lower()) if code else None,
                          "sourcify": sourcify(addr), "tokenURI1_raw": turi,
                          "seconds": round(time.time() - t0, 1)}
    print(name, json.dumps(out["items"][name])[:600], flush=True)

# Track-C sales: generic sale views
SALE_VIEWS = ["totalSupply()", "sharesMinted()", "freeMinted()", "freeSharesRemaining()",
              "MAX_FREE()", "FREE_SHARES()", "freeClaimed(address)", "saleStart()", "mintOpen()"]
sales = {
    "ORDIagent": "0x7D10516D08f3bE98aaFD9Ac4169E6Cc30D6bCeB8",
    "Pacture": "0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9",
    "NIBULL": "0x29666Bc0004824dc2B282c82aAC206b8b1711839",
    "NUSA": "0x7D08289E962f5aEc00d56D67322eb2FD056B687c",
}
out["track_c"] = {}
for name, addr in sales.items():
    t0 = time.time()
    out["track_c"][name] = {"address": addr, "reads": raw_batch(addr, SALE_VIEWS),
                            "seconds": round(time.time() - t0, 1)}
    print("TC", name, json.dumps(out["track_c"][name]), flush=True)

# Track-B binanceai
out["binanceai"] = {"mint": "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
                    "reads": raw_batch("0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
                                       ["launched()", "failed()", "isRefundPhase()",
                                        "totalShares()", "tokenClaimed(address)"])}
print("BINANCEAI", json.dumps(out["binanceai"]), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1731-triage.json", "w"), indent=1)
print("TRIAGE 1731 DONE block", out["block"], flush=True)
