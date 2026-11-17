import json, urllib.request, time
from Crypto.Hash import keccak
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS="2026-11-05-1339"
RPCS=["https://bsc.publicnode.com","https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org"]
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE="0xb21583A08581278BcF925351a99C61A4562C62f0"
TOKEN="0xc50c9b132af459Fa7b351Fd6f3AAeeFd8E9E1E96"
TX="0xf7d880c4812f29b238d912df272cda415b8526a20cba59872c52d3e489574f88"
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def rpc(method,params):
    for r in RPCS:
        try:
            body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(r,data=body,headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req,timeout=15) as resp: out=json.load(resp)
            if "error" in out: continue
            return out["result"]
        except Exception: continue
    return None
def call(to,data):
    r=rpc("eth_call",[{"to":to,"data":data},"latest"])
    if r is None or (isinstance(r,dict)): return r
    try: return int(r,16) if r and r!="0x" else 0
    except Exception: return r
receipt=None
for i in range(12):
    receipt=rpc("eth_getTransactionReceipt",[TX])
    if receipt: break
    time.sleep(5)
print("RECEIPT", json.dumps(receipt,indent=1)[:1500] if receipt else None)
out={"tx":TX,"receipt":receipt}
if receipt:
    out["status"]=int(receipt["status"],16)
    out["blockNumber"]=int(receipt["blockNumber"],16)
    out["gasUsed"]=int(receipt["gasUsed"],16)
    eff=int(receipt.get("effectiveGasPrice","0x0"),16)
    out["effectiveGasPriceWei"]=eff
    out["gasCostBNB"]=out["gasUsed"]*eff/1e18
    out["sale:freeClaimed"]=call(SALE,sel("freeClaimed()"))
    out["sale:paidSold"]=call(SALE,sel("paidSold()"))
    out["sale:hasFreeShare(user)"]=call(SALE,sel("hasFreeShare(address)")+enc(USER))
    out["sale:freeVested(user)"]=call(SALE,sel("freeVested(address)")+enc(USER))
    out["sale:phase"]=call(SALE,sel("phase()"))
    out["token:balanceOf(user)"]=call(TOKEN,sel("balanceOf(address)")+enc(USER))
    print(json.dumps(out,indent=1))
json.dump(out,open(f"{BASE}/hot-leg-{TS}-senbazuru-verify.json","w"),indent=1)
