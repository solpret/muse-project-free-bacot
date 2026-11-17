#!/usr/bin/env python3
"""Hot-leg 2149 follow-up: RPC recovered after transient failure in main script.
Leg3 verify for the 2 new S1 sale-shapes + Leg4 re-read of the 20 snapshot items.
Read-only except own hot-leg state file updates (seen status notes)."""
import json, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _single as _fast_single
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-07-2149"
NOW = "2026-11-07T21:53:00+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
NEW_S1 = ["0xa46D33862124Da90385cEb58acba63718729DEe0",
          "0x2df7435f5bce0577bee213e13da68313c74d7d0b"]
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/",
       "https://rpc.ankr.com/bsc"]
DEADLINE = time.time() + 100
t0 = time.time()
out = {"run": "free-mint-hot-leg 2026-11-07 21:49:38 WIB - follow-up verify (RPC recovered)"}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def raw(to, data):
    if time.time() > DEADLINE:
        return "deadline"
    for ep in EPS:
        if time.time() > DEADLINE:
            return "deadline"
        try:
            v = _fast_single(ep, "eth_call", [{"to": to, "data": data}, "latest"], 8, retries=0)
            if v is None or v == "0x":
                return None
            try:
                return int(v, 16)
            except Exception:
                return v
        except Exception:
            continue
    return None
def call(to, sig, args=""): return raw(to, sel(sig) + args)

blk = None
for ep in EPS:
    try:
        v = _fast_single(ep, "eth_blockNumber", [], 8, retries=0)
        if v:
            blk = int(v, 16); break
    except Exception:
        continue
out["block"] = blk

def decode_str(v):
    if not isinstance(v, str) or not v.startswith("0x") or len(v) < 138:
        return None
    try:
        b = bytes.fromhex(v[2:])
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "replace")
    except Exception:
        return None

leg3 = {}
for a in NEW_S1:
    d = {"S1": True}
    for sig, key in [("freeClaimed()", "freeClaimed"), ("freeMinted()", "freeMinted"),
                     ("freeSharesRemaining()", "freeSharesRemaining"), ("freeLeft(address)", "freeLeft_user"),
                     ("quote(address,uint256)", "quote_user1"), ("freeFor(address)", "freeFor_user"),
                     ("mintOpen()", "mintOpen"), ("totalSupply()", "totalSupply"),
                     ("balanceOf(address)", "balanceOf_user"), ("freeUsed()", "freeUsed"),
                     ("freeSharesClaimed()", "freeSharesClaimed"),
                     ("name()", "name"), ("symbol()", "symbol")]:
        if sig.startswith("quote("):
            d[key] = call(a, sig, enc(USER) + enc_uint(1))
        elif "address" in sig:
            d[key] = call(a, sig, enc(USER))
        else:
            d[key] = call(a, sig)
    for k in ("name", "symbol"):
        if d.get(k):
            d[k] = decode_str(d[k])
    d["age"] = "UNVERIFIED this run (getLogs age check skipped for speed; watchlist-only until verified by main job)"
    leg3[a] = d
out["leg3_verify"] = leg3

# Boltbook context for the Boltbook-found S1 contract
try:
    p = subprocess.run(["curl", "-sS", "-L", "--max-time", "15", "-A", "hot-leg/1.0",
                        "https://boltbook.fun/?lang=en"], capture_output=True, text=True, timeout=20)
    html = p.stdout or ""
    idxs = [m.start() for m in re.finditer(r"0x2df7435f5bce0577bee213e13da68313c74d7d0b", html, re.I)]
    ctx = []
    for i in idxs:
        seg = html[max(0, i-800):i+800]
        seg = re.sub(r"<[^>]+>", " ", seg)
        seg = re.sub(r"\s+", " ", seg).strip()
        ctx.append(seg[:1200])
    slugs = sorted(set(re.findall(r"/p/([A-Za-z0-9_-]+)", html)))
    out["boltbook_context_0x2df7"] = {"occurrences": len(idxs), "snippets": ctx, "post_slugs_on_page": slugs[:40]}
except Exception as e:
    out["boltbook_context_0x2df7"] = {"error": f"{type(e).__name__}: {e}"}

# Leg 4 re-read (same ITEMS as main script)
NFT_VIEWS = ["totalSupply()", "freeClaimed()", "freeMinted()", "FREE_SUPPLY()",
             "balanceOf(address)", "mintedBy(address)", "freeUsed(address)",
             "claimedFree(address)", "mintOpen()"]
SALE_VIEWS = ["freeClaimed()", "freeSharesRemaining()", "freeLeft(address)",
              "quote(address,uint256)", "mintedBy(address)", "mintOpen()",
              "totalMinted()", "freeMinted()", "totalSupply()", "balanceOf(address)",
              "freeFor(address)"]
LEAD_VIEWS = ["totalMints()", "MAX_MINTS()", "freeLeft(address)", "quote(address,uint256)",
              "mintedBy(address)", "mintOpen()", "totalSupply()", "balanceOf(address)"]
ITEMS = {
 "Orchidia": ("0x09bcdd97186f6f37521bd1b281d329e48ac54b89", NFT_VIEWS),
 "Agent Goats": ("0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6", NFT_VIEWS),
 "Tacotron": ("0x05debe4445232205ae7e79d02cb5de5aa0641eff", NFT_VIEWS),
 "Agent Frogs": ("0x4fEA4Ed6e70389245c41b2c9D85E8032E3C6Ce31", NFT_VIEWS),
 "Wuyuhive": ("0x250e800025a9a7861970e253bab6975a57f80567", NFT_VIEWS),
 "Thronemind": ("0xC97Cdd183bc61bdFCf00D97284e7bdd707Cb0a90", NFT_VIEWS),
 "Ink Koi": ("0xbd4B4e7189ae9356514664146b0eD683601200A9", NFT_VIEWS),
 "Night Bandits Club": ("0xa849aEd9dC19FBA823CcEf1FA01BdA72Fbb8fcDf", NFT_VIEWS),
 "ADCHAR": ("0x6E8b05C2dD1C625D839f33f60B837d9AF25E6044", NFT_VIEWS),
 "Saturnagent": ("0xef870a9b4a529373fb2e174b59ca7a66eb018074", SALE_VIEWS),
 "Lumenhold": ("0x9701980b0afd825134390ee46fb3bd675a2f356f", SALE_VIEWS),
 "Horus AI": ("0x794ad67a5590c7e5848e49181297f9cc7c6ce00e", NFT_VIEWS),
 "AURISLE": ("0xC52a979C20C5a43e5Be4Ffa6d1A4DD50069D5E2D", NFT_VIEWS),
 "DinoAgent": ("0xcE19D6A5FF15e088D4bf23614242927139084895", NFT_VIEWS),
 "Tri333": ("0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f", NFT_VIEWS),
 "LOCKSMITH": ("0x05e8738290be6639fD0f7236ebF444E5466D3164", NFT_VIEWS),
 "AgentBook": ("0xEECaCBE6eAC6D6F2a38e8daA9049C7AA08aD43b0", SALE_VIEWS),
 "CipherAgent": ("0x158b5e25015758a94703A27c152889451E5d52E5", LEAD_VIEWS),
 "MarsAgent": ("0x2231FdAe405c33dc4993f8C577c453802FF1AcE9", LEAD_VIEWS),
 "fab7dd20-variant": ("0xfab7dd20e8816e10227C1222bd4Bd446FecF1B72",
    ["totalSupply()", "freeMinted()", "FREE_SHARES()", "freeClaimed(address)", "balanceOf(address)", "startTime()"]),
}
from concurrent.futures import ThreadPoolExecutor
snap = json.load(open(f"{BASE}/onchain-snapshot.json"))
def read_item(args):
    name, (addr, views) = args
    d = {"address": addr}
    for sig in views:
        key = sig.split("(")[0]
        if sig.startswith("quote("):
            v = call(addr, sig, enc(USER) + enc_uint(1)); key += "_user1"
        elif "address" in sig:
            v = call(addr, sig, enc(USER)); key += "_user"
        else:
            v = call(addr, sig)
        d[key] = v
    snap_v = snap.get("contracts", {}).get(name, {}) or snap.get("track_c", {}).get(name, {})
    d["snap"] = {k: snap_v.get(k) for k in ("freeClaimed", "FREE_SUPPLY", "freeSupply", "totalSupply", "status", "freeMinted", "totalMinted") if snap_v.get(k) is not None}
    return name, d
if blk is None:
    out["leg4_reread"] = {"block": None, "status": "SKIPPED - RPC unreachable again"}
else:
    with ThreadPoolExecutor(max_workers=20) as ex:
        leg4 = dict(ex.map(read_item, list(ITEMS.items())))
    out["leg4_reread"] = {"block": blk, "items": leg4}
out["duration_s"] = round(time.time() - t0, 1)
json.dump(out, open(f"{BASE}/hot-leg-run-{TS}-verify.json", "w"), indent=1)
print(json.dumps({"block": blk, "leg3": leg3, "leg4_block": out["leg4_reread"].get("block"),
                  "duration_s": out["duration_s"]}, indent=1, default=str))
