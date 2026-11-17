#!/usr/bin/env python3
"""Probe Cosmic Sentinel (temuan sweep run 0201) — read-only.
Kontrak 0x88731d1eb41c36f3d705fdb58b658244c06afc36, situs cosmic-sentinel.pages.dev.
Cek: code/registry bytes, Sourcify, name/symbol/supply/free views, owner,
dan first-mint Transfer-from-zero via eth_getLogs (dataseed, chunk 1000 blok mundur)."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x88731d1eb41c36f3d705fdb58b658244c06afc36"
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

out = {"address": ADDR}
# head
head = None
for ep in EPS:
    try:
        r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=30)
        head = int(r["result"], 16); break
    except Exception:
        continue
out["head"] = head
print("head", head)
# code
code = None
for ep in EPS:
    try:
        r = rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [ADDR, "latest"]}, timeout=60)
        code = r.get("result")
        if code and code != "0x": break
    except Exception as ex:
        out.setdefault("errors", []).append(str(ex))
out["has_code"] = bool(code and code != "0x")
out["code_len"] = (len(code) - 2) // 2 if code else 0
out["registry_bytes"] = bool(code and REG in code.lower())
print("code", out["has_code"], out["code_len"], "registry", out["registry_bytes"])
# Sourcify
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contracts/56/{ADDR}",
                                 headers={"User-Agent": "free-mint-search/0201"})
    with urllib.request.urlopen(req, timeout=25) as r:
        sj = json.loads(r.read().decode())
    out["sourcify"] = "verified"
    out["sourcify_match"] = sj.get("stdJson", {}).get("match") if isinstance(sj.get("stdJson"), dict) else None
except urllib.error.HTTPError as he:
    out["sourcify"] = f"HTTP {he.code}"
except Exception as ex:
    out["sourcify"] = f"error {ex}"
print("sourcify", out["sourcify"])
# views
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
calls = [(ADDR, "name()", [], "name"), (ADDR, "symbol()", [], "symbol"),
         (ADDR, "totalSupply()", [], "totalSupply"), (ADDR, "totalMinted()", [], "totalMinted"),
         (ADDR, "freeMinted()", [], "freeMinted"), (ADDR, "freeRemaining()", [], "freeRemaining"),
         (ADDR, "freeClaimed()", [], "freeClaimed"), (ADDR, "FREE_SUPPLY()", [], "FREE_SUPPLY"),
         (ADDR, "MAX_SUPPLY()", [], "MAX_SUPPLY"), (ADDR, "mintActive()", [], "mintActive"),
         (ADDR, "mintOpen()", [], "mintOpen"), (ADDR, "owner()", [], "owner"),
         (ADDR, "freeMintedBy(address)", [USER], "freeMintedBy_user")]
payload = [{"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
            "params": [{"to": c[0], "data": build(c[1], c[2])}, "latest"]} for i, c in enumerate(calls)]
res = {}
for ep in EPS:
    try:
        r = rpc(ep, payload, timeout=60)
        if isinstance(r, list):
            res = {c[3]: it.get("result") for it, c in zip(r, calls)}
            if any(v for v in res.values()): break
    except Exception as ex:
        out.setdefault("errors", []).append(str(ex))
def dec_str(h):
    if not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:])
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64 + ln].decode("utf-8", "ignore")
    except Exception:
        return None
out["name"] = dec_str(res.get("name"))
out["symbol"] = dec_str(res.get("symbol"))
for k in ("totalSupply", "totalMinted", "freeMinted", "freeRemaining", "freeClaimed",
          "FREE_SUPPLY", "MAX_SUPPLY", "mintActive", "mintOpen", "freeMintedBy_user"):
    out[k] = to_int(res.get(k))
out["owner"] = ("0x" + res["owner"][-40:]) if res.get("owner") and len(res["owner"]) >= 42 else None
print({k: out.get(k) for k in ("name", "symbol", "totalSupply", "totalMinted", "freeMinted",
                               "freeRemaining", "FREE_SUPPLY", "MAX_SUPPLY", "mintActive", "mintOpen", "owner")})
# first-mint probe: Transfer from zero, search backwards in 1000-block chunks (max 10 chunks ~ 7.5 menit x 10)
ZERO_TOPIC = "0x" + "0" * 24 + "0" * 40
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
first = None
if head and out.get("totalSupply"):
    to_b = head
    for _ in range(10):
        frm = to_b - 999
        try:
            r = rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_getLogs",
                             "params": [{"fromBlock": hex(frm), "toBlock": hex(to_b),
                                         "address": ADDR,
                                         "topics": [TRANSFER, ZERO_TOPIC]}]}, timeout=90)
            logs = r.get("result") or []
            if logs:
                first = {"block": int(logs[0]["blockNumber"], 16), "tx": logs[0]["transactionHash"],
                         "count_in_chunk": len(logs)}
                break
            to_b = frm - 1
        except Exception as ex:
            out.setdefault("errors", []).append(f"getLogs {frm}-{to_b}: {ex}")
            break
out["first_mint_transfer"] = first
if first:
    try:
        r = rpc(EPS[0], {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                         "params": [hex(first["block"]), False]}, timeout=30)
        ts = int(r["result"]["timestamp"], 16)
        import datetime
        out["first_mint_wib"] = datetime.datetime.fromtimestamp(
            ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        out["first_mint_unix"] = ts
    except Exception as ex:
        out.setdefault("errors", []).append(str(ex))
print("first_mint", first, out.get("first_mint_wib"))
json.dump(out, open(BASE + "run-2026-11-15-0201-cosmic.json", "w"), indent=1)
print("COSMIC PROBE DONE")
