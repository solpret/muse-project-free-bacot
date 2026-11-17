import json, urllib.request
ROUT="0x10ED43C718714eb63d5aA57B78B54704E256024E"
WBNB="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
TOK="0xd23be069c3c3a7f631af52584a16a9e46bb41da1"
PAIR="0xd15c928b7b777cac7d613fe840c6ec3de8e4edda"
def pad(a): return a[2:].lower().rjust(64,'0')
def call(ep, method, params):
    payload=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(ep, data=payload, headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r: return json.load(r)
def eth_call(ep, to, data):
    j=call(ep,"eth_call",[{"to":to,"data":data},"latest"])
    if "error" in j: raise Exception(str(j["error"]))
    return j["result"]
ep="https://bsc-dataseed.binance.org"
# token0/token1 of pair
t0=eth_call(ep,PAIR,"0x0dfe1681")
t1=eth_call(ep,PAIR,"0xd21220a7")
print("token0","0x"+t0[-40:],"token1","0x"+t1[-40:])
sell=177600000000000
data="0xd06ca61f"+format(sell,'064x')+"0000000000000000000000000000000000000000000000000000000000000040"+"0000000000000000000000000000000000000000000000000000000000000002"+pad(TOK)+pad(WBNB)
q=eth_call(ep,ROUT,data)
print("raw",q)
print("amounts[0] (in) =", int(q[130:194],16))
print("amounts[1] (out, WBNB wei) =", int(q[194:258],16), "=", int(q[194:258],16)/1e18, "BNB")
