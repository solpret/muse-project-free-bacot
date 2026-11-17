import json, urllib.request
from eth_abi import encode
from eth_utils import keccak
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPCS = ["https://bsc-dataseed3.binance.org/", "https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed.binance.org/"]
def sel(s): return keccak(text=s).hex()[:8]
out = {}
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":FACTORY,"data":"0x"+sel("getPair(address,address)")+encode(["address","address"],["0x10b80088fDAf9363d83671BE66b64f231f9e92f6",WBNB]).hex()},"latest"]}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=20).read())
        if r.get("result"):
            v = int(r["result"],16)
            out["PACTURE_pair_wbnb"] = ("0x"+r["result"][-40:]) if v else None
            out["PACTURE_pair_rpc"] = rpc
            break
    except Exception: continue
print(json.dumps(out, indent=1))
