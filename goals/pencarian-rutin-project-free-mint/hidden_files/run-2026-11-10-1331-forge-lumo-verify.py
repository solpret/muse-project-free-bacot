#!/usr/bin/env python3
"""Run 1331 verify Forge Pass + Lucky Moments (LUMO) from Boltbook post 13:20 WIB (read-only)."""
import json, subprocess, urllib.request
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
CANDS = {
    "Forge Pass": "0x733358348e07c46332a01c76e2bf6ee5d40a6d89",
    "Lucky Moments (LUMO)": "0x1e340592665889735c1f871aa13d038fa58bd09e",
}
VIEWS = ["name()", "symbol()", "totalSupply()", "totalMinted()", "freeMinted()",
         "freeClaimed()", "paidMinted()", "FREE_SUPPLY()", "MAX_SUPPLY()",
         "FREE_PER_WALLET()", "MAX_PER_WALLET()", "mintOpen()", "owner()",
         "agentRegistry()", "registry()", "price()", "gateSigner()",
         "freeClaimed(address)", "balanceOf(address)", "freeMinted(address)",
         "claimable(address)"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def raw_batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        base = sig.split("(")[0]
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = base + "_user"
        else:
            data = sel(sig); key = base
        calls.append({"jsonrpc":"2.0","id":i+1,"method":"eth_call",
                      "params":[{"to":addr,"data":data},"latest"]})
        keys.append(key)
    for ep in EPS:
        try:
            res = post_rpc(ep, calls, timeout=25)
            if not isinstance(res, list) or len(res) != len(calls): continue
            outd = {}
            for item, key in zip(res, keys):
                if isinstance(item, dict) and "error" in item: outd[key] = None
                elif isinstance(item, dict): outd[key] = item.get("result")
                else: outd[key] = None
            return outd
        except Exception:
            continue
    return {k: None for k in keys}
def fetch_json(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent":"free-bacot/1331"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())
out = {}
for name, addr in CANDS.items():
    d = {"address": addr}
    raw = raw_batch(addr, VIEWS)
    for k, v in raw.items():
        if k in ("name","symbol"):
            try: d[k] = bytes.fromhex(v[130:]).split(b"\x00")[0].decode() if v and len(v) > 130 else None
            except Exception: d[k] = None
        elif k in ("owner","agentRegistry","registry","gateSigner"):
            try: d[k] = "0x" + v[-40:] if v and len(v) >= 42 else None
            except Exception: d[k] = None
        else:
            d[k] = to_int(v)
    try:
        meta = fetch_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi", timeout=30)
        d["sourcify"] = meta.get("match") or meta.get("status") or "found"
        abi = meta.get("abi", [])
        d["abi_fns"] = sorted({e["name"] for e in abi if e.get("type")=="function"})
        d["registry_ref"] = any("60B9262456dE011F7d15a54CdD8c48bAaa8B022F".lower() in json.dumps(e).lower() for e in abi)
    except Exception as e:
        d["sourcify"] = f"ERROR {e}"
        d["abi_fns"] = []; d["registry_ref"] = None
    # discards check
    disc = json.load(open(f"{BASE}/same-owner-discards.json"))
    d["owner_discarded"] = any((x.get("owner") or "").lower() == (d.get("owner") or "").lower() for x in disc if isinstance(x, dict))
    out[name] = d
    print(json.dumps(d, indent=1), flush=True)
json.dump(out, open(f"{BASE}/run-2026-11-10-1331-forge-lumo-verify.json","w"), indent=1)
print("WROTE run-2026-11-10-1331-forge-lumo-verify.json")
