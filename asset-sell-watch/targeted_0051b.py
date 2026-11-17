import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS = ["https://bsc-dataseed3.binance.org/", "https://bsc-dataseed4.binance.org/",
        "https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed1.binance.org/", "https://bsc-dataseed.binance.org/",
        "https://bsc.publicnode.com", "https://bsc-rpc.publicnode.com"]
def sel(s): return keccak(text=s).hex()[:8]
def call(rpc, to, data):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=20).read())
    if r.get("error") or not r.get("result"): return None
    return r["result"]
out = {}
for rpc in RPCS:
    try:
        v = call(rpc, "0x10b80088fDAf9363d83671BE66b64f231f9e92f6",
                 "0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex())
        if v is not None:
            out["PACTURE_balance_raw"] = str(int(v,16)); out["PACTURE_balance_human"] = int(v,16)/1e18; out["PACTURE_rpc"] = rpc; break
    except Exception: continue
else:
    out["PACTURE_balance_raw"] = None
for rpc in RPCS:
    try:
        v = call(rpc, "0xb34105002B19EF0ce43B59011fE848df5c8B174f", "0x"+sel("launched()"))
        if v is not None:
            out["KAGENT_launched"] = decode(["bool"], bytes.fromhex(v[2:]))[0]; out["KAGENT_rpc"] = rpc; break
    except Exception: continue
else:
    out["KAGENT_launched"] = None
print(json.dumps(out, indent=1))
