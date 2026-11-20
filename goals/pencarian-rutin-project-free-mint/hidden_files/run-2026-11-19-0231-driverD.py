#!/usr/bin/env python3
"""Run 2026-11-19 02:31 WIB, driver D: supplementary user-slot reads for the
3 new early leads (mintedCount/hasMinted for the user wallet) + head block.
Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.quicknode/bin")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from eth_hash.auto import keccak
from quicknode import ProxyHTTPSConnection
from dynamic_credentials import dynamic_credential_entry
QN_HOST = "stylish-thrilling-star.bsc.quiknode.pro"
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def rpc(calls, timeout=40):
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": to, "data": data}, "latest"]}
               for i, (to, data) in enumerate(calls)]
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=timeout)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(payload).encode(),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read(); status = resp.status
    finally:
        conn.close()
    if status != 200:
        raise IOError(f"quicknode http {status}")
    resp = json.loads(raw.decode())
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    res = []
    for i in range(len(calls)):
        it = by_id.get(i + 1, {})
        if "result" in it and it["result"] not in (None, "0x"):
            try:
                res.append(int(it["result"], 16))
            except Exception:
                res.append(it["result"])
        elif "error" in it:
            res.append("revert")
        else:
            res.append(None)
    return res

calls = [
 ("0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0", "0x" + sel("mintedCount(address)") + enc_addr(USER)),
 ("0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0", "0x" + sel("hasMinted(address)") + enc_addr(USER)),
 ("0x5b63bd45e61a2e6540548c3509b598b6384206c5", "0x" + sel("hasMinted(address)") + enc_addr(USER)),
 ("0x5b63bd45e61a2e6540548c3509b598b6384206c5", "0x" + sel("mintedCount(address)") + enc_addr(USER)),
 ("0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9", "0x" + sel("hasMinted(address)") + enc_addr(USER)),
 ("0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9", "0x" + sel("mintedCount(address)") + enc_addr(USER)),
 ("0xfcadfb7cc85b6ea540d64e4f4b9f162e630f55c0", "0x" + sel("totalMinted()")),
 ("0x5b63bd45e61a2e6540548c3509b598b6384206c5", "0x" + sel("totalMinted()")),
 ("0x1dd8740ffca0be3caac3b4a3eb41fdff506e38a9", "0x" + sel("totalMinted()")),
]
labels = ["AMP_mintedCount_user", "AMP_hasMinted_user", "AGATE_hasMinted_user",
          "AGATE_mintedCount_user", "ADROP_hasMinted_user", "ADROP_mintedCount_user",
          "AMP_totalMinted", "AGATE_totalMinted", "ADROP_totalMinted"]
try:
    vals = rpc(calls)
except Exception as e:
    vals = [f"error: {type(e).__name__}: {str(e)[:120]}"] * len(calls)
head = rpc([("0x0000000000000000000000000000000000000000", "0x")]) if False else None
try:
    entry = dynamic_credential_entry("custom.quicknode")
    surrogate = str(entry["surrogate"]).strip()
    conn = ProxyHTTPSConnection(QN_HOST, 443, timeout=40)
    try:
        conn.request("POST", f"/{surrogate}/", body=json.dumps(
            [{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode(),
            headers={"Content-Type": "application/json"})
        resp = conn.getresponse(); raw = resp.read()
    finally:
        conn.close()
    head = int(json.loads(raw.decode())[0]["result"], 16)
except Exception as e:
    head = f"error: {str(e)[:120]}"
out = {"labels": labels, "values": vals, "block": head, "run": "free-mint-search 2026-11-19 02:31 WIB (driver D)"}
json.dump(out, open(f"{HF}/run-2026-11-19-0231-driverD.json", "w"), indent=1)
print(json.dumps(out, indent=1, default=str))
