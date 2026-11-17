#!/usr/bin/env python3
"""Run 2026-11-08 20:31 WIB: fresh re-verify 3 PENDING-REPORT items (HELIX, Pokechain, BAHUANG2).
Single eth_call per view (batch-revert safe). Read-only; writes only its own JSON.
None = UNVERIFIED (revert/RPC artifact), never zero."""
import json, sys, time, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u256(n): return "%064x" % n
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=10, retries=0)
            if isinstance(out, dict) and "result" in out:
                return out["result"]
            if isinstance(out, dict) and "error" in out:
                return None
        except Exception:
            continue
    return None

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

def quote_raw(addr):
    h = call(addr, sel("quote(address,uint256)") + enc_addr(USER) + enc_u256(1))
    if not h or h == "0x": return {"raw": None, "words": None}
    try:
        b = bytes.fromhex(h[2:])
        words = [int.from_bytes(b[i:i+32], "big") for i in range(0, min(len(b), 128), 32)]
        return {"raw": h, "words": words}
    except Exception: return {"raw": h, "words": None}

def read(addr, noargs, uargs):
    r = {"address": addr}
    for sig in noargs:
        r[sig.split("(")[0]] = to_int(call(addr, sel(sig)))
    for sig in uargs:
        r[sig.split("(")[0] + "_user"] = to_int(call(addr, sel(sig) + enc_addr(USER)))
    return r

discards = json.load(open(BASE + "/same-owner-discards.json"))
disc_owners = {str(d.get("owner", "")).lower() for d in discards if isinstance(d, dict)}

out = {"started_wib": "2026-11-08 20:31 WIB"}

# HELIX
h = read("0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665",
         ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()", "FREE_SUPPLY()",
          "MAX_SUPPLY()", "mintActive()", "mintOpen()", "publicRemaining()", "totalPaidMinted()",
          "PRICE()", "agentRegistry()", "requireAgentId()"],
         ["freeUsed(address)", "freeClaimed(address)", "balanceOf(address)", "mintedBy(address)",
          "hasAgentId(address)"])
# hasAgentId takes address arg; the uarg loop above already called it with USER
h["owner"] = dec_addr(call("0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665", sel("owner()")))
h["owner_in_discards"] = (h["owner"] or "").lower() in disc_owners if h["owner"] else None
h["quote_user_1"] = quote_raw("0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665")
uri = dec_str(call("0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665", sel("contractURI()")))
h["contractURI_raw"] = uri
if uri and uri.startswith("data:application/json;base64,"):
    try: h["contractURI_json"] = json.loads(base64.b64decode(uri.split(",", 1)[1]).decode())
    except Exception as e: h["contractURI_json"] = {"decode_error": str(e)[:100]}
out["HELIX"] = h
print("HELIX", json.dumps(h), flush=True)

# Pokechain
p = read("0x4EF929aF00cB93993c3D01834C4DA79200d31e32",
         ["totalSupply()", "totalMinted()", "MAX_SUPPLY()", "mintOpen()", "PRICE()",
          "freeMinted()", "freeClaimed()", "FREE_SUPPLY()", "mintPrice()"],
         ["balanceOf(address)", "freeClaimed(address)", "mintedBy(address)"])
p["owner"] = dec_addr(call("0x4EF929aF00cB93993c3D01834C4DA79200d31e32", sel("owner()")))
p["owner_in_discards"] = (p["owner"] or "").lower() in disc_owners if p["owner"] else None
p["quote_user_1"] = quote_raw("0x4EF929aF00cB93993c3D01834C4DA79200d31e32")
uri = dec_str(call("0x4EF929aF00cB93993c3D01834C4DA79200d31e32", sel("contractURI()")))
p["contractURI_raw"] = uri
if uri and uri.startswith("data:application/json;base64,"):
    try: p["contractURI_json"] = json.loads(base64.b64decode(uri.split(",", 1)[1]).decode())
    except Exception as e: p["contractURI_json"] = {"decode_error": str(e)[:100]}
# tokenURI(0) for metadata website/X claim
turi = dec_str(call("0x4EF929aF00cB93993c3D01834C4DA79200d31e32",
                    sel("tokenURI(uint256)") + enc_u256(0)))
p["tokenURI_0_raw"] = (turi or "")[:500]
out["Pokechain"] = p
print("Pokechain", json.dumps(p), flush=True)

# BAHUANG2
b = read("0x57CC350b844484Eac0DE444526d295C90F9cCbB5",
         ["totalMinted()", "totalSupply()", "freeMinted()", "FREE_CAP()", "FREE_PER_WALLET()",
          "MAX_SUPPLY()", "mintStart()", "mintOpen()", "PRICE()"],
         ["freeCount(address)", "freeClaimed(address)", "balanceOf(address)", "mintedBy(address)"])
b["owner"] = dec_addr(call("0x57CC350b844484Eac0DE444526d295C90F9cCbB5", sel("owner()")))
b["owner_in_discards"] = (b["owner"] or "").lower() in disc_owners if b["owner"] else None
b["quote_user_1"] = quote_raw("0x57CC350b844484Eac0DE444526d295C90F9cCbB5")
if b.get("freeMinted") is not None and b.get("FREE_CAP"):
    b["freePct"] = round(100.0 * b["freeMinted"] / b["FREE_CAP"], 2)
out["BAHUANG2"] = b
print("BAHUANG2", json.dumps(b), flush=True)

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "/run-2026-11-08-2031-pending-verify.json", "w"), indent=1)
print(f"DONE in {out['elapsed_s']}s", flush=True)
