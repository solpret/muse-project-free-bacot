#!/usr/bin/env python3
"""Run 1831 parent: gate checks (C/H/I) + fresh free reads for DinoAgent + Tri333,
plus 5c-extra Sourcify shape-check for the 9 ERC20 from scan 1831. Read-only except own output."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc.publicnode.com/", "https://bsc-dataseed2.bnbchain.org/"]
REG = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None
def call(addr, sig, arg=None, arg2=None):
    data = sel(sig) + (enc(arg) if arg else "") + (arg2.rjust(64, "0") if arg2 else "")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            return to_int(r[0])
        except Exception:
            continue
    return None
def call_str(addr, sig):
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": sel(sig)}, "latest"])], endpoint=ep, timeout=10)
            raw = bytes.fromhex(r[0][2:])
            ln = int.from_bytes(raw[32:64], "big")
            return raw[64:64+ln].decode(errors="replace")
        except Exception:
            continue
    return None
def head_block():
    for ep in EPS:
        try:
            r = batch([("eth_blockNumber", [])], endpoint=ep, timeout=10)
            return int(r[0], 16)
        except Exception:
            continue
    return None
def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contracts/56/{addr}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.loads(resp.read().decode())
        src = d.get("stdJson", {}).get("sources", {})
        text = json.dumps(src)
        return {"verified": True, "match": d.get("match"), "has_url": ("http" in text),
                "urls": [w for w in ["http://" in text and text[text.find('http'):text.find('http')+120]] if w],
                "source_len": len(text)}
    except Exception as e:
        return {"verified": False, "error": str(e)[:200]}

out = {"run": "1831", "head": head_block(), "wib": time.strftime("%H:%M")}
# ---- DinoAgent + Tri333 ----
for label, addr in [("DinoAgent", "0xcE19D6A5FF15e088D4bf23614242927139084895"),
                    ("Tri333", "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f")]:
    e = {"address": addr}
    e["name"] = call_str(addr, "name()"); e["symbol"] = call_str(addr, "symbol()")
    for v in ["totalSupply()", "totalMinted()", "freeMinted()", "freeClaimed()", "freeLeft()",
              "FREE_SUPPLY()", "FREE_CAP()", "MAX_SUPPLY()", "mintOpen()", "paidMinted()",
              "paidMintedCount()", "totalMinted()"]:
        e[v] = call(addr, v)
    e["freeClaimed_user"] = call(addr, "freeClaimed(address)", USER)
    e["freeCount_user"] = call(addr, "freeCount(address)", USER)
    e["balanceOf_user"] = call(addr, "balanceOf(address)", USER)
    e["contractURI"] = call_str(addr, "contractURI()")
    e["tokenURI_1"] = call_str(addr, "tokenURI(uint256)") if False else None
    e["sourcify"] = sourcify(addr)
    out[label] = e
# tokenURI(1) needs uint arg
def call_token_uri(addr, tid):
    data = sel("tokenURI(uint256)") + str(tid).rjust(64, "0")
    for ep in EPS:
        try:
            r = batch([("eth_call", [{"to": addr, "data": data}, "latest"])], endpoint=ep, timeout=10)
            raw = bytes.fromhex(r[0][2:])
            ln = int.from_bytes(raw[32:64], "big")
            return raw[64:64+ln].decode(errors="replace")
        except Exception:
            continue
    return None
for label, addr in [("DinoAgent", "0xcE19D6A5FF15e088D4bf23614242927139084895"),
                    ("Tri333", "0x157D860e30b6c6d4dC0abe3bD6e66e659A9d524f")]:
    out[label]["tokenURI_1"] = call_token_uri(addr, 1)

# ---- 5c-extra: 9 ERC20 from scan 1831 ----
erc20 = ["0x5D28C44bAd17d75D2207C4A042b73AF5297971C2","0x62926C83729fB7d54b211C2dd9D5A9116be38a87",
"0x68Cf8Eb34F99d8c86F9E5518B9b5Cea45b1Bb889","0x2760e5D359EB84512207A91C02E2eC29fd30a1b2",
"0x71E8639b242FFaf9e2a5ab0247FaacD17E25eE4E","0x54Ff11c7a6850a442E0029Bd454ef000e5131191",
"0x28a4F0BbdC1bE886f9e5a290e6598A83F248B224","0xD89651A8B8B79C7F65543Dd428837b98D63ba60E",
"0x597bE001b48891620Da1440CdfA82D08297dfB45"]
FREE_VIEWS = ["freeSharesRemaining","freeClaimed","freeFor","freeLeft","freeUsed","freeAvailable",
              "freeSharePoolExhausted","freeSharesClaimed","freeMinted","freeMint","isFreeMintAvailable"]
res = []
for a in erc20:
    url = f"https://sourcify.dev/server/v2/contracts/56/{a}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.loads(resp.read().decode())
        abi = d.get("abi", [])
        names = [f.get("name","") for f in abi if isinstance(f, dict)]
        has_mint = any(n in ("mint","mintFree","mintPaid") for n in names)
        has_quote = any("rice" in n or "quote" in n.lower() or n in ("currentPriceFor","price") for n in names)
        has_free = [n for n in names if n in FREE_VIEWS]
        has_reg = REG.lower() in json.dumps(d.get("stdJson",{}).get("sources",{})).lower() or any(
            n in ("agentRegistry","AGENT_ID_REGISTRY","agentIdRegistry","AGENT_ID") for n in names)
        is_token = all(n in names for n in ("name","symbol","decimals","totalSupply"))
        noarg_free = "mintFree" in names
        res.append({"address": a, "verified": True, "match": d.get("match"),
                    "S1": bool(has_mint and has_quote and has_free and has_reg),
                    "S2": bool(is_token and noarg_free and has_free and has_reg),
                    "detail": {"mint": has_mint, "quote": has_quote, "free_views": has_free,
                               "registry": has_reg, "is_token": is_token, "name": call_str(a, "name()"),
                               "symbol": call_str(a, "symbol()")}})
    except Exception as ex:
        res.append({"address": a, "verified": False, "error": str(ex)[:150]})
out["track_c_5c_extra"] = res
json.dump(out, open(f"{BASE}/run-2026-11-07-1831-gate-dino-tri333.json", "w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
