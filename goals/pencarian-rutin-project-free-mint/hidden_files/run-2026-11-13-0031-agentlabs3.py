#!/usr/bin/env python3
"""AgentLabs launch-time: genesisStart()/experimentStart(1) views + first-mint
log search with 1000-block chunks (public RPC eth_getLogs)."""
import json, subprocess, time
from Crypto.Hash import keccak
SPEC = "0x639329f5dc4317c44D9Fed961a1217ba845012F7"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_u(n): return hex(n)[2:].rjust(64,"0")
def rpc(ep, method, params, timeout=30):
    r = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
                        "-H","Content-Type: application/json",
                        "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})],
                       capture_output=True, text=True, timeout=timeout+5)
    return json.loads(r.stdout)
# genesisStart + experimentStart(1)
for name, data in [("genesisStart", sel("genesisStart()")),
                   ("experimentStart(1)", sel("experimentStart(uint256)")+enc_u(1))]:
    val = None
    for ep in EPS:
        try:
            res = rpc(ep, "eth_call", [{"to": SPEC, "data": data}, "latest"])
            if "result" in res and res["result"] not in (None, "0x"):
                val = int(res["result"], 16); break
        except Exception: continue
    if val:
        print(f"{name} = {val} | UTC {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(val))} | WIB {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(val+7*3600))}", flush=True)
    else:
        print(f"{name} = None", flush=True)
# head
head = None
for ep in EPS:
    try:
        head = int(rpc(ep, "eth_blockNumber", []).get("result"), 16); break
    except Exception: continue
print("HEAD:", head, flush=True)
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x"+"00"*32
def getlogs(ep, frm, to):
    body = {"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{
        "fromBlock": hex(frm), "toBlock": hex(to), "address": SPEC, "topics": [TRANSFER, ZERO]}]}
    r = subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,
                        "-H","Content-Type: application/json","-d", json.dumps(body)],
                       capture_output=True, text=True, timeout=35)
    d = json.loads(r.stdout)
    if "error" in d: raise RuntimeError(str(d["error"])[:200])
    return d.get("result", [])
earliest = None
to_b = head
for i in range(40):
    frm = max(0, to_b - 999)
    found = None; err = None
    for ep in EPS:
        try:
            found = getlogs(ep, frm, to_b); break
        except Exception as e:
            err = str(e)[:150]; continue
    print(f"chunk {i}: {frm}-{to_b} mint-logs={len(found) if found is not None else 'ERR '+str(err)}", flush=True)
    if found:
        earliest = min(int(x["blockNumber"],16) for x in found)
    if not found:
        break
    to_b = frm - 1
print("EARLIEST_MINT_BLOCK:", earliest)
if earliest:
    for ep in EPS:
        try:
            b = rpc(ep, "eth_getBlockByNumber", [hex(earliest), False])
            ts = int(b["result"]["timestamp"], 16)
            print("EARLIEST_MINT_TS:", ts, "| UTC:", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts)),
                  "| WIB:", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts+7*3600)))
            break
        except Exception as e:
            print("block ts error:", str(e)[:120])
