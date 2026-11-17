import json, urllib.request
EP="https://bsc-dataseed.binance.org"
def keccak_sel(sig):
    try:
        from eth_hash.auto import keccak
        return "0x"+keccak(sig.encode()).hex()[:8]
    except Exception:
        import subprocess
        return None
def call(to, data):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    r=urllib.request.Request(EP,data=p,headers={"Content-Type":"application/json"},method="POST")
    j=json.load(urllib.request.urlopen(r,timeout=15))
    if "error" in j: return None, str(j["error"])
    return j["result"], None
sels=["tradingOpen()","totalMinted()","launched()","pair()","isOpen()","opened()","phase()","saleEnded()","ended()","mintEnded()","freeSharesRemaining()","totalSold()","sold()"]
out={}
for name, addr in [("CHEEMSA","0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2"),("PACTURE","0x95AF9fe16fE5c1741b5E3F1b3b045a8c2470eca9")]:
    row={}
    for s in sels:
        sel=keccak_sel(s)
        v,err=call(addr,sel)
        if err or v is None or v=="0x": row[s]=None
        else:
            try: row[s]=int(v,16)
            except: row[s]=v
    out[name]=row
print(json.dumps(out,indent=1))
