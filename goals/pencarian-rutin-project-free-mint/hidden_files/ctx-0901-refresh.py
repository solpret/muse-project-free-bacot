#!/usr/bin/env python3
"""Ctx refresh + Boltbook-new triage, run free-mint-search 2026-11-20 09:01 WIB.
Read-only. Writes ctx-0901.json and boltbook-triage-0901.json."""
import json, subprocess, time
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

# Contextgraph Graph 4
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

# Boltbook-new triage (3 addresses)
NEW = ["0x48afa54a08ef30e1af87e12c929cf7700ccde983",
       "0x79F55DAa8a3CF2Eb76EE40e26ff6E244a4cC1eD4",
       "0xd301d472f2e469a1aafa1af6f214e312f1858873"]
for a in NEW:
    add(a, "totalSupply()", "", f"{a}|totalSupply")
    add(a, "totalMinted()", "", f"{a}|totalMinted")
    add(a, "freeClaimed()", "", f"{a}|freeClaimed")
    add(a, "FREE_SUPPLY()", "", f"{a}|FREE_SUPPLY")
    add(a, "freeLeft()", "", f"{a}|freeLeft")
    add(a, "agentRegistry()", "", f"{a}|agentRegistry")
    add(a, "mintOpen()", "", f"{a}|mintOpen")
    add(a, "owner()", "", f"{a}|owner")

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

ctx_views, triage = {}, {}
for lab, v in zip(labels, results):
    if "|" in lab:
        a, vk = lab.split("|", 1)
        if isinstance(v, dict):
            triage.setdefault(a, {})[vk] = v
        elif vk == "agentRegistry":
            triage.setdefault(a, {})[vk] = "0x" + v[-40:] if len(v) >= 42 else v
        elif vk == "owner":
            triage.setdefault(a, {})[vk] = "0x" + v[-40:] if len(v) >= 42 else v
        else:
            try:
                triage.setdefault(a, {})[vk] = int(v, 16)
            except Exception:
                triage.setdefault(a, {})[vk] = v
    else:
        if isinstance(v, dict):
            ctx_views[lab] = v
        else:
            try:
                ctx_views[lab] = int(v, 16)
            except Exception:
                ctx_views[lab] = v

ctx = {"block": block, "read_wib": "2026-11-20 ~09:0x WIB",
       "elapsed_s": round(time.time() - t0, 1), "views": ctx_views}
json.dump(ctx, open(BASE + "ctx-0901.json", "w"), indent=1)
json.dump({"block": block, "triage": triage}, open(BASE + "boltbook-triage-0901.json", "w"), indent=1)
print(json.dumps({"block": block, "ctx": ctx_views, "triage": triage}, indent=1))
