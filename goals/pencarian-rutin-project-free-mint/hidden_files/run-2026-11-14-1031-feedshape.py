#!/usr/bin/env python3
"""Run 2026-11-14 10:31 WIB: (1) Ankr pre-flight via scan.ankr_logs;
(2) Sourcify ABI shape-check (S1/S2, hot-leg heuristic) for new feed contracts;
(3) on-chain AGENT_ID() value + basic views for each (WANGCAI-variant lesson).
Read-only. Writes run-2026-11-14-1031-feedshape.json."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/")
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-rpc.publicnode.com/"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
              "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed"]
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
t0 = time.time()
out = {"started_wib": "2026-11-14T10:31+07:00"}
# --- (2)+(3) shape checks ---
def fetch_abi(addr):
    url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
    try:
        p = subprocess.run(["curl", "-sS", "-m", "60", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True, timeout=70)
        if p.returncode != 0 or not p.stdout:
            return None, f"curl rc={p.returncode} err={p.stderr[:100]}"
        return json.loads(p.stdout).get("abi", []), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def post_rpc(ep, payload, timeout=60):
    o = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 10).stdout
    return json.loads(o)
def call1(addr, data):
    payload = {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
               "params": [{"to": addr, "data": data}, "latest"]}
    for ep in EPS:
        try:
            r = post_rpc(ep, payload, timeout=60)
            if isinstance(r, dict) and isinstance(r.get("result"), str) and r["result"] not in (None, "0x"):
                return r["result"]
        except Exception:
            continue
    return None
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None
NEW = [("0x2dA715175F0298d240b6551c19DedcF62172fe23", "2026-11-14T03:31:22Z"),
       ("0xE9563DF445e8625A28017333d757394F8fB8abcD", "2026-11-14T03:29:53Z"),
       ("0x6Ce231182E1663B2b454f43a1aB0C3C6F6660941", "2026-11-14T03:28:46Z"),
       ("0x893e89Ef732E62c3C07bf683E8C73fb2ffD2C4cF", "2026-11-14T03:26:54Z"),
       ("0x1F02F7d9460b3569bDB17f7C5c21C4B35828aA22", "2026-11-14T03:21:09Z"),
       ("0x50A4ffAF7A1Fc22f648895924f7525eF32A54cF4", "2026-11-14T03:19:07Z"),
       ("0x7143467fd3Bc5e4358cfaf1Da71833aDB15657CC", "2026-11-14T03:17:37Z"),
       ("0x3ee8689F5566d079Ed068823471e034A470bAC63", "2026-11-14T03:15:23Z"),
       ("0x2296367f74b2ec266cf4667d98501ae7110f5a58", "boltbook-1031"),
       ("0x4bfc32d8ea0981739f328ce8e16bb7398bafa4e0", "boltbook-1031"),
       ("0xc755f66b7873e53bb4f006956e49a1c8daf66930", "boltbook-1031"),
       ("0xdb7257dbf18ca1539159c64534ffd68ef14c2f32", "boltbook-1031"),
       ("0xe4eE5375910C692a0316D800063250ad0db69359", "boltbook-1031")]
results = []
for addr, vat in NEW:
    abi, err = fetch_abi(addr)
    if abi is None:
        results.append({"address": addr, "verifiedAt": vat, "S1": None, "S2": None,
                        "error": err, "status": "shape-check-failed"})
        print(addr, "ABI FETCH FAILED", err, flush=True); continue
    names = set()
    fns = {}
    for e in abi:
        if e.get("type") == "function":
            names.add(e["name"]); fns.setdefault(e["name"], []).append(e)
    has_mint = any(n.lower().startswith("mint") for n in names)
    has_quote = bool(names & {"quote", "cost", "getQuote", "mintCost", "price", "getPrice"})
    free_views = sorted(names & set(FREE_VIEWS))
    agent_ref = bool(names & {"agentId", "agentRegistry", "registry", "getAgentId",
                              "agentGate", "AgentGate", "AGENT_ID_REGISTRY", "agentIdRegistry", "AGENT_ID"})
    is_token = bool(names & {"name", "symbol", "decimals", "totalSupply"})
    mintfree = "mintFree" in fns and any(len(e.get("inputs", [])) == 0 for e in fns["mintFree"])
    s1 = bool(has_mint and has_quote and free_views and agent_ref)
    s2 = bool(is_token and mintfree and (names & {"freeClaimed", "freeMinted"})
              and (names & {"FREE_SLOTS", "FREE_SUPPLY"}) and agent_ref)
    # on-chain: AGENT_ID() value + basic views (catches WANGCAI-variant)
    agent_id_raw = call1(addr, sel("AGENT_ID()"))
    agent_id = None
    if agent_id_raw and len(agent_id_raw) >= 66:
        agent_id = "0x" + agent_id_raw[-40:]
    ts = to_int(call1(addr, sel("totalSupply()")))
    tm = to_int(call1(addr, sel("totalMinted()")))
    mo = to_int(call1(addr, sel("mintOpen()")))
    fc = to_int(call1(addr, sel("freeClaimed()")))
    nm = call1(addr, sel("name()"))
    results.append({"address": addr, "verifiedAt": vat, "S1": s1, "S2": s2,
                    "has_mint": has_mint, "has_quote": has_quote, "free_views": free_views,
                    "agent_ref": agent_ref, "is_token": is_token, "n_fns": len(names),
                    "AGENT_ID_value": agent_id, "AGENT_ID_is_registry": (agent_id or "").lower() == REGISTRY.lower(),
                    "totalSupply": ts, "totalMinted": tm, "mintOpen": mo, "freeClaimed": fc,
                    "name_raw": (nm[:130] if nm else None), "status": "checked"})
    print(addr, "S1", s1, "S2", s2, "AGENT_ID", agent_id, "ts", ts, "tm", tm, "mo", mo, "fc", fc, flush=True)
out["shapes"] = results
out["elapsed_s"] = round(time.time() - t0, 1)
json.dump(out, open(BASE + "run-2026-11-14-1031-feedshape.json", "w"), indent=1)
print("DONE elapsed", out["elapsed_s"])
