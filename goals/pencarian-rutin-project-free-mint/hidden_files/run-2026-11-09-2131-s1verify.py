#!/usr/bin/env python3
"""Run 2131: on-chain verify the two 5a S1 hits. Read-only."""
import json, subprocess
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed1.bnbchain.org/","https://bsc-dataseed2.bnbchain.org/","https://bsc-dataseed.binance.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def enc_u(n): return format(n, "064x")
def ti(v):
    try: return int(v,16) if v not in (None,"0x") else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,text=True,timeout=timeout+5).stdout
    return json.loads(out)
def call(addr, sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":addr,"data":data},"latest"]})
            if isinstance(r, dict) and "result" in r: return ti(r["result"])
        except Exception: continue
    return None
def call_str(addr, sig):
    v = call(addr, sig)
    return v
def code(addr):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]})
            if isinstance(r, dict) and "result" in r: return r["result"]
        except Exception: continue
    return None
def block():
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})
            return int(r["result"],16)
        except Exception: continue
    return None
out = {"block": block(), "items": {}}
# --- S1 hit 1: NFT cards 0x3f508d88 ---
a1 = "0x3f508d8826517123Fdd39c776e55F85Fa188E5fD"
d1 = {}
for sig in ["totalSupply()","freeLeft()","freeMinted()","FREE_CAP()","mintStart()","mintEnd()","mintOpen()","MAX_SUPPLY()","paidMinted()","earlyBirdLeft()","bonusMinted()","remaining()"]:
    d1[sig.split("(")[0]] = call(a1, sig)
d1["quote_user_1"] = call(a1, "quote(address,uint256)", enc_addr(USER)+enc_u(1))
d1["freeClaimed_user"] = call(a1, "freeClaimed(address)", enc_addr(USER))
d1["balanceOf_user"] = call(a1, "balanceOf(address)", enc_addr(USER))
c1 = code(a1); d1["code_len"] = len(c1)-2 if c1 else None
d1["registry_bytes"] = (REG in (c1 or "").lower()) if c1 else None
out["items"]["S1-3f50-cards"] = d1
print("S1-3f50", json.dumps(d1), flush=True)
# --- S1 hit 2: share sale 0x4Bc1A172 ---
a2 = "0x4Bc1A1723a5D8A893695f78c8b2cD39028478d43"
d2 = {}
for sig in ["MAX_FREE_SHARES()","freeMinted()","SALE_START()","SALE_END()","saleActive()","mintOpen()","opened()","openedAt()","startTime()","saleStart()","saleEnd()","TOKENS_PER_SHARE()","MAX_SHARES()","TOTAL_SHARES()","totalMinted()","totalSold()","soldOut()","phase()","paused()"]:
    d2[sig.split("(")[0]] = call(a2, sig)
d2["quoteCost_user_1"] = call(a2, "quoteCost(address,uint256)", enc_addr(USER)+enc_u(1))
d2["quoteTokens_user_1"] = call(a2, "quoteTokens(address,uint256)", enc_addr(USER)+enc_u(1))
d2["sharesOf_user"] = call(a2, "sharesOf(address)", enc_addr(USER))
d2["freeGranted_user"] = call(a2, "freeGranted(address)", enc_addr(USER))
d2["token_addr_raw"] = call(a2, "token()")
d2["REGISTRY_raw"] = call(a2, "REGISTRY()")
c2 = code(a2); d2["code_len"] = len(c2)-2 if c2 else None
d2["registry_bytes"] = (REG in (c2 or "").lower()) if c2 else None
out["items"]["S1-4Bc1-sale"] = d2
print("S1-4Bc1", json.dumps(d2), flush=True)
print("BLOCK", out["block"])
json.dump(out, open("run-2026-11-09-2131-s1verify.json","w"), indent=1)
