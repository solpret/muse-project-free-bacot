#!/usr/bin/env python3
"""Parent triage for run 2231 first-seen wave contracts (read-only).
Sourcify ABI via curl retry + on-chain views (PRICE/quote/free views/baseURI/agentRegistry).
None = failed read, never zero."""
import json, subprocess, urllib.request, time
from concurrent.futures import ThreadPoolExecutor
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-2231"
RPCS = ["https://bsc-dataseed1.bnbchain.org", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org/", "https://bsc-dataseed2.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"

CONTRACTS = [
 ("Buzzkill", "0x4854cE8e3eC3a1AcB0dd4EAE3f547E5A214c2a0d"),
 ("Whale Alert", "0xA1ecd20893Dbb2BEDc7141434d20125F028E871B"),
 ("Blend In", "0x9cA2C07B67CD97109f40378aE90c815feB878B1F"),
 ("Fresh Hatch", "0xC3Ba321124e0F621Da8C4A0c1875705c83d6ce8C"),
 ("Lion's Share", "0x6AC03204aFE631D673938Eb82D2F121B015eAB3F"),
 ("Otter Nonsense", "0xFF6b4bb96C86c0E2e2F942F907F9F6eD1bBbCaDf"),
 ("PRICKLY", "0x4e557ae3824ae3E837Aa4a8Da2A45A04501BEAEE"),
 ("unicorn.exe", "0x965286f9662a6dACeFf9bD3C4D58ABaBDD9C87A5"),
 ("Hot Springs", "0xc7bFeA97f02E9118eD88111A79E43a9CE481B96A"),
 ("Down Under", "0x5Bb425ad2069de77ABC8c341d4d322Bcff26c550"),
 ("V64", "0xfDeAD0B025B270751347325fa143531ACe0570e2"),
 ("N30", "0xC877c3FAC533e142074afCb685F304B692250608"),
 ("Pulse Quokka Agent", "0x2FDA062a7B3990A5575aF1a282713a5Be746dd94"),
]

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")

def raw(to, data):
    for rpc in RPCS:
        try:
            body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                               "params": [{"to": to, "data": data}, "latest"]}).encode()
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=8) as r: out = json.load(r)
            if "error" in out: continue
            v = out["result"]
            if not v or v == "0x": return None
            return v
        except Exception:
            continue
    return None

def as_int(v):
    if isinstance(v, str) and v.startswith("0x"):
        try: return int(v, 16)
        except Exception: return v
    return v

def dec_str(v):
    if not isinstance(v, str) or not v.startswith("0x") or len(v) < 130: return None
    try:
        ln = int(v[66:130], 16)
        return bytes.fromhex(v[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def sourcify_abi(addr):
    for attempt in range(3):
        try:
            r = subprocess.run(["curl", "-s", "-m", "20",
                                f"https://sourcify.dev/server/v2/contracts/56/{addr}/source"],
                               capture_output=True, text=True, timeout=30)
            if r.returncode == 0 and r.stdout:
                d = json.loads(r.stdout)
                std = d.get("stdJson", {})
                abi = std.get("abi") or (std.get("output", {}).get("abi"))
                if abi:
                    fns = sorted({f.get("name") for f in abi if f.get("type") == "function" and f.get("name")})
                    return {"verified": True, "functions": fns}
                return {"verified": True, "functions": [], "note": "abi empty"}
        except Exception as e:
            time.sleep(2)
    return {"verified": False, "functions": None, "note": "fetch failed after 3 tries"}

def triage(item):
    name, addr = item
    d = {"address": addr, "name": name}
    d["sourcify"] = sourcify_abi(addr)
    fns = d["sourcify"].get("functions") or []
    d["totalSupply"] = as_int(raw(addr, sel("totalSupply()")))
    d["totalMinted"] = as_int(raw(addr, sel("totalMinted()")))
    d["freeClaimed"] = as_int(raw(addr, sel("freeClaimed()")))
    d["freeMinted"] = as_int(raw(addr, sel("freeMinted()")))
    d["FREE_SUPPLY"] = as_int(raw(addr, sel("FREE_SUPPLY()")))
    d["PRICE"] = as_int(raw(addr, sel("PRICE()")))
    d["price"] = as_int(raw(addr, sel("price()")))
    d["quote_user_1"] = as_int(raw(addr, sel("quote(address,uint256)") + enc(USER) + enc_uint(1)))
    d["mintOpen"] = as_int(raw(addr, sel("mintOpen()")))
    d["AGENT_REGISTRY"] = raw(addr, sel("AGENT_REGISTRY()"))
    d["agentRegistry"] = raw(addr, sel("agentRegistry()"))
    d["BASE_URI"] = dec_str(raw(addr, sel("BASE_URI()")))
    d["baseURI"] = dec_str(raw(addr, sel("baseURI()")))
    d["balanceOf_user"] = as_int(raw(addr, sel("balanceOf(address)") + enc(USER)))
    print(name, json.dumps(d)[:900], flush=True)
    return name, d

out = {}
t0 = time.time()
with ThreadPoolExecutor(max_workers=4) as ex:
    for name, d in ex.map(triage, CONTRACTS):
        out[name] = d
        json.dump(out, open(f"{BASE}/run-{TS}-triage-wave.json", "w"), indent=1)
print("DONE in %.1fs" % (time.time() - t0), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-triage-wave.json", "w"), indent=1)
