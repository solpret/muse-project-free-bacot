#!/usr/bin/env python3
"""KaijuNFT verify, single batch call, race endpoints."""
import json, subprocess, sys
from Crypto.Hash import keccak
from datetime import datetime, timezone, timedelta
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x1A3889C7C568c44A2bd4a6F1791865bd2F8a2237"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed1.defibit.io/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
calls = []
keys = []
def add(key, sig, arg=None):
    d = sel(sig)
    if arg == "user": d += enc(USER)
    elif isinstance(arg, int): d += enc_u(arg)
    calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_call",
                  "params":[{"to":ADDR,"data":d},"latest"]})
    keys.append(key)
for sig in ["FREE_CAP()","freeMinted()","totalMinted()","MAX_SUPPLY()","MAX_PER_WALLET()",
            "mintOpen()","mintOpensAt()","price()","nextTokenId()"]:
    add(sig[:-2], sig)
add("freeClaimed_user","freeClaimed(address)","user")
add("holdsAgentId_user","holdsAgentId(address)","user")
add("balanceOf_user","balanceOf(address)","user")
add("mintsBy_user","mintsBy(address)","user")
add("tokenURI_1","tokenURI(uint256)",1)
add("agentIdRegistry","agentIdRegistry()")
add("owner","owner()")
add("treasury","treasury()")
calls.append({"jsonrpc":"2.0","id":len(calls)+1,"method":"eth_blockNumber","params":[]})
keys.append("block")
def to_int(v):
    try: return int(v,16) if v and v!="0x" else None
    except Exception: return None
def dec_str(raw):
    try:
        b = bytes.fromhex(raw[2:])
        off = int.from_bytes(b[32:64],"big"); ln = int.from_bytes(b[off:off+32],"big")
        return b[off+32:off+32+ln].decode(errors="replace")
    except Exception: return None
res = {}
used_ep = None
for ep in EPS:
    try:
        r = subprocess.run(["curl","-sL","--max-time","20","-X","POST",ep,
                            "-H","Content-Type: application/json","-d",json.dumps(calls)],
                           capture_output=True, text=True, timeout=25)
        out = json.loads(r.stdout)
        if isinstance(out, list) and len(out)==len(calls):
            used_ep = ep; break
    except Exception as e:
        print("ep fail", ep, str(e)[:80], file=sys.stderr)
if not used_ep:
    print("ALL ENDPOINTS FAILED"); sys.exit(2)
for it, key in zip(out, keys):
    v = it.get("result") if isinstance(it, dict) else None
    if key in ("tokenURI_1",):
        res[key] = dec_str(v) if v else None
    elif key in ("agentIdRegistry","owner","treasury"):
        res[key] = ("0x"+v[-40:]) if v and len(v)>=42 else v
    elif key == "block":
        res[key] = to_int(v)
    else:
        res[key] = to_int(v)
# name/symbol need separate batch (string returns) — reuse same approach
calls2, keys2 = [], []
for sig in ["name()","symbol()"]:
    calls2.append({"jsonrpc":"2.0","id":len(calls2)+1,"method":"eth_call",
                   "params":[{"to":ADDR,"data":sel(sig)},"latest"]})
    keys2.append(sig[:-2])
for ep in EPS:
    try:
        r = subprocess.run(["curl","-sL","--max-time","15","-X","POST",ep,
                            "-H","Content-Type: application/json","-d",json.dumps(calls2)],
                           capture_output=True, text=True, timeout=20)
        out2 = json.loads(r.stdout)
        if isinstance(out2, list) and len(out2)==2: break
    except Exception: continue
else:
    out2 = []
for it, key in zip(out2, keys2):
    v = it.get("result") if isinstance(it, dict) else None
    res[key] = dec_str(v) if v else None
mo = res.get("mintOpensAt")
if mo:
    res["mintOpensAt_wib"] = datetime.fromtimestamp(mo, timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
res["endpoint"] = used_ep
res["checked_wib"] = datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
json.dump(res, open(BASE+"hot-leg-2026-11-12-1209-kaiju.json","w"), indent=1)
print(json.dumps(res, indent=1))
