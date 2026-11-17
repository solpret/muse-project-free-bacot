#!/usr/bin/env python3
"""Zorrie verify for run 1901 (2026-11-08). Read-only.
Contract 0x47feee72353358a61618cE640265F9f406f88E47 (zorrie.fun/mint).
Checks: snapshot/seen membership, on-chain views, Sourcify, registry bytes,
first mint via Ankr getLogs walk-back (chunked <=1000 blocks)."""
import json, sys, time, urllib.request, subprocess
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import batch
from eth_hash.auto import keccak
import onchain_nft_scan as scan

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
A = "0x47feee72353358a61618cE640265F9f406f88E47"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

snap = json.load(open(BASE + "/onchain-snapshot.json"))
seen = json.load(open(BASE + "/onchain-scan-seen.json"))
print("in snapshot:", any(A.lower() in k.lower() or A.lower() in json.dumps(v).lower()[:50] for k, v in snap["contracts"].items()))
print("in seen:", A.lower() in {k.lower() for k in seen})

def sel(sig): return "0x" + keccak(sig.encode()).hex()[:8]
def enc_addr(a): return "000000000000000000000000" + a[2:].lower()
def call(data, timeout=15):
    for ep in EPS:
        try:
            return batch([("eth_call", [{"to": A, "data": data}, "latest"])], endpoint=ep, timeout=timeout)[0]
        except Exception:
            continue
    return {"error": "all endpoints failed"}
def dec(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None

out = {}
out["totalMinted"] = dec(call(sel("totalMinted()")))
out["maxSupply"] = dec(call(sel("maxSupply()")))
out["freeMintedPerWallet_user"] = dec(call(sel("freeMintedPerWallet(address)") + enc_addr(USER)))
out["paidMintedPerWallet_user"] = dec(call(sel("paidMintedPerWallet(address)") + enc_addr(USER)))
out["signer"] = call(sel("signer()"))
out["quoteBypassWei"] = dec(call(sel("quoteBypassWei()")))
out["owner"] = call(sel("owner()"))
print(json.dumps(out, indent=1))

# Sourcify
url = f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi"
try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        j = json.load(r)
    abi = j.get("abi") or []
    fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
    print("Sourcify: verified, fns:", len(fns), fns)
    print("registryRef in source:", REG_BYTES in json.dumps(j).lower())
    print("contractURI fn:", "contractURI" in fns, "| tokenURI fn:", "tokenURI" in fns)
except Exception as e:
    print("Sourcify error:", str(e)[:200])

# bytecode registry-bytes check
try:
    code = batch([("eth_getCode", [A, "latest"])], endpoint=EPS[0], timeout=15)[0]
    print("registry bytes in code:", REG_BYTES in str(code).lower(), "| code len:", len(str(code)))
except Exception as e:
    print("getCode error:", e)

# first mint: walk back from head in 1000-block chunks (max 12 chunks ~ 12k blocks ~ 90 min)
head = int(scan.rpc_call("eth_blockNumber", []), 16)
print("head:", head)
first = None
to_b = head
for i in range(12):
    frm = max(0, to_b - 999)
    try:
        logs, _ = scan.ankr_logs(frm, to_b, [scan.TRANSFER, scan.ZERO_TOPIC])
    except Exception as e:
        print(f"chunk {frm}-{to_b} ERROR {e}", flush=True); break
    mine = [l for l in logs if l.get("address", "").lower() == A.lower()]
    print(f"chunk {frm}-{to_b}: {len(logs)} logs, {len(mine)} zorrie mints", flush=True)
    if mine:
        first = min(int(l["blockNumber"], 16) for l in mine)
        # keep walking back to find earliest
        to_b = first - 1
        if i >= 11:
            break
        continue
    break
print("earliest zorrie mint block (walk-back):", first)
if first:
    blk = scan.rpc_call("eth_getBlockByNumber", [hex(first), False])
    print("first mint block ts:", blk)
json.dump({"views": out, "first_mint_block": first, "head": head},
          open(BASE + "/run-2026-11-08-1901-zorrie-verify.json", "w"), indent=1)
print("DONE")
