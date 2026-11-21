#!/usr/bin/env python3
"""Refresh read-only Contextgraph Graph 4 (Nodes v2) priority views, run 0801
follow-up. Chunked eth_call (5/chunk + 1s), read-only. Updates ctx-0801.json
with a 'refresh' block and run-2026-11-20-0801-interim.json with
'contextgraph_graph4' (full verification incl. first read)."""
import json, subprocess, time
from datetime import datetime, timezone
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
NODES = "0x189DB6602B8D41a0d14CcCc9e999DC3aF895c3f2"
CLAIM = "0x35B69a4204DC143B8CfEe5D91541D25e8D4095E9"
G = 4

def sel(sig):
    return keccak(sig.encode())[:4].hex()
def enc_addr(a):
    return "0" * 24 + a[2:].lower()
def enc_u(n):
    return "%064x" % n

calls, labels = [], []
def add(addr, sig, args, lab):
    calls.append((addr, "0x" + sel(sig) + args))
    labels.append(lab)

add(NODES, "currentGraph()", "", "currentGraph")
add(NODES, "mintOpen()", "", "mintOpen")
add(NODES, "isSealed(uint256)", enc_u(G), "isSealed(4)")
add(NODES, "totalNodes()", "", "totalNodes")
add(NODES, "nodesInGraph(uint256)", enc_u(G), "nodesInGraph(4)")
add(NODES, "participantsOf(uint256)", enc_u(G), "participantsOf(4)")
add(NODES, "nodesOf(uint256,address)", enc_u(G) + enc_addr(USER), "nodesOf(user,4)")
add(NODES, "holdsAgentId(address)", enc_addr(USER), "holdsAgentId(user)")
add(NODES, "priceFor(address)", enc_addr(USER), "priceFor(user)")
add(NODES, "balanceOf(address)", enc_addr(USER), "balanceOf(user)")
add(CLAIM, "claimOpen()", "", "claimOpen")

results = [None] * len(calls)
t0 = time.time()
for i in range(0, len(calls), 5):
    chunk = calls[i:i + 5]
    payload = [{"jsonrpc": "2.0", "id": j + 1, "method": "eth_call",
                "params": [{"to": a, "data": d}, "latest"]} for j, (a, d) in enumerate(chunk)]
    try:
        o = subprocess.run(["curl", "-sL", "--max-time", "60", "-X", "POST", RPC,
                            "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                           capture_output=True, text=True)
        resp = json.loads(o.stdout)
        by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(chunk)):
            it = by_id.get(j + 1, {})
            results[i + j] = it.get("result") if it.get("result") not in (None, "0x") else {"error": str(it.get("error", "null"))[:160]}
    except Exception as e:
        for j in range(len(chunk)):
            results[i + j] = {"error": f"transport {type(e).__name__}: {str(e)[:100]}"}
    time.sleep(1)

try:
    blk = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST", RPC,
                          "-H", "Content-Type: application/json",
                          "-d", json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])],
                         capture_output=True, text=True)
    block = int(json.loads(blk.stdout)[0]["result"], 16)
except Exception:
    block = "ERR"

views = {}
for lab, v in zip(labels, results):
    if isinstance(v, dict):
        views[lab] = v
    else:
        try:
            views[lab] = int(v, 16)
        except Exception:
            views[lab] = v

now_wib = datetime.now(timezone.utc).astimezone(timezone.utc).strftime("%H:%M UTC")
refresh = {"block": block, "read_wib": "2026-11-20 ~08:2x WIB", "elapsed_s": round(time.time() - t0, 1),
           "views": views}
ctx = json.load(open(BASE + "ctx-0801.json"))
ctx["refresh"] = refresh
json.dump(ctx, open(BASE + "ctx-0801.json", "w"), indent=1)

# first-read values for comparison
first = ctx["views"]
def num(d, k):
    x = d.get(k)
    return x if isinstance(x, int) else None
delta_nodes = None
if num(first, "nodesInGraph(4)") is not None and num(views, "nodesInGraph(4)") is not None:
    delta_nodes = views["nodesInGraph(4)"] - first["nodesInGraph(4)"]

cg = {
  "finding": "EARLY LEAD — Contextgraph Graph 4 (Nodes v2), fase baru proyek yang sudah dikenal user",
  "contracts": {"nodes_v2": NODES, "claim_v2": CLAIM,
                "ctx_token": "0x9E1A59c0e073B12E0546f1321eA4cb5A51C71b88",
                "pass": "0x8BDfAf227D04a7f531c670D39728F9D2adf56aab",
                "registry": "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"},
  "website": "https://contextgraph.art",
  "website_evidence": "/skill.md resmi mencetak semua kontrak persis",
  "x": "https://x.com/contextgraphart",
  "discussion": "Post Facebook 2026-11-19 09:23 UTC (Zaomin Merana): Graph 4 dibuka, first node gratis",
  "launch": {"graph": 4, "opened_utc": "2026-11-19 09:00 UTC", "seal_utc": "2026-11-20 09:00 UTC",
             "age_hours_at_run": 16.4, "age_verified": True,
             "source": "graphStart(4) on-chain 1795078800 + /skill.md resmi (genesis 1794819600)"},
  "first_read": {"block": ctx["block"], "views": first},
  "refresh_read": refresh,
  "delta_nodes_since_first_read": delta_nodes,
  "user_slot": {"nodesOf_user_graph4": views.get("nodesOf(user,4)"),
                "holdsAgentId": views.get("holdsAgentId(user)"),
                "holdsPass": None,
                "balanceOf_user_v2": views.get("balanceOf(user)"),
                "priceFor_user": views.get("priceFor(user)"),
                "answer": 67, "question": {"a": 54, "b": 13, "op": 0},
                "slot_open": views.get("nodesOf(user,4)") == 0 and views.get("priceFor(user)") == 0,
                "note": "User sudah mint Node #2337 di Graph 3 (kontrak v1, 18 Nov) — TIDAK menghalangi: "
                        "jatah free dihitung per-wallet PER GRAPH di kontrak v2; nodesOf(user,4)=0 = "
                        "jatah free Graph 4 masih utuh"},
  "free_views_missing_in_abi": ["totalSupply", "totalMinted", "freeClaimed", "freeMinted",
                                "freeSupply", "FREE_SUPPLY", "freeLeft", "quote", "mintedBy"],
  "free_pct": "UNVERIFIED — tidak ada free cap global (free = 1 Node pertama per wallet per Graph, "
              "tanpa cap global); TIDAK disubstitusi dengan % total supply",
  "claim_v2": {"claimOpen": first.get("claimOpen"), "totalClaimed": first.get("totalClaimed"),
               "poolBalance": "2000000000 CTX",
               "note": "Klaim butuh fee (0,000277 BNB biasa) — bukan klaim gratis; perlu Node dulu"},
  "classification": "EARLY LEAD (kontrak agent-shaped baru + first mints terverifikasi on-chain). "
                    "BUKAN strong lead (kaki free% global tak terukur). BUKAN kandidat "
                    "(velocity tanpa baseline). TIDAK PERNAH auto-mint/preview.",
  "snapshot_entry": "Contextgraph Graph 4 (Nodes v2), status early-lead",
  "executions": "none - read-only"
}
interim = json.load(open(BASE + "run-2026-11-20-0801-interim.json"))
interim["contextgraph_graph4"] = cg
json.dump(interim, open(BASE + "run-2026-11-20-0801-interim.json", "w"), indent=1)
print(json.dumps({"refresh_block": block, "views": views, "delta_nodes": delta_nodes}, indent=1))
print("interim updated with contextgraph_graph4")
