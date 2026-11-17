import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch as _batch
EPS = ["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/"]
def single(addr, sig, arg=""):
    for ep in EPS:
        try:
            r = _batch([("eth_call", [{"to": addr, "data": "0x"+sig+arg}, "latest"])], endpoint=ep, timeout=15)[0]
            return r
        except Exception as e:
            last = e
    return "ERR:"+str(last)
def to_int(h):
    if not isinstance(h,str) or not h.startswith("0x"): return None
    try: return int(h,16)
    except: return None
def enc_addr(a): return a[2:].lower().rjust(64,"0")
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
# selectors
def sel(s):
    from Crypto.Hash import keccak
    return keccak.new(digest_bits=256, data=s.encode()).hexdigest()[:8]
# binanceai MINT 0x46cb1D3efd4307506Cda7EbBa5a51be64746739E, TOKEN 0x209173F09aFbCA053C0de9e9763f503e9fb54a3c
MINT="0x46cb1D3efd4307506Cda7EbBa5a51be64746739E"
TOKEN="0x209173F09aFbCA053C0de9e9763f503e9fb54a3c"
out={}
out['block']=int(_batch([("eth_blockNumber",[])],endpoint=EPS[0],timeout=15)[0],16)
out['binanceai_launched']=to_int(single(MINT, sel("launched()")))
out['binanceai_failed']=to_int(single(MINT, sel("failed()")))
out['binanceai_isRefundPhase']=to_int(single(MINT, sel("isRefundPhase()")))
out['binanceai_tokenClaimed_user']=to_int(single(MINT, sel("tokenClaimed(address)"), enc_addr(USER)))
out['binanceai_claimable_user']=to_int(single(MINT, sel("claimable(address)"), enc_addr(USER)))
out['binanceai_balance_token_user']=to_int(single(TOKEN, sel("balanceOf(address)"), enc_addr(USER)))
# Cedar Kiln: helper mint sim + collection balance
HELPER="0x6AA2C9B7C73BF6351E41EaD32Dd082951336953e"
COLL="0x7ac89Ff65D1e4aa9C2BBCdEE0bBafAaa092B02bE"
out['cedar_userBalance']=to_int(single(COLL, sel("balanceOf(address)"), enc_addr(USER)))
# eth_call mint(1) from user: need from field
def call_from(addr, data, frm):
    for ep in EPS:
        try:
            r=_batch([("eth_call",[{"to":addr,"data":data,"from":frm},"latest"])],endpoint=ep,timeout=15)[0]
            return r
        except Exception as e:
            last=e
    return "ERR:"+str(last)
mint1 = "0x"+sel("mint(uint256)") + (1).to_bytes(32,"big").hex()
out['cedar_mint1_user']=call_from(HELPER, mint1, USER)
out['cedar_mint1_dead']=call_from(HELPER, mint1, "0x000000000000000000000000000000000000dEaD")
print(json.dumps(out, indent=1))
json.dump(out, open('run-2026-11-08-1101-recheck.json','w'), indent=1)
