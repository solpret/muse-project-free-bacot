#!/usr/bin/env python3
"""Hot-leg 0929 leg-3: verify 3 new S1 sale-shape contracts on-chain (read-only).
Reads free-pool views, user slot (quote/freeUsed), names, and first-mint age
via Ankr ankr_getLogs (Transfer from zero address). Writes s1-verify-0929.json."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from ankr import ankr_post
from fast_rpc import _single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed1.defibit.io/", "https://bsc.publicnode.com/",
       "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed.binance.org"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO_TOPIC = "0x" + "00" * 32

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def call(to, data):
    last = None
    for ep in EPS:
        try:
            v = _single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if isinstance(v, str) and v.startswith("0x"):
                return v
            last = v
        except Exception as e:
            last = f"err:{type(e).__name__}"
    return last

def dec_uint(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 66:
        try: return int(v[-64:], 16)
        except Exception: return v
    return v

def dec_str(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) > 130:
        try:
            ln = int(v[130:194], 16)
            raw = bytes.fromhex(v[194:194 + ln * 2])
            return raw.decode("utf-8", errors="ignore")
        except Exception: return v
    return v

def dec_bool(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 66:
        try: return int(v[-64:], 16) != 0
        except Exception: return v
    return v

def dec_addr(v):
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 66:
        return "0x" + v[-40:]
    return v

USER_PAD = "0x" + "0" * 24 + USER[2:].lower()
Q1 = USER_PAD[2:] + format(1, "064x")

def views(addr, spec):
    out = {}
    for name, sig, dec in spec:
        v = call(addr, sel(sig))
        try: out[name] = dec(v)
        except Exception: out[name] = v
    return out

def block_ts(n):
    for ep in EPS:
        try:
            b = _single(ep, "eth_getBlockByNumber", [hex(n), False], 8, retries=0)
            if isinstance(b, dict) and b.get("timestamp"):
                return int(b["timestamp"], 16)
        except Exception:
            continue
    return None

def head_block():
    for ep in EPS:
        try:
            v = _single(ep, "eth_blockNumber", [], 8, retries=0)
            if isinstance(v, str) and v.startswith("0x"):
                return int(v, 16)
        except Exception:
            continue
    return None

def first_mint(addr, head):
    frm = max(0, head - 300000)
    logs, page_token, pages = [], None, 0
    while True:
        p = {"blockchain": "bsc", "fromBlock": hex(frm), "toBlock": hex(head),
             "address": addr, "topics": [TRANSFER, ZERO_TOPIC],
             "pageSize": 1000, "decodeLogs": False}
        if page_token: p["pageToken"] = page_token
        try:
            body = ankr_post("ankr_getLogs", p, timeout=30)
        except Exception as e:
            return {"error": f"ankr:{type(e).__name__}:{e}", "range": [frm, head], "logs": len(logs)}
        res = body.get("result", {}) if isinstance(body, dict) else {}
        logs.extend(res.get("logs", []))
        page_token = res.get("pageToken")
        pages += 1
        if not page_token or pages >= 10:
            break
        time.sleep(1.0)
    blocks = sorted({int(l["blockNumber"], 16) for l in logs if l.get("blockNumber")})
    out = {"range": [frm, head], "mint_logs": len(logs), "distinct_blocks": len(blocks),
           "pages": pages, "earliest_block": blocks[0] if blocks else None,
           "latest_block": blocks[-1] if blocks else None,
           "at_range_start": bool(blocks) and blocks[0] == frm}
    if blocks:
        ts = block_ts(blocks[0])
        out["earliest_ts"] = ts
        if ts:
            import datetime
            out["earliest_wib"] = datetime.datetime.fromtimestamp(
                ts, datetime.timezone(datetime.timedelta(hours=7))).isoformat(timespec="seconds")
    return out

head = head_block()
out = {"run": "2026-11-07-0929-leg3", "head_block": head}
print("head:", head, flush=True)

SHARE_SPEC = [
    ("name", "name()", dec_str), ("symbol", "symbol()", dec_str),
    ("decimals", "decimals()", dec_uint),
    ("MAX_SHARES", "MAX_SHARES()", dec_uint), ("sharesSold", "sharesSold()", dec_uint),
    ("FREE_PER_AGENT", "FREE_PER_AGENT()", dec_uint),
    ("AGENT_PRICE_PER_SHARE", "AGENT_PRICE_PER_SHARE()", dec_uint),
    ("PRICE_PER_SHARE", "PRICE_PER_SHARE()", dec_uint),
    ("TOKENS_PER_SHARE", "TOKENS_PER_SHARE()", dec_uint),
    ("MAX_PER_WALLET", "MAX_PER_WALLET()", dec_uint),
    ("MAX_PER_TX", "MAX_PER_TX()", dec_uint),
    ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", dec_addr),
    ("treasury", "treasury()", dec_addr),
    ("freeUsed_user", "freeUsed(address)", dec_uint),
    ("mintedBy_user", "mintedBy(address)", dec_uint),
    ("balanceOf_user", "balanceOf(address)", dec_uint),
    ("isAgent_user", "isAgent(address)", dec_bool),
]
NFT_SPEC = [
    ("name", "name()", dec_str), ("symbol", "symbol()", dec_str),
    ("FREE_SUPPLY", "FREE_SUPPLY()", dec_uint), ("freeMinted", "freeMinted()", dec_uint),
    ("MAX_SUPPLY", "MAX_SUPPLY()", dec_uint), ("PAID_SUPPLY", "PAID_SUPPLY()", dec_uint),
    ("paidMinted", "paidMinted()", dec_uint), ("totalMinted", "totalMinted()", dec_uint),
    ("price", "price()", dec_uint), ("paused", "paused()", dec_bool),
    ("passSigner", "passSigner()", dec_addr),
    ("MAX_PER_WALLET", "MAX_PER_WALLET()", dec_uint),
    ("AGENT_REGISTRY", "AGENT_REGISTRY()", dec_addr),
    ("mintedBy_user", "mintedBy(address)", dec_uint),
    ("balanceOf_user", "balanceOf(address)", dec_uint),
]

def quote1(addr):
    v = call(addr, sel("quote(address,uint256)") + Q1)
    if isinstance(v, str) and v.startswith("0x") and len(v) >= 130:
        try: return [int(v[2:66], 16), int(v[66:130], 16)]
        except Exception: return v
    return v

targets = [
    ("GlorpixAgent", "0xba5cde0ceea8704b8944deb51228ca59a7bd9cf0", SHARE_SPEC, True),
    ("PlonkraAgent", "0xec266bdd979b19d8a2f1266ef0610b4791dbd24b", SHARE_SPEC, True),
    ("PunkApeNFT", "0xbac6b6de36a54b2815c02ad3cc5e6551e306aa90", NFT_SPEC, False),
]
for label, addr, spec, is_share in targets:
    d = {"address": addr}
    vs = views(addr, spec)
    # user-address views need the padded arg appended
    for nm in ("freeUsed_user", "mintedBy_user", "balanceOf_user", "isAgent_user"):
        sig = {"freeUsed_user": "freeUsed(address)", "mintedBy_user": "mintedBy(address)",
               "balanceOf_user": "balanceOf(address)", "isAgent_user": "isAgent(address)"}[nm]
        if nm in vs:
            dec = {"freeUsed_user": dec_uint, "mintedBy_user": dec_uint,
                   "balanceOf_user": dec_uint, "isAgent_user": dec_bool}[nm]
            vs[nm] = dec(call(addr, sel(sig) + USER_PAD[2:]))
    d["views"] = vs
    if is_share:
        d["quote_user_1"] = quote1(addr)
    else:
        # tokenURI(1) if any minted; tokenURI(0) fallback
        for tid in (1, 0):
            v = call(addr, sel("tokenURI(uint256)") + format(tid, "064x"))
            t = dec_str(v)
            d[f"tokenURI_{tid}"] = t
            if isinstance(t, str) and t.startswith(("http", "ipfs", "data:")):
                break
    if head:
        d["first_mint"] = first_mint(addr, head)
    out[label] = d
    print(label, json.dumps(d, default=str)[:1500], flush=True)

json.dump(out, open(f"{BASE}/s1-verify-0929.json", "w"), indent=1)
print("DONE", flush=True)
