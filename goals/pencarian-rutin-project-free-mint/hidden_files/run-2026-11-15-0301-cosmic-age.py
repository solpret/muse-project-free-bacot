#!/usr/bin/env python3
"""Cosmic Sentinel first-mint deep-dive lanjutan run 0301 (read-only).
Run 0201 cek 10.000 blok (head-10000..head), run 0231 cek 10.000 blok (head-20000..head-10000), tanpa hit.
Run ini cek 10.000 blok berikutnya ke belakang (head-30000 .. head-20000),
chunk 1000 blok, eth_getLogs Transfer-from-zero via dataseed."""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x88731d1eb41c36f3d705fdb58b658244c06afc36"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
t0 = time.time()
def rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+10).stdout
    return json.loads(out)
head = None
for ep in EPS:
    try:
        r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, 30)
        head = int(r["result"],16); break
    except Exception: continue
out = {"address": ADDR, "head": head, "window": [head-30000, head-20000], "chunks": []}
found = []
for i in range(10):
    frm = head-30000 + i*1000
    to = frm + 999
    hit = None
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{
                "fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                "topics": [TRANSFER, ZERO]}]}, 60)
            logs = r.get("result", [])
            hit = {"from": frm, "to": to, "n": len(logs)}
            if logs: found.extend(logs)
            break
        except Exception as e:
            hit = {"from": frm, "to": to, "error": str(e)[:100]}
    out["chunks"].append(hit)
    print(f"chunk {i+1}/10 {frm}-{to}: {hit}", flush=True)
out["found_count"] = len(found)
if found:
    first = min(found, key=lambda l: int(l["blockNumber"],16))
    out["first_mint_block"] = int(first["blockNumber"],16)
    out["first_mint_tx"] = first["transactionHash"]
    # block timestamp
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                         "params":[first["blockNumber"], False]}, 30)
            out["first_mint_ts"] = int(r["result"]["timestamp"],16)
            break
        except Exception: pass
out["elapsed_s"] = round(time.time()-t0,1)
json.dump(out, open(BASE+"run-2026-11-15-0301-cosmic-age.json","w"), indent=1)
print("DONE found", len(found), "elapsed", out["elapsed_s"])
