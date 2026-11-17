#!/usr/bin/env python3
"""Triage run 2026-11-16 01:31 WIB (read-only; no preview/mint).
1) NURU 0x9d7ffe074fb139cad8e69190fd2d1da19540cff7 - baru di Boltbook EN+ZH
   run ini (post cskh.ai ~01:28 WIB): klaim 214/222 free claimed (8 left),
   48h window, Agent ID gated, Sourcify-verified, freeMint() value 0.
   BUKAN di snapshot, BUKAN di hot-leg-seen/reported -> triase penuh run ini.
2) 4 kontrak Sourcify terbaru yang belum di-shape-check hot leg
   (verifiedAt 18:28-18:34 UTC): S1/S2 shape check.
3) Pi token 0xdaad1170af9bc70536498e894fc52103a3254923 - cek cepat plain ERC-20.
"""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
t0 = time.time()
out = {}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42: d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"): d += enc_u(int(a, 16))
        else: d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=120):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10)
    return json.loads(r.stdout)
def batch_call(addr, views):
    calls, meta = [], []
    for key, sig, args in views:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        meta.append((key, sig))
    for ep in EPS:
        try:
            res = post_rpc(ep, calls)
            if not isinstance(res, list) or len(res) != len(calls): continue
            d = {}
            for it, (key, sig) in zip(res, meta):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    d[key] = None
                else:
                    r = it["result"]
                    d[key] = to_int(r[:66]) if len(r) >= 66 else r
            return d, ep
        except Exception:
            continue
    return None, None
def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]})
            if isinstance(r, dict) and r.get("result"): return r["result"]
        except Exception:
            continue
    return None
def sourcify_abi(addr):
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "60",
                            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                           capture_output=True, text=True, timeout=70)
        if r.returncode != 0 or not r.stdout.strip(): return "fetch-fail", None
        j = json.loads(r.stdout)
        abi = j.get("abi") or (j.get("stdJson", {}).get("abi") if isinstance(j.get("stdJson"), dict) else None)
        if abi is None: return ("404" if "not" in r.stdout.lower()[:200] else "no-abi"), None
        return "verified", abi
    except Exception as e:
        return f"error:{e}", None

# ---- 1) NURU ----
NURU = "0x9d7ffe074fb139cad8e69190fd2d1da19540cff7"
views = [("totalSupply","totalSupply()",[]),("freeMinted","freeMinted()",[]),
 ("freeClaimed","freeClaimed()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
 ("FREE_CAP","FREE_CAP()",[]),("FREE_MAX","FREE_MAX()",[]),
 ("mintOpen","mintOpen()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
 ("mintedBy_user","mintedBy(address)",[USER]),("freeUsed_user","freeUsed(address)",[USER]),
 ("freeClaimed_user","freeClaimed(address)",[USER]),
 ("priceFor_user_1","priceFor(address,uint256)",[USER,1]),
 ("owner","owner()",[]),("mintPrice","mintPrice()",[]),
 ("totalMinted","totalMinted()",[])]
vals, ep = batch_call(NURU, views)
code = get_code(NURU)
status, abi = sourcify_abi(NURU)
fns = [f.get("name") for f in abi if isinstance(f, dict) and f.get("type") == "function"] if abi else []
nuru = {"address": NURU, "views": vals, "via": ep, "code_bytes": (len(code)-2)//2 if code else None,
        "registry_bytes": (REG in code.lower()) if code else None,
        "sourcify": status, "fns": fns}
out["NURU"] = nuru
print("NURU views:", json.dumps(vals))
print("NURU code_bytes:", nuru["code_bytes"], "registry_bytes:", nuru["registry_bytes"], "sourcify:", status)
print("NURU fns:", fns)

# ---- 2) 4 newest Sourcify contracts: S1/S2 shape ----
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed",
 "freeAvailable","freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMintedBy"]
for addr in ["0x1aAE920F026801DD224462747537bb83dE38CD36",
             "0xc66C25e76551C3e4c5b3Ab5fBe33F8D837F57dA5",
             "0x3ab9C948E989991bfD13666594b09a5608ED964b",
             "0xCF974333dBbB97a14eaa5E975a4d434eE60496bF"]:
    st, ab = sourcify_abi(addr)
    fns2 = [f.get("name") for f in ab if isinstance(f, dict) and f.get("type") == "function"] if ab else []
    low = [f.lower() for f in fns2]
    has_mint = any("mint" in f for f in low)
    has_quote = any(f in low for f in ["quote","costfor","pricefor","getprice","mintprice","cost"])
    free_hits = [f for f in fns2 if any(fv.lower() in f.lower() for fv in FREE_VIEWS)]
    code2 = get_code(addr)
    agent = (REG in code2.lower()) if code2 else None
    agent = agent or any("agent" in f for f in low)
    s1 = bool(has_mint and has_quote and free_hits and agent)
    s2 = bool(any(f in low for f in ["name","symbol","decimals","totalsupply"]) and
              any(f in low for f in ["mintfree"]) and free_hits and agent)
    out[addr] = {"sourcify": st, "fns": fns2, "mint": has_mint, "quote": has_quote,
                 "free": free_hits, "agent": agent, "S1": s1, "S2": s2,
                 "code_bytes": (len(code2)-2)//2 if code2 else None,
                 "registry_bytes": (REG in code2.lower()) if code2 else None}
    print(addr, "->", json.dumps(out[addr]))

# ---- 3) Pi token quick check ----
PI = "0xdaad1170af9bc70536498e894fc52103a3254923"
pvals, pep = batch_call(PI, [("name","name()",[]),("symbol","symbol()",[]),
                             ("totalSupply","totalSupply()",[]),("decimals","decimals()",[])])
pcode = get_code(PI)
out["PI"] = {"views": pvals, "code_bytes": (len(pcode)-2)//2 if pcode else None,
             "registry_bytes": (REG in pcode.lower()) if pcode else None}
print("PI:", json.dumps(out["PI"]))

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-16-0131-nuru-probe.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
