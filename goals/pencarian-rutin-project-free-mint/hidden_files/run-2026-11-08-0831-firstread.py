#!/usr/bin/env python3
"""Run 0831: first-read batch for Boltbook ZH/EN new discoveries (not in snapshot).
Read-only; writes run-2026-11-08-0831-firstread.json. LEAN single-call views + Sourcify shape.
"""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-08-0831"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TARGETS = {
    "HOPKIN": "0x2728c134d79d34a977d6d35d8a3014abb5c97ed4",
    "GOAT": "0xe7a548606eecb32a93b227411b6343b0399dc7c0",
    "PXSNT": "0x4e4e43f84E2E80716d03153F3c675e8E715Fa698",
    "OinkHash-Pigs": "0x56155fd1818b31256E7f435956D6dff5C732f35f",
    "WOJAGENT": "0x62EC413381B74387b57F1E2734cdd2E5b96a57B7",
    "HokiCat": "0xdb51dcc2d8caf9942d9a975a2e68e023ab5e1fca",
    "Ink Koi": "0xbd4b4e7189ae9356514664146b0ed683601200a9",
}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def single(addr, data, timeout=10):
    for ep in EPS:
        try:
            res = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=timeout)
            return res[0]
        except Exception:
            continue
    return None

def view(addr, sig, arg=None, arg2=None):
    data = sel(sig)
    if arg is not None:
        data += enc(arg) if isinstance(arg, str) and arg.startswith("0x") else enc_uint(arg)
    if arg2 is not None:
        data += enc_uint(arg2)
    return to_int(single(addr, data))

def raw_str(addr, sig):
    r = single(addr, sel(sig))
    if r is None: return None
    try:
        ln = int(r[66:130], 16)
        return bytes.fromhex(r[130:130+ln*2]).decode("utf-8", "replace")
    except Exception:
        return None

def addr_view(addr, sig):
    r = single(addr, sel(sig))
    if r is None: return None
    try: return "0x" + r[-40:]
    except Exception: return None

def sourcify_shape(addr):
    try:
        r = subprocess.run(["curl", "-sS", "--max-time", "20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True, timeout=25)
        d = json.loads(r.stdout)
        abi = d.get("abi")
        if abi is None:
            return {"sourcify": "not_verified"}
        fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
        mint = [f for f in fns if "mint" in f.lower()]
        quote = [f for f in fns if f.lower().startswith("quote") or f.lower().startswith("cost") or f.lower() in ("price",)]
        free = [f for f in fns if f.lower() in ("freeclaimed","freefor","freeleft","freeused","freeavailable","freesharesremaining","freesharesclaimed","freeminted","freeremaining")]
        gate = [f for f in fns if any(g in f.lower() for g in ("agentid","agent_id","agentregistry","agent_registry","agentgate","agent_gate","hasagentid","isagent"))]
        token = [f for f in fns if f.lower() in ("name","symbol","decimals","totalsupply")]
        noarg = [f for f in fns if f.lower() in ("mintfree","claimfree")]
        s1 = bool(mint) and bool(quote) and bool(free) and bool(gate)
        s2 = len(token) >= 3 and bool(noarg) and bool(free) and bool(gate)
        return {"sourcify": "verified", "fns": len(fns), "mint": mint, "quote": quote,
                "free": free, "gate": gate, "token": token, "noarg_free": noarg, "S1": s1, "S2": s2,
                "match": d.get("match")}
    except Exception as e:
        return {"sourcify": f"error {e}"}

out = {"run": TS, "targets": {}}
for name, addr in TARGETS.items():
    t = time.time()
    d = {"address": addr}
    d["name"] = raw_str(addr, "name()")
    d["symbol"] = raw_str(addr, "symbol()")
    for sig in ["totalSupply()", "totalMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "freeClaimed()",
                "freeMinted()", "freeLeft()", "mintOpen()", "FREE_PER_WALLET()", "MAX_PER_WALLET()",
                "PRICE()", "freeSupply()", "maxSupply()", "freeSharesRemaining()", "totalShares()",
                "sharesSold()", "freeSharesClaimed()"]:
        d[sig.split("(")[0]] = view(addr, sig)
        time.sleep(0.05)
    d["freeClaimed_user"] = view(addr, "freeClaimed(address)", USER)
    d["freeFor_user"] = view(addr, "freeFor(address)", USER)
    d["mintedBy_user"] = view(addr, "mintedBy(address)", USER)
    d["balanceOf_user"] = view(addr, "balanceOf(address)", USER)
    d["quote_user_1"] = view(addr, "quote(address,uint256)", USER, 1)
    d["quote_1"] = view(addr, "quote(uint256)", 1)
    d["mintFree_user"] = view(addr, "mintFree(address)", USER) if False else None
    d["owner"] = addr_view(addr, "owner()")
    d["agentId"] = addr_view(addr, "AGENT_ID()")
    d["contractURI"] = raw_str(addr, "contractURI()")
    r = single(addr, sel("tokenURI(uint256)") + enc_uint(1))
    if r:
        try:
            ln = int(r[66:130], 16)
            d["tokenURI_1"] = bytes.fromhex(r[130:130+ln*2]).decode("utf-8", "replace")[:500]
        except Exception:
            d["tokenURI_1"] = "decode-fail"
    def supports(iface):
        rr = single(addr, sel("supportsInterface(bytes4)") + iface[2:].ljust(64, "0"))
        return rr is not None and int(rr, 16) == 1
    d["isERC721"] = supports("0x80ac58cd")
    d["isERC1155"] = supports("0xd9b67a26")
    d["shape"] = sourcify_shape(addr)
    out["targets"][name] = d
    print(f"FIRSTREAD {name} {addr[:10]} name={d['name']} sym={d['symbol']} ts={d.get('totalSupply')} freeClaimed={d.get('freeClaimed')} FREE_SUPPLY={d.get('FREE_SUPPLY')} MAX={d.get('MAX_SUPPLY')} open={d.get('mintOpen')} q_user1={d.get('quote_user_1')} bal_user={d.get('balanceOf_user')} ERC721={d['isERC721']} shape={d['shape'].get('sourcify')} S1={d['shape'].get('S1')} S2={d['shape'].get('S2')} ({time.time()-t:.1f}s)", flush=True)

json.dump(out, open(f"{BASE}/run-{TS}-firstread.json", "w"), indent=1)
print("FIRSTREAD DONE", flush=True)
