#!/usr/bin/env python3
"""Run 2331 parent triage: probe 10 first-seen scan contracts + MORPHA.
Read-only, threaded, 5s timeout, 2 RPCs. Classify agent-shaped vs paid-only."""
import json, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-2331"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as r: out = json.load(r)
            if "error" in out: return None
            v = out["result"]
            if not v or v == "0x": return None
            try: return int(v, 16)
            except Exception: return v
        except Exception:
            continue
    return None

def call(to, sig, args=""): return raw(to, sel(sig) + args)

def tx_receipt(txh):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionReceipt",
                               "params": [txh]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if out.get("result"): return out["result"]
        except Exception:
            continue
    return None

def tx_info(txh):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getTransactionByHash",
                               "params": [txh]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if out.get("result"): return out["result"]
        except Exception:
            continue
    return None

ITEMS = [
 ("Moonfall", "0x4232308c31927e493e96FdB05134Fa39C26c24D0"),
 ("Toucan Play", "0x5ABe8974d554Ea0c797fBC4c6B01EA4446616B2f"),
 ("BEWORK", "0x78eDD42101e889cC3Ce4B24CBb0Fc774082BcAee"),
 ("Synthetic Ghost", "0xA224bb6B4B89D9c22C140Ea8d37D2290E99AECAc"),
 ("Not Financial Advice39", "0x2Fb4598Cc4c0758d9a541CAe813E81f0b138024A"),
 ("Delta Yeti Agent", "0x282885b50ee2B8e539d695f859A87B1A18F2B66e"),
 ("Void Quokka Agent", "0x4D0e44744baF36Ad27f736BA023bdFbB0B9823Eb"),
 ("Cope Harder39", "0xD9A49dF66443bA35e7A96bEE63b0B8913F47c22c"),
 ("SENSHI", "0x759a2c237ee454004aA1029622483954a248c320"),
 ("jelly.exe", "0x807E86F6d1bc8fc5E8f53052DAC5d379D4efc120"),
 ("MORPHA", "0xb40e4d3b33c5d70ab31a1dde3c240727691cb738"),
]

def probe(item):
    name, addr = item
    d = {"address": addr}
    d["totalSupply"] = call(addr, "totalSupply()")
    if not isinstance(d["totalSupply"], int):
        d["totalMinted"] = call(addr, "totalMinted()")
    d["freeClaimed"] = call(addr, "freeClaimed()")
    d["freeMinted"] = call(addr, "freeMinted()")
    d["FREE_SUPPLY"] = call(addr, "FREE_SUPPLY()")
    d["MAX_SUPPLY"] = call(addr, "MAX_SUPPLY()")
    d["PRICE"] = call(addr, "PRICE()")
    d["price"] = call(addr, "price()")
    d["mintOpen"] = call(addr, "mintOpen()")
    d["owner"] = call(addr, "owner()")
    d["balanceOf_user"] = call(addr, "balanceOf(address)", enc(USER))
    d["quote_user_1"] = call(addr, "quote(address,uint256)", enc(USER) + enc_uint(1))
    d["canFreeMint_user"] = call(addr, "canFreeMint(address)", enc(USER))
    d["mintedBy_user"] = call(addr, "mintedBy(address)", enc(USER))
    print(name, d, flush=True)
    return name, d

out = {"triage": {}}
t0 = time.time()
with ThreadPoolExecutor(max_workers=6) as ex:
    for name, d in ex.map(probe, ITEMS):
        out["triage"][name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-triage.json", "w"), indent=1)

# MORPHA claimed free-mint tx check
MORPHA_TX = "0x6380d031659b60204d1b08149760f9387936c17e5ed42124521a82eebd494c01"
tx = tx_info(MORPHA_TX)
rc = tx_receipt(MORPHA_TX)
out["morph_tx"] = {
    "tx": {"to": tx.get("to") if tx else None, "from": tx.get("from") if tx else None,
           "value": tx.get("value") if tx else None, "input_prefix": (tx.get("input") or "")[:18] if tx else None} if tx else None,
    "receipt": {"status": rc.get("status") if rc else None, "blockNumber": rc.get("blockNumber") if rc else None,
                "logs": len(rc.get("logs", [])) if rc else None} if rc else None,
}
print("MORPH_TX", json.dumps(out["morph_tx"]), flush=True)
print("DONE in %.1fs" % (time.time() - t0), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-triage.json", "w"), indent=1)
