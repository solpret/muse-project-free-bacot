#!/usr/bin/env python3
"""Triage for free-mint-search run 2026-11-13 22:01 WIB.
New Boltbook leads: Wraith, ME24, Azimuth, SnakeAgent, MORFO, Sable, Ember,
Vorn, Frie + FERO (upcoming). Read-only; no preview/mint.
Writes run-2026-11-13-2201-triage.json."""
import json, subprocess, time, urllib.request
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
t0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u(n): return format(n, "064x")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def build_data(sig, args):
    d = sel(sig)
    for a in args:
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            d += enc_addr(a)
        else:
            d += enc_u(int(a))
    return d

def raw_batch(addr, views):
    calls, keys = [], []
    for i, (key, sig, args) in enumerate(views):
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": build_data(sig, args)}, "latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls):
                continue
            out = {}
            for it, key in zip(res, keys):
                if not isinstance(it, dict) or "error" in it or it.get("result") in (None, "0x"):
                    out[key] = None
                else:
                    r = it["result"]
                    out[key] = to_int(r[:66]) if len(r) >= 66 else r
            return out
        except Exception:
            continue
    return None

def get_code(addr):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                              "params": [addr, "latest"]}, timeout=20)
            if isinstance(r, dict) and isinstance(r.get("result"), str):
                code = r["result"]
                return {"bytes": (len(code) - 2) // 2 if code.startswith("0x") else None,
                        "registry_bytes": REGISTRY in code.lower(),
                        "code_prefix": code[:80]}
        except Exception:
            continue
    return None

def sourcify(addr):
    url = "https://sourcify.dev/server/v2/contracts/56/" + addr
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            d = json.load(resp)
            std = d.get("stdJson", {}) or {}
            return {"status": d.get("status"), "verifiedAt": std.get("verifiedAt"),
                    "match": (d.get("match") or [{}])[0].get("type") if d.get("match") else None}
    except Exception as e:
        return {"status": "fetch_error", "error": str(e)[:120]}

U = [USER]
VIEWS = [
    ("totalSupply", "totalSupply()", []), ("totalMinted", "totalMinted()", []),
    ("freeMinted", "freeMinted()", []), ("freeClaimed", "freeClaimed()", []),
    ("freeRemaining", "freeRemaining()", []), ("freeLeft", "freeLeft()", []),
    ("FREE_SUPPLY", "FREE_SUPPLY()", []), ("FREE_CAP", "FREE_CAP()", []),
    ("FREE_MAX", "FREE_MAX()", []), ("MAX_SUPPLY", "MAX_SUPPLY()", []),
    ("mintOpen", "mintOpen()", []), ("saleOpen", "saleOpen()", []),
    ("saleStart", "saleStart()", []), ("mintOpensAt", "mintOpensAt()", []),
    ("mintStart", "mintStart()", []), ("price", "price()", []),
    ("paidMinted", "paidMinted()", []),
    ("freeAvailable_user", "freeAvailable(address)", U),
    ("freeClaimed_user", "freeClaimed(address)", U),
    ("balanceOf_user", "balanceOf(address)", U),
    ("name", "name()", []), ("symbol", "symbol()", []),
]

ITEMS = {
    "Wraith": "0x4a318eb842c8c95876e895258bc70d0bee767def",
    "ME24": "0x391a13af7819e36a84f16754c133ca39d08d273d",
    "Azimuth": "0x85f1522401aaf9e3f19e7f79cc4b2fb3969a8f77",
    "SnakeAgent": "0xf7c1ba2286cee6eef10cc264664168fd015127b1",
    "MORFO": "0xb22ac9b2ac90e77f342cba2cc38b28eb8c718186",
    "Sable": "0x23d356173ff227d5bf6d622f4a8907f208871d76",
    "Ember": "0x4241866a617161c73762dfc693a3597439b9d1e5",
    "Vorn": "0x8c2f7bec2d7b31d9c706d25eb4d008f0754ce255",
    "Frie": "0x6fdb4d8e9868540dafadc9b23ce9bbdbcd1e8da5",
    "FERO": "0x76FB0A89c8618A1d7Cf3E2123ae43E5aeb36f2F4",
}

# hot-leg seen info for these addresses
seen = {}
try:
    seen_all = json.load(open(BASE + "hot-leg-seen.json"))
    for addr in ITEMS.values():
        for k, v in seen_all.items():
            if addr.lower() in k.lower() or (isinstance(v, dict) and addr.lower() in json.dumps(v).lower()):
                seen[addr] = v
                break
except Exception as e:
    seen = {"error": str(e)[:200]}

out = {"started_wib": "2026-11-13T22:01+07:00", "items": {}, "hotleg_seen": seen}
for name, addr in ITEMS.items():
    views = raw_batch(addr, VIEWS)
    code = get_code(addr)
    src = sourcify(addr)
    out["items"][name] = {"address": addr, "views": views, "code": code, "sourcify": src}
    print(name, json.dumps({"views": views, "code_bytes": (code or {}).get("bytes"),
          "registry_bytes": (code or {}).get("registry_bytes"), "sourcify": src})[:600], flush=True)

out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-13-2201-triage.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
