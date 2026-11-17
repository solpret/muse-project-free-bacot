#!/usr/bin/env python3
"""Run 63 detail: token 0x4a9c...7777 identity, 23 creation contractAddresses,
and buy-vs-transfer check for the 0x4a9c receives. Read-only."""
import json, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
import fast_rpc
from eth_abi import decode as abi_decode
from Crypto.Hash import keccak

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def call(to, data):
    for _ in range(3):
        try:
            return fast_rpc.race("eth_call", [{"to": to, "data": data}, "latest"])
        except Exception as e:
            print("call retry", e, flush=True); time.sleep(3)
    return None

TOK = "0x4a9c499574ea003846e81522d59aa4c27ca47777"
for fn in ["name()", "symbol()"]:
    r = call(TOK, sel(fn))
    try:
        print(fn, abi_decode(["string"], bytes.fromhex(r[2:]))[0] if r else None, flush=True)
    except Exception as e:
        print(fn, "decode ERR", e, "raw", (r or "")[:200], flush=True)
r = call(TOK, sel("decimals()"))
print("decimals()", int(r, 16) if r else None, flush=True)
r = call(TOK, sel("totalSupply()"))
print("totalSupply()", int(r, 16) if r else None, flush=True)

sent = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run63-sent.json"))
hashes = []
for w, rr in sent["results"].items():
    if not rr.get("ok"):
        continue
    for t in rr["in_window"]:
        if t["input_prefix"] == "0x60806040":
            hashes.append(t["hash"])
created = []
for h in hashes:
    for _ in range(3):
        try:
            r = fast_rpc.race("eth_getTransactionReceipt", [h]); break
        except Exception as e:
            print("receipt retry", h[:12], e, flush=True); time.sleep(3); r = None
    created.append((h, (r or {}).get("contractAddress")))
    time.sleep(1)
print("CREATED:", flush=True)
for h, c in created:
    print(" ", h[:14], c, "IS-4A9C" if (c or "").lower() == TOK.lower() else "", flush=True)
json.dump(created, open("/home/hatch/workspace/narrative-pulse/scan-runs/run63-created.json", "w"), indent=1)

# buy-vs-transfer: fetch full receipt of a 0xb6f9de95 swap tx from a wallet in the 27-set
paid = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run63-paid.json"))
recv = set(paid[TOK])
sample = None
for w, rr in sent["results"].items():
    if w in recv:
        for t in rr["in_window"]:
            if t["input_prefix"] == "0xb6f9de95":
                sample = (w, t); break
    if sample:
        break
print("SAMPLE", sample[0][:12], sample[1]["hash"][:14], sample[1]["time_wib"], flush=True)
r = fast_rpc.race("eth_getTransactionReceipt", [sample[1]["hash"]])
T_TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
for lg in r.get("logs") or []:
    if (lg.get("address") or "").lower() == TOK.lower() and (lg.get("topics") or [None])[0] == T_TRANSFER:
        topics = lg["topics"]
        print("  4A9C Transfer from=", "0x" + topics[1][-40:], "to=", "0x" + topics[2][-40:],
              "amount_raw=", int(lg["data"], 16), flush=True)
print("DONE", flush=True)
