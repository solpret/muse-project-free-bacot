#!/usr/bin/env python3
"""Run 2026-11-09 1201 — META BLOOM shape-check + ORDIagent re-check. Read-only."""
import json, subprocess, urllib.request, sys
sys.path.insert(0, "/home/hatch/workspace/custom-connectors/custom.ankr/bin")
from Crypto.Hash import keccak
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/"]
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
OUT = {}

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v not in (None, "0x") else None
    except Exception: return None
def post(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig: data = sel(sig) + enc(USER); key = base + "_user"
        elif "(uint256)" in sig: data = sel(sig) + "0" * 63 + "1"; key = base + "_1"
        else: data = sel(sig); key = base
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]}); keys.append(key)
    for ep in EPS:
        try:
            res = post(ep, calls)
            if not isinstance(res, list) or len(res) != len(calls): continue
            return {k: (None if (isinstance(it, dict) and "error" in it) else (to_int(it.get("result")) if isinstance(it, dict) else None)) for it, k in zip(res, keys)}
        except Exception: continue
    return None
def sourcify_abi(addr):
    try:
        with urllib.request.urlopen(f"https://sourcify.dev/server/v2/contract/56/{addr}", timeout=20) as r:
            d = json.load(r)
        return d.get("stdJson", {}).get("output", {}).get("abi") or d.get("abi")
    except Exception as e:
        return {"_error": str(e)}
def code_has_registry(addr):
    for ep in EPS:
        try:
            r = post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [addr, "latest"]})
            code = (r.get("result") or "").lower()
            return REG in code
        except Exception: continue
    return None

MB = "0x381c23f3859abb093c1275292a700b1089073f05"
abi = sourcify_abi(MB)
fns = [it for it in (abi if isinstance(abi, list) else []) if isinstance(it, dict) and it.get("type") == "function"]
names = [f.get("name", "") for f in fns]
lower = [n.lower() for n in names]
QUOTE = ["quote", "costof", "priceof", "getprice", "mintprice", "cost"]
FREE_VIEWS = ["freesharesremaining", "freeclaimed", "freefor", "freeleft", "freeused",
              "freeavailable", "freesharepoolexhausted", "freessharesclaimed", "freeminted",
              "freeremaining", "free_cap", "freecount", "freeallowance", "freemint"]
has_mint = any("mint" in n for n in lower)
has_quote = any(any(q in n for q in QUOTE) for n in lower)
free_views = [n for n in names if n.lower() in FREE_VIEWS]
has_reg_abi = any("agent" in n for n in lower)
reg_bytes = code_has_registry(MB)
mb = {"address": MB, "sourcify": "exact_match" if isinstance(abi, list) else str(abi)[:120],
      "fns": len(names), "has_mint": has_mint, "has_quote": has_quote,
      "free_views": free_views, "agent_fns": [n for n in names if "agent" in n.lower()],
      "registry_bytes_in_code": reg_bytes,
      "S1": bool(has_mint and has_quote and free_views and (has_reg_abi or reg_bytes)),
      "names": names}
# free-pool + user-slot reads (best effort across common view names)
views = ["freeSharesRemaining()", "freeClaimed()", "freeMinted()", "freeRemaining()",
         "FREE_CAP()", "FREE_SHARES()", "FREE_SUPPLY()", "totalShares()", "totalMinted()",
         "totalSupply()", "mintOpen()", "isOpen()", "launched()", "saleStart()",
         "openedAt()", "freeClaimed(address)", "freeFor(address)", "owner()"]
mb["reads"] = batch(MB, views)
# quote(user,1) if a quote fn exists
for q in ["quote(address,uint256)", "costOf(address,uint256)", "quoteFor(address,uint256)"]:
    r = batch(MB, [q])
    if r and list(r.values())[0] is not None:
        mb["quote_user_1"] = {q: list(r.values())[0]}; break
# owner vs same-owner discards
try:
    disc = json.load(open(f"{HF}/same-owner-discards.json"))
    owners = set()
    if isinstance(disc, dict):
        for v in disc.values():
            if isinstance(v, dict):
                o = v.get("owner") or v.get("owner_address")
                if o: owners.add(o.lower())
            elif isinstance(v, str): owners.add(v.lower())
    elif isinstance(disc, list):
        for v in disc:
            if isinstance(v, str): owners.add(v.lower())
    mb["owner_in_discards"] = (mb["reads"] or {}).get("owner") and hex(mb["reads"]["owner"]) in owners
    mb["discard_owner_count"] = len(owners)
except Exception as e:
    mb["discards_check_error"] = str(e)
OUT["meta_bloom"] = mb
print("META BLOOM:", json.dumps(mb, indent=1)[:2500], flush=True)

# ORDIagent re-check
OA = "0x7D10516D08f3bE98aaFD9Ac4169E6Cc30D6bCeB8"
oa_reads = batch(OA, ["isOpen()", "openedAt()", "saleStart()", "freeClaimed()",
                      "FREE_SHARES()", "totalShares()", "sold()", "freeClaimed(address)"])
OUT["ordiagent"] = {"sale": OA, "reads": oa_reads}
print("ORDIAGENT:", json.dumps(oa_reads), flush=True)
with open(f"{HF}/run-2026-11-09-1201-metabloom-ordiagent.json", "w") as f:
    json.dump(OUT, f, indent=1)
print("WROTE run-2026-11-09-1201-metabloom-ordiagent.json", flush=True)
