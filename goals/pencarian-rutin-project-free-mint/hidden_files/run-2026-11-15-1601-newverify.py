#!/usr/bin/env python3
"""Shape-check new contracts, free-mint-search run 2026-11-15 16:01 WIB.
Targets: 9 Sourcify-new (verifiedAt 08:36-08:49Z, after hot-leg 15:59 top 08:57:12Z; 2 top contracts already checked by hot-leg 15:59).
Read-only: Sourcify ABI (?fields=abi) + on-chain views via eth_call batch.
No preview/mint. Writes run-2026-11-15-1601-newverify.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
t0 = time.time()

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
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        elif isinstance(a, str) and a.startswith("0x"):
            d += enc_u(int(a, 16))
        else:
            d += enc_u(int(a))
    return d
def post_rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def get(url, timeout=60):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), url],
                       capture_output=True, text=True, timeout=timeout + 10)
    return r.stdout, r.returncode

TARGETS = {
 "sourcify-947555eb": "0x947555EBa43CFF5454B7102A04b19168Ee743E03",
 "sourcify-a44bf4fc": "0xa44Bf4fc00D8DEb06c56edDc92B5B12c4892F216",
 "sourcify-2c85b774": "0x2c85b774C6e17c45c601b58798B1dCE03182Fff0",
 "sourcify-e4014008": "0xE401400889A9D498f63C6b568331CDb439a9817a",
 "sourcify-63005483": "0x6300548308B618aAD035b692F98f108f109d7E7C",
 "sourcify-50103722": "0x5010372201ccC5Bc55D6f54b92C6FcAa8BD877C2",
 "sourcify-81f86011": "0x81f86011B420b35245a4eDA1b8c8652dbD81404A",
 "sourcify-855c11b4": "0x855C11B4cBc1408e7bF2318f213441D28CDDeCF7",
 "sourcify-13179da2": "0x13179Da21Af5C12D1b9A897d90b4f47A560E540c",
}
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
              "freeSupply", "FREE_SUPPLY", "FREE_CAP", "FREE_MAX", "FREE_SLOTS"]
VIEWS = [("name", "name()", []), ("symbol", "symbol()", []),
         ("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
         ("MAX_SUPPLY", "MAX_SUPPLY()", []), ("mintOpen", "mintOpen()", []),
         ("freeMinted", "freeMinted()", []), ("freeClaimed", "freeClaimed()", []),
         ("freeLeft", "freeLeft()", []), ("FREE_SUPPLY", "FREE_SUPPLY()", []),
         ("AGENT_ID", "AGENT_ID()", []), ("owner", "owner()", []),
         ("mintedBy_user", "mintedBy(address)", [USER]),
         ("balanceOf_user", "balanceOf(address)", [USER])]

def shape(abi):
    fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
    fnset = set(fns)
    has_mint = any(n.startswith("mint") for n in fnset)
    has_quote = any(("quote" in n.lower() or "cost" in n.lower() or "price" in n.lower()) for n in fnset)
    free = [n for n in fnset if n in FREE_VIEWS]
    agent = ("agentIdRegistry" in fnset or "AGENT_ID" in fnset or "agentRegistry" in fnset
             or "agentId" in fnset)
    is_token = all(n in fnset for n in ("name", "symbol", "decimals", "totalSupply"))
    s1 = bool(has_mint and has_quote and free and agent)
    s2 = bool(is_token and ("mintFree" in fnset or "freeMint" in fnset)
              and free and agent)
    return {"S1": s1, "S2": s2, "has_mint": has_mint, "has_quote": has_quote,
            "free_views": free, "agent_ref": agent, "is_token": is_token, "n_fns": len(fns)}

def read_views(addr):
    calls = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
              "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]}
             for i, (key, sig, args) in enumerate(VIEWS)]
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=60)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, (key, sig, args) in zip(res, VIEWS):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    if key in ("name", "symbol"):
                        out[key] = r  # raw; decode below if needed
                    else:
                        out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out, ep
        except Exception:
            continue
    return None, None

out = {}
for name, addr in TARGETS.items():
    raw, rc = get(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=60)
    verified, abi = False, None
    try:
        j = json.loads(raw)
        if isinstance(j, dict) and "abi" in j:
            abi = j["abi"]; verified = True
        elif isinstance(j, dict) and j.get("stdJson"):
            verified = True
    except Exception:
        pass
    if not verified:
        out[name] = {"address": addr, "sourcify": "not_verified", "shape": None, "views": None}
        print(f"{name}: Sourcify NOT VERIFIED", flush=True)
        continue
    sh = shape(abi)
    views, ep = read_views(addr)
    out[name] = {"address": addr, "sourcify": "verified", "shape": sh, "views": views, "via": ep}
    print(f"{name}: shape={json.dumps(sh)} views={json.dumps(views)}", flush=True)

json.dump(out, open(BASE + "run-2026-11-15-1601-newverify.json", "w"), indent=1)
print("DONE elapsed", round(time.time() - t0, 1))
