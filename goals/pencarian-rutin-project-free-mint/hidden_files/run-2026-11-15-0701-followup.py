#!/usr/bin/env python3
"""On-chain follow-up run 0701 for sweep items Golden Agents + WOJAGENT.
Deep-dive duty: first-mint corroboration (chunked eth_getLogs Transfer-from-zero,
1000-block chunks, dataseed) + free-pool/user-slot reads. Read-only. No preview/mint."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
ZERO = "0x0000000000000000000000000000000000000000000000000000000000000000"
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build_data(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def block_number():
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, 30)
            if isinstance(r, dict) and r.get("result"): return int(r["result"], 16)
        except Exception: continue
    return None
def call_many(addr, views):
    calls = [{"jsonrpc": "2.0", "id": i+1, "method": "eth_call",
              "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]}
             for i, (key, sig, args) in enumerate(views)]
    for ep in EPS:
        try:
            res = rpc(ep, calls, 60)
            if not isinstance(res, list) or len(res) != len(calls): continue
            out = {}
            for it, (key, sig, args) in zip(res, views):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception: continue
    return None
def first_mint(addr, head, back_blocks=30000):
    """Walk back in 1000-block chunks from head; return earliest Transfer-from-zero found."""
    earliest = None
    chunks = []
    n = back_blocks // 1000
    for i in range(n):
        to = head - i*1000
        frm = to - 999
        hit = None
        for ep in EPS:
            try:
                r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                             "params": [{"fromBlock": hex(frm), "toBlock": hex(to),
                                         "address": addr, "topics": [TRANSFER, ZERO]}]}, 60)
                logs = r.get("result", []) if isinstance(r, dict) else []
                hit = {"from": frm, "to": to, "n": len(logs)}
                if logs:
                    cand = min(logs, key=lambda l: int(l["blockNumber"], 16))
                    b = int(cand["blockNumber"], 16)
                    if earliest is None or b < earliest["block"]:
                        earliest = {"block": b, "tx": cand["transactionHash"]}
                break
            except Exception as e:
                hit = {"from": frm, "to": to, "error": str(e)[:80]}
        chunks.append(hit)
        print(f"  {addr[:10]} chunk {i+1}/{n} {frm}-{to}: {hit}", flush=True)
        if earliest is not None and i >= 2:
            # keep walking a bit to confirm earliest in window, but stop after 3 chunks past first hit
            pass
    return earliest, chunks

head = block_number()
print("head", head)
out = {"run": "free-mint-search 2026-11-15 07:01 WIB", "head": head, "items": {}}

GA = "0x4233c62919cc03168a361c547117c1553c375bfc"
ga_views = call_many(GA, [("totalSupply","totalSupply()",[]),("publicMinted","publicMinted()",[]),
    ("MAX_SUPPLY","MAX_SUPPLY()",[]),("mintActive","mintActive()",[]),
    ("mintedBy_user","mintedBy(address)",[USER]),("balanceOf_user","balanceOf(address)",[USER]),
    ("AGENT_ID_REGISTRY","AGENT_ID_REGISTRY()",[]),("owner","owner()",[])])
print("GoldenAgents views:", ga_views)
ga_first, ga_chunks = first_mint(GA, head, 30000)
print("GoldenAgents first mint in window:", ga_first)
ga_ts = None
if ga_first:
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                         "params":[hex(ga_first["block"]), False]}, 30)
            ga_ts = int(r["result"]["timestamp"], 16); break
        except Exception: continue
out["items"]["GoldenAgents"] = {"address": GA, "views": ga_views,
    "first_mint_in_30000_blocks": ga_first, "first_mint_ts": ga_ts,
    "chunks_checked": len(ga_chunks)}

WO = "0x62EC413381B74387b57F1E2734cdd2E5b96a57B7"
wo_views = call_many(WO, [("name","name()",[]),("symbol","symbol()",[]),
    ("totalShares","totalShares()",[]),("FREE_SHARES","FREE_SHARES()",[]),
    ("freeClaimed_user","freeClaimed(address)",[USER]),("saleStart","saleStart()",[]),
    ("saleState","saleState()",[]),("mintPaused","mintPaused()",[]),
    ("MAX_SHARES","MAX_SHARES()",[]),("pair","pair()",[]),
    ("REGISTRY","REGISTRY()",[]),("balanceOf_user","balanceOf(address)",[USER]),
    ("failed","failed()",[]),("tradingOpen","tradingOpen()",[])])
print("WOJAGENT views:", wo_views)
wo_first, wo_chunks = first_mint(WO, head, 30000)
print("WOJAGENT first mint in window:", wo_first)
wo_ts = None
if wo_first:
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber",
                         "params":[hex(wo_first["block"]), False]}, 30)
            wo_ts = int(r["result"]["timestamp"], 16); break
        except Exception: continue
out["items"]["WOJAGENT"] = {"address": WO, "views": wo_views,
    "first_mint_in_30000_blocks": wo_first, "first_mint_ts": wo_ts,
    "chunks_checked": len(wo_chunks)}
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-15-0701-followup.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
