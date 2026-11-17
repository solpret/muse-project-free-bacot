#!/usr/bin/env python3
"""Triage 3 addresses for run 2026-11-10 0231 WIB. Read-only.
0x0ee89b62 (0201 5a S1/S2-pass claim vs hot-leg correction 0 sale-shape),
0xb4609310 + 0x6fca4bb2 (Boltbook ZH front-page new addresses, hot-leg 0214).
Checks: Sourcify ABI + classify S1/S2 + agent-mint shape; eth_call views via dataseed;
eth_getCode registry-bytes. Writes run-2026-11-10-0231-triage3.json + .log
"""
import json, time, subprocess, urllib.request, urllib.error
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/custom-connectors/custom.ankr/bin"
TS = "2026-11-10-0231"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
ADDRS = ["0x0ee89b62d0b19C6BF4eDe98aC0542cd604B0E011",
         "0xb460931092a321648586d9fd3f8Bba61EbA4B60f",
         "0x6fca4bb25600c7d28c80eefc3813235cac31b689"]
FREE_SHARE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft",
                    "freeused", "freeavailable", "freesharepoolexhausted",
                    "freesharesclaimed", "freeminted", "freeremaining"]
QUOTE_FNS = ["quote", "quotefor", "quotemint", "quotemintfor", "cost", "costfor",
             "getcost", "price", "mintprice", "feefor"]
GATE_WORDS = ["agentid", "agentregistry", "agentgate", "hasagentid", "isagent"]

def log(*a):
    print(*a, flush=True)

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def sourcify_abi(address, tries=4):
    url = f"https://sourcify.dev/server/v2/contract/56/{address}?fields=abi"
    for i in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                return ("verified", data.get("abi"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ("not_verified", None)
            time.sleep(3)
        except Exception:
            time.sleep(3)
    return ("error:retry-exhausted", None)

def classify(abi):
    funcs = []
    if isinstance(abi, list):
        for item in abi:
            if item.get("type") == "function":
                funcs.append(item.get("name", ""))
    low = [f.lower() for f in funcs]
    mint_fns = [f for f in funcs if "mint" in f.lower()]
    quote_fns = [f for f in funcs if f.lower() in QUOTE_FNS or f.lower().startswith("quote") or f.lower().startswith("cost")]
    free_views = [f for f in funcs if f.lower() in FREE_SHARE_VIEWS]
    gate = [f for f in funcs if any(g in f.lower() for g in GATE_WORDS)]
    token_fns = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    noarg_free = [f for f in funcs if f.lower() in ("mintfree", "mint", "claimfree")]
    s1 = bool(mint_fns) and bool(quote_fns) and bool(free_views) and bool(gate)
    s2 = len(token_fns) >= 3 and bool(noarg_free) and bool(free_views) and bool(gate)
    nft = any(x in low for x in ("tokenuri", "ownerof", "tokenofownerbyindex"))
    return {"functions": len(funcs), "mint_fns": mint_fns, "quote_fns": quote_fns,
            "free_views": free_views, "gate_fns": gate, "token_fns": token_fns,
            "S1": s1, "S2": s2, "nft_shaped": nft, "all_fns": funcs}

def eth_call(addr, sig, arg=None):
    data = sel(sig) + (enc(arg) if arg else "")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": addr, "data": data}, "latest"]}
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=25)
            if isinstance(res, dict) and "result" in res:
                return res["result"]
        except Exception:
            continue
    return None

def eth_call_str(addr, sig):
    raw = eth_call(addr, sig)
    if not raw or raw == "0x": return None
    try:
        b = bytes.fromhex(raw[2:])
        # string ABI: offset(32) + len(32) + data
        if len(b) >= 64:
            ln = int.from_bytes(b[32:64], "big")
            return b[64:64+ln].decode("utf-8", "ignore")
    except Exception:
        pass
    return None

def get_code(addr):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]}
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=25)
            if isinstance(res, dict) and "result" in res:
                return res["result"]
        except Exception:
            continue
    return None

VIEWS = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()",
         "FREE_SUPPLY()", "MAX_SUPPLY()", "mintOpen()", "balanceOf(address)",
         "freeClaimed(address)", "freeSharesRemaining()", "mintPrice()"]

def main():
    out = {}
    for addr in ADDRS:
        r = {"address": addr}
        status, abi = sourcify_abi(addr)
        r["sourcify"] = status
        if abi is not None:
            r.update(classify(abi))
        else:
            r["S1"] = False; r["S2"] = False; r["nft_shaped"] = None
        code = get_code(addr)
        r["code_len"] = len(code) - 2 if code else None
        r["registry_bytes"] = (REG in (code or "").lower()) if code else None
        r["name"] = eth_call_str(addr, "name()")
        r["symbol"] = eth_call_str(addr, "symbol()")
        views = {}
        for sig in VIEWS:
            arg = USER if "(address)" in sig else None
            raw = eth_call(addr, sig, arg)
            views[sig] = to_int(raw) if raw not in (None, "0x") else ("ERR" if raw is None else None)
            # distinguish revert (None from missing result) vs 0
        r["views"] = views
        r["contractURI_raw"] = eth_call(addr, "contractURI()")
        out[addr] = r
        log(addr, "sourcify=", status, "S1=", r.get("S1"), "S2=", r.get("S2"),
            "nft=", r.get("nft_shaped"), "reg_bytes=", r.get("registry_bytes"),
            "name=", r.get("name"), "sym=", r.get("symbol"), "views=", json.dumps(views))
    json.dump(out, open(f"/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/run-{TS}-triage3.json", "w"), indent=1)
    log("DONE")

if __name__ == "__main__":
    main()
