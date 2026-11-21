#!/usr/bin/env python3
"""Retry leg for run 2026-11-20 07:01 WIB verify-new. Read-only.
- Pocket Ai views retry (single-call batches of 5)
- YAMA ABI + free-pool/user reads
- VEIN sale raw Sourcify + candidate free views
- eth_getLogs as SINGLE (non-batch) JSON-RPC, small windows first, then
  backwards scan in 20k-block chunks up to ~200k blocks for first mint
- site gate grep (curl, same class as Boltbook reads in run script)
Writes run-2026-11-20-0701-verify-new-b.json."""
import json, subprocess, time
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
RUN = "2026-11-20-0701"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
TRANSFER = "0x" + keccak(b"Transfer(address,address,uint256)").hex()
ZERO_TOPIC = "0x0000000000000000000000000000000000000000000000000000000000000000"

def sel(sig):
    return keccak(sig.encode())[:4].hex()
def enc_addr(a):
    return "0" * 24 + a[2:].lower()
def encode(sig, arg=None):
    d = "0x" + sel(sig)
    if arg == "user":
        d += enc_addr(USER)
    elif arg == "one":
        d += "%064x" % 1
    elif arg == "user1":
        d += enc_addr(USER) + "%064x" % 1
    return d

def curl_post(payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", RPC,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True)
    return o.stdout

def rpc_single(method, params, timeout=60):
    raw = curl_post({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout)
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "JSONDecodeError", "raw_head": raw[:200]}

def batch_calls(calls, chunk=5):
    out = [None] * len(calls)
    for i in range(0, len(calls), chunk):
        ch = calls[i:i + chunk]
        payload = [{"jsonrpc": "2.0", "id": j + 1, "method": "eth_call",
                    "params": [{"to": c[0], "data": c[1]}, "latest"]} for j, c in enumerate(ch)]
        raw = curl_post(payload)
        try:
            resp = json.loads(raw)
        except Exception:
            for j in range(len(ch)):
                out[i + j] = {"error": "transport JSONDecodeError"}
            time.sleep(2)
            continue
        by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(ch)):
            it = by_id.get(j + 1, {})
            if "result" in it and it["result"] not in (None, "0x"):
                out[i + j] = it["result"]
            elif "error" in it:
                out[i + j] = {"error": str(it["error"])[:120]}
            else:
                out[i + j] = None
        time.sleep(1)
    return out

def dec_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64:
            return None
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "replace")
    except Exception:
        return None

def read_views(addr, viewdefs):
    calls, labels = [], []
    for vk, (sig, arg) in viewdefs.items():
        calls.append((addr, encode(sig, arg)))
        labels.append(vk)
    res = batch_calls(calls)
    views = {}
    for vk, v in zip(labels, res):
        if isinstance(v, dict):
            views[vk] = v
        elif isinstance(v, str):
            if vk in ("name", "symbol", "contractURI"):
                views[vk] = dec_str(v)
            elif vk in ("owner", "core", "agentRegistry", "token", "agentIdRegistry"):
                views[vk] = "0x" + v[-40:] if len(v) >= 42 else v
            else:
                try:
                    views[vk] = int(v, 16)
                except Exception:
                    views[vk] = v
        else:
            views[vk] = v
    return views

def get_logs_single(addr, fb, tb):
    r = rpc_single("eth_getLogs", [{"fromBlock": hex(fb), "toBlock": hex(tb),
                                    "address": addr, "topics": [TRANSFER, ZERO_TOPIC]}])
    if isinstance(r, dict) and "error" in r:
        return {"error": str(r["error"])[:200]}
    if isinstance(r, dict) and "result" in r:
        logs = r["result"]
        return {"count": len(logs),
                "first_block": int(logs[0]["blockNumber"], 16) if logs else None,
                "first_tx": logs[0].get("transactionHash") if logs else None,
                "last_block": int(logs[-1]["blockNumber"], 16) if logs else None}
    return {"error": f"unexpected {str(r)[:200]}"}

def first_mint_scan(addr, head, chunk_blocks=20000, max_back=200000):
    """Scan backwards in chunks from head; return first mint block found, or
    the oldest chunk scanned with no mints (lower bound on launch)."""
    scanned = []
    start = head
    while head - start < max_back:
        fb = max(start - chunk_blocks, head - max_back)
        r = get_logs_single(addr, fb, start)
        scanned.append({"from": fb, "to": start, "result": r})
        if "error" in r:
            return {"status": "error", "scanned": scanned}
        if r.get("count"):
            return {"status": "found", "first_block": r["first_block"],
                    "first_tx": r["first_tx"], "count_in_chunk": r["count"],
                    "scanned": scanned}
        start = fb
        time.sleep(0.5)
    return {"status": "not_found_in_window", "window_blocks": max_back, "scanned": scanned}

def block_ts(block):
    r = rpc_single("eth_getBlockByNumber", [hex(block), False])
    if isinstance(r, dict) and isinstance(r.get("result"), dict):
        return int(r["result"]["timestamp"], 16)
    return {"error": str(r)[:150]}

def site_grep(url, needles):
    try:
        o = subprocess.run(["curl", "-sL", "--max-time", "30", url],
                           capture_output=True, text=True)
        html = o.stdout
        low = html.lower()
        return {"url": url, "bytes": len(html), "http_ok": len(html) > 0,
                "prints": {n: (n.lower() in low) for n in needles}}
    except Exception as e:
        return {"url": url, "error": f"{type(e).__name__}: {str(e)[:120]}"}

blk = rpc_single("eth_blockNumber", [])
head = int(blk["result"], 16) if isinstance(blk, dict) and "result" in blk else None
out = {"run": RUN, "head": head, "retry": {}}

# ---- Pocket Ai views retry ----
POCKET = "0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102"
pocket_views = {
    "totalSupply": ("totalSupply()", None), "totalMinted": ("totalMinted()", None),
    "freeClaimed": ("freeClaimed()", None), "freeMinted": ("freeMinted()", None),
    "FREE_SUPPLY": ("FREE_SUPPLY()", None), "freeSupply": ("freeSupply()", None),
    "freeLeft": ("freeLeft()", None), "mintOpen": ("mintOpen()", None),
    "mintActive": ("mintActive()", None), "MAX_SUPPLY": ("MAX_SUPPLY()", None),
    "FREE_PRICE": ("FREE_PRICE()", None), "PAID_PRICE": ("PAID_PRICE()", None),
    "MAX_FREE_PER_WALLET": ("MAX_FREE_PER_WALLET()", None),
    "balanceOf_user": ("balanceOf(address)", "user"),
    "mintedBy_user": ("mintedBy(address)", "user"),
    "freeMintedBy_user": ("freeMintedBy(address)", "user"),
    "freeMintedByWallet_user": ("freeMintedByWallet(address)", "user"),
    "name": ("name()", None), "symbol": ("symbol()", None),
    "contractURI": ("contractURI()", None), "owner": ("owner()", None),
}
out["retry"]["pocket_views"] = read_views(POCKET, pocket_views)
out["retry"]["pocket_first_mint"] = first_mint_scan(POCKET, head)

# ---- YAMA: full ABI + pool/user reads ----
YAMA_SALE = "0x86D779fc4d83044cCECCb53639f9a98E367D6E46"
try:
    o = subprocess.run(["curl", "-sL", "--max-time", "25",
                        f"https://sourcify.dev/server/v2/contract/56/{YAMA_SALE}?fields=abi"],
                       capture_output=True, text=True).stdout
    abi = json.loads(o).get("abi", [])
    yama_fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
except Exception as e:
    yama_fns = {"error": str(e)[:120]}
out["retry"]["yama_abi_fns"] = yama_fns
yama_views = {
    "totalFreeShares": ("totalFreeShares()", None),
    "totalPaidShares": ("totalPaidShares()", None),
    "totalShares": ("totalShares()", None),
    "freeUsed_user": ("freeUsed(address)", "user"),
    "quotaOf_user": ("quotaOf(address)", "user"),
    "sharesOf_user": ("sharesOf(address)", "user"),
    "isAgent_user": ("isAgent(address)", "user"),
    "agentIdRegistry": ("agentIdRegistry()", None),
    "token": ("token()", None),
    "PRICE": ("PRICE()", None),
    "TOKENS_PER_SHARE": ("TOKENS_PER_SHARE()", None),
    "MAX_SHARES": ("MAX_SHARES()", None),
    "BASE_QUOTA": ("BASE_QUOTA()", None),
    "quote_user_1": ("quote(address,uint256)", "user1"),
    "quote_user_0": ("quote(address,uint256)", "user"),
}
# quote_user_0 uses arg user with amount 0 encoded? encode('quote(address,uint256)','user')
# gives only address; need address+0 -> build manually below if needed
out["retry"]["yama_views"] = read_views(YAMA_SALE, yama_views)
out["retry"]["yama_first_mint"] = first_mint_scan(YAMA_SALE, head)

# ---- VEIN sale: raw sourcify + candidate views ----
VEIN_SALE = "0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6"
try:
    o = subprocess.run(["curl", "-sL", "--max-time", "25",
                        f"https://sourcify.dev/server/v2/contract/56/{VEIN_SALE}"],
                       capture_output=True, text=True)
    out["retry"]["vein_sale_sourcify_raw_head"] = o.stdout[:400]
except Exception as e:
    out["retry"]["vein_sale_sourcify_raw_head"] = f"ERR {e}"
vein_sale_views = {
    "freeClaimed": ("freeClaimed()", None),
    "freeMinted": ("freeMinted()", None),
    "FREE_SUPPLY": ("FREE_SUPPLY()", None),
    "totalFreeShares": ("totalFreeShares()", None),
    "freeSharesRemaining": ("freeSharesRemaining()", None),
    "MAX_FREE_SHARES": ("MAX_FREE_SHARES()", None),
    "totalShares": ("totalShares()", None),
    "sharesOf_user": ("sharesOf(address)", "user"),
    "claimed_user": ("claimed(address)", "user"),
    "freeClaimedBy_user": ("freeClaimedBy(address)", "user"),
    "agentRegistry": ("agentRegistry()", None),
    "owner": ("owner()", None),
}
out["retry"]["vein_sale_views"] = read_views(VEIN_SALE, vein_sale_views)
out["retry"]["vein_first_mint"] = first_mint_scan(VEIN_SALE, head)

# ---- site gate grep: does the site print the exact contracts? ----
out["retry"]["site_gates"] = {
    "pocket": site_grep("https://pocket.agenticwallet.workers.dev/",
                        ["0xf9D00B7a2992de00EBc5F9f04BAf95d44C542102",
                         "0x7D72D6D06d1240F927039fB364e1B55bd4473d80"]),
    "yama": site_grep("https://yamaproject.pages.dev/",
                      ["0x86D779fc4d83044cCECCb53639f9a98E367D6E46",
                       "0xa84EA20a667B3b1859aB9a9984FF5F03D8688aE2"]),
    "vein": site_grep("https://agent-miner-vein.vercel.app/skill.md",
                      ["0x17ccdcd9763e824a59c78f60c10e6976d5663479",
                       "0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6"]),
    "vein_site": site_grep("https://agent-miner-vein.vercel.app/",
                           ["0x17ccdcd9763e824a59c78f60c10e6976d5663479",
                            "0x869d0edf28cc79b16c1b6f8fb3b399edcbe539f6"]),
}

# block timestamps for any first-mint blocks found
for k in ("pocket_first_mint", "yama_first_mint", "vein_first_mint"):
    r = out["retry"].get(k, {})
    if isinstance(r, dict) and r.get("first_block"):
        out["retry"][k + "_ts"] = block_ts(r["first_block"])

json.dump(out, open(BASE + f"run-{RUN}-verify-new-b.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:9000])
print("HEAD", head)
