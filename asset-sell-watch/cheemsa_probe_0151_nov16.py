import json, urllib.request
from eth_utils import keccak
def sel(s): return keccak(text=s).hex()[:8]
def call(to, data):
    req = urllib.request.Request("https://bsc-dataseed.binance.org/", data=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode(), headers={"Content-Type":"application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        return r.get("result")
    except Exception as e:
        return "ERR:"+str(e)
sc = "0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"
print(json.dumps({
  "tradingOpen_raw": call(sc, "0x"+sel("tradingOpen()")),
  "launched_raw": call(sc, "0x"+sel("launched()")),
}, indent=1))
