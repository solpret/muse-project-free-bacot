#!/usr/bin/env python3
"""GLOOP pre-launch check (Boltbook post oqYny-tjhjfL, 18:54 run).
NFT 0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE, site https://gloopagent.xyz,
window opens 12:00 UTC = 19:00 WIB. Read-only: Sourcify ABI shape + on-chain
state. Not a lead (window closed, totalMinted 0, no first mint yet)."""
import json, subprocess, sys
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x183CBb52B3C7BCB2433d50dE0Add99B59f4DE4fE"
EP = "https://bsc-dataseed1.bnbchain.org/"
out = subprocess.run(["curl","-sL","--max-time","20",
    f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"],
    capture_output=True, text=True).stdout
try:
    abi = json.loads(out).get("abi", [])
    names = sorted({e["name"] for e in abi if e.get("type")=="function"})
except Exception as ex:
    names = []; out_err = str(ex)
    print("ABI error", out_err)
FREE = {"freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
        "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"}
s1 = any(n.lower().startswith("mint") for n in names) and bool(set(names) & {"quote","cost","mintCost"}) \
     and bool(set(names) & FREE) and bool(set(names) & {"agentId","agentRegistry","registry","AGENT_ID","AGENT_REGISTRY","hasAgentId"})
s2 = bool(set(names) & {"name","symbol","decimals","totalSupply"}) and "mintFree" in names \
     and bool(set(names) & {"freeClaimed","freeMinted"}) and bool(set(names) & {"FREE_SLOTS","FREE_SUPPLY"}) \
     and bool(set(names) & {"agentId","agentRegistry","registry","AGENT_ID","AGENT_REGISTRY"})
shape = {"address": ADDR, "n_fns": len(names), "fns": names, "S1": s1, "S2": s2}
print(json.dumps(shape, indent=1))
# on-chain state via fast_rpc single calls
from Crypto.Hash import keccak
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x"+k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64,"0")
def to_int(v):
    try: return int(v,16)
    except Exception: return None
def call(sig, arg=""):
    data = sel(sig)
    if arg=="USER": data += enc(USER)
    try:
        r = batch([("eth_call", [{"to": ADDR, "data": data}, "latest"])], endpoint=EP, timeout=20)
        return to_int(r[0])
    except Exception as ex:
        return f"ERR {str(ex)[:90]}"
views = {}
for sig in ["totalMinted()","totalSupply()","mintOpen()","mintActive()","freeMinted()",
            "MAX_SUPPLY()","FREE_SUPPLY()","freeClaimed(address)","mintedBy(address)",
            "freeLeft()","mintStart()","mintEnd()","price()","mintPrice()","costWei(uint256)"]:
    views[sig.split("(")[0]] = call(sig, "USER" if "(address" in sig else "")
try:
    blk = int(batch([("eth_blockNumber", [])], endpoint=EP, timeout=20)[0], 16)
except Exception:
    blk = None
res = {"block": blk, "shape": shape, "views": views,
       "site_from_post": "https://gloopagent.xyz",
       "window_opens_wib": "2026-11-08 19:00 WIB (12:00 UTC)",
       "status": "pre-launch watchlist-only: window closed, no first mint yet; NOT a lead, NOT previewed/minted"}
json.dump(res, open(BASE+"hot-leg-2026-11-08-1854-gloop.json","w"), indent=1)
print(json.dumps(res, indent=1))
# record in seen as watchlist-only
seen = json.load(open(BASE+"hot-leg-seen.json"))
seen[ADDR] = {"first_seen_wib": "2026-11-08T18:54:38+07:00", "source": "boltbook-post-oqYny-tjhjfL",
  "status": "watchlist-only-prelaunch",
  "note": f"GLOOP NFT (site https://gloopagent.xyz per Boltbook post). S1={s1} S2={s2} fns={len(names)}. Window opens 19:00 WIB; totalMinted={views.get('totalMinted')} mintOpen={views.get('mintOpen')} at block {blk}. Age unverified (no first mint yet) - watchlist-only, never reported as lead."}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
print("seen total now:", len(seen))
