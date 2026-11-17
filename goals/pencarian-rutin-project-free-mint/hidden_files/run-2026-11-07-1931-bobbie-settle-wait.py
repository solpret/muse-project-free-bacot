import json, time, urllib.request
from Crypto.Hash import keccak
RPC = "https://bsc-dataseed.binance.org"
ADDR = "0x3BF121dC4c5a1Ba567F3eE801d0e447601726207"
SEQ = 1585
TARGET = 132206420
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def rpc(method, params, timeout=30):
    body = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode()
    req = urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)
def call(data):
    return rpc("eth_call", [{"to": ADDR, "data": data}, "latest"])
for i in range(40):
    try:
        head = int(rpc("eth_blockNumber", [])["result"], 16)
        nts = call(sel("nextToSettle()"))
        nts_v = int(nts["result"], 16) if nts.get("result") else None
        print(f"try {i}: head={head} target={TARGET} nextToSettle={nts_v} (need head>{TARGET} and nts=={SEQ})", flush=True)
        if head > TARGET and nts_v == SEQ:
            print("READY")
            break
    except Exception as e:
        print("try", i, "ERR", e, flush=True)
    time.sleep(5)
else:
    print("NOT READY after 200s")
