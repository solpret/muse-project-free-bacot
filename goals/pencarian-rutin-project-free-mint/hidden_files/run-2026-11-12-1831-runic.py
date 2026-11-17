#!/usr/bin/env python3
"""Free-mint-search run 2026-11-12 18:31 WIB — RunicKey fresh re-read + gate methods (H)/(I)/(E).
Read-only; writes run-2026-11-12-1831-runic.json. No preview/mint.
RunicKey 0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4 — strong-lead check:
hot-leg refresh 18:32 WIB read freeMinted 257/325 = 79.1% (>70%); this run
re-verifies all three strong-lead legs fresh before any gate/execution step."""
import json, subprocess, time, base64
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
ADDR = "0x0ec2c86B8E79c9A664b1ae0D6E3cB06B58ecCFe4"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def batch(calls):
    """calls: list of (key, data). Returns dict key->int|None (raw for strings handled separately)."""
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": ADDR, "data": d}, "latest"]} for i, (_, d) in enumerate(calls)]
    for ep in EPS:
        try:
            res = post_rpc(ep, payload, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for (key, _), it in zip(calls, res):
                if isinstance(it, dict) and "error" in it:
                    out[key] = None
                elif isinstance(it, dict):
                    out[key] = to_int(it.get("result"))
                else:
                    out[key] = None
            return out, ep
        except Exception:
            continue
    return {k: None for k, _ in calls}, None

def raw_string(data):
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
                if 0 < ln < 20000 and off + 32 + ln <= len(b):
                    return b[32 + off:32 + off + ln].decode("utf-8", errors="replace")
            return b.decode("utf-8", errors="replace").strip("\x00")
        except Exception:
            continue
    return None

def raw_addr(data):
    """eth_call returning address."""
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": ADDR, "data": data}, "latest"]}, timeout=25)
            r = res.get("result") if isinstance(res, dict) else None
            if not r or r == "0x":
                return None
            return "0x" + r[-40:]
        except Exception:
            continue
    return None

def get_block():
    for ep in EPS:
        try:
            res = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(res, dict) and res.get("result"):
                return to_int(res["result"])
        except Exception:
            continue
    return None

# ABI signatures for cost/quote views (from cached Sourcify ABI)
abi = json.load(open(BASE + "hot-leg-2026-11-12-1814-runic-abi.json"))["abi"]
sigs = {}
for f in abi:
    if f.get("type") == "function" and f.get("name") in (
            "costOf", "costOfMint", "quote", "quoteMint", "mintCost", "freeAvailable",
            "canMintFor", "remainingQuota", "cost"):
        sigs[f["name"]] = f["name"] + "(" + ",".join(i["type"] for i in f.get("inputs", [])) + ")"

views = [
    ("totalSupply", sel("totalSupply()")),
    ("totalMinted", sel("totalMinted()")),
    ("freeMinted", sel("freeMinted()")),
    ("FREE_SUPPLY", sel("FREE_SUPPLY()")),
    ("MAX_SUPPLY", sel("MAX_SUPPLY()")),
    ("freeRemaining", sel("freeRemaining()")),
    ("mintOpen", sel("mintOpen()")),
    ("isFreeOpen", sel("isFreeOpen()")),
    ("saleStart", sel("saleStart()")),
    ("saleEnd", sel("saleEnd()")),
    ("balanceOf_user", sel("balanceOf(address)") + enc(USER)),
    ("freeAvailable_user", sel("freeAvailable(address)") + enc(USER)),
    ("freeMintedBy_user", sel("freeMintedBy(address)") + enc(USER)),
    ("mintedBy_user", sel("mintedBy(address)") + enc(USER)),
    ("FREE_MODE", sel("FREE_MODE()")),
    ("PRICE", sel("PRICE()")),
    ("paidMinted", sel("paidMinted()")),
]
# cost/quote for 1 free mint if signature known
cost_key = None
for name in ("costOfMint", "costOf", "quoteMint", "quote", "mintCost"):
    if name in sigs:
        s = sigs[name]
        if s.endswith("(uint256)"):
            views.append((name + "_1", sel(s) + enc_u(1))); cost_key = name + "_1"
        elif s.endswith("(address,uint256)"):
            views.append((name + "_user1", sel(s) + enc(USER) + enc_u(1))); cost_key = name + "_user1"
        break

res, ep = batch(views)
block = get_block()

# Method (H): contractURI
contract_uri = raw_string(sel("contractURI()"))
# Method (I): tokenURI(1) — token 1 exists (257 minted)
token_uri = raw_string(sel("tokenURI(uint256)") + enc_u(1))
# Method (E): owner()
owner = raw_addr(sel("owner()"))
# agentIdRegistry
registry = raw_addr(sel("agentIdRegistry()"))

def decode_uri(u):
    if not u:
        return None
    if u.startswith("data:application/json;base64,"):
        try:
            return json.loads(base64.b64decode(u.split(",", 1)[1]).decode("utf-8"))
        except Exception as e:
            return {"decode_error": str(e)}
    return {"raw": u[:500]}

out = {
    "run": "free-mint-search 2026-11-12 18:31 WIB",
    "at_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime()),
    "block": block,
    "endpoint": ep,
    "elapsed_s": round(time.time() - t0, 1),
    "address": ADDR,
    "views": res,
    "cost_key": cost_key,
    "cost_sigs": sigs,
    "contractURI_raw": (contract_uri or "")[:800],
    "contractURI_decoded": decode_uri(contract_uri),
    "tokenURI_raw": (token_uri or "")[:800],
    "tokenURI_decoded": decode_uri(token_uri),
    "owner": owner,
    "agentIdRegistry": registry,
}
free = res.get("freeMinted")
cap = res.get("FREE_SUPPLY")
out["freePct"] = (round(100.0 * free / cap, 2) if free is not None and cap else None)
out["strong_lead_legs"] = {
    "age_verified_lt24h": res.get("saleStart") == 1794481219,
    "freePct_gt70": (out["freePct"] is not None and out["freePct"] > 70),
    "slot_open": (res.get("freeAvailable_user") in (1, True) and res.get("balanceOf_user") == 0),
}
json.dump(out, open(BASE + "run-2026-11-12-1831-runic.json", "w"), indent=1)
print(json.dumps(out, indent=1))
