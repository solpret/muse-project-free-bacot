#!/usr/bin/env python3
"""Retry leg-4 chunks 2-3 (calls 20-59) of the 02:59 hot-leg run - read-only."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
RPC_URL = "https://bsc-dataseed.binance.org/"
def sel(sig): return keccak(sig.encode())[:4].hex()
def enc_addr(a): return "0"*24 + a[2:].lower()
def encode(sig, arg):
    data = "0x" + sel(sig)
    if arg == "user": data += enc_addr(USER)
    elif arg == "one": data += "%064x" % 1
    elif arg == "user1": data += enc_addr(USER) + "%064x" % 1
    return data
def rpc_batch(calls, timeout=25):
    payload = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for i,(t,d) in enumerate(calls)]
    r = subprocess.run(["curl","-s","-L","--max-time",str(timeout),RPC_URL,"-H","Content-Type: application/json","-d",json.dumps(payload)],capture_output=True,timeout=timeout+5)
    resp = json.loads(r.stdout.decode())
    if not isinstance(resp, list): raise IOError(f"non-list: {str(resp)[:200]}")
    by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
    out=[]
    for i in range(len(calls)):
        it = by_id.get(i+1, {})
        if "result" in it and it["result"] not in (None,"0x"):
            try: out.append(int(it["result"],16))
            except Exception: out.append(it["result"])
        elif "error" in it: out.append(f"err:{it['error']}")
        else: out.append(None)
    return out
PLAN = [
 ("AGCLUB","0x67270bb351515abf3089ca5420456897363f5e75",[("totalMinted","totalMinted()",None),("freeMinted","freeMinted()",None),("FREE_CAP","FREE_CAP()",None),("mintOpen","mintOpen()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("BNBG","0x1595013dfc8c6b3f4b172254bf09bdaf1421002b",[("totalMinted","totalMinted()",None)]),
 ("SPARKS","0xd52fd117c4b47d03e4e16e778871f09faa5a024b",[("totalSupply","totalSupply()",None)]),
 ("Ledgera","0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d",[("freeClaimed","freeClaimed()",None),("totalSupply","totalSupply()",None),("mintOpen","mintOpen()",None),("freeUsed_user","freeUsed(address)","user"),("balanceOf_user","balanceOf(address)","user")]),
 ("BoldLeonidas","0x84bcb8c16566e81ce902530c9da1e3de291f9941",[("totalSupply","totalSupply()",None),("mintOpen","mintOpen()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("RaceAgents","0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f",[("totalSupply","totalSupply()",None),("freeMinted","freeMinted()",None),("mintOpen","mintOpen()",None)]),
 ("CPASS","0x5877d2bb9f226cc3e438f4d656caeb27deafc576",[("totalMinted","totalMinted()",None),("mintOpen","mintOpen()",None),("balanceOf_user","balanceOf(address)","user")]),
 ("REOPIR","0x12f65bc14037ccdf3f97afc0e67a0e4aca3cf5b9",[("freeClaimed","freeClaimed()",None),("totalSupply","totalSupply()",None),("mintOpen","mintOpen()",None)]),
 ("RAVE","0x7c40B78992d86EDfFB5553C74dB5EF427100bb95",[("totalMinted","totalMinted()",None),("freeMinted","freeMinted()",None),("mintOpen","mintOpen()",None)]),
 ("MORFO","0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",[("totalMinted","totalMinted()",None),("mintOpen","mintOpen()",None)]),
 ("AgentNOVA","0x43462d7f269fde4914b03e1e07067a61b62b9540",[("totalSupply","totalSupply()",None)]),
 ("Zephyra","0x00a9791be6317d6e3a6c60f75a706c870d882048",[("totalMinted","totalMinted()",None)]),
 ("Pengu","0x5AEc03C90656743475810926B2B2bd443D5c26a4",[("totalMinted","totalMinted()",None),("freeMinted","freeMinted()",None)]),
 ("Kryntar","0xB77D3495d3ed4427dA78c9D0f7Cb76C21c23D9fe",[("totalMinted","totalMinted()",None),("standardRemaining","standardRemaining()",None),("legendaryRemaining","legendaryRemaining()",None),("mintOpen","mintOpen()",None)]),
 ("ONI","0x99d01eD93829DBB0EEc11F3a733388c789dA6caD",[("totalMinted","totalMinted()",None),("totalSupply","totalSupply()",None)]),
 ("HAPPE","0x72c14121681F1133545947B0735563835CC07B67",[("totalMinted","totalMinted()",None)]),
]
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append((addr, encode(sig, arg))); meta.append((name, label))
res = rpc_batch(calls)
reads = {}
for (name, label), val in zip(meta, res):
    reads.setdefault(name, {})[label] = val
prev = json.load(open(f"{HF}/hot-leg-run-2026-11-18-0254-reread.json"))
prev_reads = prev.get("reads", {})
diffs = []
for name, views in reads.items():
    pv = prev_reads.get(name, {}).get("views", {})
    d = {k: {"prev": pv.get(k), "now": v} for k, v in views.items() if pv.get(k) != v}
    if d: diffs.append({"item": name, "diff": d})
nones = {n: [k for k,v in vs.items() if v is None] for n, vs in reads.items() if any(v is None for v in vs.values())}
blk = json.loads(subprocess.run(["curl","-s","-L","--max-time","15",RPC_URL,"-H","Content-Type: application/json","-d",'[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}]'],capture_output=True,timeout=20).stdout.decode())[0]["result"]
out = {"reads": reads, "diffs_vs_0254": diffs, "still_none": nones, "block": int(blk,16), "n_calls": len(calls)}
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-18-0259-retry.json","w"), indent=1)
print(json.dumps(out, indent=1))
