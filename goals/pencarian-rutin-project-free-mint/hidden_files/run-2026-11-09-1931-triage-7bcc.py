#!/usr/bin/env python3
"""Triage run 2026-11-09 19:31 WIB — 0x7BcC29c5 (Sourcify feed new, hot-leg 19:29 S2-flagged).
Read-only: contract state + first-mint search via dataseed eth_getLogs (Ankr 401).
Writes run-2026-11-09-1931-triage-7bcc.json"""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0x7BcC29c5405286b4Dd8b5b23FE7097F9EE65e4e5"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def call(sig, args=""):
    data = sel(sig) + args
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": ADDR, "data": data}, "latest"]}, timeout=25)
            res = r.get("result")
            if res is None or res == "0x":
                continue
            return res
        except Exception:
            continue
    return None

def to_int(v):
    try:
        return int(v, 16) if v and v != "0x" else None
    except Exception:
        return v

def to_str(v):
    if not v or v == "0x":
        return None
    try:
        b = bytes.fromhex(v[2:])
        # ABI string: offset(32) + len(32) + data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception:
        return v

out = {"address": ADDR, "started_wib": "2026-11-09 19:31 WIB"}
# head block
for ep in EPS:
    try:
        r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
        out["block"] = int(r["result"], 16)
        break
    except Exception:
        continue
print("BLOCK", out.get("block"), flush=True)

views = {
    "name": ("name()", "str"), "symbol": ("symbol()", "str"),
    "totalMinted": ("totalMinted()", "int"), "freeMinted": ("freeMinted()", "int"),
    "FREE_SUPPLY": ("FREE_SUPPLY()", "int"), "MAX_SUPPLY": ("MAX_SUPPLY()", "int"),
    "paidPrice": ("paidPrice()", "int"), "DEFAULT_PAID_PRICE": ("DEFAULT_PAID_PRICE()", "int"),
    "registry": ("registry()", "addr"), "owner": ("owner()", "addr"),
    "hasFreeMinted_user": ("hasFreeMinted(address)", "int", enc(USER)),
    "balanceOf_user": ("balanceOf(address)", "int", enc(USER)),
}
for k, spec in views.items():
    sig, kind = spec[0], spec[1]
    args = spec[2] if len(spec) > 2 else ""
    raw = call(sig, args)
    if raw is None:
        out[k] = None
    elif kind == "int":
        out[k] = to_int(raw)
    elif kind == "str":
        out[k] = to_str(raw)
    elif kind == "addr":
        out[k] = "0x" + raw[-40:] if len(raw) >= 42 else raw
    print(k, "=", out[k], flush=True)

# same-owner discards check
try:
    disc = json.load(open(f"{BASE}/same-owner-discards.json"))
    owners = set()
    if isinstance(disc, list):
        for e in disc:
            if isinstance(e, dict):
                owners.add(str(e.get("owner", "")).lower())
                owners.add(str(e.get("address", "")).lower())
            elif isinstance(e, str):
                owners.add(e.lower())
    out["owner_in_discards"] = (out.get("owner") or "").lower() in owners
    out["discards_count"] = len(disc)
except Exception as e:
    out["owner_in_discards"] = None
    out["discards_error"] = str(e)
print("owner_in_discards:", out.get("owner_in_discards"), flush=True)

# first-mint search: Transfer events from zero address, dataseed, 1000-block chunks
# backwards from head. Contract verified 2026-11-09T12:26:25Z; search back up to 20000 blocks.
TRANSFER = "0x" + keccak.new(digest_bits=256, data=b"Transfer(address,address,uint256)").hexdigest()
ZERO_PAD = "0x" + "0" * 64
head = out.get("block") or 0
first = None
searched = []
if head:
    frm = head
    while frm > head - 20000 and first is None:
        to = frm
        frm = max(head - 20000, frm - 999)
        payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                   "params": [{"fromBlock": hex(frm), "toBlock": hex(to), "address": ADDR,
                               "topics": [TRANSFER, ZERO_PAD]}]}
        ok = False
        for ep in EPS:
            try:
                r = post_rpc(ep, payload, timeout=30)
                res = r.get("result")
                if isinstance(res, list):
                    ok = True
                    searched.append([frm, to, len(res)])
                    if res:
                        # earliest log in window (ascending order)
                        first = res[0]
                        first["window"] = [frm, to]
                    break
            except Exception:
                continue
        if not ok:
            searched.append([frm, to, "error"])
            break
        print("logs window", frm, to, "->", (len(res) if ok else "err"), flush=True)
out["log_windows_searched"] = searched
if first:
    out["first_mint"] = {"block": int(first["blockNumber"], 16),
                         "tx": first["transactionHash"],
                         "tokenId": int(first["topics"][3], 16) if len(first.get("topics", [])) > 3 else None}
    # block timestamp via dataseed eth_getBlockByNumber (fast_rpc rule: dataseed ok)
    blk = first["blockNumber"]
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [blk, False]}, timeout=25)
            ts = r.get("result", {}).get("timestamp")
            if ts:
                out["first_mint"]["timestamp"] = int(ts, 16)
                break
        except Exception:
            continue
    print("first_mint:", out["first_mint"], flush=True)
else:
    print("first_mint: NOT FOUND in searched windows", flush=True)

with open(f"{BASE}/run-2026-11-09-1931-triage-7bcc.json", "w") as f:
    json.dump(out, f, indent=1)
print("TRIAGE DONE", flush=True)
