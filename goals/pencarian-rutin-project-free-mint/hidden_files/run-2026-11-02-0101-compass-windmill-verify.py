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
def iv(v): return int(v,16) if v else None
def dec_str(v):
    if not v: return None
    b=bytes.fromhex(v[2:])
    if len(b)>=64:
        ln=int.from_bytes(b[32:64],"big")
        if 0<ln<=len(b)-64: return b[64:64+ln].decode('utf-8','replace')
    return None
def blk():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0),16)
        except Exception: pass
head=blk(); print("head", head)
contracts={
 "cD99":"0xcD99F565df63756D2AF46cf96Fd8e868d96Fc7e7",
 "BEeB":"0xBEeBD269A7636591823BCD5fdf0E378b33f24112",
 "35C9":"0x35C9CDed0eC5d2b9A9f365b87Ef954b19E08465f",
}
for nm, C in contracts.items():
    print("==", nm, C)
    print(" name", dec_str(call(C, sel("name()"))), "symbol", dec_str(call(C, sel("symbol()"))))
    for fn in ["totalSupply()","totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","currentPrice()","MINT_PRICE()","freeCount()","transferCount()"]:
        print(" ", fn, iv(call(C, sel(fn))))
    print("  mintedBy(user)", iv(call(C, sel("mintedBy(address)")+enc_addr(USER)[2:])), "mintedByWallet", iv(call(C, sel("mintedByWallet(address)")+enc_addr(USER)[2:])), "balance", iv(call(C, sel("balanceOf(address)")+enc_addr(USER)[2:])))
    print("  agentRegistry", call(C, sel("agentRegistry()")), "agentIdRegistry", call(C, sel("agentIdRegistry()")))
    v=call(C, sel("costFor(uint256)")+enc_uint(1)[2:]); print("  costFor(1)", v, iv(v))
    v=call(C, sel("priceFor(uint256)")+enc_uint(1)[2:]); print("  priceFor(1)", v)
    # first mints via ankr, address-filtered
    logs=[]; tok=None; pages=0; err=None
    while True:
        params={"blockchain":"bsc","fromBlock":hex(131060000),"toBlock":hex(head),"pageSize":1000,"decodeLogs":False,
                "topics":["0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef","0x"+"00"*32],
                "address":C}
        if tok: params["pageToken"]=tok
        try: body=ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e: err=str(e)[:200]; break
        res=body.get("result",{}) if isinstance(body,dict) else {}
        got=res.get("logs",[])
        # filter to this contract just in case
        got=[l for l in got if l.get("address","").lower()==C.lower()]
        logs.extend(got); tok=res.get("nextPageToken"); pages+=1
        if not tok or pages>=10: break
        time.sleep(1)
    print("  ankr Transfer-from-zero logs (addr-filtered) from 131060000:", len(logs), "err:", err)
    if logs:
        blks=sorted(int(l["blockNumber"],16) for l in logs)
        minters=set()
        for l in logs:
            t=l.get("topics",[])
            if len(t)>=3: minters.add(t[2])
        print("   first block", blks[0], "last", blks[-1], "distinct minters(topics)", len(minters))
        # block timestamp for first block
        for ep in EPS:
            try:
                b=_single(ep, "eth_getBlockByNumber", [hex(blks[0]), False], 8, retries=0); print("   first block ts", int(b["timestamp"],16)); break
            except Exception as e: pass
