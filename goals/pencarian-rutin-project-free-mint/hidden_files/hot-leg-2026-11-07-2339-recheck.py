import sys, json
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
def single(addr, sig):
    for ep in EPS:
        try:
            r = _single(ep, "eth_call", [{"to": addr, "data": sel(sig)}, "latest"], 8, retries=0)
            return int(r, 16)
        except Exception:
            continue
    return None
targets = {
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", "freeMinted()"),
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", "freeMinted()"),
 "WAR3": ("0x1Aa9797cC762b838388566Daa45A56b1709F4Bbe", "freeMinted()"),
 "HUNT PASS": ("0x885128Cf234c768F1353e2C1432D55873C6b67dD", "totalMinted()"),
 "fab7-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72", "freeMinted()"),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", "totalMinted()"),
}
out = {n: single(a, s) for n, (a, s) in targets.items()}
print(json.dumps(out))
json.dump(out, open("hot-leg-2026-11-07-2339-recheck.json", "w"))
