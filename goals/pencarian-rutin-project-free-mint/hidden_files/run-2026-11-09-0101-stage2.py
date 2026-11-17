#!/usr/bin/env python3
"""Run 0101 stage 2: (a) walkback for AGENT BOTS + AGENT PASS (early-lead check:
any mints in the 3000 blocks before the scan window?); (b) track-C 5c
shape-check for new ERC-20 mint contracts (mint_count>=10, max 20, skip
already-checked). Read-only except writing the 5c output json."""
import json, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
import onchain_nft_scan as scan

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
REG = "60b9262456de011f7d15a54cdd8c48baaa8b022f"
out = {}

# (a) walkback: 3 x 1000-block chunks before scan window start 132438824
for name, addr in [("AGENT BOTS", "0xef4Fa905b107A431FcaEB50F1183B712dc3eb9D6"),
                   ("AGENT PASS", "0x6a90E032D50C6FF44608167f7a8634c77ACAeE34")]:
    total = 0
    chunks = []
    for frm, to in [(132435824, 132436823), (132436824, 132437823), (132437824, 132438823)]:
        try:
            logs, _ = scan.ankr_logs(frm, to, [scan.TRANSFER, scan.ZERO_TOPIC])
        except Exception as e:
            chunks.append({"chunk": f"{frm}-{to}", "error": str(e)})
            continue
        mine = [l for l in logs if l.get("address", "").lower() == addr.lower()]
        chunks.append({"chunk": f"{frm}-{to}", "mints": len(mine)})
        total += len(mine)
        print(f"  {name} {frm}-{to}: {len(mine)} mints", flush=True)
    out[name] = {"address": addr, "earlier_mints_3000b": total, "chunks": chunks}
    print(name, "earlier mints (3000 blocks before window):", total, flush=True)

# (b) 5c shape-check
scan_out = json.load(open(f"{BASE}/run-2026-11-09-0101-scan.json"))
e20 = scan_out.get("erc20_mint_contracts_list", [])
checked = json.load(open(f"{BASE}/track-c-scan-checked.json"))
checked_set = set(checked.get("checked", [])) | {k for k in checked if k.startswith("0x")}
cands = sorted([e for e in e20 if e.get("mint_count", 0) >= 10],
               key=lambda x: -x.get("mint_count", 0))
new = [e for e in cands if e["address"] not in checked_set][:20]
print(f"5c: {len(cands)} with mint_count>=10, {len(new)} new to check (cap 20)", flush=True)

def sourcify(addr):
    url = f"https://sourcify.dev/server/v2/contracts/56/{addr}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception as e:
        return {"_error": str(e)}

shapes = {}
for e in new:
    addr = e["address"]
    sc = sourcify(addr)
    abi = None
    try:
        abi = sc.get("stdJson", {}).get("output", {}).get("abi") or sc.get("abi")
    except Exception:
        pass
    if abi:
        fns = [f.get("name") for f in abi if f.get("type") == "function"]
        free = [f for f in fns if "free" in f.lower()]
        mint = any("mint" in f.lower() for f in fns)
        quote = any("quote" in f.lower() or "cost" in f.lower() for f in fns)
        agent = any("agent" in f.lower() or "registry" in f.lower() for f in fns)
        token = all(x in fns for x in ["name", "symbol", "decimals", "totalSupply"])
        s1 = bool(mint and quote and free and agent)
        s2 = bool(token and any("mintfree" in f.lower() or f.lower() == "mintfree" for f in fns) and free and agent)
        shapes[addr] = {"mint_count": e["mint_count"], "S1": s1, "S2": s2,
                        "mint": mint, "quote": quote, "free": free, "agent": agent,
                        "token": token, "registry_bytes": REG in json.dumps(sc).lower()}
    else:
        shapes[addr] = {"mint_count": e["mint_count"], "error": sc.get("_error"),
                        "S1": False, "S2": False}
    print("  5c", addr, shapes[addr], flush=True)
out["5c"] = shapes
out["5c_targets"] = [e["address"] for e in new]
out["5c_dropped"] = len(cands) - len(new)
json.dump(out, open(f"{BASE}/run-2026-11-09-0101-5c.json", "w"), indent=1)
print("STAGE2 DONE", flush=True)
