#!/usr/bin/env python3
"""Hot-leg 2234 legs2b-3: shape-check Boltbook new contracts + fresh reads NUSA/LOCKSMITH."""
import json, subprocess, time
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
TAG = "hot-leg-2026-11-08-2249"
NOW = "2026-11-08T22:49:38+07:00"
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
snap = json.load(open(BASE + "onchain-snapshot.json"))
snap_addrs = set()
for v in snap.get("contracts", {}).values():
    if isinstance(v, dict):
        for f in ("address", "sale", "token"):
            if v.get(f): snap_addrs.add(str(v[f]).lower())
for v in snap.get("track_c", {}).values():
    if isinstance(v, dict):
        for f in ("address", "sale", "token"):
            if v.get(f): snap_addrs.add(str(v[f]).lower())
log = {"run": "free-mint-hot-leg 2026-11-08 22:49:38 WIB legs2b-3"}
t0 = time.time()

def curl_json(url, payload=None, timeout=20):
    cmd = ["curl", "-sL", "--max-time", str(timeout)]
    if payload is not None:
        cmd += ["-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(payload)]
    cmd.append(url)
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16)
    except Exception: return None

def shape_check(addr, source):
    if addr.lower() == REGISTRY.lower() or addr.lower() in {e.lower() for e in EXCLUDED}:
        return {"addr": addr, "skipped": "registry-or-excluded"}
    try:
        code = curl_json(RPC, {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                                "params": [addr, "latest"]}).get("result")
    except Exception as ex:
        return {"addr": addr, "error": f"eth_getCode {ex}"}
    if code is None:
        return {"addr": addr, "error": "eth_getCode empty response (transport artifact, not recorded)"}
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
                  "note": f"S1={s1} S2={s2} fns={sorted(names)} in_snapshot={addr.lower() in snap_addrs}"}
    return {"addr": addr, "result": "sale-shape-pass" if (s1 or s2) else "checked-not-sale-shape",
            "S1": s1, "S2": s2, "n_fns": len(names), "in_snapshot": addr.lower() in snap_addrs}

# TX-hash false positives from the 40-hex regex on Boltbook front page (66-hex tx hashes):
seen["0x10927971eac1bad98571395f633c7b20ca315e1c"] = {"first_seen_wib": NOW,
    "source": "boltbook-en",
    "status": "not-a-contract-tx-hash",
    "note": "40-hex prefix of Agent File mint TX HASH 0x10927971... (Series 10 Harvest #6278, soulbound), NOT a contract address - regex false positive. Not a lead."}
boltbook_new = {
    "0x6411125870d54ad4863bf196d909011b82ed86c8": "CLAUDIA token (Boltbook post, PCS v3 CLAUDIA/WBNB position NFT, owner renounced; NEW to hot-leg seen this run)",
}
log["leg2b_boltbook_shape"] = []
for addr, src in boltbook_new.items():
    r = shape_check(addr, src)
    r["label"] = src
    log["leg2b_boltbook_shape"].append(r)
json.dump(seen, open(BASE + "hot-leg-seen.json", "w"), indent=1)
log["seen_total_after"] = len(seen)

# Leg 3 fresh reads: NUSA + LOCKSMITH via direct dataseed batch
NUSA = "0x7D08289E962f5aEc00d56D67322eb2FD056B687c"
LOCK = "0x05e8738290be6639fD0f7236ebF444E5466D3164"
calls, labels = [], []
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
KITE = "0x8b8e59c014eb3e229e043ae8f3b0d7e201d21db0"
for sig in ["freeMinted()", "totalSupply()", "MAX_SUPPLY()", "FREE_CAP()", "FREE_PCT()"]:
    add(KITE, sig)
for sig in ["canFreeMint(address)", "freeClaimed(address)"]:
    add(KITE, sig, "USER")
for sig in ["freeMintedTotal()", "totalMinted()", "totalSupply()", "mintActive()", "freeMinted(address)", "mintedCount(address)", "balanceOf(address)"]:
    add(LOCK, sig, "USER" if "address" in sig else "")
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
json.dump(log, open(BASE + TAG + "-legs2b3.log", "w"), indent=1)
print(json.dumps(log, indent=1))
print("ELAPSED", round(time.time() - t0, 1))
