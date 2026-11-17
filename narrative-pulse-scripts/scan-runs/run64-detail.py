#!/usr/bin/env python3
"""Run 64 detail: identity + buy evidence for the 4 top paid ...7777 tokens,
contract creations in window, and overlap with run-63 CORLA 27-set. Read-only."""
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
            print("call retry", to[:10], e, flush=True); time.sleep(3)
    return None

def dec_str(r):
    if not r: return None
    try: return abi_decode(["string"], bytes.fromhex(r[2:]))[0]
    except Exception: return "0x:" + (r or "")[:80]

TOKS = ["0x7526782e635c2f4f9d63a7d4736194158d937777",
        "0x3e612ed93b07239efc7db9da05ff07b7ad6f7777",
        "0x455e2e30de81c25ec7788d6c08431dbfc2b77777",
        "0x729a625d9649bbe2802d2cbb4d4ba6c1bb477777"]
for tok in TOKS:
    print("TOKEN", tok, flush=True)
    print("  name()", dec_str(call(tok, sel("name()"))), flush=True)
    print("  symbol()", dec_str(call(tok, sel("symbol()"))), flush=True)
    r = call(tok, sel("decimals()"))
    print("  decimals()", int(r, 16) if r else None, flush=True)
    r = call(tok, sel("totalSupply()"))
    print("  totalSupply()", int(r, 16) if r else None, flush=True)
    r = call(tok, sel("owner()"))
    print("  owner()", ("0x" + r[-40:]) if r and len(r) >= 42 else (r or "")[:80], flush=True)
    r = call(tok, sel("tokenURI()"))
    print("  tokenURI()", (r or "")[:200], flush=True)

sent = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-sent.json"))
paid = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-paid.json"))
paid63 = json.load(open("/home/hatch/workspace/narrative-pulse/scan-runs/run63-paid.json"))
set63 = set(paid63.get("0x4a9c499574ea003846e81522d59aa4c27ca47777", []))
print("RUN63 CORLA 27-set size:", len(set63), flush=True)
for tok in TOKS:
    s = set(paid[tok])
    print(f"OVERLAP {tok[:10]} vs run63-CORLA-set: {len(s & set63)}/{len(s)} identical={s == set63}", flush=True)

BUY = "0xb6f9de95"; SELL = "0x791ac947"; APPR = "0x095ea7b3"
def val_bnb(v):
    try:
        return int(v, 16) / 1e18 if isinstance(v, str) and v.startswith("0x") else float(v) / 1e18
    except Exception:
        return 0.0

for tok in TOKS:
    ws = set(paid[tok])
    nb = ns = na = 0; tot = 0.0; times = []
    for w in ws:
        rr = sent["results"].get(w)
        if not rr or not rr.get("ok"): continue
        for t in rr["in_window"]:
            if t["input_prefix"] == BUY:
                nb += 1; tot += val_bnb(t["value"]); times.append(t["time_wib"])
            elif t["input_prefix"] == SELL:
                ns += 1
            elif t["input_prefix"] == APPR:
                na += 1
    print(f"EVID {tok[:10]} wallets={len(ws)} buy0xb6f9={nb} sell0x791a={ns} approve={na} buy_value_bnb~{tot:.4f} time={min(times) if times else None}..{max(times) if times else None}", flush=True)

# deployments in window
hashes = []
for w, rr in sent["results"].items():
    if not rr.get("ok"): continue
    for t in rr["in_window"]:
        if t["input_prefix"] == "0x60806040":
            hashes.append((w, t))
print("CREATION txs in window:", len(hashes), flush=True)
created = []
for w, t in hashes:
    r = None
    for _ in range(3):
        try:
            r = fast_rpc.race("eth_getTransactionReceipt", [t["hash"]]); break
        except Exception as e:
            print("receipt retry", t["hash"][:12], e, flush=True); time.sleep(3)
    ca = (r or {}).get("contractAddress")
    created.append((t["hash"], w, ca, t["time_wib"], t["value"]))
    time.sleep(0.5)
print("CREATED:", flush=True)
for h, w, ca, tm, v in created:
    mark = " <-- IS TOP4" if (ca or "").lower() in [x.lower() for x in TOKS] else ""
    print(f"  {h[:14]} {w[:10]} {ca} {tm} val={v}{mark}", flush=True)
json.dump(created, open("/home/hatch/workspace/narrative-pulse/scan-runs/run64-created.json", "w"), indent=1)

# sample buy transfer for first token: pair verification
T_TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
tok = TOKS[0]
recv = set(paid[tok])
sample = None
for w in recv:
    rr = sent["results"].get(w)
    if not rr or not rr.get("ok"): continue
    for t in rr["in_window"]:
        if t["input_prefix"] == BUY:
            sample = (w, t); break
    if sample: break
print("SAMPLE", sample[0][:12], sample[1]["hash"][:14], sample[1]["time_wib"], flush=True)
r = fast_rpc.race("eth_getTransactionReceipt", [sample[1]["hash"]])
pair = None
for lg in r.get("logs") or []:
    if (lg.get("address") or "").lower() == tok.lower() and (lg.get("topics") or [None])[0] == T_TRANSFER:
        topics = lg["topics"]
        print("  TOK Transfer from=", "0x" + topics[1][-40:], "to=", "0x" + topics[2][-40:],
              "amount_raw=", int(lg["data"], 16), flush=True)
        pair = "0x" + topics[1][-40:]
if pair:
    for fn in ["token0()", "token1()"]:
        rr2 = call(pair, sel(fn))
        print("  pair", pair, fn, ("0x" + rr2[-40:]) if rr2 else None, flush=True)
print("DONE", flush=True)
