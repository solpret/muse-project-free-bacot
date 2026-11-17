#!/usr/bin/env python3
"""Hot-leg 2059 legs 1-3: Sourcify new (3) + Boltbook GLOOP-slow/Pokechain/Wisps/Orin + carryover retry + NUSA/Oddlode/Project402 fresh reads.
Run 2026-11-08 21:04:38 WIB. Lightweight: no chain-wide scan, no snapshot writes.
Leg 3 uses direct dataseed JSON-RPC batch (fast_rpc eth_call hit HTTP 429 last run)."""
import json, subprocess, time
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2104"
NOW = "2026-11-08T21:04:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
        "freeCardsRemaining"}
AGENT = {"agentId", "agentRegistry", "registry", "AGENT_ID", "AGENT_REGISTRY", "hasAgentId"}
RPC = "https://bsc-dataseed.bnbchain.org/"

seen = json.load(open(BASE + "hot-leg-seen.json"))
log = {"run": "free-mint-hot-leg 2026-11-08 21:04:38 WIB legs1-3"}
t0 = time.time()

def curl_json(url, payload=None, timeout=20):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if payload is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def shape_check(addr, source):
    if addr.lower() == REGISTRY.lower() or addr.lower() in {e.lower() for e in EXCLUDED}:
        return {"addr": addr, "skipped": "registry-or-excluded"}
    try:
        code = curl_json(RPC, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                "params": [addr, "latest"]}).get("result")
    except Exception as ex:
        return {"addr": addr, "error": f"eth_getCode {ex}"}
    if code == "0x":
        seen[addr] = {"first_seen_wib": NOW, "source": source,
                      "status": "checked-not-contract",
                      "note": "eth_getCode 0x - EOA/wallet address, not a contract; no sale shape, not a lead."}
        return {"addr": addr, "result": "EOA-checked-not-contract"}
    try:
        abi = curl_json(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi",
                        timeout=20).get("abi", [])
        names = {e["name"] for e in abi if e.get("type") == "function"}
    except Exception as ex:
        return {"addr": addr, "error": f"ABI fetch {ex}"}
    if not names:
        return {"addr": addr, "result": "ABI-0-functions-unverified-not-recorded"}
    s1 = any(n.lower().startswith("mint") for n in names) and bool(names & {"quote", "cost"}) \
        and bool(names & FREE) and bool(names & AGENT)
    s2 = bool(names & {"name", "symbol", "decimals", "totalSupply"}) and "mintFree" in names \
        and bool(names & {"freeClaimed", "freeMinted"}) and bool(names & {"FREE_SLOTS", "FREE_SUPPLY"}) \
        and bool(names & AGENT)
    seen[addr] = {"first_seen_wib": NOW, "source": source,
                  "status": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
                  "note": f"S1={s1} S2={s2} fns={sorted(names)}"}
    return {"addr": addr, "result": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
            "S1": s1, "S2": s2, "n_fns": len(names)}

# Leg 1: 3 Sourcify-feed contracts new since the 20:54 run
new_feed = ["0xa1269485458f923E8C3aF644660c3F9D39C4753f",
            "0xc1BBbbB78eF33a26D1aB0Df020b8A2b9F7a51b27",
            "0x284C4d785B13D29e65b3328b31272c13bEbEd462"]
log["leg1_sourcify_new"] = [shape_check(a, "sourcify-feed") for a in new_feed]

# Leg 2: Boltbook new addresses (GLOOP slow lane, Pokechain, Wisps, Orin) + carryover 3 unverified retry
bolt = ["0x79d1821bc6e7576aac4422bead0951a4adc7075a",
        "0x4ef929af00cb93993c3d01834c4da79200d31e32",
        "0x7998dd32be1c7bf98d3075c1d0f12de2f0e1d6ec",
        "0xa04513d85e02e1a1623a985269b3ebd46fa76b98"]
log["leg2_boltbook_new"] = [shape_check(a, "boltbook-en") for a in bolt]
carry = ["0x8c2f7bec2d7b31d9c706d25eb4d008f0754ce255",
         "0xb2625d56a7fc855bf7432b5584b390a4b4d9c7fd",
         "0xffbced696d2667cef82ba1306016c85da5cf7777"]
log["leg2_boltbook_carryover"] = [shape_check(a, "boltbook-en") for a in carry]
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["seen_total_after"] = len(seen)

# Leg 3 fresh reads: NUSA + Oddlode + Project402 via direct dataseed batch
from Crypto.Hash import keccak
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

NUSA = "0x7D08289E962f5aEc00d56D67322eb2FD056B687c"
ODD = "0xce18531F9F639ca2351CA15FB2032D925b917472"
P402 = "0xd80d0095746999c93ae837b1de1569d5814405dc"
calls = []
labels = []
def add(addr, sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_call",
                  "params": [{"to": addr, "data": data}, "latest"]})
    labels.append((addr, sig))
for sig in ["freeMinted()", "sharesMinted()", "paidShares()", "soldOut()", "closed()"]:
    add(NUSA, sig)
for sig in ["freeAvailable(address)", "freeClaimed(address)", "hasMinted(address)"]:
    add(NUSA, sig, "USER")
for sig in ["freeMinted()", "totalSupply()", "freeClaimed(address)", "balanceOf(address)"]:
    add(ODD, sig, "USER" if "address" in sig else "")
for sig in ["freeMinted()", "FREE_CAP()", "totalMinted()", "freeClaimed(address)", "totalSupply()", "mintOpen()"]:
    add(P402, sig, "USER" if "address" in sig else "")
calls.append({"jsonrpc": "2.0", "id": len(calls) + 1, "method": "eth_blockNumber", "params": []})
try:
    res = curl_json(RPC, calls, timeout=30)
    by_id = {r["id"]: r.get("result") for r in res}
    blk = to_int(by_id[len(calls)])
    vals = {}
    for i, (addr, sig) in enumerate(labels):
        vals.setdefault(addr, {})[sig] = to_int(by_id[i + 1])
    log["fresh_reads"] = {"block": blk, "values": vals}
    json.dump({"block": blk, "values": vals},
              open(BASE + TAG + "-fresh-reads.json", "w"), indent=1)
except Exception as ex:
    log["fresh_reads_error"] = f"{type(ex).__name__}: {ex}"

log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-legs12.log", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
