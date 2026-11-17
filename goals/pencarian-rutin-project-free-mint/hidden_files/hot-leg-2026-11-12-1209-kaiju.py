#!/usr/bin/env python3
"""Verify new S1 KaijuNFT 0x1A3889... (feed 12:09 run). Read-only."""
import json, subprocess
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x1A3889C7C568c44A2bd4a6F1791865bd2F8a2237"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def post_rpc(ep, payload, timeout=15):
    r = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
                        "-H","Content-Type: application/json","-d",json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout+5)
    return json.loads(r.stdout)
def call(addr, data):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call",
                              "params":[{"to":addr,"data":data},"latest"]}, 15)
            if "result" in r: return r["result"]
        except Exception: continue
    return None
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def read_str(addr, sig):
    raw = call(addr, sel(sig))
    if not raw: return None
    try:
        b = bytes.fromhex(raw[2:])
        if len(b) < 96: return None
        off = int.from_bytes(b[32:64],"big"); ln = int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
views = ["name()","symbol()","FREE_CAP()","freeMinted()","totalMinted()","MAX_SUPPLY()",
         "MAX_PER_WALLET()","mintOpen()","mintOpensAt()","price()","agentIdRegistry()",
         "treasury()","owner()","nextTokenId()"]
res = {}
for sig in views:
    res[sig[:-2]] = to_int(call(ADDR, sel(sig)))
res["name"] = read_str(ADDR, "name()")
res["symbol"] = read_str(ADDR, "symbol()")
res["freeClaimed_user"] = to_int(call(ADDR, sel("freeClaimed(address)")+enc(USER)))
res["holdsAgentId_user"] = to_int(call(ADDR, sel("holdsAgentId(address)")+enc(USER)))
res["balanceOf_user"] = to_int(call(ADDR, sel("balanceOf(address)")+enc(USER)))
res["mintsBy_user"] = to_int(call(ADDR, sel("mintsBy(address)")+enc(USER)))
# registry address as address type
raw = call(ADDR, sel("agentIdRegistry()"))
res["agentIdRegistry_addr"] = ("0x"+raw[-40:]) if raw else None
# block number
blk = None
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}, 15)
        blk = int(r["result"],16); break
    except Exception: continue
res["block"] = blk
# tokenURI for token 1 (if minted) - website evidence method (I)
res["tokenURI_1"] = read_str(ADDR, "tokenURI(uint256)") if False else None
# tokenURI needs arg; do it manually
d = sel("tokenURI(uint256)") + "0000000000000000000000000000000000000000000000000000000000000001"
res["tokenURI_1"] = read_str(ADDR, "tokenURI(uint256)")  # wrong: no-arg call; fix below
# proper call with arg:
raw = call(ADDR, d)
if raw:
    try:
        b = bytes.fromhex(raw[2:])
        off = int.from_bytes(b[32:64],"big"); ln = int.from_bytes(b[off:off+32],"big")
        res["tokenURI_1"] = b[off+32:off+32+ln].decode(errors="replace")
    except Exception: res["tokenURI_1"] = f"decode-fail {raw[:80]}"
else:
    res["tokenURI_1"] = None
# mintOpensAt -> WIB
mo = res.get("mintOpensAt")
if mo:
    res["mintOpensAt_wib"] = datetime.fromtimestamp(mo, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
    res["mintOpensAt_utc"] = datetime.fromtimestamp(mo, timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
now = datetime.now(timezone(timedelta(hours=7)))
res["checked_wib"] = now.strftime("%Y-%m-%d %H:%M:%S WIB")
json.dump(res, open(BASE+"hot-leg-2026-11-12-1209-kaiju.json","w"), indent=1)
print(json.dumps(res, indent=1))
