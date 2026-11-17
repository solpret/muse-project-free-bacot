#!/usr/bin/env python3
"""Main run 2026-11-02 17:01 WIB: verify 8 agent-shaped first-seen scan contracts."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
        except Exception: pass
    return None
def enc(a): return a[2:].lower().rjust(64, "0")
def dec(v):
    try: return int(v, 16)
    except Exception: return None
def dec_addr(v):
    try: return "0x" + v[-40:]
    except Exception: return None
TARGETS = {
 "Fenara": "0x857e3C15985A0c0bB0De11F18459390D754A10DA",
 "Glasscore": "0xe2826b507Da79a642aa1fce108Aa8dD11cE67e3f",
 "Kigae": "0x33fd00aF8bfF3db611D3222D394da33eaaa6a566",
 "Gourdwitch": "0x30405B8442Cf2F1C488F256A8DF12e1A2e22E581",
 "Gargrowl": "0x2BD4983c8f5E734D6E24d4Dba04F4C722a88F9DF",
 "Neonpurrix": "0xd2136C5aF996D264414cbF981E7B1804ba80177C",
 "Qilinara": "0x46d0eE06a3b919091B006D7818C3Ae405E0f3774",
 "Wraithmoth": "0x6575c26173d8A18Ad4823Aaf3b0906DE2ff1B568",
}
out = {}
for name, addr in TARGETS.items():
    r = {}
    for fn, sig, arg in [
        ("totalSupply", "totalSupply()", ""), ("freeClaimed", "freeClaimed()", ""),
        ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("FREE_PER_WALLET", "FREE_PER_WALLET()", ""),
        ("mintedBy", "mintedBy(address)", enc(USER)), ("freeUsed", "freeUsed(address)", enc(USER)),
        ("balance", "balanceOf(address)", enc(USER)),
        ("quote", "quote(address,uint256)", enc(USER) + "0000000000000000000000000000000000000000000000000000000000000001"),
        ("owner", "owner()", "")]:
        v = call(addr, sel(sig) + arg)
        r[fn] = dec(v) if v else None
    for fn, sig in [("AGENT_ID", "AGENT_ID()"), ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()"),
                    ("AGENT_REGISTRY", "AGENT_REGISTRY()"), ("agentRegistry", "agentRegistry()")]:
        v = call(addr, sel(sig))
        if v: r[fn] = dec_addr(v)
    # name/symbol dynamic strings
    def dec_str(v):
        try:
            b = bytes.fromhex(v[2:]); ln = int.from_bytes(b[32:64], "big"); return b[64:64+ln].decode()
        except Exception: return None
    for fn, sig in [("name", "name()"), ("symbol", "symbol()")]:
        v = call(addr, sel(sig))
        r[fn] = dec_str(v) if v else None
    out[name] = r
    pct = round(100 * r["freeClaimed"] / r["FREE_SUPPLY"], 2) if r.get("freeClaimed") is not None and r.get("FREE_SUPPLY") else None
    print(f"{name} {addr}: ts={r['totalSupply']} fc={r['freeClaimed']}/{r['FREE_SUPPLY']} pct={pct} mintedBy={r['mintedBy']} freeUsed={r['freeUsed']} bal={r['balance']} quote={r['quote']} registry={[r.get(k) for k in ('AGENT_ID','AGENT_ID_REGISTRY','AGENT_REGISTRY','agentRegistry') if r.get(k)]} name={r.get('name')} sym={r.get('symbol')}")
json.dump(out, open(BASE + "run-2026-11-02-1701-scan-early-verify.json", "w"), indent=1)
