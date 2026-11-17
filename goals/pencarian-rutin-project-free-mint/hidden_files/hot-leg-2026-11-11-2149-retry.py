#!/usr/bin/env python3
"""Targeted sequential re-read (curl-based) for hot-leg 2026-11-11 21:49 WIB.
Salvage run: block_number OK (132988228) but ALL 65 parallel urllib eth_calls
timed out (burst overload on public RPCs; curl eth_blockNumber just tested
OK at ~2s on dataseed + nodereal). This script re-reads ONLY the two
decision-critical items sequentially via curl: Stampooor (gate-blocked strong
lead) + AgentPals (sold-out watch). Updates the run JSON with an addendum."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
STAMP = "2026-11-11-2149"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a.lower().replace("0x", "").rjust(64, "0")

def eth_call(addr, sig, args=""):
    data = sel(sig) + args
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                       "params": [{"to": addr, "data": data}, "latest"]})
    for ep in ("https://bsc-dataseed.binance.org/", "https://bsc.nodereal.io/"):
        try:
            r = subprocess.run(["curl", "-s", "-m", "10", "-H", "Content-Type: application/json",
                                "-d", body, ep], capture_output=True, timeout=15)
            j = json.loads(r.stdout.decode(errors="replace"))
            if "error" in j:
                last = {"error": str(j["error"])[:120]}; continue
            raw = j.get("result")
            if raw in (None, "0x"): return {"error": "empty-return"}
            if len(raw) >= 66:
                v = raw[2:66]
                if set(v) <= set("0123456789abcdef"):
                    try: return int(v, 16)
                    except Exception: return raw
            return raw
        except Exception as e:
            last = {"error": f"{type(e).__name__}: {str(e)[:90]}"}
            continue
    return last

U = enc_addr(USER)
ITEMS = {
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459",
               [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
                ("FREE_SUPPLY", "FREE_SUPPLY()", ""), ("mintOpen", "mintOpen()", ""),
                ("freeAvailable_user", "freeAvailable(address)", U),
                ("balanceOf_user", "balanceOf(address)", U)]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2",
               [("totalMinted", "totalMinted()", ""), ("freeMinted", "freeMinted()", ""),
                ("hasFreeMinted_user", "hasFreeMinted(address)", U),
                ("balanceOf_user", "balanceOf(address)", U)]),
}
out = {}
t0 = time.time()
for name, (addr, calls) in ITEMS.items():
    out[name] = {}
    for key, sig, args in calls:
        out[name][key] = eth_call(addr, sig, args)
        time.sleep(0.3)
print(json.dumps(out, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
json.dump(out, open(BASE + f"hot-leg-{STAMP}-prio-retry.json", "w"), indent=1)

# Patch run JSON with addendum + recompute changes for these two items vs 21:39 baseline
run = json.load(open(BASE + f"hot-leg-{STAMP}-run.json".replace("-run.json", "-run.json")) if False else open(BASE + "hot-leg-run-2026-11-11-2149.json"))
base = {"Stampooor": {"freeMinted": 862, "totalMinted": 862},
        "AgentPals": {"totalMinted": 301, "freeMinted": 300}}
changes = []
for name, vals in out.items():
    for key, new in vals.items():
        old = base.get(name, {}).get(key)
        if isinstance(new, int) and old is not None and new != old:
            changes.append(f"{name}.{key}: {old} -> {new} (vs 2139-main-reread)")
st = out.get("Stampooor", {})
crossed = isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int) and st["freeMinted"] > 840
pct = (st["freeMinted"] / st["FREE_SUPPLY"] * 100) if isinstance(st.get("freeMinted"), int) and isinstance(st.get("FREE_SUPPLY"), int) else None
run["leg4_retry_targeted_curl"] = {
    "note": "sequential curl eth_call retry after parallel-urllib leg4 failed entirely; only Stampooor + AgentPals re-read",
    "values": out,
    "changes_vs_2139": changes or "NONE",
    "stampooor_crossed": crossed,
    "stampooor_pct": pct,
    "stampooor_slot_open": st.get("freeAvailable_user"),
}
run["stampooor_crossed"] = crossed
if pct is not None:
    run["threshold_watch"] = [f"Stampooor freeMinted {st['freeMinted']}/{st['FREE_SUPPLY']} = {pct:.1f}% (strong-lead needs >70% = >840; slot freeAvailable={st.get('freeAvailable_user')}; age: mintStart 09:00:19 WIB 11 Nov, <24h; STRONG-LEAD-CROSSED={crossed}; GATE-BLOCKED (site stampooor.com/packs/ + stampooor.com both curl 000:0 this run) -> NO preview/mint)"]
json.dump(run, open(BASE + "hot-leg-run-2026-11-11-2149.json", "w"), indent=1)
print("CHANGES:", changes or "NONE")
print("STAMPOOOR crossed:", crossed, "pct:", pct)
