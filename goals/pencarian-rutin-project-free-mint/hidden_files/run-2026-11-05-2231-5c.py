#!/usr/bin/env python3
"""FREE BACOT run 2231 route 5c — ERC-20 backlog sale-shape check (read-only).
Top 20 by window mint_count (>=10), skipping already-checked. Sourcify ABI only."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
TS = "2026-11-05-2231"
REG = "60b9262456de011f7d15a54cdD8c48bAaa8B022F".lower()

TODO = [
 "0xa1057326821680F98290897f2edf39E1926C8cAc",
 "0xF677c719c1aF23Fd9a8B8972ca3d1d6D538bBffa",
 "0x1f8955E640Cbd9abc3C3Bb408c9E2E1f5F20DfE6",
 "0x5e1A6b3041873b05d21C24Cce8c1af763846BeA7",
 "0x2eA26Bc29042763c6afdBda3C8E451bD5D0b8377",
 "0xe6cae4094352a670c3eb0fcbDa17c898b71c7F2A",
 "0x0c84aED253EaaB9b7263665D7e213B7aEC718f23",
 "0xBee5804df012745F51980926d7726c971AA26cb5",
 "0xFB06c427c752890A529a4269f33823435307a55b",
 "0xf156d97202D715f869c6dF6E1F8685b1744CDACC",
 "0x76096218ea7E6e1a3C6A549c88e2928C633B5F63",
 "0xc3B6ef4604FD2B6245f0719db438Cb69Fd9E6fDD",
 "0xa9251ca9DE909CB71783723713B21E4233fbf1B1",
 "0x9705241E663B8963E94F111bB2FbeB3638666666",
 "0x8CAfc39863386538B04172B268Bdd38E9f626E94",
 "0xa08D18c6c437677Bd2a4A65Fae5fAE991B714165",
 "0xC58C1117DA964aEbe91fEF88f6f5703e79bdA574",
 "0x2E070f34d831DaA7c7a811D701644942d2C70f95",
 "0xAc5A5d4cbd6c0780E8b0Aa06AD330A94C6002881",
 "0x9F10a122a921d25Fa9084955c87c3FcAB103267F",
]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeCount", "freeSupply"]

def fetch_abi(addr):
    for attempt in range(2):
        try:
            r = subprocess.run(["curl", "-s", "-m", "15",
                                f"https://sourcify.dev/server/v2/contracts/56/{addr}/source"],
                               capture_output=True, text=True, timeout=25)
            if r.returncode == 0 and r.stdout:
                d = json.loads(r.stdout)
                std = d.get("stdJson", {})
                abi = std.get("abi") or (std.get("output", {}).get("abi"))
                if abi:
                    return abi
                return "no-abi"
        except Exception:
            time.sleep(2)
    return None

def shape(abi):
    if abi is None: return {"S1": None, "S2": None, "note": "sourcify fetch failed"}
    if abi == "no-abi": return {"S1": None, "S2": None, "note": "sourcify no abi"}
    fns = {f.get("name") for f in abi if f.get("type") == "function" and f.get("name")}
    src = json.dumps(abi).lower()
    has_mint = bool(fns & {"mint", "mintFree", "claimFree", "mintShare", "buyShare"})
    has_quote = bool(fns & {"quote", "cost", "getPrice", "PRICE", "price"})
    free = sorted(fns & set(FREE_VIEWS))
    agent = ("60b9262456de011f7d15a54cdd8c48baaa8b022f" in src) or bool(
        fns & {"agentRegistry", "AGENT_REGISTRY", "agentId", "AgentGate"})
    tokenish = bool(fns & {"name", "symbol", "decimals", "totalSupply"})
    s1 = has_mint and has_quote and bool(free) and agent
    s2 = tokenish and ("mintFree" in fns) and bool(free) and agent
    return {"S1": s1, "S2": s2, "mint": has_mint, "quote": has_quote,
            "free": free, "agent": agent, "token": tokenish,
            "functions": sorted(fns)[:60]}

def check(addr):
    abi = fetch_abi(addr)
    r = shape(abi)
    r["address"] = addr
    print(addr, "S1:", r["S1"], "S2:", r["S2"], "mint:", r.get("mint"),
          "quote:", r.get("quote"), "free:", r.get("free"), "agent:", r.get("agent"),
          flush=True)
    return addr, r

out = {}
t0 = time.time()
with ThreadPoolExecutor(max_workers=5) as ex:
    for addr, r in ex.map(check, TODO):
        out[addr] = r
        json.dump(out, open(f"{BASE}/run-{TS}-5c-shape.json", "w"), indent=1)
print("DONE in %.1fs; pass: %s" % (time.time() - t0,
      [a for a, r in out.items() if r.get("S1") or r.get("S2")]), flush=True)
json.dump(out, open(f"{BASE}/run-{TS}-5c-shape.json", "w"), indent=1)
