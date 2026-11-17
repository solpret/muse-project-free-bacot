import json, subprocess
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
MINT = "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
views = ["launched()", "failed()", "isRefundPhase()", "totalShares()", "tokenClaimed(address)"]
calls = []
for i, sig in enumerate(views):
    data = sel(sig) + enc(USER) if "(address)" in sig else sel(sig)
    calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":MINT,"data":data},"latest"]})
for ep in ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]:
    try:
        out = subprocess.run(["curl","-sL","--max-time","25","-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(calls)],capture_output=True,text=True,timeout=30).stdout
        res = json.loads(out)
        if isinstance(res, list):
            print(json.dumps({v: (None if ("error" in it) else int(it["result"],16)) for v,it in zip(views,res)}))
            break
    except Exception as e:
        print("fail", ep, e)
