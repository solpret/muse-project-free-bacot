#!/usr/bin/env python3
"""Triage run 0131: (a) Forge Pass first-mint corroboration via totalSupply at blocks
133590098/133590099 + block timestamp; (b) quick shape probe of sweep items
BUGHOUND, ACORE, Agent Harvest. Read-only."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def call_at(ep, to, data, block):
    r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call",
        "params":[{"to":to,"data":data}, block]}, timeout=60)
    return r.get("result")
# (a) Forge first-mint corroboration
FORGE = "0xd4a038253d19E058a5653dFf177F7F21FeE59D52"
ts_data = sel("totalSupply()")
for blk, lbl in [(133590098, "pre-first-mint"), (133590099, "first-mint-block"), (133590100, "next")]:
    got = None
    for ep in EPS:
        try:
            v = call_at(ep, FORGE, ts_data, hex(blk))
            if v not in (None, "0x"):
                got = int(v, 16); break
        except Exception:
            pass
    print(f"FORGE totalSupply @ {blk} ({lbl}): {got}")
for blk in [133590099]:
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                              "params":[hex(blk), False]}, timeout=60)
            ts = int(r["result"]["timestamp"], 16)
            print(f"FORGE block {blk} timestamp: {ts} = {time.strftime('%Y-%m-%d %H:%M:%S WIB', time.gmtime(ts+7*3600))}")
            break
        except Exception as e:
            print("block ts fail", ep, e)
# (b) sweep probes
def probe(addr):
    out = {"address": addr}
    try:
        s = subprocess.run(["curl","-sL","--max-time","45",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=stdJson"],
            capture_output=True, text=True, timeout=50).stdout
        sj = json.loads(s)
        abi = (sj.get("stdJson",{}).get("output",{}).get("abi") or sj.get("stdJson",{}).get("abi") or [])
        fns = [e.get("name") for e in abi if e.get("type")=="function"]
        out["sourcify_verified"] = bool(abi)
        out["n_fns"] = len(fns)
        out["fns"] = fns
        out["registry_in_abi_src"] = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in json.dumps(sj).lower()
    except Exception as e:
        out["sourcify_error"] = str(e)
    # on-chain basic views
    def rd(sig, args=[]):
        d = sel(sig)
        for a in args:
            d += a[2:].lower().rjust(64,"0") if isinstance(a,str) and a.startswith("0x") and len(a)==42 else format(int(a),"064x")
        for ep in EPS:
            try:
                v = call_at(ep, addr, d, "latest")
                if v not in (None,"0x"): return v
            except Exception: pass
        return None
    def toint(v):
        try: return int(v,16) if v else None
        except Exception: return v
    out["totalSupply"] = toint(rd("totalSupply()"))
    out["totalMinted"] = toint(rd("totalMinted()"))
    out["freeMinted"] = toint(rd("freeMinted()"))
    out["freeRemaining"] = toint(rd("freeRemaining()"))
    out["mintActive"] = toint(rd("mintActive()"))
    out["mintOpen"] = toint(rd("mintOpen()"))
    out["FREE_SUPPLY"] = toint(rd("FREE_SUPPLY()"))
    out["MAX_SUPPLY"] = toint(rd("MAX_SUPPLY()"))
    out["owner"] = rd("owner()")
    # bytecode registry bytes
    try:
        r = post_rpc(EPS[0], {"jsonrpc":"2.0","id":1,"method":"eth_getCode","params":[addr,"latest"]}, timeout=60)
        code = (r.get("result") or "")
        out["code_bytes"] = (len(code)-2)//2 if code.startswith("0x") else 0
        out["registry_bytes"] = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in code.lower()
    except Exception as e:
        out["code_error"] = str(e)
    print(json.dumps(out, indent=1)[:1800])
    return out
res = {}
res["BUGHOUND"] = probe("0x8a7be94d1c36a60bcdd155d37faf84403b8a26ae")
res["ACORE"] = probe("0xf4bacf30fb8f69373f63d99c657f53dd7774af1d")
res["AgentHarvest"] = probe("0xacf150d9eC909E3d339Bf4c6D090b18495674E66")
json.dump(res, open(BASE+"run-2026-11-15-0131-triage.json","w"), indent=1)
