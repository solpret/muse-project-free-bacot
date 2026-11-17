#!/usr/bin/env python3
"""Hot-leg 2034 legs 1-3 (Sourcify new + Boltbook carryover shape-check) + NUSA/Oddlode fresh reads.
Run 2026-11-08 20:34 WIB. Lightweight: no chain-wide scan, no snapshot writes."""
import json, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2034"
NOW = "2026-11-08T20:34:38+07:00"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EXCLUDED = {"0x827E83E49Bd7E15b67efa0e90fC25f17b8D96124",
            "0x8b47354E7b76B1970a0D06365c8244a810d37493"}
FREE = {"freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft", "freeUsed",
        "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed", "freeMinted",
        "freeCardsRemaining"}
AGENT = {"agentId", "agentRegistry", "registry", "AGENT_ID", "AGENT_REGISTRY", "hasAgentId"}

seen = json.load(open(BASE + "hot-leg-seen.json"))
log = {"run": "free-mint-hot-leg 2026-11-08 20:34:38 WIB legs1-3"}
t0 = time.time()

def shape_check(addr, source):
    """Return dict with S1/S2 verdict; records into seen when decisive."""
    if addr.lower() == REGISTRY.lower() or addr.lower() in {e.lower() for e in EXCLUDED}:
        return {"addr": addr, "skipped": "registry-or-excluded"}
    try:
        code = batch([("eth_getCode", [addr, "latest"])], timeout=15)[0]
    except Exception as ex:
        return {"addr": addr, "error": f"eth_getCode {ex}"}
    if code == "0x":
        seen[addr] = {"first_seen_wib": NOW, "source": source,
                      "status": "checked-not-contract",
                      "note": "eth_getCode 0x on bsc-dataseed - EOA/wallet address, not a contract; no sale shape, not a lead."}
        return {"addr": addr, "result": "EOA-checked-not-contract"}
    try:
        out = subprocess.run(["curl", "-sL", "--max-time", "20",
                              f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"],
                             capture_output=True, text=True).stdout
        abi = json.loads(out).get("abi", [])
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

# Leg 1: the 6 Sourcify-feed contracts new since the 20:24 run
new_feed = ["0xD42d73bbBCb15C22f4d8983B0aC14696f9efA8c0",
            "0x263bceE9880ff2cEdcFC549689c0E0Be5Cdc6B37",
            "0xc9e60127CADe5bdaeC55788881411070185e8944",
            "0xd7CEbB0B0267BA15Ef926963aBA7e9fA72A99999",
            "0x43Fd01E67a89E07BE7D824ee32e34900D348A65d",
            "0x4e3A35DC2411AA4Bf81E8796c322b3d96cd092fF"]
log["leg1_sourcify_new"] = [shape_check(a, "sourcify-feed") for a in new_feed]

# Leg 2: carryover 3 unverified Boltbook addresses + HELIX + renderer from post LI3ihjPX_mz2
carry = ["0x8c2f7bec2d7b31d9c706d25eb4d008f0754ce255",
         "0xb2625d56a7fc855bf7432b5584b390a4b4d9c7fd",
         "0xffbced696d2667cef82ba1306016c85da5cf7777",
         "0x5e0ca9e1ecb5a6205e0b0d7a1fbe16983d2e8665",
         "0x0c1c3d40bf2503226b71a6a94dbe9f3163eb66b5"]
log["leg2_boltbook_carryover_retry"] = [shape_check(a, "boltbook-en") for a in carry]
log["leg2_boltbook_frontpage"] = ("EN+ZH front pages read via browser.open 20:37 WIB: "
    "HELIX 0x5e0ca9e1... (post LI3ihjPX_mz2, freeMint(), 125/4444 @20:26 WIB, already in main snapshot) "
    "and renderer 0x0c1c3d40... shape-checked above; AgentVOLT v6 0xe0deb1a7... already checked-not-sale-shape; "
    "Dronegent 0xf6ab7131... already checked-not-track-c (NFT, not share sale); Lion's Share 0x6ac03204... "
    "already checked-not-sale-shape; OBSIDIAN 0x57e3f981... already checked-not-sale-shape, sold out 1111/1111; "
    "GLOOP 0x183cbb52... watchlist-only-prelaunch in seen; Jinchan 0xccc127d1... already checked-not-sale-shape; "
    "NUSA 0x7d08289e... lead reported 17:04; Oddlode sold out, reported run utama 1801; "
    "HOPKIN + Wisp Agent posts carry no contract address in the front-page snippet — not shape-checkable this run.")
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["seen_total_after"] = len(seen)

# Leg 3 fresh reads: NUSA (track-C lead, pool moving) + Oddlode (confirm sold out)
def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

NUSA = "0x7D08289E962f5aEc00d56D67322eb2FD056B687c"
ODD = "0xce18531F9F639ca2351CA15FB2032D925b917472"
calls = []
labels = []
def add(addr, sig, arg=""):
    data = sel(sig)
    if arg == "USER": data += enc_addr(USER)
    calls.append(("eth_call", [{"to": addr, "data": data}, "latest"]))
    labels.append((addr, sig))
for sig in ["freeMinted()", "sharesMinted()", "paidShares()", "soldOut()", "closed()"]:
    add(NUSA, sig)
for sig in ["freeAvailable(address)", "freeClaimed(address)", "hasMinted(address)"]:
    add(NUSA, sig, "USER")
for sig in ["freeMinted()", "totalSupply()", "freeClaimed(address)", "balanceOf(address)"]:
    add(ODD, sig, "USER" if "address" in sig else "")
calls.append(("eth_blockNumber", []))
try:
    res = batch(calls, timeout=25)
    blk = int(res[-1], 16)
    vals = {}
    for (addr, sig), r in zip(labels, res[:-1]):
        vals.setdefault(addr, {})[sig] = to_int(r)
    log["fresh_reads"] = {"block": blk, "values": vals}
    json.dump({"block": blk, "values": vals},
              open(BASE + TAG + "-fresh-reads.json", "w"), indent=1)
except Exception as ex:
    log["fresh_reads_error"] = f"{type(ex).__name__}: {ex}"

log["elapsed_sec"] = round(time.time() - t0, 1)
json.dump(log, open(BASE + TAG + "-legs12.log", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
