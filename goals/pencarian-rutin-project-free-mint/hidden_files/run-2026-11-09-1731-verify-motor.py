#!/usr/bin/env python3
"""Verify Motor Agent mint tx on-chain. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
TX = "0x1faa1e314eb461a32c260cf7f93a5f73defa02d314e921898667ee7eb101b18c"
NFT = "0x86F83E98437A1DcF0e4A62828f68C1D53B3c7AB5"
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
    tid = None
    for log in receipt.get("logs", []):
        if log.get("topics", [None])[0] == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" and len(log.get("topics", [])) >= 4:
            tid = to_int(log["topics"][3])
    out["tokenId_from_log"] = tid
    print("RECEIPT status", out["status"], "block", out["blockNumber"], "gas", out["gasUsed"], "tokenId", tid, flush=True)
    def ec(data):
        r = call("eth_call", [{"to": NFT, "data": data}, "latest"])
        return to_int(r)
    out["post"] = {
        "balanceOf_user": ec(sel("balanceOf(address)") + enc(USER)),
        "agentFreeUsed": ec(sel("agentFreeUsed()")),
        "freeUsedByWallet_user": ec(sel("freeUsedByWallet(address)") + enc(USER)),
        "totalSupply": ec(sel("totalSupply()")),
        "ownerOf_token": ec(sel("ownerOf(uint256)") + format(tid, "064x")) if tid else None,
        "modelOf_token": ec(sel("modelOf(uint256)") + format(tid, "064x")) if tid else None,
        "tierOf_token": ec(sel("tierOf(uint256)") + format(tid, "064x")) if tid else None,
    }
    print("POST", json.dumps(out["post"]), flush=True)
    # tokenURI for rarity traits
    if tid:
        r = call("eth_call", [{"to": NFT, "data": sel("tokenURI(uint256)") + format(tid, "064x")}, "latest"])
        out["post"]["tokenURI_raw_len"] = len(r or "")
        out["post"]["tokenURI_raw"] = (r or "")[:600]
        print("tokenURI len", out["post"]["tokenURI_raw_len"], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-09-1731-verify-motor.json", "w"), indent=1)
print("VERIFY MOTOR DONE", flush=True)
