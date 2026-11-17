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
targets = {
 "River Agent": ("0x211AF92EF42641ef4fD94EEccb88FAe1e7e51667", ["totalMinted()","FREE_SUPPLY()","freeMinted()","mintedBy(address)","costFor(uint256)"]),
 "Deco Agent": ("0xfe8D985cB19380805B01cf7FCFc65c3819e030C8", ["totalMinted()","FREE_SUPPLY()","freeMinted()","mintedBy(address)","costFor(uint256)"]),
 "Opera Agent": ("0x32ddd7d98bB711976cCfE19548Df52D0cdeC197c", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "Silk Agent": ("0xF888787f39dD5a5adCEC1b0d9833cF40a655c60e", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "Peony Agent": ("0x58bA07CEd2803f40DE2d00b411580Eea7CC2D2FC", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)","freeMinted()"]),
 "QAFUAI": ("0xB731e00019c64F44F89F484D1D10d2C6b56375f4", ["freeMinted()","FREE_POOL()","freeRemaining()","FREE_PER_WALLET()","mintOpen()","balanceOf(address)","freeClaimed(address)","freeOf(address)"]),
 "Yunjin Agent": ("0x6F726D4cF7263f1F7562d5868EC09806d7ef70f8", ["totalMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintedBy(address)","costFor(uint256)"]),
 "Crtdroid-extra": ("0xDe67dc24C9B37af22bC6C995cA99e86809b01286", ["totalMinted()","totalSupply()","FREE_SUPPLY()","freeClaimed()","mintedBy(address)"]),
}
out = {"block": None}
for ep in EPS:
    try: out["block"] = int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16); break
    except Exception: pass
for name,(addr,fns) in targets.items():
    r={}
    for fn in fns:
        arg=""
        if fn=="mintedBy(address)" or fn in ("balanceOf(address)","freeClaimed(address)","freeOf(address)"): arg=enc(USER)
        elif fn=="costFor(uint256)": arg="0"*63+"1"
        r[fn]=iv(call(addr, sel(fn)+arg))
    out[name]=r; print(name, r)
json.dump(out, open(BASE+"run-2026-11-03-0301-extra.json","w"), indent=1)
print("BLOCK", out["block"])
