#!/usr/bin/env python3
"""Probe S1 trio + 0x7B1ca439 + 0xca764053 for free-mint-search run 2026-11-13 23:31 WIB.
Read-only; writes run-2026-11-13-2331-probe-s1trio.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d

def dec_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "replace")
    except Exception:
        return None

def dec_addr(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 32: return None
        return "0x" + b[12:32].hex()
    except Exception:
        return None

def raw_batch(addr, views):
    """views: list of (key, sig, args, kind) kind in uint/bool/addr/str."""
    calls, keys, kinds = [], [], []
    for i, (key, sig, args, kind) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key); kinds.append(kind)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key, kind in zip(res, keys, kinds):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    if kind == "str":
                        out[key] = dec_str(r)
                    elif kind == "addr":
                        out[key] = dec_addr(r)
                    else:
                        out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception:
            continue
    return None

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=25)
            if isinstance(r, dict) and r.get("result"):
                return r["result"]
        except Exception:
            continue
    return None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

U = [USER]
TRIO_VIEWS = [
    ("AI_AGENT_REGISTRY","AI_AGENT_REGISTRY()",[],"addr"),
    ("FREE_SUPPLY","FREE_SUPPLY()",[],"uint"),
    ("freeMinted","freeMinted()",[],"uint"),
    ("totalSupply","totalSupply()",[],"uint"),
    ("totalMinted","totalMinted()",[],"uint"),
    ("mintOpen","mintOpen()",[],"uint"),
    ("MINT_END","MINT_END()",[],"uint"),
    ("roundEndTime","roundEndTime()",[],"uint"),
    ("quote_user_1","quote(address,uint256)",[USER, 1],"uint"),
    ("mintedPerWallet_user","mintedPerWallet(address)",U,"uint"),
    ("userShares_user","userShares(address)",U,"uint"),
    ("checkAiAgent_user","checkAiAgent(address)",U,"uint"),
    ("owner","owner()",[],"addr"),
    ("WEBSITE","WEBSITE()",[],"str"),
    ("contractURI","contractURI()",[],"str"),
    ("name","name()",[],"str"),
    ("symbol","symbol()",[],"str"),
]
ITEMS = {
 "S1-5106": ("0x5106640f80D13e8E796b021FFb6F9735ad00a416", TRIO_VIEWS),
 "S1-Bedf": ("0xBedf504A6e383c2a46827b7151b3732D7d791a08", TRIO_VIEWS),
 "S1-FA0A": ("0xFA0A8297E746cf3662E1065CB4D07bD7BC230484", TRIO_VIEWS),
 "T7B1ca": ("0x7B1ca439312368dE8652b9B5d7A54cA74A884680", [
    ("agentId","agentId()",[],"addr"),
    ("FREE_QUOTA","FREE_QUOTA()",[],"uint"),
    ("freeMinted","freeMinted()",[],"uint"),
    ("freeClaimed_user","freeClaimed(address)",U,"uint"),
    ("mintOpen","mintOpen()",[],"uint"),
    ("totalMinted","totalMinted()",[],"uint"),
    ("totalSupply","totalSupply()",[],"uint"),
    ("nextFreeId","nextFreeId()",[],"uint"),
    ("owner","owner()",[],"addr"),
    ("name","name()",[],"str"),
    ("symbol","symbol()",[],"str")]),
 "CA76": ("0xca76405325A172803aC5682E286cE1ebCEBAcA71", [
    ("AGENT_ID_REGISTRY","AGENT_ID_REGISTRY()",[],"addr"),
    ("LOT_PRICE","LOT_PRICE()",[],"uint"),
    ("SALE_WINDOW","SALE_WINDOW()",[],"uint"),
    ("mintOpen","mintOpen()",[],"uint"),
    ("totalSupply","totalSupply()",[],"uint"),
    ("owner","owner()",[],"addr"),
    ("name","name()",[],"str"),
    ("symbol","symbol()",[],"str")]),
}
reads = {}
for name, (addr, views) in ITEMS.items():
    r = raw_batch(addr, views)
    code = get_code(addr)
    reg_hit = (code or "").lower().find(REGISTRY) >= 0 if code else None
    reads[name] = {"address": addr, "views": r, "code_len": len(code) if code else None,
                   "registry_bytes_hit": reg_hit}
    print(name, "OK" if r is not None else "FAIL", json.dumps(r)[:500], "regbytes:", reg_hit, flush=True)

blk = block_number()
out = {"started_wib": "2026-11-13T23:31+07:00", "reads": reads, "block": blk,
       "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-13-2331-probe-s1trio.json", "w"), indent=1)
print("DONE block", blk, "elapsed", round(time.time() - t0, 1))
