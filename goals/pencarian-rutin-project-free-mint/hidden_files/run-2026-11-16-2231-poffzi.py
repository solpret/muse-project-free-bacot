import json, subprocess
from Crypto.Hash import keccak
ADDR="0x3D7A6e3d007990B36ab092404C9027a3CD989C14"
EP="https://bsc-dataseed.binance.org/"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def rpc(method, params, timeout=60):
    p=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params})
    out=subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",EP,"-H","Content-Type: application/json","-d",p],capture_output=True,text=True,timeout=timeout+10).stdout
    return json.loads(out)
for name,sig in [("totalSupply","totalSupply()"),("mintOpen","mintOpen()"),("saleOpen","saleOpen()"),("saleStart","saleStart()"),("totalMinted","totalMinted()"),("freeMinted","freeMinted()"),("FREE_SUPPLY","FREE_SUPPLY()")]:
    try:
        r=rpc("eth_call",[{"to":ADDR,"data":sel(sig)},"latest"])
        res=r.get("result")
        print(name,"=",int(res,16) if res and res!="0x" else r,flush=True)
    except Exception as e:
        print(name,"ERR",str(e)[:80],flush=True)
import datetime
print("saleStart 1794844811 =",datetime.datetime.fromtimestamp(1794844811,datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB"),flush=True)
