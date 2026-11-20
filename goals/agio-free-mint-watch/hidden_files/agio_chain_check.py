#!/usr/bin/env python3
"""Read-only AGIO mint-contract state check (eth_call only, no signing)."""
import json, urllib.request

RPCS = ["https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed3.binance.org/",
        "https://bsc-dataseed4.binance.org/",
        "https://bsc-dataseed1.bnbchain.org/",
        "https://bsc-dataseed2.bnbchain.org/",
        "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org/",
        "https://bsc-dataseed1.binance.org/",
        "https://bsc-dataseed1.bnbchain.org"]
MINT = "0xeF98407D55b3506275732b94c300866a16D6A3BB"
AGENT = 107187496765866644729837695198686237165740365523485558112864918211974996443404
TASKS = {
    "REPOST_COMMENT": "0x2737e8378ddc9f403160ff120e70bd9e1a5d6183096d6c182f29e53a49338388",
    "AVATAR": "0x4270bfca07279b2d8717bab7cefb7943a69c398f45151b67b5ad61e75c144e59",
}

def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for url in RPCS:
        try:
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as r:
                out = json.load(r)
            if "error" in out:
                last = out["error"]
                continue
            return out["result"]
        except Exception as e:
            last = str(e)
    raise RuntimeError(f"all RPCs failed, last={last}")

def call(data):
    return rpc("eth_call", [{"to": MINT, "data": data}, "latest"])

def u256(hexstr):
    return int(hexstr, 16)

out = {}
out["blockNumber"] = u256(rpc("eth_blockNumber", []))
out["paused"] = u256(call("0x5c975abb")) != 0
out["opened"] = u256(call("0x5f88eade")) != 0
out["totalMinted"] = u256(call("0xa2309ff8"))
out["totalPaid"] = u256(call("0xe7b0f666"))
agent_hex = format(AGENT, "064x")
out["freeMintDone"] = {}
for name, task in TASKS.items():
    data = "0x797cc2c5" + agent_hex + task[2:]
    out["freeMintDone"][name] = u256(call(data)) != 0
print(json.dumps(out, indent=2))
