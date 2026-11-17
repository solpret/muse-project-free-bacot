#!/usr/bin/env python3
"""Web-leg triage run 2026-11-15 13:01 WIB: Sourcify shape-check (5 new) + Boltbook new-address on-chain triage. Read-only."""
import json, urllib.request, concurrent.futures
from Crypto.Hash import keccak

RPC = "https://bsc-dataseed.binance.org/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]

def post(payload):
    req = urllib.request.Request(RPC, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def batch_call(calls):
    """calls: list of (label, addr, data). Returns {label: result-hex or None}.
    bsc-dataseed rejects batches >~25 calls: chunk to 15."""
    out = {}
    for start in range(0, len(calls), 15):
        chunk = calls[start:start+15]
        payload = [{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                    "params": [{"to": a, "data": d}, "latest"]} for i, (_, a, d) in enumerate(chunk)]
        try:
            res = post(payload)
        except Exception as e:
            out["_error"] = str(e)
            continue
        if isinstance(res, dict):
            out["_error"] = f"non-list response: {str(res)[:200]}"
            continue
        for pos, item in enumerate(res):
            i = item.get("id")
            if i is None:
                i = pos
            label = chunk[i][0]
            if "error" in item: out[label] = None
            else: out[label] = item.get("result")
    return out

def dec(h):
    if not h: return None
    try: return int(h, 16)
    except Exception: return None

def dec_str(h):
    # decode abi string return
    if not h or len(h) < 130: return None
    try:
        b = bytes.fromhex(h[2:])
        off = int.from_bytes(b[0:32], "big"); ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode(errors="ignore")
    except Exception: return None

def get_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "free-mint-search/1301"})
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read().decode()).get("abi", [])
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {str(e)[:120]}"}

FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]

# ---------- 1. Sourcify shape-check: 5 new vs 1231 ----------
SRC_NEW = ["0x8748f1b35b2e154033bc058f48d973d2beb8ed85",
           "0xe228070b0b7a0a408ee7eff00a9d38b243a81ced",
           "0x757f9fea333a70311b1773807df7b618a8f4e076",
           "0x409967357bfcbbb690281a7c02ed719125fb9b88",
           "0xc25d8398d953cc9dc05af788ecd0b3cc9d9cfaf0"]
FEED = json.load(open("run-2026-11-15-1301-sourcify.json"))
VA = {it["address"].lower(): it.get("verifiedAt") for it in FEED.get("results", FEED)}

def shape(addr):
    abi = get_abi(addr)
    if isinstance(abi, dict):
        return {"address": addr, "verifiedAt": VA.get(addr.lower()), "error": abi["_error"]}
    names = {e["name"] for e in abi if e.get("type") == "function"}
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate"})
    is_token = bool(names & {"name","symbol","decimals","totalSupply"})
    s1 = has_mint and has_quote and bool(free_views) and agent_ref
    s2 = is_token and ("mintFree" in names) and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
    return {"address": addr, "verifiedAt": VA.get(addr.lower()), "fns": len(names),
            "fn_names": sorted(names), "mint": has_mint, "quote": has_quote,
            "free_views": free_views, "agent": agent_ref, "is_token": is_token,
            "sale_shape_S1": s1, "sale_shape_S2": s2, "agent_shaped": bool(has_mint and agent_ref)}

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
    shapes = list(ex.map(shape, SRC_NEW))
json.dump(shapes, open("run-2026-11-15-1301-shape.json", "w"), indent=1)
for s in shapes:
    print(json.dumps({k: s.get(k) for k in ("address","verifiedAt","fns","mint","quote","free_views","agent","sale_shape_S1","sale_shape_S2","agent_shaped","error")}))

# ---------- 2. Boltbook triage ----------
CANDS = {
    "PICK": "0x2296367f74b2ec266cf4667d98501ae7110f5a58",
    "GearMachine": "0x391a13af7819e36a84f16754c133ca39d08d273d",
    "AZEN": "0x699b6397986cc6c444069efe692023b1253dc26d",
    "KIJIN_Claim": "0x94534656fc286e86c6a04a1fc19724e4da6264ed",
    "KIJIN_Token": "0xad758224f7674976cbce6b9bd7ba7358503a7599",
    "ACORE": "0xf4bacf30fb8f69373f63d99c657f53dd7774af1d",
}
USER_PAD = USER[2:].lower().rjust(64, "0")

def triage(name, addr):
    abi = get_abi(addr)
    fn_names = []
    if isinstance(abi, list):
        fn_names = [e["name"] for e in abi if e.get("type") == "function"]
    # generic view calls
    calls = []
    def add(label, sig, arg=""):
        calls.append((label, addr, sel(sig) + arg))
    add("name", "name()"); add("symbol", "symbol()")
    add("totalSupply", "totalSupply()"); add("totalMinted", "totalMinted()")
    add("MAX_SUPPLY", "MAX_SUPPLY()"); add("FREE_SUPPLY", "FREE_SUPPLY()"); add("FREE_SLOTS", "FREE_SLOTS()")
    add("freeMinted", "freeMinted()"); add("freeClaimed", "freeClaimed()"); add("freeLeft", "freeLeft()")
    add("freeSupply", "freeSupply()"); add("freeRemaining", "freeRemaining()")
    add("mintOpen", "mintOpen()"); add("mintOpensAt", "mintOpensAt()"); add("mintStart", "mintStart()")
    add("mintOpens", "mintOpens()"); add("mintStartTime", "mintStartTime()"); add("startTime", "startTime()")
    add("agentRegistry", "agentRegistry()"); add("agentIdRegistry", "agentIdRegistry()")
    add("holdsAgentId_user", "holdsAgentId(address)", USER_PAD)
    add("freeClaimed_user", "freeClaimed(address)", USER_PAD)
    add("freeMintedBy_user", "freeMintedBy(address)", USER_PAD)
    add("mintsRemainingFor_user", "mintsRemainingFor(address)", USER_PAD)
    add("mintsBy_user", "mintsBy(address)", USER_PAD)
    add("price", "price()"); add("currentMintPriceWei", "currentMintPriceWei()")
    add("mintPrice", "mintPrice()"); add("priceFor_user1", "priceFor(address,uint256)", USER_PAD + "0000000000000000000000000000000000000000000000000000000000000001")
    add("quote_user1", "quote(address,uint256)", USER_PAD + "0000000000000000000000000000000000000000000000000000000000000001")
    add("balanceOf_user", "balanceOf(address)", USER_PAD)
    res = batch_call(calls)
    # code check
    try:
        code = post({"jsonrpc": "2.0", "id": 0, "method": "eth_getCode", "params": [addr, "latest"]}).get("result", "")
    except Exception as e:
        code = f"ERR {e}"
    out = {"name": name, "address": addr, "code_len": (len(code) - 2) // 2 if code and code.startswith("0x") else code,
           "abi_fns": len(fn_names), "fn_names": sorted(set(fn_names))}
    for label in ["name", "symbol"]:
        out[label] = dec_str(res.get(label))
    for label in ["totalSupply", "totalMinted", "MAX_SUPPLY", "FREE_SUPPLY", "FREE_SLOTS",
                  "freeMinted", "freeClaimed", "freeLeft", "freeSupply", "freeRemaining",
                  "mintOpensAt", "mintStart", "mintOpens", "mintStartTime", "startTime",
                  "holdsAgentId_user", "freeClaimed_user", "freeMintedBy_user",
                  "mintsRemainingFor_user", "mintsBy_user", "price", "currentMintPriceWei",
                  "mintPrice", "priceFor_user1", "quote_user1", "balanceOf_user"]:
        v = dec(res.get(label))
        if v is not None: out[label] = v
    for label in ["mintOpen", "agentRegistry", "agentIdRegistry"]:
        v = res.get(label)
        if v: out[label] = v
    return out

results = {}
for name, addr in CANDS.items():
    results[name] = triage(name, addr)
    print(json.dumps(results[name], indent=1))
json.dump(results, open("run-2026-11-15-1301-triage.json", "w"), indent=1)

# sweeper EOA check
try:
    code = post({"jsonrpc": "2.0", "id": 0, "method": "eth_getCode",
                 "params": ["0xdba68827e6a71aebca686f1e31baff86cbe033f5", "latest"]}).get("result", "")
    print("sweeper 0xdba6... code:", code)
except Exception as e:
    print("sweeper code check err:", e)
