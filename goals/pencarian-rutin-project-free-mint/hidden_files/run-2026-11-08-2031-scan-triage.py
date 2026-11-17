#!/usr/bin/env python3
"""Triage scan first-seen contracts, run 2026-11-08 20:31 WIB. Read-only.
Agent-shape: registry bytes (from scan) + Sourcify ABI free/mint fns + on-chain
agentRegistry/AGENT_ID + free views + owner vs same-owner-discards.
First-mint block time via dataseed eth_getBlockByNumber (Ankr returns fake timestamps).
Writes run-2026-11-08-2031-scan-triage.json. NEVER writes snapshot/seen."""
import sys, json, datetime, time
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
REG = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
T0 = time.time()

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_u256(n): return "%064x" % n
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None
def call(addr, data):
    for ep in EPS:
        try:
            out = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                                "params": [{"to": addr, "data": data}, "latest"]},
                           timeout=10, retries=0)
            if isinstance(out, dict) and "result" in out: return out["result"]
            if isinstance(out, dict) and "error" in out: return None
        except Exception: continue
    return None
def dec_addr(h):
    if not isinstance(h, str) or len(h) < 42: return None
    return "0x" + h[-40:]
def block_time_wib(blk):
    for ep in EPS:
        try:
            r = _fr_post(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(blk), False]}, timeout=10, retries=0)
            if r and r.get("result"):
                ts = int(r["result"]["timestamp"], 16)
                return datetime.datetime.fromtimestamp(
                    ts, datetime.timezone(datetime.timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S WIB")
        except Exception: continue
    return None

first = json.load(open(f"{BASE}/run-2026-11-08-2031-firstseen.json"))
discards = json.load(open(f"{BASE}/same-owner-discards.json"))
disc_owners = {}
for d in discards:
    if isinstance(d, dict) and d.get("owner"):
        disc_owners.setdefault(str(d["owner"]).lower(), d)
# exception owners: listed but explicitly NOT discarded
EXCEPTION = "0xcbcadc7c9897d21fa6e3a8f941f9f271a39598e3"

out = {}
for c in first:
    addr = c["address"]
    r = {"name": c.get("name"), "symbol": c.get("symbol"), "kind": c.get("kind"),
         "scan_mints": c.get("mint_count"), "scan_minters": c.get("distinct_minters"),
         "first_block": c.get("first_block"), "last_block": c.get("last_block"),
         "registry_bytes_hit": c.get("registry_bytes_hit"), "sourcify": c.get("sourcify"),
         "free_shaped": c.get("free_shaped"), "mint_funcs": c.get("mint_funcs")}
    r["first_block_wib"] = block_time_wib(c["first_block"]) if c.get("first_block") else None
    r["totalSupply"] = to_int(call(addr, sel("totalSupply()")))
    r["totalMinted"] = to_int(call(addr, sel("totalMinted()")))
    r["MAX_SUPPLY"] = to_int(call(addr, sel("MAX_SUPPLY()")))
    r["freeClaimed"] = to_int(call(addr, sel("freeClaimed()")))
    r["freeMinted"] = to_int(call(addr, sel("freeMinted()")))
    r["FREE_SUPPLY"] = to_int(call(addr, sel("FREE_SUPPLY()")))
    r["mintOpen"] = to_int(call(addr, sel("mintOpen()")))
    r["AGENT_ID"] = dec_addr(call(addr, sel("AGENT_ID()")))
    r["agentRegistry"] = dec_addr(call(addr, sel("agentRegistry()")))
    r["owner"] = dec_addr(call(addr, sel("owner()")))
    ow = (r["owner"] or "").lower()
    r["owner_in_discards"] = ow in disc_owners if ow else None
    r["owner_discard_exception"] = (ow == EXCEPTION)
    if r["owner_in_discards"] and ow != EXCEPTION:
        r["discard_reason"] = str(disc_owners[ow].get("reason", ""))[:200]
    r["freeLeft_user"] = to_int(call(addr, sel("freeLeft(address)") + enc_addr(USER)))
    r["freeUsed_user"] = to_int(call(addr, sel("freeUsed(address)") + enc_addr(USER)))
    r["mintedBy_user"] = to_int(call(addr, sel("mintedBy(address)") + enc_addr(USER)))
    r["balanceOf_user"] = to_int(call(addr, sel("balanceOf(address)") + enc_addr(USER)))
    # agent-shaped verdict: registry bytes + (verified ABI with free/mint fns) + on-chain registry ref
    reg_ref = (r["AGENT_ID"] == REG) or (r["agentRegistry"] == REG) or r["registry_bytes_hit"] is True
    has_free = bool(r["free_shaped"]) or r["freeClaimed"] is not None or r["freeMinted"] is not None or r["FREE_SUPPLY"] is not None
    has_mint = bool(r["mint_funcs"])
    r["agent_shaped"] = bool(reg_ref and has_free and has_mint and r["sourcify"] == "verified")
    if r["freeClaimed"] is not None and r["FREE_SUPPLY"]:
        r["freePct"] = round(100.0 * r["freeClaimed"] / r["FREE_SUPPLY"], 2)
    if r["freeMinted"] is not None and r["FREE_SUPPLY"]:
        r["freePct_freeMinted"] = round(100.0 * r["freeMinted"] / r["FREE_SUPPLY"], 2)
    out[addr] = r
    print(f"{r['name']} {addr} agent_shaped={r['agent_shaped']} owner={r['owner']} disc={r['owner_in_discards']} "
          f"ts={r['totalSupply']} tm={r['totalMinted']} free%={r.get('freePct') or r.get('freePct_freeMinted')} "
          f"first={r['first_block_wib']} mints={r['scan_mints']}/{r['scan_minters']}", flush=True)

json.dump(out, open(f"{BASE}/run-2026-11-08-2031-scan-triage.json", "w"), indent=1)
print(f"DONE in {time.time()-T0:.1f}s, triaged {len(out)}")
