#!/usr/bin/env python3
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG_INT = 552192074493313695968015109214105588393044541999
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
def dec_str(raw):
    try:
        b = bytes.fromhex(raw[2:]); ln = int.from_bytes(b[32:64], "big"); return b[64:64+ln].decode(errors="replace")
    except Exception: return None
targets = {
 "Dronagent": "0x307157fb80A63bD4C845f44f5a55Dd90127D8C50",
 "Catties": "0x73288b54F881af643Aea2B742875906E410705B4",
 "Fanerswan": "0x07A67233c92f69dE838F43A5803BBedC2bcDCFeF",
 "Bakunap": "0x0F02DE011F293CfBF49977C21E212f39b4485D27",
 "Zephyr Agent": "0xE41b54504aa171D92E01384aE3aB3007E170Aa70",
 "PSYKO Licence": "0x2Bdf3cB9138F3Ef71DD6A83aB24eA25DD540B974",
 "Blunt Signal": "0xe489b2e46A4B21Ac769aA20cE703F0d47AD227Cf",
 "Drift Alloy": "0x738304412FD058C912cAD05FBAc7c89ab9495732",
 "Ember Lattice": "0x6fd05699cA5A9d325298CFB9F95B19ed9D02a880",
 "Flint Vector": "0x3A808A23dC299C5c6BcEEEa900ba5FE9B1cD43B6",
}
views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "freeLeft()", "FREE_SUPPLY()",
         "mintedBy(address)", "freeUsed(address)", "balanceOf(address)", "owner()",
         "AGENT_ID()", "agentIdRegistry()", "agentRegistry()", "costFor(uint256)", "quote(address,uint256)"]
out = {}
for name, addr in targets.items():
    d = {}
    for sig in views:
        arg = ""
        if "(address)" in sig: arg = enc(USER)
        elif "(uint256)" in sig: arg = "0"*63+"1"
        elif sig.startswith("quote"): arg = enc(USER)+"0"*63+"1"
        d[sig] = iv(call(addr, sel(sig)+arg))
    d["name"] = dec_str(call(addr, sel("name()")))
    d["symbol"] = dec_str(call(addr, sel("symbol()")))
    reg = any(d.get(k) == REG_INT for k in ("AGENT_ID()", "agentIdRegistry()", "agentRegistry()"))
    free = any(d.get(k) is not None for k in ("freeClaimed()", "freeMinted()", "freeLeft()", "FREE_SUPPLY()"))
    d["agent_shape"] = bool(reg and free)
    out[name] = d
    print(f"{name} {addr}: reg={reg} free={free} shape={d['agent_shape']} | " +
          ", ".join(f"{k}={v}" for k, v in d.items() if v is not None and k not in ("name", "symbol", "agent_shape")))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-03-0401-shape.json", "w"), indent=1)
