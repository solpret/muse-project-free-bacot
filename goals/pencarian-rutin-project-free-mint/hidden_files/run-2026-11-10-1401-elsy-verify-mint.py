#!/usr/bin/env python3
"""ELSY mint verification: receipt + ownership + free counters (read-only)."""
import json, subprocess, time
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x9e2c16ee581e0d4f0a36ae70205c5599bbb9b22f"
TX = "0xdb09e20fc92089fdbdf6dab6f09a1d22b7f268b960562098a183a0045bdd3a88"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc.nodereal.io/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def rpc(method, params, timeout=25):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    for ep in EPS:
        try:
            out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                                  "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                                 capture_output=True, text=True, timeout=timeout + 5).stdout
            r = json.loads(out)
            if "result" in r: return r["result"]
        except Exception: continue
    return None
receipt = None
for i in range(12):
    receipt = rpc("eth_getTransactionReceipt", [TX])
    if receipt: break
    print(f"poll {i}: no receipt yet", flush=True); time.sleep(10)
print("RECEIPT:", json.dumps(receipt, indent=1)[:1200] if receipt else None, flush=True)
def call(data):
    return rpc("eth_call", [{"to": ADDR, "data": data}, "latest"])
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
out = {}
for tid in (878, 879):
    r = call(sel("ownerOf(uint256)") + format(tid, "064x"))
    out[f"ownerOf_{tid}"] = ("0x" + r[-40:]) if r else None
out["balanceOf_user"] = to_int(call(sel("balanceOf(address)") + enc(USER)))
out["freeMintedByWallet_user"] = to_int(call(sel("freeMintedByWallet(address)") + enc(USER)))
out["mintedByWallet_user"] = to_int(call(sel("mintedByWallet(address)") + enc(USER)))
out["totalSupply"] = to_int(call(sel("totalSupply()")))
out["freeLeft"] = to_int(call(sel("freeLeft()")))
out["tokenURI_878"] = call(sel("tokenURI(uint256)") + format(878, "064x"))
out["tokenURI_879"] = call(sel("tokenURI(uint256)") + format(879, "064x"))
print(json.dumps(out, indent=1), flush=True)
json.dump({"tx": TX, "receipt": receipt, "checks": out},
          open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-10-1401-elsy-receipt.json", "w"), indent=1)
print("DONE")
