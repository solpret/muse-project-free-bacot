import json, urllib.request
from eth_utils import keccak
W="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT="0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT="0x10ED43C718714eb63d5aA57B78B54704E256024E"
ENDPOINTS=["https://bsc-dataseed.binance.org","https://bsc-dataseed1.binance.org","https://bsc-dataseed1.defibit.io","https://bsc-dataseed2.binance.org"]
def pad(a): return a[2:].lower().rjust(64,'0')
def sel(s): return keccak(text=s).hex()[:8]
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
entries=json.load(open("/home/hatch/workspace/asset-sell-watch/pending-swaps.json"))["entries"]
out=[]
gas=None
try:
    gas, gep = try_all(lambda ep: int(call(ep,"eth_gasPrice",[])["result"],16))
except Exception as e:
    out.append({"gas_error":str(e)})
for e in entries:
    tok=e["token"]; sym=e["symbol"]
    amt=int(e["amount_to_sell_raw"]) if e.get("amount_to_sell_raw") else None
    row={"symbol":sym,"token":tok}
    try:
        bal, ep = try_all(lambda ep, t=tok: int(eth_call(ep,t,"0x70a08231"+pad(W)),16))
        row["balance_raw"]=str(bal); row["balance_human"]=bal/(10**e.get("decimals",18)); row["balance_ep"]=ep
    except Exception as ex:
        row["balance_error"]=str(ex); out.append(row); continue
    try:
        pair, ep = try_all(lambda ep, t=tok: eth_call(ep,FACT,"0xe6a43905"+pad(t)+pad(WBNB)))
        pair_addr="0x"+pair[-40:]
        row["pair_wbnb"]=pair_addr if int(pair,16)!=0 else None; row["pair_ep"]=ep
    except Exception as ex:
        row["pair_error"]=str(ex); out.append(row); continue
    if row["pair_wbnb"]:
        try:
            res, ep = try_all(lambda ep, p=row["pair_wbnb"]: eth_call(ep,p,"0x0902f1ac"))
            r0=int(res[2:66],16); r1=int(res[66:130],16)
            row["reserves"]=[str(r0),str(r1)]
        except Exception as ex:
            row["reserves_error"]=str(ex)
        sell = amt if amt is not None else bal
        if sell>0 and row.get("reserves") and int(row["reserves"][0])>0 and int(row["reserves"][1])>0:
            data="0xd06ca61f"+format(sell,'064x')+"0000000000000000000000000000000000000000000000000000000000000040"+"0000000000000000000000000000000000000000000000000000000000000002"+pad(tok)+pad(WBNB)
            try:
                q, ep = try_all(lambda ep, d=data: eth_call(ep,ROUT,d))
                # getAmountsOut returns [amountIn, amountOut]; amountOut = 2nd word = hex chars 194:258
                row["quote_raw"]=str(int(q[194:258],16)); row["quote_bnb"]=int(q[194:258],16)/1e18
            except Exception as ex:
                row["quote_error"]=str(ex)
    # sale-contract state probes (best effort; 0x / revert = function absent)
    sc=e.get("sale_contract")
    if sc:
        st={}
        for fname in ["launched()","tradingOpen()","isOpen()","opened()","phase()"]:
            try:
                r, _ep = try_all(lambda ep, s=sc, f=fname: eth_call(ep,s,"0x"+sel(f)))
                st[fname]=r
            except Exception as ex:
                st[fname]="ERR:"+str(ex)[:80]
        row["sale_state"]=st
    out.append(row)
print(json.dumps({"gas_price_wei":gas,"gas_price_gwei":(gas/1e9 if gas else None),"results":out}, indent=1))
