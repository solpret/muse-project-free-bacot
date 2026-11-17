#!/usr/bin/env python3
"""Read-only verification of track-C contract 0xc43f7Ab11728FC884662B35AD974ff703cb4221d
for free-mint-search run 2026-11-13 20:31 WIB. No preview/mint/execution.
Batch eth_call via public BSC dataseeds. Writes run-2026-11-13-2031-c43f-verify.json."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0xc43f7Ab11728FC884662B35AD974ff703cb4221d"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed1.defibit.io/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def batch(calls):
    """calls: list of (key, data). Returns dict key->int|addr-hex|None, plus raw errors."""
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": ADDR, "data": d}, "latest"]} for i, (_, d) in enumerate(calls)]
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for (key, _), it in zip(calls, res):
                if not isinstance(it, dict) or "error" in it:
                    out[key] = {"value": None, "error": str(it.get("error"))[:120] if isinstance(it, dict) else "bad-response"}
                else:
                    r = it.get("result")
                    out[key] = {"value": to_int(r), "raw": r}
            return out, ep
        except Exception as e:
            continue
    return None, None

def raw_string(sig, args_hex=""):
    data = sel(sig) + args_hex
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": ADDR, "data": data}, "latest"]}, timeout=25)
            r = res.get("result") if isinstance(res, dict) else None
            if not r or r == "0x":
                return None
            b = bytes.fromhex(r[2:])
            if len(b) >= 64:
                off = int.from_bytes(b[:32], "big")
                ln = int.from_bytes(b[32:64], "big")
                if 0 < ln < 10000 and off + 32 + ln <= len(b):
                    try:
                        return b[32 + off:32 + off + ln].decode("utf-8", errors="replace")
                    except Exception:
                        pass
            try:
                return b.decode("utf-8", errors="replace").strip("\x00")
            except Exception:
                return r[:200]
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16), ep
        except Exception:
            continue
    return None, None

block, block_ep = get_block()
print("HEAD BLOCK", block, "via", block_ep, flush=True)

# --- string views ---
strings = {}
for sig in ["name()", "symbol()", "contractURI()", "tokenURI(uint256)"]:
    args = enc_u(0) if "uint256" in sig else ""
    strings[sig] = raw_string(sig, args)
    print(sig, "->", str(strings[sig])[:200], flush=True)
# tokenURI(1) too
strings["tokenURI(1)"] = raw_string("tokenURI(uint256)", enc_u(1))
print("tokenURI(1) ->", str(strings["tokenURI(1)"])[:200], flush=True)

# --- address views (decode as address from raw) ---
addr_views = ["token()", "saleToken()", "shareToken()", "agentRegistry()", "registry()",
              "agentId()", "owner()", "treasury()", "paymentToken()", "usdt()", "USDT()"]
addr_calls = [(s, sel(s)) for s in addr_views]
ares, aep = batch(addr_calls)
addrs = {}
for s in addr_views:
    v = ares[s]
    raw = v.get("raw")
    addrs[s] = ("0x" + raw[-40:]) if raw and len(raw) >= 42 and raw != "0x" else None
    print(s, "->", addrs[s], "err:", v.get("error"), flush=True)

# --- int views (no-arg) ---
int_views = ["totalSupply()", "totalMinted()", "freeClaimed()", "freeMinted()", "freeLeft()",
             "FREE_SUPPLY()", "FREE_SHARES()", "MAX_SUPPLY()", "freeSharesRemaining()",
             "freeSharesLeft()", "freeSupply()", "freeCap()", "MAX_FREE()", "freeMax()",
             "totalFreeMinted()", "decimals()", "saleStart()", "mintOpensAt()", "freeStart()",
             "START_TIME()", "startTime()", "saleEnd()", "openedAt()", "launched()",
             "mintOpen()", "saleOpen()", "PRICE()", "price()", "tokensPerShare()",
             "TOKENS_PER_SHARE()", "FREE_AMOUNT()", "freeAmount()", "totalShares()",
             "sharesSold()", "paidMinted()", "totalPaid()", "version()"]
int_calls = [(s, sel(s)) for s in int_views]
ires = {}
for ci in range(0, len(int_calls), 10):
    chunk = int_calls[ci:ci+10]
    cres, cep = batch(chunk)
    if cres is None:
        print("INT CHUNK", ci, "BATCH-FAIL (all endpoints)", flush=True)
        for s, _ in chunk:
            ires[s] = {"value": None, "error": "batch-fail"}
    else:
        ires.update(cres)
    time.sleep(0.5)
ints = {}
for s in int_views:
    v = ires[s]
    ints[s] = v["value"]
    print(s, "->", v["value"], "err:", v.get("error"), flush=True)

# --- address-arg views (user) ---
u_views = ["balanceOf(address)", "freeClaimed(address)", "freeMintedBy(address)",
           "freeUsed(address)", "mintedBy(address)", "freeAvailable(address)",
           "freeLeftFor(address)", "claimed(address)", "hasClaimed(address)",
           "freeFor(address)", "sharesOf(address)", "allowance(address,address)"]
u_calls = [(s + "_user", sel(s) + enc(USER)) for s in u_views]
ures = {}
for ci in range(0, len(u_calls), 10):
    chunk = u_calls[ci:ci+10]
    cres, cep = batch(chunk)
    if cres is None:
        print("USER CHUNK", ci, "BATCH-FAIL", flush=True)
        for k, _ in chunk:
            ures[k] = {"value": None, "error": "batch-fail"}
    else:
        ures.update(cres)
    time.sleep(0.5)
uvals = {}
for s in u_views:
    v = ures[s + "_user"]
    uvals[s] = v["value"]
    print(s, "(user) ->", v["value"], "err:", v.get("error"), flush=True)

# --- quote variants ---
q_calls = [
    ("quote(uint256)_1", sel("quote(uint256)") + enc_u(1)),
    ("quote(address,uint256)_user_1", sel("quote(address,uint256)") + enc(USER) + enc_u(1)),
    ("quote(address)_user", sel("quote(address)") + enc(USER)),
    ("cost(uint256)_1", sel("cost(uint256)") + enc_u(1)),
    ("getQuote(uint256)_1", sel("getQuote(uint256)") + enc_u(1)),
    ("priceFor(address,uint256)_user_1", sel("priceFor(address,uint256)") + enc(USER) + enc_u(1)),
]
qres = {}
for ci in range(0, len(q_calls), 6):
    chunk = q_calls[ci:ci+6]
    cres, cep = batch(chunk)
    if cres is None:
        print("QUOTE CHUNK", ci, "BATCH-FAIL", flush=True)
        for k, _ in chunk:
            qres[k] = {"value": None, "error": "batch-fail"}
    else:
        qres.update(cres)
    time.sleep(0.5)
quotes = {}
for k, _ in q_calls:
    v = qres[k]
    quotes[k] = v
    print(k, "->", v["value"], "raw:", str(v.get("raw"))[:130], "err:", v.get("error"), flush=True)

res = {
    "contract": ADDR,
    "verified_at_wib": "2026-11-13 20:36-20:45 WIB (run 20:31 WIB)",
    "head_block": block,
    "head_block_endpoint": block_ep,
    "user_wallet": USER,
    "registry_expected": REGISTRY,
    "strings": strings,
    "address_views": addrs,
    "int_views": ints,
    "user_views": uvals,
    "quotes": {k: {"value": v["value"], "raw": v.get("raw"), "error": v.get("error")} for k, v in quotes.items()},
    "elapsed_s": round(time.time() - t0, 1),
}
json.dump(res, open(BASE + "run-2026-11-13-2031-c43f-verify.json", "w"), indent=1)
print("ELAPSED", res["elapsed_s"], "written to", BASE + "run-2026-11-13-2031-c43f-verify.json")
