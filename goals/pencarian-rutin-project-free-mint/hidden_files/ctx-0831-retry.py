#!/usr/bin/env python3
"""Retry the 6 transport-failed Contextgraph Graph 4 views from ctx-0831 refresh."""
import json, subprocess, time
from eth_hash.auto import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC = "https://bsc-dataseed.binance.org/"
NODES = "0x189DB6602B8D41a0d14CcCc9e999DC3aF895c3f2"
CLAIM = "0x35B69a4204DC143B8CfEe5D91541D25e8D4095E9"
def sel(s): return keccak(s.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def enc_u(n): return "%064x" % n
calls = [
 (NODES, "0x"+sel("participantsOf(uint256)")+enc_u(4), "participantsOf(4)"),
 (NODES, "0x"+sel("nodesOf(uint256,address)")+enc_u(4)+enc_addr(USER), "nodesOf(user,4)"),
 (NODES, "0x"+sel("holdsAgentId(address)")+enc_addr(USER), "holdsAgentId(user)"),
 (NODES, "0x"+sel("priceFor(address)")+enc_addr(USER), "priceFor(user)"),
 (NODES, "0x"+sel("balanceOf(address)")+enc_addr(USER), "balanceOf(user)"),
 (CLAIM, "0x"+sel("claimOpen()"), "claimOpen"),
]
payload = [{"jsonrpc":"2.0","id":j+1,"method":"eth_call","params":[{"to":a,"data":d},"latest"]} for j,(a,d,_) in enumerate(calls)]
for attempt in range(3):
    try:
        o = subprocess.run(["curl","-sL","--max-time","30","-X","POST",RPC,"-H","Content-Type: application/json","-d",json.dumps(payload)], capture_output=True, text=True)
        resp = json.loads(o.stdout)
        break
    except Exception as e:
        resp = []; print("attempt", attempt, "transport fail", type(e).__name__)
    time.sleep(2)
views = {}
for j,(a,d,lab) in enumerate(calls):
    it = next((x for x in resp if isinstance(x,dict) and x.get("id")==j+1), {})
    if "result" in it and it["result"] not in (None,"0x"):
        try: views[lab] = int(it["result"],16)
        except Exception: views[lab] = it["result"]
    elif "error" in it: views[lab] = {"error": str(it["error"])[:120]}
    else: views[lab] = None
try:
    blk = subprocess.run(["curl","-sL","--max-time","30","-X","POST",RPC,"-H","Content-Type: application/json","-d",json.dumps([{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}])], capture_output=True, text=True)
    block = int(json.loads(blk.stdout)[0]["result"],16)
except Exception: block = "ERR"
out = {"block": block, "views": views}
json.dump(out, open(BASE+"ctx-0831-retry.json","w"), indent=1)
print(json.dumps(out, indent=1))
