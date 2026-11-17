import json, urllib.request, time
W="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
FACT="0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
ROUT="0x10ED43C718714eb63d5aA57B78B54704E256024E"
TOK="0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
EPS=["https://bsc-dataseed.binance.org","https://bsc-dataseed1.binance.org","https://bsc-dataseed1.defibit.io","https://bsc-dataseed2.binance.org","https://bsc-dataseed3.binance.org","https://bsc-dataseed4.binance.org"]
def pad(a): return a[2:].lower().rjust(64,'0')
def call(ep, method, params, tries=3):
    last=None
    for i in range(tries):
        try:
            payload=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
            req=urllib.request.Request(ep, data=payload, headers={"Content-Type":"application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=20) as r:
                j=json.load(r)
            if "error" in j: raise Exception(str(j["error"]))
            return j["result"]
        except Exception as e:
            last=e; time.sleep(2)
    raise last
out={}
for ep in EPS:
    try:
        pair=call(ep,"eth_call",[{"to":FACT,"data":"0xe6a43905"+pad(TOK)+pad(WBNB)},"latest"])
        out["pair"]="0x"+pair[-40:]; out["pair_ep"]=ep; break
    except Exception as e:
        out.setdefault("pair_errors",[]).append(f"{ep}:{e}")
if out.get("pair") and int(out["pair"],16)!=0:
    p=out["pair"]
    for ep in EPS:
        try:
            res=call(ep,"eth_call",[{"to":p,"data":"0x0902f1ac"},"latest"])
            out["reserves"]=[str(int(res[2:66],16)),str(int(res[66:130],16))]; out["reserves_ep"]=ep; break
        except Exception as e:
            out.setdefault("res_errors",[]).append(f"{ep}:{e}")
    sell=177600000000000
    data="0xd06ca61f"+format(sell,'064x')+"0000000000000000000000000000000000000000000000000000000000000040"+"0000000000000000000000000000000000000000000000000000000000000002"+pad(TOK)+pad(WBNB)
    for ep in EPS:
        try:
            q=call(ep,"eth_call",[{"to":ROUT,"data":data},"latest"])
            out["quote_raw"]=str(int(q[194:258],16)); out["quote_bnb"]=int(q[194:258],16)/1e18; out["quote_ep"]=ep; break
        except Exception as e:
            out.setdefault("quote_errors",[]).append(f"{ep}:{e}")
print(json.dumps(out, indent=1))
