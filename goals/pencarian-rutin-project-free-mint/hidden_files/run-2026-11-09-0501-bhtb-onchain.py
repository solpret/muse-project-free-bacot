import json, urllib.request, time
from eth_hash.auto import keccak
CTR="0xffcA030c6C69A5b75392AAfaF5BF1980c0ed0467"
AGENT="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPCS=["https://bsc-dataseed1.bnbchain.org","https://bsc-dataseed2.bnbchain.org","https://bsc-dataseed.binance.org"]
def sel(sig): return "0x"+keccak(sig.encode()).hex()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_uint(n): return format(n,"064x")
CALLS=[
 ("name()",""),("symbol()",""),("decimals()",""),("totalSupply()",""),
 ("FREE_QUOTA()",""),("FREE_TOKENS()",""),("PAID_QUOTA()",""),("PAID_TOKENS()",""),
 ("PRICE_PER_PAID_SHARE()",""),("TOTAL_SHARES()",""),("TOTAL_SUPPLY()",""),
 ("freeUsed()",""),("totalSold()",""),("paidSold()",""),("mintEnd()",""),
 ("startTime()",""),("saleEnded()",""),("agentIdRegistry()",""),("payout()",""),
 ("DEV_LOCKED()",""),("lockUntil()",""),("totalRevenueWei()",""),
 ("quote(uint256,address)",enc_uint(1)+enc_addr(AGENT)),
 ("freeClaimed(address)",enc_addr(AGENT)),
 ("maxSharesOf(address)",enc_addr(AGENT)),
 ("remainingSharesOf(address)",enc_addr(AGENT)),
 ("sharesOf(address)",enc_addr(AGENT)),
 ("balanceOf(address)",enc_addr(AGENT)),
 ("MINT_DURATION()",""),("BASE_MAX_PER_WALLET()",""),
]
def rpc_call(rpc, payload):
    req=urllib.request.Request(rpc, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)
out={"contract":CTR,"rpc_used":None,"block":None,"reads":{},"errors":{}}
payload=[{"jsonrpc":"2.0","id":i,"method":"eth_call","params":[{"to":CTR,"data":sel(s)+args},"latest"]} for i,(s,args) in enumerate(CALLS)]
payload.append({"jsonrpc":"2.0","id":99,"method":"eth_blockNumber","params":[]})
payload.append({"jsonrpc":"2.0","id":100,"method":"eth_getCode","params":[CTR,"latest"]})
t0=time.time()
resp=None
for rpc in RPCS:
    try:
        resp=rpc_call(rpc,payload); out["rpc_used"]=rpc; break
    except Exception as e:
        out["errors"][rpc]=str(e)[:200]
if resp is None:
    out["status"]="RPC_FAILED"; print(json.dumps(out,indent=1)); open("run-2026-11-09-0501-bhtb-onchain.json","w").write(json.dumps(out,indent=1)); raise SystemExit
if isinstance(resp,dict): resp=[resp]
for item in resp:
    i=item.get("id")
    if i==99:
        out["block"]=int(item.get("result","0x0"),16) if item.get("result") else None
    elif i==100:
        out["code_len"]=(len(item.get("result",""))-2)//2 if item.get("result") else 0
    elif isinstance(i,int) and i<len(CALLS):
        name=CALLS[i][0]
        if "error" in item: out["reads"][name]={"error":str(item["error"])[:150]}
        else: out["reads"][name]=item.get("result")
out["duration_s"]=round(time.time()-t0,1); out["status"]="OK"
print(json.dumps(out,indent=1))
open("run-2026-11-09-0501-bhtb-onchain.json","w").write(json.dumps(out,indent=1))
