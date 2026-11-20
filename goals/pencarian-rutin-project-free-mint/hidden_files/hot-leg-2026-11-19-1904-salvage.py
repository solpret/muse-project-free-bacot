#!/usr/bin/env python3
"""Hot-leg 2026-11-19 19:04 salvage: main run script was killed by timeout 280
(exit 124) inside leg-4 batch calls. Legs 1-2 completed (shape file + boltbook
html saved, seen.json written). This salvage (a) shape-checks the 2 Boltbook
addresses missing from seen.json (likely lost to a concurrent writer race at
12:09:45 UTC), records them; (b) sequentially re-reads the 4 decision-relevant
items (STOCKAGENT, Lumenhold, AUGENT, binanceai-mint) via race() single calls,
proven fast in the 1859 salvage. Read-only except own hot-leg state files."""
import json, sys, time, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import race
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.localtime())
START = time.time()
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
UA = "0x" + USER[2:].lower().rjust(64, "0")
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def iv(v):
    try: return int(v, 16) if v else None
    except Exception: return None
def call(to, data):
    try:
        return race("eth_call", [{"to": to, "data": data}, "latest"], timeout=10)
    except Exception as ex:
        return {"error": f"{type(ex).__name__}: {str(ex)[:100]}"}

out = {"run": "free-mint-hot-leg 2026-11-19 19:04 WIB salvage", "started_wib": NOW}

# (a) shape-check the 2 Boltbook addresses missing from seen.json
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeCardsRemaining"]
def shape(addr):
    try:
        _o = subprocess.run(["curl","-sL","--max-time","20",
            f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
            capture_output=True, text=True).stdout
        meta = json.loads(_o)
        abi = meta.get("abi", [])
        fns = {}
        for e in abi:
            if e.get("type") == "function": fns.setdefault(e["name"], []).append(e)
        names = set(fns)
        has_mint = any(n.lower().startswith("mint") for n in names)
        has_quote = bool(names & {"quote","cost","getQuote","mintCost","price","getPrice"})
        free_views = sorted(names & set(FREE_VIEWS))
        agent_ref = bool(names & {"agentId","agentRegistry","registry","getAgentId","agentGate","AgentGate","AGENT_ID","AGENT_ID_REGISTRY","agentIdOf","hasAgentId"})
        s1 = has_mint and has_quote and bool(free_views) and agent_ref
        is_token = bool(names & {"name","symbol","decimals","totalSupply"})
        mintfree = "mintFree" in fns and any(len(e.get("inputs",[]))==0 for e in fns["mintFree"])
        s2 = is_token and mintfree and bool(names & {"freeClaimed","freeMinted"}) and bool(names & {"FREE_SLOTS","FREE_SUPPLY"}) and agent_ref
        return {"address": addr, "S1": s1, "S2": s2, "is_nft": bool(names & {"ownerOf","tokenURI"}),
                "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names)}
    except Exception as ex:
        return {"address": addr, "error": f"{type(ex).__name__}: {str(ex)[:120]}"}

seen = json.load(open(BASE + "hot-leg-seen.json"))  # fresh reload (concurrent-writer race)
bb_missing = ["0x126af9585953004cbb9c5a0b37fc5616dd5f3b43",
              "0x5bc4fb61270c2628c93bf507c4ba125b868d34ff"]
bb_shapes = [shape(a) for a in bb_missing]
out["boltbook_missing_shapes"] = bb_shapes
for s in bb_shapes:
    a = s["address"]
    if s.get("error") or not s.get("n_fns"):
        continue
    seen[a] = {"first_seen_wib": NOW, "source": "boltbook-en",
        "status": "checked-not-track-c" if ((s.get("S1") or s.get("S2")) and s.get("is_nft"))
                 else ("sale-shape-pass" if (s.get("S1") or s.get("S2")) else "checked-not-sale-shape"),
        "note": f"S1={s.get('S1')} S2={s.get('S2')} mint={s.get('has_mint')} quote={s.get('has_quote')} free={s.get('free_views')} agent={s.get('agent_ref')} token={s.get('is_token')}"}
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
out["seen_n"] = len(seen)

# (b) key-item re-reads, sequential race() single calls
def enc_uint(n): return "0x" + format(n, "064x")
ITEMS = [
 ("STOCKAGENT", "0xba7068233da805bdebcc167be361c219002e6b7f",
  [("totalSupply","totalSupply()",""),("freeLeft","freeLeft()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("mintOpen","mintOpen()",""),("quote_user_1","quote(address,uint256)","addr_uint1"),
   ("freeMintedByWallet_user","freeMintedByWallet(address)","addr"),
   ("balanceOf_user","balanceOf(address)","addr")]),
 ("Lumenhold", "0x9701980b0afd825134390ee46fb3bd675a2f356f",
  [("totalSupply","totalSupply()",""),("freeClaimed","freeClaimed()",""),("FREE_SUPPLY","FREE_SUPPLY()",""),
   ("mintOpen","mintOpen()",""),("balanceOf_user","balanceOf(address)","addr"),
   ("mintedBy_user","mintedBy(address)","addr")]),
 ("AUGENT", "0xAAdD9058b3DaaB00439457D82c2C508a5cc1c393",
  [("freeClaimed","freeClaimed()",""),("freeClaimed_user","freeClaimed(address)","addr"),
   ("totalSupply","totalSupply()",""),("balanceOf_user","balanceOf(address)","addr")]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched","launched()",""),("failed","failed()",""),("isRefundPhase","isRefundPhase()",""),
   ("totalShares","totalShares()",""),("tokenClaimed_user","tokenClaimed(address)","addr")]),
]
reads = {}
for name, addr, views in ITEMS:
    reads[name] = {"address": addr, "views": {}}
    for vk, sig, argt in views:
        data = sel(sig)
        if argt == "addr": data += UA[2:]
        elif argt == "addr_uint1": data += UA[2:] + enc_uint(1)[2:]
        r = call(addr, data)
        reads[name]["views"][vk] = iv(r) if isinstance(r, str) else r
try:
    blk = int(race("eth_blockNumber", [], timeout=8), 16)
except Exception:
    blk = None
out["block"] = blk
out["reads"] = reads
st = reads["STOCKAGENT"]["views"]; lu = reads["Lumenhold"]["views"]
def pct(c, t): return round(100*c/t, 1) if c is not None and t else None
out["threshold_check"] = {
  "STOCKAGENT_free_pct": pct((st.get("FREE_SUPPLY")-st.get("freeLeft")) if st.get("FREE_SUPPLY") is not None and st.get("freeLeft") is not None else None, st.get("FREE_SUPPLY")),
  "STOCKAGENT": st,
  "Lumenhold_free_pct": pct(lu.get("freeClaimed"), lu.get("FREE_SUPPLY")),
  "Lumenhold": lu,
  "AUGENT": reads["AUGENT"]["views"],
  "binanceai": reads["binanceai-mint"]["views"],
}
out["elapsed_s"] = round(time.time()-START, 1)
json.dump(out, open(BASE + "hot-leg-run-2026-11-19-1904-salvage.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
