#!/usr/bin/env python3
"""Intensive watch for GHOST + SONO early leads (FREE BACOT).
Read-only: eth_call views only. No preview/mint/approve/swap/tx.
Compares fresh reads against state file, updates state, prints a short
machine-readable verdict block for the worker to deliver on material change.
Material change = strong-lead promotion (free% >= 25% + slot open),
free pool exhausted, user slot lost, mint closed, or 48h age-exclusion.
"""
import json, sys, time, urllib.request
from datetime import datetime, timezone, timedelta
from Crypto.Hash import keccak

STATE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/ghost-sono-watch-state.json"
RPCS = ["https://bsc-dataseed1.ninicoin.io", "https://bsc.publicnode.com",
        "https://bsc-dataseed.binance.org", "https://bsc-dataseed1.bnbchain.org",
        "https://bsc-dataseed2.bnbchain.org"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
WIB = timezone(timedelta(hours=7))

CONTRACTS = {
    "GHOST": {"addr": "0x474949EBCee9E3A425B6d8033f1E2c8DD3Ae755e",
              "first_mint_wib": "2026-11-05 20:38:08", "free_supply": None},
    "SONO":  {"addr": "0x1eF7588Dff561b7390D3AF23d06E684D64217419",
              "first_mint_wib": "2026-11-05 20:41:43", "free_supply": 2260},
}

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode())
    return "0x" + k.hexdigest()[:8]

def call(to, data):
    body = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                       "params": [{"to": to, "data": data}, "latest"], "id": 1}).encode()
    for rpc in RPCS:
        try:
            req = urllib.request.Request(rpc, data=body, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
            r = json.loads(urllib.request.urlopen(req, timeout=20).read())
            if r.get("result") not in (None, "0x"):
                return r["result"]
        except Exception:
            continue
    return None

def u(h):
    return None if h is None else int(h, 16)

def read_one(addr):
    out = {}
    for sig in ["totalSupply()", "freeMinted()", "MAX_SUPPLY()", "FREE_SUPPLY()", "mintOpen()"]:
        out[sig] = u(call(addr, sel(sig)))
    out["freeClaimed(user)"] = u(call(addr, sel("freeClaimed(address)") + USER[2:].rjust(64, "0")))
    out["balanceOf(user)"] = u(call(addr, sel("balanceOf(address)") + USER[2:].rjust(64, "0")))
    return out

def main():
    try:
        state = json.load(open(STATE))
    except Exception:
        state = {"items": {}}
    now = datetime.now(WIB)
    now_s = now.strftime("%Y-%m-%d %H:%M:%S")
    events = []
    resolved = []
    for name, cfg in CONTRACTS.items():
        r = read_one(cfg["addr"])
        prev = state["items"].get(name, {})
        free_supply = r.get("FREE_SUPPLY()") or cfg["free_supply"] or prev.get("free_supply")
        free_pct = None
        if r.get("freeMinted()") is not None and free_supply:
            free_pct = round(100.0 * r["freeMinted()"] / free_supply, 2)
        # velocity vs previous read
        vel = None
        if prev.get("freeMinted") is not None and r.get("freeMinted()") is not None and prev.get("ts"):
            try:
                t0 = datetime.strptime(prev["ts"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=WIB)
                mins = max(1.0, (now - t0).total_seconds() / 60.0)
                vel = round((r["freeMinted()"] - prev["freeMinted"]) / mins, 2)
            except Exception:
                vel = None
        # FAIL-CLOSED: slot hilang hanya bila baca BERHASIL dan menunjukkan
        # claimed (freeClaimed==1) atau sudah punya (balance>0). Bila salah
        # satu baca None (RPC gagal), slot_open=None -> tidak diputuskan,
        # tidak ada event, status dipertahankan (bukan slot_lost).
        fc = r.get("freeClaimed(user)")
        bal = r.get("balanceOf(user)")
        if fc is None or bal is None:
            slot_open = None
        else:
            slot_open = (fc == 0 and bal == 0)
        first = datetime.strptime(cfg["first_mint_wib"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=WIB)
        age_h = round((now - first).total_seconds() / 3600.0, 1)
        age_excluded = age_h > 48
        pool_done = (free_supply is not None and r.get("freeMinted()") is not None
                     and r["freeMinted()"] >= free_supply)
        closed = r.get("mintOpen()") == 0
        promoted = (free_pct is not None and free_pct >= 25 and slot_open
                    and not age_excluded and not pool_done)
        status = prev.get("status", "early")
        new_status = status
        if promoted and status != "strong":
            new_status = "strong"
            events.append(f"PROMOSI STRONG LEAD: {name} free {free_pct}% (>=25%), slot terbuka, umur {age_h} jam, vel {vel}/mnt")
        if pool_done and status != "soldout":
            new_status = "soldout"
            events.append(f"FREE POOL HABIS: {name} freeMinted {r.get('freeMinted()')}/{free_supply}")
        if slot_open is False and status not in ("slot_lost", "soldout"):
            new_status = "slot_lost"
            events.append(f"SLOT USER HILANG: {name} freeClaimed={r.get('freeClaimed(user)')}, balance={r.get('balanceOf(user)')}")
        if slot_open is True and status == "slot_lost":
            # pulih dari slot_lost palsu (mis. baca RPC gagal sebelumnya)
            new_status = "early"
        if closed and status != "closed":
            new_status = "closed"
            events.append(f"MINT DITUTUP: {name} mintOpen=0")
        if age_excluded and status != "age_excluded":
            new_status = "age_excluded"
            events.append(f"AGE-EXCLUDED: {name} umur {age_h} jam > 48 jam")
        if new_status in ("soldout", "slot_lost", "closed", "age_excluded"):
            resolved.append(name)
        state["items"][name] = {
            "ts": now_s, "totalSupply": r.get("totalSupply()"),
            "freeMinted": r.get("freeMinted()"), "max_supply": r.get("MAX_SUPPLY()"),
            "free_supply": free_supply, "free_pct": free_pct,
            "mintOpen": r.get("mintOpen()"), "slot_open": slot_open,
            "velocity_per_min": vel, "age_h": age_h, "status": new_status,
        }
        print(f"{name}: totalSupply={r.get('totalSupply()')} freeMinted={r.get('freeMinted()')} "
              f"free%={free_pct} vel={vel}/mnt slot_open={slot_open} age={age_h}h status={new_status}")
    state["last_run"] = now_s
    json.dump(state, open(STATE, "w"), indent=1)
    print("EVENTS:" + (" NONE" if not events else ""))
    for e in events:
        print(" - " + e)
    print("RESOLVED: " + ",".join(resolved) if resolved else "RESOLVED: none")
    print("BOTH_RESOLVED: " + str(len(resolved) == 2 or all(
        state["items"].get(n, {}).get("status") in ("soldout", "slot_lost", "closed", "age_excluded")
        for n in CONTRACTS)))

if __name__ == "__main__":
    main()
