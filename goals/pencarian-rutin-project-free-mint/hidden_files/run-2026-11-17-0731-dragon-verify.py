#!/usr/bin/env python3
"""Verify DRAGON mint tx on-chain. Writes run-2026-11-17-0731-dragon-verify.json."""
import json, time, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TX = "0x6ea21ebb9b15229d9e14c0bf4f963757993382f77a2ad50f172c6be3c8bc6581"
ADDR = "0xfc191b76041498b14dcae3c802af3389c74263e6"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s): return keccak(s.encode())[:4].hex()
def rpc(method, params, timeout=15):
    payload = json.dumps([{"jsonrpc":"2.0","id":1,"method":method,"params":params}]).encode()
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=payload, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())[0].get("result")
        except Exception:
            continue
    return None
receipt = None
for i in range(12):
    receipt = rpc("eth_getTransactionReceipt", [TX])
    if receipt:
        break
    time.sleep(5)
out = {"tx": TX, "receipt": receipt}
if receipt:
    out["status"] = int(receipt.get("status","0x0"),16)
    out["blockNumber"] = int(receipt.get("blockNumber","0x0"),16)
    out["gasUsed"] = int(receipt.get("gasUsed","0x0"),16)
    out["contractAddress_receipt"] = receipt.get("contractAddress")
    # post-state reads (batch)
    calls = [
        ("totalMinted", "totalMinted()"),
        ("freeMinted", "freeMinted()"),
        ("freeRemaining", "freeRemaining()"),
        ("hasClaimedFree_user", "hasClaimedFree(address)"),
        ("mintedBy_user", "mintedBy(address)"),
        ("balanceOf_user", "balanceOf(address)"),
        ("ownerOf_537", "ownerOf(uint256)"),
    ]
    payload = []
    for i,(lab,sig) in enumerate(calls):
        data = "0x"+sel(sig)
        if "address" in sig:
            data += "0"*24 + USER[2:].lower()
        elif "uint256" in sig:
            data += "%064x" % 537
        payload.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":ADDR,"data":data},"latest"]})
    body = json.dumps(payload).encode()
    res = None
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                res = json.loads(r.read().decode())
            break
        except Exception:
            continue
    vals = {}
    if res:
        by = {it["id"]: it for it in res if isinstance(it, dict)}
        for i,(lab,sig) in enumerate(calls):
            it = by.get(i+1, {})
            v = it.get("result")
            if lab == "ownerOf_537":
                vals[lab] = ("0x"+v[-40:]) if v else None
            else:
                vals[lab] = int(v,16) if v not in (None,"0x") else None
    out["post_state"] = vals
    # gas price paid: tx details
    tx = rpc("eth_getTransactionByHash", [TX])
    if tx:
        out["gasPrice_wei"] = int(tx.get("gasPrice","0x0"),16)
        out["gas_cost_bnb"] = out["gasUsed"] * out["gasPrice_wei"] / 1e18
json.dump(out, open(f"{HF}/run-2026-11-17-0731-dragon-verify.json","w"), indent=1)
print(json.dumps(out, indent=1))
