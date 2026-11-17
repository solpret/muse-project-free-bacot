import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPCS = ["https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed2.binance.org/",
        "https://bsc-dataseed1.binance.org/", "https://bsc-dataseed3.binance.org/",
        "https://bsc.publicnode.com"]

def sel(sig): return keccak(text=sig).hex()[:8]
def call_one(rpc, to, data):
    body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":to,"data":data},"latest"]}).encode()
    req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if r.get("error") or not r.get("result"): return None
    return r["result"]
def call(to, data):
    for rpc in RPCS:
        try:
            v = call_one(rpc, to, data)
            if v is not None: return v, rpc
        except Exception: continue
    return None, None
def u256(h): return int(h,16) if h else 0

out = {}
# gas price
gp = None
for rpc in RPCS:
    try:
        body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_gasPrice","params":[]}).encode()
        req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
        r = json.loads(urllib.request.urlopen(req, timeout=30).read())
        if r.get("result"):
            gp = int(r["result"],16); out["gas_price_wei"]=gp; out["gas_price_gwei"]=gp/1e9
            out["gas_est_300k_bnb"]=gp*300000/1e18; out["gas_rpc"]=rpc; break
    except Exception: continue
if gp is None: out["gas_price_wei"]=None

for sym, tok, sell_raw in [
    ("PATCH","0xBbA053567846842F95C060867a5C9eb6b3983c80", None),
    ("QAGENT","0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB", None),
    ("YYDS","0xd23be069c3c3a7f631af52584a16a9e46bb41da1", None),
    ("bianjiayou","0x397BF425926F521Ac5BEbe5062793BB224e3eF8f", "50000000000000000000000000"),
    ("PACTURE","0x10b80088fDAf9363d83671BE66b64f231f9e92f6", "10000000000000000000000000"),
    ("KAGENT","0xb34105002B19EF0ce43B59011fE848df5c8B174f", "50000000000000000000000"),
]:
    bal_h, rpc = call(tok, "0x"+sel("balanceOf(address)")+encode(["address"],[W]).hex())
    item = {"balance_raw": str(u256(bal_h)) if bal_h else None, "rpc": rpc}
    if bal_h is not None:
        bal = u256(bal_h)
        item["balance_human"] = bal/1e18
        pair_h, _ = call(FACTORY, "0x"+sel("getPair(address,address)")+encode(["address","address"],[tok,WBNB]).hex())
        pair = ("0x"+pair_h[-40:]) if pair_h and u256(pair_h) else None
        item["pair_wbnb"] = pair
        if pair:
            res_h, _ = call(pair, "0x"+sel("getReserves()"))
            if res_h:
                r0,r1,_ = decode(["uint112","uint112","uint32"], bytes.fromhex(res_h[2:]))
                item["reserves"] = [str(r0),str(r1)]
                if r0 and r1:
                    amt = int(sell_raw) if sell_raw else bal
                    q_h, _ = call(ROUTER, "0x"+sel("getAmountsOut(uint256,address[])")+encode(["uint256","address[]"],[amt,[tok,WBNB]]).hex())
                    if q_h:
                        outs = decode(["uint256[]"], bytes.fromhex(q_h[2:]))[0]
                        item["quote_bnb"] = outs[1]/1e18 if len(outs)==2 else None
    out[sym] = item
lh, _ = call("0xb34105002B19EF0ce43B59011fE848df5c8B174f", "0x"+sel("launched()"))
out["kagent_launched_raw"] = lh
if lh:
    try: out["kagent_launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
    except Exception: out["kagent_launched"] = None
print(json.dumps(out, indent=1, ensure_ascii=False))
