#!/usr/bin/env python3
"""Retry for free-mint-search run 2026-11-13 23:31 WIB (8 transport FAILs).
Fresh re-read of the active watchlist (same set as run 20:31 + BUILD, Moon, Zora, D8DA, Cinder Agents, PIXELPHARAOH, Ponke, Early5877; minus Agentx (age-excluded) and GoldVein (sold out)).
Read-only; writes run-2026-11-13-2331-retry.json. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d

def raw_batch(addr, views):
    """views: list of (key, sig, args). Returns dict key->int|raw|None."""
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception:
            continue
    return None

def block_number():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=15)
            if isinstance(r, dict) and r.get("result"):
                return int(r["result"], 16)
        except Exception:
            continue
    return None

U = [USER]
ITEMS = {
 "Ochre": ("0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("freeRemaining","freeRemaining()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("FREE_PER_WALLET","FREE_PER_WALLET()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("saleStart","saleStart()",[]),
    ("saleOpen","saleOpen()",[]),("mintOpen","mintOpen()",[]),("isFreeOpen","isFreeOpen()",[]),
    ("balanceOf_user","balanceOf(address)",U)]),
 "LNFT": ("0xb2ac84b0d2c9684436f2cf2dc7dfc8e80be78657", [
    ("totalSupply","totalSupply()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("MAX_FREE_PER_WALLET","MAX_FREE_PER_WALLET()",[]),("MAX_PER_WALLET","MAX_PER_WALLET()",[]),
    ("TOKENS_PER_FREE_MINT","TOKENS_PER_FREE_MINT()",[]),("TOKENS_PER_MINT","TOKENS_PER_MINT()",[]),
    ("TOKEN_PRICE","TOKEN_PRICE()",[]),("freeMintedPerWallet_user","freeMintedPerWallet(address)",U),
    ("mintedPerWallet_user","mintedPerWallet(address)",U),("balanceOf_user","balanceOf(address)",U),
    ("pixelReserve","pixelReserve()",[]),("AGENT_ID","AGENT_ID()",[])]),
 "CDD8": ("0xcdd887ff20114601ebf8905cf5dd91572d3214a6", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("saleOpen","saleOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Mihao": ("0xea4ef9da567f59ea7b5f5b7e08305f4e613bab73", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("saleOpen","saleOpen()",[]),
    ("freeAvailable_user","freeAvailable(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Kitebots": ("0x8B8e59c014eb3E229e043AE8F3B0D7E201d21DB0", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "PIXELPHARAOH": ("0xBb90Cc15F7302Bbb7e114a5329d41dBb104F5350", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SUPPLY","FREE_SUPPLY()",[]),
    ("FREE_CAP","FREE_CAP()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
 "Ponke": ("0x0c222b11a380df4f68cee7cacb162357e60c7215", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("FREE_SLOTS","FREE_SLOTS()",[]),
    ("FREE_SUPPLY","FREE_SUPPLY()",[]),("mintOpen","mintOpen()",[]),
    ("freeClaimed_user","freeClaimed(address)",U),("balanceOf_user","balanceOf(address)",U)]),
 "Early5877": ("0x5877D2bb9F226cC3E438F4d656cAeb27DEAFC576", [
    ("totalSupply","totalSupply()",[]),("totalMinted","totalMinted()",[]),
    ("freeMinted","freeMinted()",[]),("MAX_SUPPLY","MAX_SUPPLY()",[]),
    ("mintOpen","mintOpen()",[]),("balanceOf_user","balanceOf(address)",U)]),
}


reads, ok = {}, 0
for name, (addr, views) in ITEMS.items():
    r = raw_batch(addr, views)
    reads[name] = {"address": addr, "views": r, "summary": r}
    if r is not None:
        ok += 1
    print(name, "OK" if r is not None else "FAIL", json.dumps(r)[:220], flush=True)

blk = block_number()
out = {"started_wib": "2026-11-13T23:31+07:00", "reads": reads, "reads_ok": ok,
       "reads_total": len(ITEMS), "block": blk, "elapsed_s": round(time.time() - t0, 1)}
json.dump(out, open(BASE + "run-2026-11-13-2331-retry.json", "w"), indent=1)
print("DONE reads_ok", ok, "/", len(ITEMS), "block", blk, "elapsed", round(time.time() - t0, 1))
