#!/usr/bin/env python3
"""Run 0231 follow-up: retry fresh reads for DRAGON + XCOPY via chunked curl
batch (run.py pattern) + single-call verification on 3 endpoints."""
import json, subprocess, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a[2:].lower()

def call(to, sig, arg=None):
    data = "0x" + sel(sig)
    if arg == "user":
        data += enc_addr(USER)
    return (to, data)

def curl_batch(calls, timeout=20):
    out = []
    for i in range(0, len(calls), 5):
        chunk = calls[i:i+5]
        payload = [{"jsonrpc": "2.0", "id": j+1, "method": "eth_call",
                    "params": [{"to": to, "data": data}, "latest"]}
                   for j, (to, data) in enumerate(chunk)]
        r = subprocess.run(["curl", "-s", "--max-time", str(timeout),
                            "https://bsc-dataseed.binance.org/",
                            "-H", "Content-Type: application/json",
                            "-d", json.dumps(payload)],
                           capture_output=True, timeout=timeout+5)
        if r.returncode != 0 or not r.stdout:
            raise IOError(f"curl batch failed rc={r.returncode}")
        resp = json.loads(r.stdout.decode())
        by_id = {it["id"]: it for it in resp if isinstance(it, dict)}
        for j in range(len(chunk)):
            it = by_id.get(j+1, {})
            if "result" in it and it["result"] not in (None, "0x"):
                try:
                    out.append(int(it["result"], 16))
                except Exception:
                    out.append(it["result"])
            else:
                out.append(None)
    return out

def single(ep, to, data, timeout=12):
    payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}]).encode()
    req = urllib.request.Request(ep, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        resp = json.loads(r.read().decode())
    it = resp[0] if isinstance(resp, list) else resp
    if "result" in it and it["result"] not in (None, "0x"):
        try:
            return int(it["result"], 16)
        except Exception:
            return it["result"]
    return None

DRAGON = "0xfc191b76041498b14dcae3c802af3389c74263e6"
XCOPY = "0x3fbec44c7c845374267b06033940abe45c63edfa"

PLAN = [
 ("DRAGON", DRAGON, [("totalMinted", "totalMinted()", None), ("freeMinted", "freeMinted()", None),
   ("FREE_SUPPLY", "FREE_SUPPLY()", None), ("MAX_SUPPLY", "MAX_SUPPLY()", None),
   ("mintStart", "mintStart()", None), ("mintEnd", "mintEnd()", None),
   ("mintEnded", "mintEnded()", None), ("freeRemaining", "freeRemaining()", None),
   ("paidMinted", "paidMinted()", None), ("hasClaimedFree_user", "hasClaimedFree(address)", "user"),
   ("mintedBy_user", "mintedBy(address)", "user"), ("balanceOf_user", "balanceOf(address)", "user"),
   ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()", None), ("owner", "owner()", None)]),
 ("XCOPY", XCOPY, [("totalSupply", "totalSupply()", None), ("totalMinted", "totalMinted()", None),
   ("MAX_SUPPLY", "MAX_SUPPLY()", None), ("mintOpen", "mintOpen()", None),
   ("remaining", "remaining()", None), ("mintedCount", "mintedCount()", None),
   ("balanceOf_user", "balanceOf(address)", "user"),
   ("AGENT_REGISTRY", "AGENT_REGISTRY()", None), ("owner", "owner()", None),
   ("mintPriceFor_user", "mintPriceFor(address)", "user")]),
]
calls, meta = [], []
for name, addr, views in PLAN:
    for label, sig, arg in views:
        calls.append(call(addr, sig, arg))
        meta.append((name, addr, label))
out = {"run": "free-mint-search 2026-11-17 02:31 WIB follow-up reads"}
try:
    res = curl_batch(calls)
    out["batch_method"] = "curl-batch-5"
except Exception as e:
    out["batch_method"] = f"curl-batch FAILED: {e}"
    res = [None] * len(calls)
reads = {}
for (name, addr, label), val in zip(meta, res):
    reads.setdefault(name, {"address": addr, "views": {}})["views"][label] = val
out["reads"] = reads

# Single-call verification on 3 endpoints for the key views
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
verify = {}
for name, addr, labels in [
    ("DRAGON", DRAGON, [("totalMinted", "totalMinted()"), ("freeMinted", "freeMinted()"),
                         ("FREE_SUPPLY", "FREE_SUPPLY()"), ("mintStart", "mintStart()"),
                         ("AGENT_ID_REGISTRY", "AGENT_ID_REGISTRY()")]),
    ("XCOPY", XCOPY, [("totalSupply", "totalSupply()"), ("totalMinted", "totalMinted()"),
                       ("MAX_SUPPLY", "MAX_SUPPLY()"), ("AGENT_REGISTRY", "AGENT_REGISTRY()")]),
]:
    for label, sig in labels:
        vals = []
        for ep in EPS:
            try:
                vals.append(single(ep, addr, "0x" + sel(sig)))
            except Exception as e:
                vals.append(f"ERR:{type(e).__name__}")
        verify[f"{name}.{label}"] = vals
out["single_call_verify_3ep"] = verify

# Block + timestamps for mintStart/mintEnd interpretation
try:
    payload = json.dumps([{"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}]).encode()
    req = urllib.request.Request("https://bsc-dataseed.binance.org/", data=payload,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        out["block"] = int(json.loads(r.read().decode())[0]["result"], 16)
except Exception as e:
    out["block_error"] = str(e)[:120]
out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(f"{HF}/run-2026-11-17-0231-verify-reads.json", "w"), indent=1)
print(json.dumps(out, indent=1))
