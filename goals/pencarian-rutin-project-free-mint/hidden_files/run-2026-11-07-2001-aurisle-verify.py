#!/usr/bin/env python3
"""AURISLE early-lead parent verification — run 2001. Read-only.
Reads free views / supply / quote / contractURI / tokenURI, single-call
(revert-prone views one at a time); None = read failure, never zero.
No preview / mint / execution."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from Crypto.Hash import keccak
from fast_rpc import race

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AUR = "0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

t0 = time.time()
out = {}
try:
    blk = int(race("eth_blockNumber", []), 16)
except Exception as e:
    blk = None
    print("BLOCK-FAIL", e, flush=True)
out["block"] = blk
out["contract"] = AUR

def read_raw(to, data):
    try:
        return race("eth_call", [{"to": to, "data": data}, "latest"])
    except Exception:
        return None

def read_int(to, data):
    return to_int(read_raw(to, data))

def read_str(to, data):
    raw = read_raw(to, data)
    if raw is None: return None
    try:
        h = raw[2:]
        if len(h) < 128: return raw
        off = int(h[64:128], 16) * 2
        ln = int(h[off:off+64], 16)
        return bytes.fromhex(h[off+64:off+64+ln*2]).decode("utf-8", "replace")
    except Exception:
        return raw

views = {}
for sig in ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()", "freeLeft()",
            "freeSupply()", "FREE_SUPPLY()", "FREE_SLOTS()", "MAX_SUPPLY()", "mintOpen()",
            "mintStartsAt()", "mintEndsAt()", "AGENT_ID()", "owner()"]:
    views[sig] = read_int(AUR, sel(sig))
    print(f"{sig} = {views[sig]}", flush=True)
views["freeClaimed(user)"] = read_int(AUR, sel("freeClaimed(address)") + enc(USER))
views["freeMintedBy(user)"] = read_int(AUR, sel("freeMintedBy(address)") + enc(USER))
views["balanceOf(user)"] = read_int(AUR, sel("balanceOf(address)") + enc(USER))
views["name()"] = read_str(AUR, sel("name()"))
views["symbol()"] = read_str(AUR, sel("symbol()"))
views["contractURI()"] = read_str(AUR, sel("contractURI()"))
views["tokenURI(0)"] = read_str(AUR, sel("tokenURI(uint256)") + enc_u(0))
views["tokenURI(1)"] = read_str(AUR, sel("tokenURI(uint256)") + enc_u(1))
out["views"] = views
print("VIEWS", json.dumps(views, indent=1), flush=True)

# quote attempts: quote(address,uint256,bool) and quote(address,uint256)
for sig in ["quote(address,uint256,bool)", "quote(address,uint256)", "getQuote(address,uint256)"]:
    d = sel(sig) + enc(USER) + enc_u(1)
    if sig.endswith("bool)"):
        d += enc_u(0)
    raw = read_raw(AUR, d)
    print(f"{sig} raw = {raw}", flush=True)
    out[f"quote_{sig}"] = raw

# mint function probe: mint(uint256,uint256,bytes) style not attempted; just record selectors via getCode check done by leg 4
out["elapsed_s"] = round(time.time() - t0, 2)
json.dump(out, open(f"{BASE}/run-2026-11-07-2001-aurisle-verify.json", "w"), indent=1)
print(f"AURISLE VERIFY DONE in {time.time()-t0:.1f}s, block {blk}", flush=True)
