import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def dec_str(v):
    if not v or len(v)<130: return None
    try:
        raw=bytes.fromhex(v[2:]); ln=int.from_bytes(raw[32:64],"big")
        return raw[64:64+ln].decode("utf-8","replace")
    except Exception: return None
targets = {
 "Caravan Agent": ("0x7112010027394f0d9146885fa242e117F18D4BD8", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)","balanceOf(address)"]),
 "Kelp Agent": ("0xf76F0BB04EbC0866E8FDdf24e1eC5320fAD0c9Fb", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)","balanceOf(address)"]),
 "Peony Agent": ("0x58bA07CEd2803f40DE2d00b411580Eea7CC2D2FC", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "Yunjin Agent": ("0x6F726D4cF7263f1F7562d5868EC09806d7ef70f8", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "Deco Agent": ("0xfe8D985cB19380805B01cf7FCFc65c3819e030C8", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "Opera Agent": ("0x32ddd7d98bB711976cCfE19548Df52D0cdeC197c", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "Silk Agent": ("0xF888787f39dD5a5adCEC1b0d9833cF40a655c60e", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "QAFUAI": ("0xB731e00019c64F44F89F484D1D10d2C6b56375f4", ["freeMinted()","FREE_POOL()","freeRemaining()","mintOpen()","balanceOf(address)"]),
 "DE53_NFT": ("0xde536232c09ea778b6cb8409328362F7e9182bc9", ["totalSupply()","freeClaimed()","FREE_SUPPLY()","MAX_SUPPLY()","freeLeft()","mintOpen()","mintedBy(address)","freeUsed(address)","balanceOf(address)","quote(address,uint256)","agentIdRegistry()"]),
}
out = {"block": None}
for ep in EPS:
    try: out["block"] = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception: pass
for name,(addr,fns) in targets.items():
    r={}
    for fn in fns:
        arg=""
        if fn in ("mintedBy(address)","balanceOf(address)","freeUsed(address)"): arg=enc(USER)
        elif fn=="costFor(uint256)": arg="0"*63+"1"
        elif fn=="quote(address,uint256)": arg=enc(USER)+"0"*63+"1"
        elif fn=="agentIdRegistry()": pass
        raw=call(addr, sel(fn)+arg)
        if fn=="agentIdRegistry()":
            r[fn]=("0x"+raw[-40:]) if raw and len(raw)>=42 else raw
        else:
            r[fn]=iv(raw)
    # name/symbol for DE53
    if name=="DE53_NFT":
        r["name"]=dec_str(call(addr, sel("name()")))
        r["symbol"]=dec_str(call(addr, sel("symbol()")))
    out[name]=r; print(name, r)
json.dump(out, open(BASE+"run-2026-11-03-0331-extra.json","w"), indent=1)
print("BLOCK", out["block"])
