#!/usr/bin/env python3
"""Run 0401: shape-check new Sourcify feed addresses. Read-only."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k=keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
EPS=["https://bsc-dataseed.binance.org/","https://bsc-dataseed1.bnbchain.org/"]
def call(to,data):
    for ep in EPS:
        try: return _single(ep,"eth_call",[{"to":to,"data":data},"latest"],8,retries=0)
        except Exception: pass
    return None
def iv(v): return int(v,16) if v else None
CANDS=["0x626cd91e26Da5AC49B713Ab14894f54AbC4DC4DB","0xaB453745b37634C27d65b347B3aC514882cB2F37","0xcc5608A7F5A5Bc8F1bEABcD010A8C0066a0243Ae","0xB5a083bd9E8E330085e8F459F13f080d4F8fE5B4","0x33D66b461E55d6969ACfAe0C95dACf158F8d04B0","0x5C4359bfc685413732D44E0A9eFcdE639BA137Fe","0x1B81095D46a65aeCa06E72f61388cffd2F27efDC","0xBB3820Cff9e2529947F8560c2b0B5A3D9f3f3067","0x7BAa3CF4F1237e04b980e9963EC7D4E1A6EBb6e1","0xC00314eC2b65b8534276d9EA15BB4ffC5c4EF94c","0x1306da0F248d427A0854eE3fb19a93bE67Fb55d9","0xf145437843D19788e0F4a736ecD40bCc2664977d","0x8B209532e3391f0A4e0EE08aC6226d5d57d17777","0x2D21d125C207DcC891eC5FDa253EdAA6fE89A7ca"]
FREE_VIEWS=["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCount","freeMint"]
REG="0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
out={}
for C in CANDS:
    try:
        req=urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{C}?fields=abi", headers={"User-Agent":"free-mint-search/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r: meta=json.loads(r.read().decode())
        fns=sorted({e["name"] for e in meta.get("abi",[]) if e.get("type")=="function"})
    except Exception as e:
        out[C]={"abi_error":f"{type(e).__name__}: {str(e)[:120]}"}; print(C,"ABI FAIL"); continue
    has_mint=any(f in fns for f in ["mint","mintFree","freeMint"])
    has_quote=any(f in fns for f in ["quote","costFor","cost"])
    fv=[f for f in FREE_VIEWS if f in fns]
    has_reg=any(f in fns for f in ["agentRegistry","registry","AGENT_ID","agentId"])
    reg_read=None
    for fn in ["registry()","agentRegistry()","AGENT_ID()"]:
        v=call(C, sel(fn))
        if v: reg_read=v; break
    reg_ok = reg_read is not None and REG in reg_read.lower()
    is_token = all(f in fns for f in ["name","symbol","decimals","totalSupply"])
    d={"functions":fns,"has_mint":has_mint,"has_quote":has_quote,"free_views":fv,"has_reg_fn":has_reg,"reg_read_ok":reg_ok,"is_token":is_token,
       "agent_shape": bool(has_mint and fv and (has_reg or reg_ok)),
       "sale_S1": bool(has_mint and has_quote and fv and (has_reg or reg_ok)),
       "sale_S2": bool(is_token and ("mintFree" in fns) and fv and (has_reg or reg_ok))}
    for fn in ["totalSupply()","totalMinted()","freeClaimed()","freeMinted()","FREE_SUPPLY()","MAX_SUPPLY()","mintOpen()","freeMintOpen()"]:
        d[fn]=iv(call(C, sel(fn)))
    out[C]=d
    print(C, "agent", d["agent_shape"], "S1", d["sale_S1"], "S2", d["sale_S2"], "mint", has_mint, "quote", has_quote, "fv", fv, "reg", has_reg, reg_ok, "tot", d["totalSupply()"], d["totalMinted()"], "freeMinted", d["freeMinted()"])
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0401-sourcify-shape.json","w"), indent=1)
