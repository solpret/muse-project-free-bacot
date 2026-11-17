import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return '0x'+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,'0')
USER='0xeb237F6f9FB4e826739F0954e9768914F28b2c2E'
EPS=["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
def single(addr, data):
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]}, timeout=8, retries=0)
            if not isinstance(out,dict): continue
            if out.get("error"): return None
            r=out.get("result")
            if r is None or r=="0x": return None
            if r.startswith("0x") and len(r)<=66: return int(r,16)
            return r
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            out=_fr_post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, timeout=8, retries=0)
            return int(out["result"],16)
        except Exception: continue
    return None
SALE='0x816458b734d17d59058762deaadd9b952bad6985'
TOK='0x0b0b8df4d7df0b2cdd00877b476a447a8a1824ee'
out={"block": block(), "started_wib": "2026-11-08 16:01 WIB",
     "fillDeadlineWib": "2026-11-08T16:00:37+07:00", "sale": SALE, "token": TOK, "sale_views": {}, "token_views": {}}
for v in ['giftsClaimed()','GIFT_SHARES()','live()','mintingOpen()','saleOpen()','fillDeadline()','saleStart()','paidSharesSold()','totalShares()','giftTaken(address)','balanceOf(address)','claimGift()']:
    data = sel(v)+enc_addr(USER) if '(address)' in v else sel(v)
    out["sale_views"][v]=single(SALE, data)
    print(f"sale {v} =", out["sale_views"][v])
for v in ['totalSupply()','balanceOf(address)','tradingOpen()','decimals()']:
    data = sel(v)+enc_addr(USER) if '(address)' in v else sel(v)
    out["token_views"][v]=single(TOK, data)
    print(f"token {v} =", out["token_views"][v])
json.dump(out, open('run-2026-11-08-1601-njar.json','w'), indent=1)
print("WROTE run-2026-11-08-1601-njar.json block", out["block"])
