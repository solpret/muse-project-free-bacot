import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from Crypto.Hash import keccak
from ankr import ankr_post
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v): return int(v, 16) if v else None
def dec_str(v):
    if not v: return None
    b = bytes.fromhex(v[2:])
    if len(b) >= 64:
        ln = int.from_bytes(b[32:64], "big")
        if 0 < ln <= len(b) - 64: return b[64:64+ln].decode("utf-8", "replace")
    return None
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
def words(v):
    if not v: return None
    b = bytes.fromhex(v[2:]); return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
def first_mints(C, head, frm=131060000):
    logs=[]; tok=None; pages=0; err=None
    while True:
        params={"blockchain":"bsc","fromBlock":hex(frm),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,
                "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],"address":C}
        if tok: params["pageToken"]=tok
        try: body=ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err=str(e)[:200]; break
        res=body.get("result",{}) if isinstance(body,dict) else {}
        got=[l for l in res.get("logs",[]) if l.get("address","").lower()==C.lower()]
        logs.extend(got); tok=res.get("nextPageToken"); pages+=1
        if not tok or pages>=10: break
        time.sleep(1)
    out={"count":len(logs),"err":err}
    if logs:
        blks=sorted(int(l["blockNumber"],16) for l in logs)
        minters=set(l.get("topics",[])[2] for l in logs if len(l.get("topics",[]))>=3)
        out.update({"first_block":blks[0],"last_block":blks[-1],"distinct_minters":len(minters)})
        for ep in EPS:
            try:
                b=_single(ep,"eth_getBlockByNumber",[hex(blks[0]),False],8,retries=0); out["first_ts"]=int(b["timestamp"],16); break
            except Exception: pass
    return out
head=blk(); print("head",head)
out={"head":head}
CASES = {
 "Bd14": ("0xBd144C91F0bcA43Ee86a47a07488710D33281E8b", ["totalSupply()","totalMinted()","freeClaimed()","paidMinted()","MAX_SUPPLY()","mintOpen()","mintStart()","mintEnd()","priceOf(uint256)"]),
 "C48c": ("0x48c977d13ef156475F086F907D8da9583E1E072E", ["totalSupply()","totalMinted()","freeClaimed()","freeCap()","freePerAgent()","maxSupply()","mintOpen()","mintPriceWei()"]),
 "D802": ("0x802d975ba97D0220A5b25827cF5F63cE8348Fd78", ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","freeSupply()","FREE_SUPPLY()","MAX_SUPPLY()","maxSupply()","mintOpen()","paidMinted()","paidPrice()"]),
 "D1dc": ("0xD1dc944F2ad3720c38636B40Fc93A1119003CBA4", ["totalSupply()","totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","MAX_PER_WALLET()","PRICE()","currentPrice()"]),
 "F535": ("0xF5351a9c5e6eeb90051Ce7Aa7013fCCd10752b7B", ["totalSupply()","totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","MAX_PER_WALLET()","PRICE()","currentPrice()"]),
 "A22A": ("0x22A1fb5C254d18Fb0187DD27A3a070d768c982fa", ["totalSupply()","totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","MAX_PER_WALLET()","PRICE()","currentPrice()"]),
}
for tag,(C,fns) in CASES.items():
    r={"address":C,"name":dec_str(call(C,sel("name()"))),"symbol":dec_str(call(C,sel("symbol()")))}
    for fn in fns:
        sig=fn
        arg=""
        if fn=="priceOf(uint256)": arg=enc_uint(1)[2:]
        v=call(C,sel(sig)+arg); r[fn]=iv(v)
    for fn in ["AGENT_ID()","agentRegistry()","agentIdRegistry()","REGISTRY()","registry()"]:
        v=call(C,sel(fn))
        if v: r[fn]=v
    r["mintedBy_user"]=iv(call(C,sel("mintedBy(address)")+enc_addr(USER)[2:]))
    r["balance_user"]=iv(call(C,sel("balanceOf(address)")+enc_addr(USER)[2:]))
    for fn,arg in [("quote(address,uint256)",enc_addr(USER)[2:]+enc_uint(1)[2:]),("costFor(uint256)",enc_uint(1)[2:]),("costFrom(address,uint256)",enc_addr(USER)[2:]+enc_uint(1)[2:]),("freeUsed(address)",enc_addr(USER)[2:]),("freeFor(address)",enc_addr(USER)[2:])]:
        v=call(C,sel(fn)+arg)
        if v is not None: r[fn]=words(v)
    r["first_mints"]=first_mints(C,head)
    out[tag]=r; print(tag, json.dumps(r))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0701-verify3.json","w"), indent=1)
