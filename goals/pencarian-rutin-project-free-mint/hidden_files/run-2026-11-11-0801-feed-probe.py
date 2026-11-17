#!/usr/bin/env python3
"""Feed probe run 2026-11-11 0801 WIB: on-chain verify the 14 early-shape
contracts from run-2026-11-11-0801-feed-shape.json (S1/S2 false, early True).
Reads name/symbol/owner/costOf(user,1)/mintsLeft(user)/PRICE/totalSupply +
eth_getCode registry-bytes check. Read-only; writes
run-2026-11-11-0801-feed-probe.json + -names.json. Owner checked against
same-owner-discards.json.
"""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TS = "2026-11-11-0801"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None
def dec_str(h):
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[0:32], "big")
        ln = int.from_bytes(b[off:off+32], "big")
        return b[off+32:off+32+ln].decode("utf-8", "ignore")
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_batch(addr, calls):
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if isinstance(res, list) and len(res) == len(calls):
                return res
        except Exception:
            continue
    return None

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=25)
            code = r.get("result") or ""
            return len(bytes.fromhex(code[2:])) if code.startswith("0x") else 0, REGISTRY[2:].lower() in code.lower()
        except Exception:
            continue
    return None, None

shapes = json.load(open(BASE + "run-2026-11-11-0801-feed-shape.json"))
early = [s["address"] for s in shapes.get("shapes", []) if s.get("early_shape")]
print("EARLY-SHAPE addrs:", len(early), flush=True)

discards = set()
try:
    d = json.load(open(BASE + "same-owner-discards.json"))
    discards = {str(x).lower() for x in (d if isinstance(d, list) else d.keys())}
except Exception as e:
    print("discards load fail:", e, flush=True)

VIEWS = ["name()", "symbol()", "owner()", "totalSupply()", "PRICE()"]
def probe(addr):
    calls, keys = [], []
    for sig in VIEWS:
        calls.append({"jsonrpc": "2.0", "id": len(calls)+1, "method": "eth_call",
                      "params": [{"to": addr, "data": sel(sig)}, "latest"]})
        keys.append(sig.split("(")[0])
    calls.append({"jsonrpc": "2.0", "id": 6, "method": "eth_call",
                  "params": [{"to": addr, "data": sel("costOf(address,uint256)") + enc(USER) + "0"*63 + "1"}, "latest"]})
    keys.append("costOf_user_1")
    calls.append({"jsonrpc": "2.0", "id": 7, "method": "eth_call",
                  "params": [{"to": addr, "data": sel("mintsLeft(address)") + enc(USER)}, "latest"]})
    keys.append("mintsLeft_user")
    res = raw_batch(addr, calls)
    out = {"address": addr}
    if res is None:
        out["_batch_fail"] = True
        print(addr, "BATCH FAIL", flush=True)
        return addr, out
    for item, key in zip(res, keys):
        r = item.get("result") if isinstance(item, dict) else None
        if key in ("name", "symbol"):
            out[key] = dec_str(r) if r else None
        elif key == "owner":
            out[key] = ("0x" + r[-40:]) if r and len(r) >= 42 else None
        else:
            out[key] = to_int(r)
    code_len, reg = get_code(addr)
    out["code_len"] = code_len
    out["registry_bytes"] = reg
    out["ownerInDiscards"] = (out.get("owner") or "").lower() in discards
    out["verifiedAt"] = next((s.get("verifiedAt") for s in shapes.get("shapes", []) if s.get("address") == addr), None)
    print(addr, out.get("name"), "| supply:", out.get("totalSupply"), "| owner:", out.get("owner"),
          "| discards:", out.get("ownerInDiscards"), "| costOf:", out.get("costOf_user_1"),
          "| mintsLeft:", out.get("mintsLeft_user"), "| reg:", reg, flush=True)
    return addr, out

t0 = time.time()
out = {}
with ThreadPoolExecutor(max_workers=8) as ex:
    for addr, d in ex.map(probe, early):
        out[addr] = d
json.dump(out, open(BASE + f"run-{TS}-feed-probe.json", "w"), indent=1)
names = {a: {"name": d.get("name"), "symbol": d.get("symbol")} for a, d in out.items()}
json.dump(names, open(BASE + f"run-{TS}-feed-names.json", "w"), indent=1)
print(f"PROBE DONE in {time.time()-t0:.1f}s n={len(out)}", flush=True)
