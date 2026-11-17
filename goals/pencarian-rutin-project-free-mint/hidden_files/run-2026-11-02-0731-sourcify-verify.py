#!/usr/bin/env python3
"""Run 0731 Sourcify-feed verification. Read-only."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return "0x" + a[2:].lower().rjust(64, "0")
def enc_uint(n): return "0x" + format(n, "064x")
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def call(to, data):
    for ep in EPS:
        try: return _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0), None
        except Exception as e: err = f"{type(e).__name__}: {str(e)[:120]}"
    return None, err
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def words(v):
    if not v: return None
    b = bytes.fromhex(v[2:])
    return [int.from_bytes(b[i:i+32], "big") for i in range(0, len(b), 32)]
def dec_str(v):
    if not v or len(v) < 130: return None
    try:
        b = bytes.fromhex(v[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def block():
    for ep in EPS:
        try: return int(_single(ep, "eth_blockNumber", [], 8, retries=0), 16)
        except Exception: pass
    return None
CANDS = {
 "4fc3": "0x4fc39B2c1620f2561d01232f87E25581CFD72A51",
 "bA8110": "0xbA8110Fc3A01381a9724C597C9C4839224b8D875",
 "D65913": "0xD65913933ada0b429de8f17eDBAdf5FA24aa94E2",
 "C9c0De": "0xC9c0De69ea301cA9479149554bf325aE3342584B",
 "8305Bc": "0x8305Bc7cB18F00b7133B5Cf3DCE70fd026Ea6d07",
 "948A42": "0x948A4261D478394FB1a42E95e970a142F3b74bB1",
 "1979c2": "0x1979c22cfEa94aa2215edC97AED703f651158369",
 "8F8705": "0x8F8705A91cb8af615CE35179B0D33200AdE71DAb",
 "263191": "0x2631911A27Eb0eAE9dc9178A1b6bbc94ADE736b4",
 "0bc496": "0x0bc496BC51D14ae6C4A7003B05061323d4De9206",
 "Bf8e5D": "0xBf8e5D2766BbE59f1fb22586733E934b4440F8D8",
 "51fC72": "0x51fC72478f3dAe0D34202892B9b9867d14FD5903",
 "538754": "0x538754513f0a7308698D95628A9EBC7DEd8dbD63",
 "aC1486": "0xaC148668FbF899c84B82b0Ba30F6D739E0a04fBD",
 "E4cA7A": "0xE4cA7AaA82253717C0d897C10d58D59821631509",
 "46c181": "0x46c1815082ccf1273e3c07548ef2004046Bb7Fc0",
 "b2d236": "0xb2d236EC0473792eC6727e5bf41084Df3eA0137F",
 "bd297c": "0xbd297cb5158F4DcA02C336A59556FDBfa6609A70",
 "D8F2d1": "0xD8F2d1f5158135232f69Fe0605A406A51d86Ce6B",
 "69E85a": "0x69E85a43E731895abA318f106537fFEf2824beb6",
}
tests = [("totalSupply()", ""), ("totalMinted()", ""), ("freeClaimed()", ""), ("freeMinted()", ""),
 ("FREE_SUPPLY()", ""), ("MAX_SUPPLY()", ""), ("mintOpen()", ""), ("paused()", ""),
 ("mintedBy(address)", enc_addr(USER)[2:]), ("freeUsed(address)", enc_addr(USER)[2:]),
 ("freeClaimed(address)", enc_addr(USER)[2:]), ("balanceOf(address)", enc_addr(USER)[2:]),
 ("AGENT_ID()", ""), ("agentIdRegistry()", ""), ("REGISTRY()", "")]
out = {"block": block()}
for nm, addr in CANDS.items():
    d = {}
    for fn, arg in tests:
        v, e = call(addr, sel(fn) + arg)
        d[fn] = {"int": iv(v), "raw": v, "error": e if v is None else None}
    for fn in ("name()", "symbol()"):
        v, e = call(addr, sel(fn))
        d[fn] = dec_str(v)
    v, e = call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_uint(1)[2:])
    d["quote_user_1"] = {"words": words(v), "raw": v, "error": e}
    # 69E8 sale-specific
    if nm == "69E85a":
        for fn, arg in [("FREE_SHARES()", ""), ("freeMinted()", ""), ("paidMinted()", ""), ("PAID_SHARES()", ""),
                        ("claimFree()", ""), ("quota(address)", enc_addr(USER)[2:]), ("dinoUsed(address)", enc_addr(USER)[2:])]:
            v2, e2 = call(addr, sel(fn) + arg)
            d["sale_"+fn] = {"int": iv(v2), "raw": v2, "error": e2 if v2 is None else None}
    out[nm] = d
print(json.dumps(out, indent=1))
json.dump(out, open("/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-2026-11-02-0731-sourcify-verify.json", "w"), indent=1)
