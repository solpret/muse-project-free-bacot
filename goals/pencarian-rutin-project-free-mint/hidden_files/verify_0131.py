#!/usr/bin/env python3
"""Deep-dive verification run 0131 (2026-11-06). Read-only.
Verifies web-leg finds: Believe BNB (track C), AETHER, AgentX, DEWATA
(agent-shape conflict), SoulAgent/RigOrb/Tigora/MORPHA/Brinedroid updates,
ONLYAI Crystals (upcoming). For each: Sourcify ABI agent-shape, on-chain
free views, user slot, first-mint block/time via Ankr logs, site fetch
checking the site prints the exact contract. A failed read is None, never 0.
"""
import json, sys, time, urllib.request, urllib.error
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from fast_rpc import _single
from ankr import ankr_post
from eth_hash.auto import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc_call(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return _single(ep, method, params, timeout, retries=0)
        except Exception as e:
            last = e
    raise last

def dec_uint(out):
    if not isinstance(out, str) or not out.startswith("0x") or len(out) < 66:
        return None
    try:
        return int(out[2:66], 16)
    except Exception:
        return None

def dec_bool(out):
    v = dec_uint(out)
    return None if v is None else bool(v)

def dec_addr(out):
    if not isinstance(out, str) or len(out) < 66:
        return None
    return "0x" + out[26:66]

def call(addr, data, timeout=7):
    try:
        return rpc_call("eth_call", [{"to": addr, "data": data}, "latest"], timeout)
    except Exception as e:
        return {"_error": str(e)[:100]}

def logs_in(addr, frm, to, page=1000):
    logs, tok, n = [], None, 0
    while True:
        params = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(to),
                  "address": [addr], "pageSize": page, "decodeLogs": False,
                  "topics": [TRANSFER, ZERO_TOPIC]}
        if tok:
            params["pageToken"] = tok
        try:
            body = ankr_post("ankr_getLogs", params, timeout=30)
        except Exception as e:
            return {"_error": str(e)[:120]}
        res = body.get("result", {})
        logs.extend(res.get("logs", []))
        n += 1
        tok = res.get("nextPageToken")
        if not tok or n >= 15:
            break
    return logs

def ts_wib(b):
    ts = int(rpc_call("eth_getBlockByNumber", [hex(b), False], 10)["timestamp"], 16)
    return time.strftime("%Y-%m-%d %H:%M:%S WIB", time.gmtime(ts + 7 * 3600))

def sourcify_abi(address, tries=3):
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

def shape_from_abi(abi):
    if not isinstance(abi, list):
        return None
    funcs = [it.get("name", "") for it in abi if it.get("type") == "function"]
    low = [f.lower() for f in funcs]
    gate = [f for f in funcs if any(g in f.lower() for g in
            ("agentid", "agentregistry", "agentgate", "hasagentid", "isagent"))]
    mint = [f for f in funcs if "mint" in f.lower()]
    quote = [f for f in funcs if f.lower().startswith(("quote", "cost")) or f.lower() in ("price", "getcost")]
    free = [f for f in funcs if f.lower() in ("freesharesremaining", "freeclaimed", "freefor",
            "freeleft", "freeused", "freeavailable", "freesharepoolexhausted",
            "freesharesclaimed", "freeminted", "freeremaining")]
    token = [f for f in funcs if f.lower() in ("name", "symbol", "decimals", "totalsupply")]
    s1 = bool(mint) and bool(quote) and bool(free) and bool(gate)
    s2 = len(token) >= 3 and any(f.lower() in ("mintfree", "claimfree") for f in funcs) and bool(free) and bool(gate)
    return {"functions": len(funcs), "mint_fns": mint, "quote_fns": quote,
            "free_views": free, "gate_fns": gate, "token_fns": token, "S1": s1, "S2": s2}

def fetch_site(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", "ignore")
        return (r.status, body)
    except urllib.error.HTTPError as e:
        return (e.code, "")
    except Exception as e:
        return ("error:" + str(e)[:80], "")

UA = "000000000000000000000000" + USER[2:].lower()
U1 = format(1, "064x")
# views: name -> (fn signature, args hex, decoder)
NFT_VIEWS = {
    "totalSupply": ("totalSupply()", "", dec_uint), "totalMinted": ("totalMinted()", "", dec_uint),
    "freeClaimed": ("freeClaimed()", "", dec_uint), "freeMinted": ("freeMinted()", "", dec_uint),
    "FREE_SUPPLY": ("FREE_SUPPLY()", "", dec_uint), "MAX_SUPPLY": ("MAX_SUPPLY()", "", dec_uint),
    "mintOpen": ("mintOpen()", "", dec_bool), "price": ("price()", "", dec_uint),
    "owner": ("owner()", "", dec_addr),
    "quote_user_1": ("quote(address,uint256)", UA + U1, dec_uint),
    "costOf_user_1": ("costOf(address,uint256)", UA + U1, dec_uint),
    "mintedBy_user": ("mintedBy(address)", UA, dec_uint),
    "freeUsed_user": ("freeUsed(address)", UA, dec_uint),
    "balanceOf_user": ("balanceOf(address)", UA, dec_uint),
}
SALE_VIEWS = {
    "totalShares": ("totalShares()", "", dec_uint), "totalFreeShares": ("totalFreeShares()", "", dec_uint),
    "totalPaidShares": ("totalPaidShares()", "", dec_uint),
    "totalSupply": ("totalSupply()", "", dec_uint),
    "PRICE": ("PRICE()", "", dec_uint), "price": ("price()", "", dec_uint),
    "quote_user_1": ("quote(address,uint256)", UA + U1, dec_uint),
    "costOf_user_1": ("costOf(address,uint256)", UA + U1, dec_uint),
    "freeClaimed_user": ("freeClaimed(address)", UA, dec_uint),
    "balanceOf_user": ("balanceOf(address)", UA, dec_uint),
    "token": ("token()", "", dec_addr), "saleToken": ("saleToken()", "", dec_addr),
    "identity": ("identity()", "", dec_addr), "REGISTRY": ("REGISTRY()", "", dec_addr),
    "agentRegistry": ("agentRegistry()", "", dec_addr),
    "totalFree": ("totalFree()", "", dec_uint), "freeSharesRemaining": ("freeSharesRemaining()", "", dec_uint),
}

ITEMS = [
    ("BelieveBNB-sale", "0x2d15595d2e6EfB1c1EBf938Cd7Fd0f57d11C6b86", "sale", True),
    ("BelieveBNB-token", "0x5e1A6b3041873b05d21C24Cce8c1af763846BeA7", "token", True),
    ("AETHER", "0x926504d174e99DB699141049b3Dd94dF501ff813", "nft", True),
    ("AgentX-59d9", "0x59d96d8b4b82abb350868e897f25f8e021360823", "nft", False),
    ("HI-SCORE", "0xA74081fd9bc9623A2d9321223C35b41016A7fd65", "nft", False),
    ("DEWATA", "0x13628D733A26b942213BA1b3C61471925D4a2165", "nft", True),
    ("SoulAgent", "0x8fdb9411753c58476a41f7b88a44989f8d687d63", "nft", False),
    ("RigOrb", "0x72d977237f7b3931a08434cebd0d3814fe13539e", "nft", False),
    ("Tigora", "0xE8c46E7c734259FEc1A78Fc846DcFaD94Ecb70E5", "nft", False),
    ("ONLYAI-Crystals", "0x156482ad3f0eebd8e3f70d494ebd1da3f738f5ba", "nft", False),
    ("MORPHA", "0xb40e4d3b33c5d70ab31a1dde3c240727691cb738", "nft", False),
    ("Brinedroid", "0xa069401266707e1318bdff45b3f1f61e52d1ae48", "nft", False),
]

def main():
    head = int(rpc_call("eth_blockNumber", [], 10), 16)
    out = {"block": head, "wib": time.strftime("%Y-%m-%d %H:%M WIB", time.gmtime(time.time() + 7 * 3600)), "items": {}}
    for name, addr, kind, do_logs in ITEMS:
        r = {"address": addr, "kind": kind}
        st, abi = sourcify_abi(addr)
        r["sourcify"] = st
        r["shape"] = shape_from_abi(abi) if abi else None
        views = SALE_VIEWS if kind in ("sale", "token") else NFT_VIEWS
        for k, (fn_sig, args_hex, dec) in views.items():
            data = sel(fn_sig) + args_hex
            r[k] = dec(call(addr, data))
        # contractURI (method H)
        r["contractURI_raw"] = call(addr, sel("contractURI()"))
        # first mint via logs (Transfer from zero) — only for age-critical items
        if not do_logs:
            r["first_mint"] = {"skipped": "already-in-snapshot / not age-critical this run"}
        else:
            logs = logs_in(addr, 130000000, head)
            if isinstance(logs, dict) and "_error" in logs:
                r["first_mint"] = {"error": logs["_error"]}
            elif logs:
                fb = min(int(x["blockNumber"], 16) for x in logs)
                r["first_mint"] = {"block": fb, "wib": ts_wib(fb), "log_count": len(logs),
                                   "minters": len({x["topics"][2] for x in logs if len(x.get("topics", [])) > 2})}
                txs = []
                for x in logs[:2]:
                    try:
                        tx = rpc_call("eth_getTransactionByHash", [x["transactionHash"]], 10)
                        txs.append({"tx": x["transactionHash"], "value": tx.get("value"), "from": tx.get("from")})
                    except Exception as e:
                        txs.append({"tx": x["transactionHash"], "error": str(e)[:80]})
                r["first_mint"]["sample_txs"] = txs
            else:
                r["first_mint"] = {"block": None, "log_count": 0}
        out["items"][name] = r
        print(name, "| sourcify:", st, "| shape:", (r["shape"] or {}).get("S1"), (r["shape"] or {}).get("S2"),
              "| first_mint:", r["first_mint"].get("block"), r["first_mint"].get("wib"),
              "| totalSupply:", r.get("totalSupply"), "| freeClaimed:", r.get("freeClaimed"),
              "| freeMinted:", r.get("freeMinted"), "| quote1:", r.get("quote_user_1"),
              "| costOf1:", r.get("costOf_user_1"), "| totalFreeShares:", r.get("totalFreeShares"),
              "| totalShares:", r.get("totalShares"))
    # site fetches
    for label, url, needle in [
        ("believebnb.xyz", "https://believebnb.xyz/", "0x2d15595d2e6efb1c1ebf938cd7fd0f57d11c6b86"),
        ("aetheragent.site", "https://aetheragent.site/", "0x926504d174e99db699141049b3dd94df501ff813"),
    ]:
        st, body = fetch_site(url)
        low = body.lower()
        out["site_" + label] = {"url": url, "status": st, "len": len(body),
                                 "prints_contract": needle in low,
                                 "prints_token_believe": "0x5e1a6b3041873b05d21c24cce8c1af763846bea7" in low}
        print(label, "| status:", st, "| len:", len(body), "| prints_contract:", needle in low)
    json.dump(out, open(HF + "verify-2026-11-06-0131.json", "w"), indent=1)
    print("wrote verify-2026-11-06-0131.json")

if __name__ == "__main__":
    main()
