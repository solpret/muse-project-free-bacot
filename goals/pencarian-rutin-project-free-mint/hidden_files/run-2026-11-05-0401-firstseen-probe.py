#!/usr/bin/env python3
import json, urllib.request
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def call(to, data):
    p = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": to, "data": data}, "latest"]}).encode()
    for ep in EPS:
        try:
            req = urllib.request.Request(ep, data=p, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=5) as r: j = json.load(r)
            v = j.get("result")
            if v and v != "0x": return v
        except Exception: continue
    return None
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def dec_str(v):
    try:
        b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], 'big'); return b[64:64+ln].decode(errors='replace')
    except Exception: return None
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"; u = USER[2:].lower().rjust(64, "0"); one = "0"*63 + "1"
NFT = {
 "Sly Hours": "0xF19A66e4643C5D11D1522A2352331688F8a2f324",
 "AgentLattice": "0x5b9fe53468F1Aa4EDbe2b96a4387910D335e2eDB",
 "LuckyCharmAtlasII": "0x58126241BAA73B0b234e9B7F299D06eF44cCaFe9",
}
NFTVIEWS = [("totalSupply()", ""), ("totalMinted()", ""), ("FREE_SUPPLY()", ""), ("FREE_PER_WALLET()", ""),
 ("freeClaimed()", ""), ("freeLeft()", ""), ("freeClaimed(address)", u), ("freeFor(address)", u),
 ("freeUsed(address)", u), ("mintOpen()", ""), ("mintsLeft()", ""), ("owner()", "")]
out = {}
for name, addr in NFT.items():
    o = {"name": dec_str(call(addr, sel("name()"))), "symbol": dec_str(call(addr, sel("symbol()")))}
    for vn, arg in NFTVIEWS:
        v = call(addr, sel(vn) + arg)
        o[vn] = iv(v) if vn != "owner()" else (("0x" + v[-40:]) if v else None)
    out[name] = o; print("NFT", name, o, flush=True)
ERC = {
 "ERC20-3678": "0x36789C06E49f09502C3F6aA8f1A20Bebccbeaacc",
 "ERC20-b95d": "0xb95d1a2F2259a411183c731374798Cf69B4349E0",
 "STARRY": "0x65b1721Bf9ba3EA504bb13fd89D47ABc13C739a5",
}
ERCVIEWS = [("totalSupply()", ""), ("freeSharesRemaining()", ""), ("freeClaimed()", ""), ("freeMinted()", ""),
 ("FREE_SLOTS()", ""), ("FREE_SUPPLY()", ""), ("freeSharesClaimed(address)", u), ("freeClaimed(address)", u),
 ("freeAvailable(address)", u), ("saleOpen()", ""), ("mintOpen()", ""), ("launched()", ""),
 ("quote(address,uint256)", u + one), ("agentRegistry()", ""), ("registry()", "")]
for name, addr in ERC.items():
    o = {"name": dec_str(call(addr, sel("name()"))), "symbol": dec_str(call(addr, sel("symbol()"))), "decimals": iv(call(addr, sel("decimals()")))}
    for vn, arg in ERCVIEWS:
        v = call(addr, sel(vn) + arg)
        o[vn] = iv(v) if vn not in ("agentRegistry()", "registry()") else (("0x" + v[-40:]) if v else None)
    out[name] = o; print("ERC", name, o, flush=True)
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-05-0401-firstseen-probe.json", "w"), indent=1)
print("DONE")
