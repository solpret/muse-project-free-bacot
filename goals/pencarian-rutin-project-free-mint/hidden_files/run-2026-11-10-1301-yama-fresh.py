#!/usr/bin/env python3
"""Run 1301 YAMA fresh execution reads (read-only).
quote(user,1), freeUsed(user), sharesOf(user), sharesBought(user),
totalFreeShares/totalPaidShares/totalShares, MAX_SHARES, TOKENS_PER_SHARE,
PRICE, liquidityTargetReached, agentIdRegistry, devWallet/treasury/vault,
token balanceOf(user) before. Owner/devWallet/treasury/vault vs discards.
Writes run-2026-11-10-1301-yama-fresh.json."""
import json, subprocess
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SALE = "0x86d779fc4d83044cceccb53639f9a98e367d6e46"
TOKEN = "0xa84ea20a667b3b1859ab9a9984ff5f03d8688ae2"
ZERO = "0x0000000000000000000000000000000000000000"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
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

def call(addr, data, timeout=25):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout)
            if isinstance(r, dict) and "result" in r:
                return r["result"]
        except Exception:
            continue
    return None

def call_u(addr, sig):
    return to_int(call(addr, sel(sig)))
def call_addr(addr, sig):
    v = call(addr, sel(sig))
    return ("0x" + v[-40:]) if v and len(v) >= 42 else v
def call_bool(addr, sig):
    v = call(addr, sel(sig))
    return bool(to_int(v)) if v is not None else None

out = {}
# quote(user,1) -> (freeShares, costBnb)
q = call(SALE, sel("quote(address,uint256)") + enc_addr(USER) + enc_u(1))
if q and len(q) >= 130:
    out["quote_freeShares"] = int(q[2:66], 16)
    out["quote_costBnb"] = int(q[66:130], 16)
else:
    out["quote_raw"] = q
out["freeUsed_user"] = call_bool(SALE, "freeUsed(address)") if False else to_int(call(SALE, sel("freeUsed(address)") + enc_addr(USER)))
out["freeUsed_user"] = bool(out["freeUsed_user"]) if out["freeUsed_user"] is not None else None
out["sharesOf_user"] = to_int(call(SALE, sel("sharesOf(address)") + enc_addr(USER)))
out["sharesBought_user"] = to_int(call(SALE, sel("sharesBought(address)") + enc_addr(USER)))
out["quotaOf_user"] = to_int(call(SALE, sel("quotaOf(address)") + enc_addr(USER)))
out["isAgent_user"] = to_int(call(SALE, sel("isAgent(address)") + enc_addr(USER)))
out["totalFreeShares"] = call_u(SALE, "totalFreeShares()")
out["totalPaidShares"] = call_u(SALE, "totalPaidShares()")
out["totalShares"] = call_u(SALE, "totalShares()")
out["MAX_SHARES"] = call_u(SALE, "MAX_SHARES()")
out["TOKENS_PER_SHARE"] = call_u(SALE, "TOKENS_PER_SHARE()")
out["PRICE"] = call_u(SALE, "PRICE()")
out["liquidityTargetReached"] = call_bool(SALE, "liquidityTargetReached()")
out["agentIdRegistry"] = call_addr(SALE, "agentIdRegistry()")
out["token_from_sale"] = call_addr(SALE, "token()")
out["devWallet"] = call_addr(SALE, "devWallet()")
out["treasury"] = call_addr(SALE, "treasury()")
out["vault"] = call_addr(SALE, "vault()")
out["token_balanceOf_user_before"] = to_int(call(TOKEN, sel("balanceOf(address)") + enc_addr(USER)))
out["token_totalSupply"] = call_u(TOKEN, "totalSupply()")

disc = json.load(open(f"{BASE}/same-owner-discards.json"))
disc_owners = {str(x.get("owner", "")).lower() for x in disc if isinstance(x, dict)}
disc_contracts = {str(x.get("contract", "")).lower() for x in disc if isinstance(x, dict)}
out["discards_check"] = {
    "sale_in_discards": SALE.lower() in disc_contracts,
    "token_in_discards": TOKEN.lower() in disc_contracts,
    "devWallet_in_discards": str(out.get("devWallet") or "").lower() in disc_owners,
    "treasury_in_discards": str(out.get("treasury") or "").lower() in disc_owners,
    "vault_in_discards": str(out.get("vault") or "").lower() in disc_owners,
}
print(json.dumps(out, indent=1))
json.dump(out, open(f"{BASE}/run-2026-11-10-1301-yama-fresh.json", "w"), indent=1)
