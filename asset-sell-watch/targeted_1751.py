import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak
def sel(s): return keccak(text=s).hex()[:8]
def call(to, data):
    url = "https://bsc-dataseed.binance.org/"
    body = [{"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}]
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type":"application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        res = r[0].get("result")
        return res
    except Exception as e:
        return f"ERR:{e}"
# KAGENT sale/token 0xb34105002B19EF0ce43B59011fE848df5c8B174f launched()
k = call("0xb34105002B19EF0ce43B59011fE848df5c8B174f", "0x" + sel("launched()"))
print("KAGENT launched_raw:", k)
if k and not k.startswith("ERR"):
    try: print("KAGENT launched:", decode(["bool"], bytes.fromhex(k[2:]))[0])
    except Exception as e: print("decode err:", e)
# PACTURE sale 0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9 launched()
p = call("0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9", "0x" + sel("launched()"))
print("PACTURE launched_raw:", p)
