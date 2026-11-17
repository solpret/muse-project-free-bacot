#!/usr/bin/env python3
"""Probe SUDOSAINTS 0x869d330bb48e7ab32da16745ef9a36a69d34f12f for early-lead classification.
Read-only: Sourcify ABI + on-chain views + contractURI/tokenURI + owner + discards check.
No preview, no mint (early leads are never previewed/minted)."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0x869d330bb48e7ab32da16745ef9a36a69d34f12f"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
AGENT_ID = 107187496765866644729837695198686237165740365523485558112864918211974996443404
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
out = {"address": ADDR, "started_wib": "2026-11-11 14:01 WIB"}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None

def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "free-bacot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode(errors="replace")

# 1. Sourcify ABI
try:
    meta = json.loads(get(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi"))
    abi = meta.get("abi", [])
    fns = sorted({e["name"] for e in abi if e.get("type") == "function"})
    out["sourcify"] = {"verified": True, "match": meta.get("match"), "fns": fns}
    print("SOURCIFY verified, match=", meta.get("match"), "fns=", len(fns), flush=True)
    print("FNS:", fns, flush=True)
except Exception as e:
    out["sourcify"] = {"verified": False, "error": f"{type(e).__name__}: {str(e)[:150]}"}
    print("SOURCIFY FAIL", e, flush=True)

# 2. on-chain views (batch eth_call, raw results kept for strings)
VIEWS = ["totalSupply()", "freeMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()", "mintActive()",
         "priceFor(address)", "freeUsed(address)", "balanceOf(address)", "owner()",
         "contractURI()", "name()", "symbol()", "agentRegistry()"]
calls = []
for i, sig in enumerate(VIEWS):
    data = sel(sig) + (enc(USER) if "(address)" in sig else "")
    calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                  "params": [{"to": ADDR, "data": data}, "latest"]})
raw = None
for ep in EPS:
    try:
        r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                            "-H", "Content-Type: application/json", "-d", json.dumps(calls)],
                           capture_output=True, text=True, timeout=30)
        res = json.loads(r.stdout)
        if isinstance(res, list) and len(res) == len(calls):
            raw = res; break
    except Exception:
        continue
vals = {}
if raw is not None:
    for sig, item in zip(VIEWS, raw):
        key = sig.split("(")[0] + ("_user" if "(address)" in sig else "")
        res = item.get("result") if isinstance(item, dict) else None
        if res is None or res == "0x" or (isinstance(item, dict) and "error" in item):
            vals[key] = None
        else:
            vals[key] = res
    # decode strings for contractURI/name/symbol
    def dec_str(hexv):
        try:
            b = bytes.fromhex(hexv[2:])
            if len(b) < 64: return None
            off = int.from_bytes(b[32:64], "big")
            ln = int.from_bytes(b[64+off-32:64+off] if False else b[64:96], "big") if False else None
            # standard ABI: [0:32]=offset, [32:64]=? actually dynamic: first word offset=32, second word length
            ln = int.from_bytes(b[64:96], "big")
            return b[96:96+ln].decode(errors="replace")
        except Exception:
            return None
    for k in ("contractURI", "name", "symbol"):
        if vals.get(k):
            vals[k + "_decoded"] = dec_str(vals[k])
    for k in ("totalSupply", "freeMinted", "FREE_SUPPLY", "MAX_SUPPLY", "mintActive",
              "priceFor_user", "freeUsed_user", "balanceOf_user", "owner", "agentRegistry"):
        if vals.get(k) and k not in ("owner", "agentRegistry"):
            vals[k + "_int"] = to_int(vals[k])
        elif vals.get(k):
            vals[k + "_addr"] = "0x" + vals[k][-40:]
    out["views"] = vals
    print(json.dumps(vals, indent=1), flush=True)
else:
    out["views"] = {"error": "all RPC endpoints failed"}
    print("VIEWS FAIL", flush=True)

# 3. tokenURI(1) for external_url (method I)
try:
    data = sel("tokenURI(uint256)") + format(1, "064x")
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": ADDR, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = subprocess.run(["curl", "-sL", "--max-time", "25", "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                               capture_output=True, text=True, timeout=30)
            res = json.loads(r.stdout)
            if "result" in res and res["result"] not in (None, "0x"):
                b = bytes.fromhex(res["result"][2:])
                ln = int.from_bytes(b[64:96], "big")
                out["tokenURI_1"] = b[96:96+ln].decode(errors="replace")
                print("tokenURI(1):", out["tokenURI_1"][:300], flush=True)
                break
        except Exception:
            continue
    else:
        out["tokenURI_1"] = None
        print("tokenURI(1): None", flush=True)
except Exception as e:
    out["tokenURI_1"] = None
    print("tokenURI FAIL", e, flush=True)

# 4. discards check (owner + contract address vs same-owner-discards.json)
try:
    disc = json.load(open(BASE + "same-owner-discards.json"))
    disc_addrs = set()
    if isinstance(disc, dict):
        for v in disc.values():
            if isinstance(v, dict):
                for kk in ("address", "owner", "deployer"):
                    if v.get(kk): disc_addrs.add(str(v[kk]).lower())
            elif isinstance(v, str):
                disc_addrs.add(v.lower())
    elif isinstance(disc, list):
        for v in disc:
            if isinstance(v, str): disc_addrs.add(v.lower())
    owner = vals.get("owner_addr")
    out["discards"] = {"file_entries": len(disc_addrs),
                       "contract_in_discards": ADDR.lower() in disc_addrs,
                       "owner": owner,
                       "owner_in_discards": (owner.lower() in disc_addrs) if owner else None}
    print("DISCARDS:", out["discards"], flush=True)
except Exception as e:
    out["discards"] = {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    print("DISCARDS FAIL", e, flush=True)

json.dump(out, open(BASE + "run-2026-11-11-1401-probe-sudo.json", "w"), indent=1)
print("PROBE DONE", flush=True)
