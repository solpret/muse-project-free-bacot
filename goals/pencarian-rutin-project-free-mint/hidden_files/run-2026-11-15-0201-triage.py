#!/usr/bin/env python3
"""Triage run 2026-11-15 02:01 WIB: 2 new contracts.
(1) 0x259531a84BcBF484daAc8432BdAB80d5409140CA — new on Boltbook EN+ZH run 0201.
(2) 0x9b20550c0c4494e302fd51a86734957b5f14d7ab — Boltbook hot-leg 0159, Sourcify 404 then.
Read-only; checks eth_getCode for registry bytes, Sourcify verification,
name/symbol/totalSupply + free views. No preview/mint."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
def build(sig, args):
    d = sel(sig)
    for a in args:
        d += enc_addr(a) if isinstance(a, str) and a.startswith("0x") and len(a) == 42 else enc_u(int(a))
    return d
def rpc(ep, payload, timeout=60):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(out)
def batch(ep, calls):
    payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                "params": [{"to": c[0], "data": build(c[1], c[2])}, "latest"]} for i, c in enumerate(calls)]
    r = rpc(ep, payload)
    res = {}
    if isinstance(r, list):
        for item, c in zip(r, calls):
            v = item.get("result")
            res[c[3]] = v
    return res

def decode_str(hexv):
    if not hexv or hexv == "0x": return None
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[32:64], "big")
        ln = int.from_bytes(b[64 + off - 32:64 + off], "big") if False else int.from_bytes(b[32 + 32:64 + 32], "big")
        # standard ABI string: [0:32]=offset, [32:64]=len, [64:]=data
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "ignore")
    except Exception:
        return None

ADDRS = ["0x259531a84BcBF484daAc8432BdAB80d5409140CA",
         "0x9b20550c0c4494e302fd51a86734957b5f14d7ab"]
out = {}
for addr in ADDRS:
    e = {"address": addr}
    # code
    code = None
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                         "params": [addr, "latest"]}, timeout=60)
            code = r.get("result")
            if code and code != "0x": break
        except Exception as ex:
            e.setdefault("code_errors", []).append(str(ex))
    e["has_code"] = bool(code and code != "0x")
    e["code_len"] = (len(code) - 2) // 2 if code else 0
    e["registry_bytes"] = bool(code and REG in code.lower())
    # Sourcify
    try:
        req = urllib.request.Request(
            f"https://sourcify.dev/server/v2/contracts/56/{addr}",
            headers={"User-Agent": "free-mint-search/0201"})
        with urllib.request.urlopen(req, timeout=25) as r:
            sj = json.loads(r.read().decode())
        e["sourcify"] = sj.get("status") or sj.get("stdJson") and "verified" or "verified?"
        e["sourcify_match"] = sj.get("stdJson", {}).get("match") if isinstance(sj.get("stdJson"), dict) else None
    except urllib.error.HTTPError as he:
        e["sourcify"] = f"HTTP {he.code}"
    except Exception as ex:
        e["sourcify"] = f"error {ex}"
    # views
    calls = [(addr, "name()", [], "name"), (addr, "symbol()", [], "symbol"),
             (addr, "totalSupply()", [], "totalSupply"), (addr, "totalMinted()", [], "totalMinted"),
             (addr, "freeMinted()", [], "freeMinted"), (addr, "freeRemaining()", [], "freeRemaining"),
             (addr, "freeClaimed()", [], "freeClaimed"), (addr, "FREE_SUPPLY()", [], "FREE_SUPPLY"),
             (addr, "MAX_SUPPLY()", [], "MAX_SUPPLY"), (addr, "mintActive()", [], "mintActive"),
             (addr, "mintOpen()", [], "mintOpen"), (addr, "owner()", [], "owner")]
    res = {}
    ok = False
    for ep in EPS:
        try:
            res = batch(ep, calls)
            if any(v for v in res.values()): ok = True; break
        except Exception as ex:
            e.setdefault("view_errors", []).append(str(ex))
    e["views_raw"] = res
    e["name"] = decode_str(res.get("name"))
    e["symbol"] = decode_str(res.get("symbol"))
    e["totalSupply"] = to_int(res.get("totalSupply"))
    e["totalMinted"] = to_int(res.get("totalMinted"))
    e["freeMinted"] = to_int(res.get("freeMinted"))
    e["freeRemaining"] = to_int(res.get("freeRemaining"))
    e["freeClaimed"] = to_int(res.get("freeClaimed"))
    e["FREE_SUPPLY"] = to_int(res.get("FREE_SUPPLY"))
    e["MAX_SUPPLY"] = to_int(res.get("MAX_SUPPLY"))
    e["mintActive"] = to_int(res.get("mintActive"))
    e["mintOpen"] = to_int(res.get("mintOpen"))
    e["owner"] = ("0x" + res["owner"][-40:]) if res.get("owner") and len(res["owner"]) >= 42 else None
    out[addr] = e
    print(addr, "| code:", e["has_code"], e["code_len"], "| registry:", e["registry_bytes"],
          "| sourcify:", e["sourcify"], "| name:", e["name"], e["symbol"],
          "| supply:", e["totalSupply"], e["totalMinted"], "| free:", e["freeMinted"], e["freeRemaining"],
          "| owner:", e["owner"])
json.dump(out, open(BASE + "run-2026-11-15-0201-triage.json", "w"), indent=1)
print("TRIAGE DONE")
