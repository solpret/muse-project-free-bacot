#!/usr/bin/env python3
"""Hot-leg 0914 retry: chunk 1 of prio re-read returned empty (batch fail);
re-read the 7 missing items + SHINE launched() individually."""
import json, time, subprocess
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EP = "https://bsc-dataseed.binance.org/"
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")
PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
    ("agentFreeUsed", "agentFreeUsed()"), ("freeLeft", "freeLeft()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "NIGHTFORGE_B": ("0x051f04ff7b095793613b9caac197cc1051c24e2b", [
    ("totalSupply", "totalSupply()"), ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)")]),
 "SOLDERCATS": ("0x3D972EBbF7488f21b95250B867e2406c723C9DDC", [
    ("totalSupply", "totalSupply()"), ("agentFreeUsed", "agentFreeUsed()"),
    ("mintOpen", "mintOpen()"),
    ("balanceOf_user", "balanceOf(address)"),
    ("agentFreeByWallet_user", "agentFreeByWallet(address)")]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("freePhaseStart", "freePhaseStart()"), ("totalMinted", "totalMinted()"),
    ("freeMinted", "freeMinted()"), ("balanceOf_user", "balanceOf(address)")]),
 "sale-11-11": ("0x64767b1a39441e72046c2162065a2896e154b341", [
    ("freeMinted", "freeMinted()"), ("freeClaimed_user", "freeClaimed(address)")]),
 "PESI": ("0xe82BAc76C904d49AA6a240f236AFe1D1eD5F4baD", [
    ("freeMinted", "freeMinted()"), ("totalFreeShares", "totalFreeShares()"),
    ("totalShares", "totalShares()")]),
 "ORYN-sale": ("0x96135a41FA155752dc7154CDcaA480f2fBEC1493", [
    ("paused", "paused()"), ("freePoolRemaining", "freePoolRemaining()")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("launched", "launched()")]),
}
jobs = []
for name, (addr, fields) in PRIO.items():
    for fname, sig in fields:
        data = sel(sig) + enc_addr(USER) if sig.endswith("(address)") else sel(sig)
        jobs.append((name, fname, addr, data))
def curl_post(payload, timeout=30):
    pr = subprocess.run(["curl", "-s", "--max-time", str(timeout), "-X", "POST", EP,
                         "-H", "Content-Type: application/json", "--data", payload],
                        capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(pr.stdout)
out = {}
for i in range(0, len(jobs), 25):
    chunk = jobs[i:i+25]
    payload = json.dumps([{"jsonrpc": "2.0", "id": j, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for j, (_, _, to, data) in enumerate(chunk)])
    try:
        resps = curl_post(payload, 30)
    except Exception as e:
        print("chunk fail", type(e).__name__, str(e)[:100]); resps = []
    if isinstance(resps, dict): resps = [resps]
    for (name, fname, addr, _), r in zip(chunk, resps):
        raw = r.get("result") if isinstance(r, dict) else None
        val = None
        if isinstance(raw, str) and raw.startswith("0x") and len(raw) >= 66:
            try: val = int(raw[:66], 16)
            except Exception: val = None
        out.setdefault(name, {})[fname] = val
# merge into prio file
prio = json.load(open(BASE + "hot-leg-run-2026-11-11-0914-prio.json"))
prio["values"].update(out)
json.dump(prio, open(BASE + "hot-leg-run-2026-11-11-0914-prio.json", "w"), indent=1)
prev = json.load(open(BASE + "hot-leg-run-2026-11-11-0859-prio.json"))["values"]
diffs = []
for name, vals in out.items():
    for f, v in vals.items():
        old = prev.get(name, {}).get(f)
        if old != v: diffs.append({"item": name, "field": f, "old": old, "new": v})
print("RETRY VALUES:", json.dumps(out))
print("RETRY DIFFS vs 0859:", json.dumps(diffs))
