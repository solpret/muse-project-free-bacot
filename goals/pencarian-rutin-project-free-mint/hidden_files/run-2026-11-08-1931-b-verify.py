#!/usr/bin/env python3
"""Run 1931: on-chain verification of Subagent B's 5 flagged items (read-only).
NOVRA (track-C candidate), ORBIT PASS, Bound Agent, BAHUANG2 (promotion flag),
GLOOP 18-bit (status change). None = UNVERIFIED/revert, never zero."""
import sys, json, urllib.request, urllib.error, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u256(n): return "%064x" % n
def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=10, retries=0)
            if isinstance(out, dict) and "result" in out: return out["result"]
            if isinstance(out, dict) and "error" in out: return None
        except Exception: continue
    return None
def dec(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_str(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64: return b.decode(errors="replace")
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def dec_addr(h):
    if not isinstance(h, str) or len(h) < 42: return None
    return "0x" + h[-40:]
def call_tuple(addr, data):
    r = call(addr, data)
    if not isinstance(r, str) or r in (None, "0x"): return None
    h = r[2:]
    return [int(h[i:i+64], 16) if len(h) >= i+64 else None for i in range(0, min(len(h), 256), 64)]
def block_time_wib(blk):
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(blk), False]}, timeout=10, retries=0)
            if r and r.get("result"):
                ts = int(r["result"]["timestamp"], 16)
                return datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None
def sourcify_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            j = json.load(resp)
        abi = j.get("abi")
        if not isinstance(abi, list): return {"sourcify": "no-abi", "match": j.get("match")}
        fns = sorted({f.get("name", "") for f in abi if f.get("type") == "function"})
        return {"sourcify": j.get("match") or "verified", "fns": fns, "abi": abi}
    except urllib.error.HTTPError as e:
        return {"sourcify": f"http_{e.code} (not_verified)" if e.code == 404 else f"http_{e.code}"}
    except Exception as e:
        return {"sourcify": f"error:{str(e)[:80]}"}

discards = json.load(open(BASE + "/same-owner-discards.json"))
disc_owners = {str(d.get("owner", "")).lower() for d in discards if isinstance(d, dict)}

def generic(addr):
    r = {"address": addr}
    r["name"] = dec_str(call(addr, sel("name()")))
    r["symbol"] = dec_str(call(addr, sel("symbol()")))
    r["totalSupply"] = dec(call(addr, sel("totalSupply()")))
    r["totalMinted"] = dec(call(addr, sel("totalMinted()")))
    r["MAX_SUPPLY"] = dec(call(addr, sel("MAX_SUPPLY()")))
    r["FREE_SUPPLY"] = dec(call(addr, sel("FREE_SUPPLY()")))
    r["FREE_CAP"] = dec(call(addr, sel("FREE_CAP()")))
    r["freeClaimed"] = dec(call(addr, sel("freeClaimed()")))
    r["freeMinted"] = dec(call(addr, sel("freeMinted()")))
    r["freeLeft"] = dec(call(addr, sel("freeLeft()")))
    r["freeRemaining"] = dec(call(addr, sel("freeRemaining()")))
    r["mintOpen"] = dec(call(addr, sel("mintOpen()")))
    r["mintStart"] = dec(call(addr, sel("mintStart()")))
    r["mintEnd"] = dec(call(addr, sel("mintEnd()")))
    r["owner"] = dec_addr(call(addr, sel("owner()")))
    r["owner_in_discards"] = (r["owner"] or "").lower() in disc_owners if r["owner"] else None
    r["agentRegistry"] = dec_addr(call(addr, sel("agentRegistry()")))
    r["AGENT_ID"] = dec_addr(call(addr, sel("AGENT_ID()")))
    r["balanceOf_user"] = dec(call(addr, sel("balanceOf(address)") + enc_addr(USER)))
    r["freeClaimed_user"] = dec(call(addr, sel("freeClaimed(address)") + enc_addr(USER)))
    r["freeLeft_user"] = dec(call(addr, sel("freeLeft(address)") + enc_addr(USER)))
    r["freeUsed_user"] = dec(call(addr, sel("freeUsed(address)") + enc_addr(USER)))
    r["freeOf_user"] = dec(call(addr, sel("freeOf(address)") + enc_addr(USER)))
    r["freeCount_user"] = dec(call(addr, sel("freeCount(address)") + enc_addr(USER)))
    r["mintedBy_user"] = dec(call(addr, sel("mintedBy(address)") + enc_addr(USER)))
    r["quote_user_1"] = call_tuple(addr, sel("quote(address,uint256)") + enc_addr(USER) + enc_u256(1))
    r["costOf_user_1"] = call_tuple(addr, sel("costOf(address,uint256)") + enc_addr(USER) + enc_u256(1))
    return r

out = {}
# --- NOVRA (track C) ---
N = "0x75Ac13cF23a8dccC703D1496138251FD7f247890"
n = generic(N)
n.update(sourcify_abi(N))
n["totalShares"] = dec(call(N, sel("totalShares()")))
n["sharesSold"] = dec(call(N, sel("sharesSold()")))
n["freeSharesRemaining"] = dec(call(N, sel("freeSharesRemaining()")))
n["FREE_CAP_shares"] = dec(call(N, sel("FREE_CAP()")))
out["NOVRA"] = n
print("NOVRA", json.dumps({k: v for k, v in n.items() if k != "abi"}), flush=True)
# --- ORBIT PASS ---
O = "0x51d3c0101696956baf928899d5bb57544f00c9b9"
o = generic(O)
o.update(sourcify_abi(O))
o["seen_first_block"] = 132380556
o["seen_first_wib"] = block_time_wib(132380556)
out["ORBIT PASS"] = o
print("ORBIT", json.dumps({k: v for k, v in o.items() if k != "abi"}), flush=True)
# --- Bound Agent ---
B = "0xa75526d63bd5E3b3e8A65a5f2efEF45072904d04"
b = generic(B)
b.update(sourcify_abi(B))
out["Bound Agent"] = b
print("BOUND", json.dumps({k: v for k, v in b.items() if k != "abi"}), flush=True)
# --- BAHUANG2 ---
H2 = "0x57CC350b844484Eac0DE444526d295C90F9cCbB5"
h2 = generic(H2)
h2["mintStart_wib"] = None
if h2.get("mintStart"):
    h2["mintStart_wib"] = datetime.datetime.fromtimestamp(
        h2["mintStart"], datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
if h2.get("freeMinted") is not None and h2.get("FREE_CAP"):
    h2["freePct"] = round(100.0 * h2["freeMinted"] / h2["FREE_CAP"], 2)
out["BAHUANG2"] = h2
print("BAHUANG2", json.dumps(h2), flush=True)
# --- GLOOP 18-bit ---
G = "0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE"
g = generic(G)
g["difficultyBits"] = dec(call(G, sel("difficultyBits()")))
g["hasMinted_user"] = dec(call(G, sel("hasMinted(address)") + enc_addr(USER)))
g["MINT_START"] = dec(call(G, sel("MINT_START()")))
if g.get("totalMinted") is not None:
    g["freePct_vs_3333"] = round(100.0 * g["totalMinted"] / 3333, 2)
out["GLOOP 18-bit"] = g
print("GLOOP18", json.dumps(g), flush=True)

json.dump(out, open(BASE + "/run-2026-11-08-1931-b-verify.json", "w"), indent=1)
print("DONE")
