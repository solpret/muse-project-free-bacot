import json, urllib.request
from eth_utils import keccak
W="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT="0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT="0x10ED43C718714eb63d5aA57B78B54704E256024E"
ENDPOINTS=["https://bsc-dataseed.binance.org","https://bsc-dataseed1.binance.org","https://bsc-dataseed1.defibit.io","https://bsc-dataseed2.binance.org","https://bsc.publicnode.com","https://bsc-dataseed3.binance.org"]
def pad(a): return a[2:].lower().rjust(64,'0')
def call(ep, method, params):
    payload=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(ep, data=payload, headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.load(r)
def eth_call(ep, to, data):
    j=call(ep,"eth_call",[{"to":to,"data":data},"latest"])
    if "error" in j: raise Exception(str(j["error"]))
    return j["result"]
def try_all(fn):
    errs=[]
    for ep in ENDPOINTS:
        try: return fn(ep), ep
        except Exception as e: errs.append(f"{ep}:{e}")
    raise Exception(" | ".join(errs))
TOKENS=[("WNO","0x8C969a4CD49E4774908e667702C3d7C3ece164D0","1000000000000000000000000"),
("AMBR","0x88B06f59BdB54039AEBf1d308d8B9181a90385c1","10000000000000000000000"),
("CHEEMSA","0x00b4bdA5BBf83A72f1252CCEf361f107f5a728b2","5000000000000000000000000"),
("NEB","0xf08ac9c91dcfc5b74eae6c87e744cfefe0d32a68","1000000000000000000000"),
("PEPE","0x66Af3218a336CcdB675DBa37F6632CfcA3F5Fe46","10000000000000000000000000")]
out=[]
for sym,tok,amt in TOKENS:
    row={"symbol":sym,"token":tok}
    try:
        bal, ep = try_all(lambda ep, t=tok: int(eth_call(ep,t,"0x70a08231"+pad(W)),16))
        row["balance_raw"]=str(bal); row["balance_human"]=bal/1e18; row["balance_ep"]=ep
    except Exception as ex:
        row["balance_error"]=str(ex); out.append(row); continue
    try:
        pair, ep = try_all(lambda ep, t=tok: eth_call(ep,FACT,"0xe6a43905"+pad(t)+pad(WBNB)))
        row["pair_wbnb"]="0x"+pair[-40:] if int(pair,16)!=0 else None; row["pair_ep"]=ep
    except Exception as ex:
        row["pair_error"]=str(ex); out.append(row); continue
    if row["pair_wbnb"]:
        try:
            res, ep = try_all(lambda ep, p=row["pair_wbnb"]: eth_call(ep,p,"0x0902f1ac"))
            row["reserves"]=[str(int(res[2:66],16)),str(int(res[66:130],16))]
        except Exception as ex:
            row["reserves_error"]=str(ex)
        if row.get("reserves") and int(row["reserves"][0])>0 and int(row["reserves"][1])>0:
            sell=int(amt)
            data="0xd06ca61f"+format(sell,'064x')+"0000000000000000000000000000000000000000000000000000000000000040"+"0000000000000000000000000000000000000000000000000000000000000002"+pad(tok)+pad(WBNB)
            try:
                q, ep = try_all(lambda ep, d=data: eth_call(ep,ROUT,d))
                row["quote_raw"]=str(int(q[194:258],16)); row["quote_bnb"]=int(q[194:258],16)/1e18
            except Exception as ex:
                row["quote_error"]=str(ex)
    out.append(row)
print(json.dumps({"results":out}, indent=1))
