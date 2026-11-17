import json, urllib.request
from eth_abi import encode, decode
from eth_utils import keccak

W = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ROUTER = "0x10ED43C718714eb63d5aA57B78B54704E256024E"
FACTORY = "0xca143ce32fe78f1f7019d7d551a6402fc5350c73"
WBNB = "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
RPCS = ["https://bsc-dataseed1.defibit.io/", "https://bsc-dataseed.binance.org/", "https://bsc.publicnode.com"]

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
def gasprice():
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_gasPrice","params":[]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type":"application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=30).read())
            if r.get("result"): return int(r["result"],16), rpc
        except Exception: continue
    return None, None
def u256(h): return int(h,16) if h else 0

out = {}
gp, rpc_used = gasprice()
out["gas_price_wei"] = gp; out["gas_price_gwei"] = gp/1e9 if gp else None
out["gas_est_300k_bnb"] = gp*300000/1e18 if gp else None
out["gas_rpc"] = rpc_used
for sym, tok in [("BNBbaby","0xd0079025a9bb66a7a1de991de2e4326faba35729"),
                 ("QAGENT","0x25e915EEE91411b0AC3273531dbaDc34e0EAA5eB"),
                 ("KAGENT","0xb34105002B19EF0ce43B59011fE848df5c8B174f")]:
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
    out[sym] = item
# 币安加油 reserves + launched
res_h, rpc = call("0xc939e2b49eea548c4539e45b4e355c2b2aa464d6", "0x"+sel("getReserves()"))
out["bianjiayou_reserves"] = None
if res_h:
    r0,r1,_ = decode(["uint112","uint112","uint32"], bytes.fromhex(res_h[2:]))
    out["bianjiayou_reserves"] = [str(r0),str(r1)]
# KAGENT launched
lh, _ = call("0xb34105002B19EF0ce43B59011fE848df5c8B174f", "0x"+sel("launched()"))
out["kagent_launched_raw"] = lh
if lh:
    try: out["kagent_launched"] = decode(["bool"], bytes.fromhex(lh[2:]))[0]
    except Exception: out["kagent_launched"] = None
print(json.dumps(out, indent=1))
