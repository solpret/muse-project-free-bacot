#!/usr/bin/env python3
"""Read-only on-chain verification of Contextgraph Graph 4 (v2 contracts),
found by the 0801 sweep subagent. No preview/mint/claim.
Nodes v2 0x189DB6602B8D41a0d14CcCc9e999DC3aF895c3f2
Claim v2 0x35B69a4204DC143B8CfEe5D91541D25e8D4095E9
Writes ctx-0801.json."""
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

calls = []
def add(addr, sig, args=""):
    calls.append((addr, "0x" + sel(sig) + args))

add(NODES, "currentGraph()")
add(NODES, "mintOpen()")
add(NODES, "totalNodes()")
add(NODES, "MAX_PER_GRAPH()")
add(NODES, "graphStart(uint256)", enc_u(G))
add(NODES, "graphEnd(uint256)", enc_u(G))
add(NODES, "isSealed(uint256)", enc_u(G))
add(NODES, "nodesInGraph(uint256)", enc_u(G))
add(NODES, "participantsOf(uint256)", enc_u(G))
add(NODES, "nodesOf(uint256,address)", enc_u(G) + enc_addr(USER))
add(NODES, "holdsAgentId(address)", enc_addr(USER))
add(NODES, "holdsPass(address)", enc_addr(USER))
add(NODES, "balanceOf(address)", enc_addr(USER))
add(NODES, "priceFor(address)", enc_addr(USER))
add(NODES, "questionFor(address)", enc_addr(USER))
add(NODES, "answerFor(address)", enc_addr(USER))
add(CLAIM, "claimOpen()")
add(CLAIM, "totalClaimed()")
add(CLAIM, "poolBalance()")
add(CLAIM, "currentPhase()")

labels = ["currentGraph", "mintOpen", "totalNodes", "MAX_PER_GRAPH",
          "graphStart(4)", "graphEnd(4)", "isSealed(4)", "nodesInGraph(4)",
          "participantsOf(4)", "nodesOf(user,4)", "holdsAgentId(user)",
          "holdsPass(user)", "balanceOf(user)", "priceFor(user)",
          "questionFor(user)", "answerFor(user)",
          "claimOpen", "totalClaimed", "poolBalance", "currentPhase"]

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
blk = subprocess.run(["curl", "-sL", "--max-time", "30", "-X", "POST", RPC,
                      "-H", "Content-Type: application/json",
                      "-d", json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}])],
                     capture_output=True, text=True)
block = int(json.loads(blk.stdout)[0]["result"], 16)

views = {}
for j, lab in enumerate(labels):
    v = results[j]
    if isinstance(v, dict):
        views[lab] = v
    elif lab == "questionFor(user)":
        h = v[2:]
        words = [int(h[i:i + 64], 16) for i in range(0, len(h), 64)]
        views[lab] = {"a": words[0], "b": words[1], "op": words[2]} if len(words) == 3 else {"raw": v}
    else:
        try:
            views[lab] = int(v, 16)
        except Exception:
            views[lab] = v

def ts(x):
    if isinstance(x, int):
        return datetime.fromtimestamp(x, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return x

out = {"contract_nodes_v2": NODES, "contract_claim_v2": CLAIM, "graph": G,
       "block": block, "elapsed_s": round(time.time() - t0, 1),
       "views": views,
       "graphStart_utc": ts(views.get("graphStart(4)")),
       "graphEnd_utc": ts(views.get("graphEnd(4)")),
       "now_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
json.dump(out, open(BASE + "ctx-0801.json", "w"), indent=1)
print(json.dumps(out, indent=1))
