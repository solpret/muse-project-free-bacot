#!/usr/bin/env python3
"""AgentLabs deep checks run 0031: Sourcify ABI, bytecode registry bytes,
first-mint Transfer-from-zero search (chunked eth_getLogs backwards)."""
import json, subprocess, time
SPEC = "0x639329f5dc4317c44D9Fed961a1217ba845012F7"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def rpc(ep, method, params, timeout=30):
    r = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
                        "-H","Content-Type: application/json",
                        "-d", json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})],
                       capture_output=True, text=True, timeout=timeout+5)
    return json.loads(r.stdout)
# 1. Sourcify (exact legs-script URL)
try:
    r = subprocess.run(["curl","-sL","--max-time","20",
        f"https://sourcify.dev/server/v2/contract/56/{SPEC}?fields=abi"],
        capture_output=True, text=True, timeout=25)
    d = json.loads(r.stdout)
    abi = d.get("abi")
    print("SOURCIFY abi present:", bool(abi), "| keys:", list(d.keys())[:6])
    if abi:
        fns = [e.get("name") for e in abi if e.get("type")=="function"]
        print("SOURCIFY fns:", [f for f in fns if any(k in f.lower() for k in ("mint","free","question","genesis","agent","experiment"))])
        print("SOURCIFY n_fns:", len(fns))
except Exception as e:
    print("SOURCIFY error:", str(e)[:150])
# 2. bytecode: registry address bytes + known selectors
code = None
for ep in EPS:
    try:
        res = rpc(ep, "eth_getCode", [SPEC, "latest"])
        code = res.get("result","")
        if code and len(code) > 100: break
    except Exception: continue
print("CODE len:", len(code) if code else 0)
if code:
    low = code.lower()
    print("registry bytes in code:", "60b9262456de011f7d15a54cdd8c48baaa8b022f" in low)
    from Crypto.Hash import keccak
    def sel(s):
        k = keccak.new(digest_bits=256); k.update(s.encode()); return k.hexdigest()[:8]
    for sig in ["mintFree(uint256)","questionFor(address)","genesisOpen()","currentExperiment()",
                "holdsAgentId(address)","mintPaid()","priceFor(address)","openGenesis()"]:
        s = sel(sig)
        print(f"selector {sig} = {s} in code:", s in low)
# 3. head block + timestamp
head = None
for ep in EPS:
    try:
        head = int(rpc(ep, "eth_blockNumber", []).get("result"), 16); break
    except Exception: continue
print("HEAD:", head)
# 4. first-mint search: chunked eth_getLogs Transfer from zero, backwards 5000-block chunks
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x" + "00"*32
def getlogs(ep, frm, to):
    body = {"jsonrpc":"2.0","id":1,"method":"eth_getLogs","params":[{
        "fromBlock": hex(frm), "toBlock": hex(to), "address": SPEC,
        "topics": [TRANSFER, ZERO]}]}
    r = subprocess.run(["curl","-sL","--max-time","30","-X","POST",ep,
                        "-H","Content-Type: application/json","-d", json.dumps(body)],
                       capture_output=True, text=True, timeout=35)
    d = json.loads(r.stdout)
    if "error" in d: raise RuntimeError(str(d["error"])[:150])
    return d.get("result", [])
earliest = None
to_b = head
for i in range(12):
    frm = max(0, to_b - 4999)
    found = None
    for ep in EPS:
        try:
            found = getlogs(ep, frm, to_b); break
        except Exception as e:
            found = None
            continue
    n = len(found) if found is not None else -1
    print(f"chunk {i}: {frm}-{to_b} mint-logs={n}", flush=True)
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
