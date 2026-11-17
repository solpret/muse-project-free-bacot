#!/usr/bin/env python3
"""Verify Marbleworks mint tx on-chain. Read-only; writes run-2026-11-09-1731-verify-marbleworks.json."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TX = "0x595e39380ed2019f6eb3de69aceb5532ea07fc10defe156b9ecd6cf0bbc120c0"
NFT = "0xCc844748C64b9b8e45aC4504553C9757c7CDB7E0"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
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
def call(method, params):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
receipt = None
for i in range(12):
    receipt = call("eth_getTransactionReceipt", [TX])
    if receipt: break
    print(f"poll {i+1}: no receipt yet", flush=True)
    time.sleep(10)
out = {"tx": TX, "receipt": receipt}
if receipt:
    out["blockNumber"] = to_int(receipt.get("blockNumber"))
    out["status"] = to_int(receipt.get("status"))
    out["gasUsed"] = to_int(receipt.get("gasUsed"))
    out["logs"] = len(receipt.get("logs", []))
    print("RECEIPT status", out["status"], "block", out["blockNumber"], "gas", out["gasUsed"], flush=True)
    # post-mint reads
    def ec(data):
        r = call("eth_call", [{"to": NFT, "data": data}, "latest"])
        return to_int(r)
    out["post"] = {
        "balanceOf_user": ec(sel("balanceOf(address)") + enc(USER)),
        "freeMinted": ec(sel("freeMinted()")),
        "freeUsed_user": ec(sel("freeUsed(address)") + enc(USER)),
        "totalSupply": ec(sel("totalSupply()")),
        "tokenOfOwnerByIndex": None,
    }
    # tokenOfOwnerByIndex(user,0)
    r = call("eth_call", [{"to": NFT, "data": sel("tokenOfOwnerByIndex(address,uint256)") + enc(USER) + "0".rjust(64, "0")}, "latest"])
    out["post"]["tokenOfOwnerByIndex"] = to_int(r)
    # tokenURI(456) for rarity
    r = call("eth_call", [{"to": NFT, "data": sel("tokenURI(uint256)") + str(456).rjust(64, "0")}, "latest"])
    out["post"]["tokenURI_456_raw"] = (r or "")[:400]
    print("POST", json.dumps(out["post"]), flush=True)
    # MWGL balance
    MWGL = "0x458Ba0b810ff314b1D7d41a0F0f209706dcf949b"
    r = call("eth_call", [{"to": MWGL, "data": sel("balanceOf(address)") + enc(USER)}, "latest"])
    out["post"]["MWGL_balance_user"] = to_int(r)
    print("MWGL balance", out["post"]["MWGL_balance_user"], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1731-verify-marbleworks.json", "w"), indent=1)
print("VERIFY DONE", flush=True)
