#!/usr/bin/env python3
"""Run 0901: probe + state read for the 4 first-seen needing it:
- OUPE Cards 0xCa8820D36BEC22E462a45B6F658d3f7BB2542a82 (Sourcify retry-exhausted; registry bytes hit)
- intermediateCrack 0x8ED2139bE8Ac9598E513959ED8922FaB1781122f (Sourcify not_verified; registry bytes hit; linked from vaultcrack config.js)
- Cipher Mind 0x3226B724d9F81c4E09E6E07b75532e01e6f5c7B7 (agent-shaped, first-mint verified) - state for snapshot
- Cyber Lynx Agent 0x5189EAEB67d2A799CD9094AEc4Af6eb76C6E073b (agent-shaped, first-mint verified) - state for snapshot
Probe = 9 on-chain selectors (agentRegistry/AGENT_ID/FREE_SUPPLY/freeClaimed/totalMinted/mintOpen/PRICE/quote/mintedBy).
Registry-bytes hit alone is NOT agent-shape evidence (81% discriminator)."""
import sys, json, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(s):
    k=keccak.new(digest_bits=256); k.update(s.encode()); return "0x"+k.hexdigest()[:8]
BASE="/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER="0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS=["https://bsc-dataseed1.bnbchain.org","https://bsc.publicnode.com","https://bsc-dataseed2.bnbchain.org"]
def enc(a): return a[2:].lower().rjust(64,"0")
def call(addr, data):
    for ep in EPS:
        try:
            out=_single(ep,"eth_call",[{"to":addr,"data":data},"latest"],8,retries=0)
            if out is None or out=="0x": return None
            return out
        except Exception: continue
    return None
def call_int(addr, data):
    out=call(addr,data)
    if out is None: return None
    try: return int(out,16)
    except Exception: return out
PROBES=["agentRegistry()","AGENT_ID()","FREE_SUPPLY()","freeClaimed()","totalMinted()","mintOpen()","PRICE()","quote(address,uint256)","mintedBy(address)"]
TARGETS={
 "OUPE Cards": "0xCa8820D36BEC22E462a45B6F658d3f7BB2542a82",
 "intermediateCrack": "0x8ED2139bE8Ac9598E513959ED8922FaB1781122f",
 "Cipher Mind": "0x3226B724d9F81c4E09E6E07b75532e01e6f5c7B7",
 "Cyber Lynx Agent": "0x5189EAEB67d2A799CD9094AEc4Af6eb76C6E073b",
}
STATE_VIEWS=["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","spotsLeft()","MAX_SUPPLY()","PRICE()","mintOpen()","name()","symbol()"]
out={"probe":{},"state":{},"block_ts":{}}
for name, addr in TARGETS.items():
    p={}
    for sig in PROBES:
        data=sel(sig)
        if "address" in sig and "uint256" in sig: data+=enc(USER)+format(1,"064x")
        elif "address" in sig: data+=enc(USER)
        p[sig]=call(addr,data)
    out["probe"][name]={"address":addr,"hits":{k:(v is not None) for k,v in p.items()},"values":{k:v for k,v in p.items() if v is not None}}
    print(name, "probe hits:", {k:v for k,v in out["probe"][name]["hits"].items() if v}, flush=True)
    st={}
    for sig in STATE_VIEWS:
        st[sig.split("(")[0]]=call_int(addr, sel(sig))
    # name/symbol decode
    for f in ["name","symbol"]:
        raw=call(addr, sel(f+"()"))
        if raw:
            try:
                b=bytes.fromhex(raw[2:])
                if len(b)>=64:
                    ln=int.from_bytes(b[32:64],"big")
                    st[f]=b[64:64+ln].decode("utf-8","replace") if 0<ln<=len(b)-64 else None
                elif len(b)==32:
                    st[f]=b.rstrip(b"\x00").decode("utf-8","replace") or None
            except Exception: pass
    st["balanceOf_user"]=call_int(addr, sel("balanceOf(address)")+enc(USER))
    st["mintedBy_user"]=call_int(addr, sel("mintedBy(address)")+enc(USER))
    st["quote_user_1"]=call_int(addr, sel("quote(address,uint256)")+enc(USER)+format(1,"064x"))
    out["state"][name]=st
    print(name, "state:", st, flush=True)
# block timestamps for the two early leads' first blocks
for name, blk in [("Cipher Mind",131926871),("Cyber Lynx Agent",131927568)]:
    ts=None
    for ep in EPS:
        try:
            b=_single(ep,"eth_getBlockByNumber",[hex(blk),False],8,retries=0)
            ts=int(b["timestamp"],16); break
        except Exception: continue
    out["block_ts"][name]={"block":blk,"timestamp":ts,
        "wib": time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts+7*3600)) if ts else None}
    print(name, "first block ts:", out["block_ts"][name], flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-06-0901-early-probe.json","w"), indent=1)
print("PROBE DONE", flush=True)
