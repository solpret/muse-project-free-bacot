#!/usr/bin/env python3
"""First-mint + bytecode-registry + Agent ID check for 0xc43f7Ab11728FC884662B35AD974ff703cb4221d.
Read-only. Public BSC dataseeds. No Ankr."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0xc43f7Ab11728FC884662B35AD974ff703cb4221d"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
TRANSFER = "0x" + keccak.new(digest_bits=256).update(b"Transfer(address,address,uint256)").hexdigest()
ZERO = "0x" + "0" * 64

def post_rpc(ep, payload, timeout=30):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def rpc(method, params):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}, timeout=30)
            if isinstance(r, dict) and "result" in r:
                return r["result"], ep
        except Exception:
            continue
    return None, None

head, _ = rpc("eth_blockNumber", [])
head = int(head, 16)
print("HEAD", head, flush=True)

# 1. bytecode: does it contain the Agent ID registry address (lowercase, no 0x)?
code, _ = rpc("eth_getCode", [ADDR, "latest"])
reg_hex = REGISTRY[2:].lower()
has_reg = reg_hex in (code or "").lower()
print("CODE_LEN", len(code or "") // 2 - 1, "bytes; REGISTRY_IN_BYTECODE:", has_reg, flush=True)

# 2. does user hold an Agent ID? registry balanceOf(user)
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
bal, _ = rpc("eth_call", [{"to": REGISTRY, "data": sel("balanceOf(address)") + enc(USER)}, "latest"])
print("REGISTRY balanceOf(user):", int(bal, 16) if bal and bal != "0x" else bal, flush=True)

# 3. first mint: scan Transfer logs backwards in 1000-block chunks, up to 20000 blocks back
earliest = None
mints_total = 0
for back in range(0, 20000, 1000):
    to_b = head - back
    from_b = head - back - 999
    logs, ep = rpc("eth_getLogs", [{"fromBlock": hex(from_b), "toBlock": hex(to_b),
                                    "address": ADDR, "topics": [TRANSFER]}])
    if logs is None:
        print(f"chunk {from_b}-{to_b}: RPC FAIL", flush=True)
        continue
    chunk_mints = [l for l in logs if l["topics"][1] == ZERO]
    mints_total += len(chunk_mints)
    print(f"chunk {from_b}-{to_b}: {len(logs)} transfers, {len(chunk_mints)} mints", flush=True)
    if chunk_mints:
        earliest = min(chunk_mints, key=lambda l: int(l["blockNumber"], 16))
        # keep scanning older chunks to find the true first mint
        continue
    # if a chunk has transfers but no mints, and we already found mints in newer chunks, older chunks may still hold the first mint;
    # only stop when we have seen mints AND this chunk has zero transfers at all (activity gap before launch)
    if earliest is not None and len(logs) == 0:
        break

first = None
if earliest is not None:
    blk, _ = rpc("eth_getBlockByNumber", [earliest["blockNumber"], False])
    first = {"block": int(earliest["blockNumber"], 16),
             "tx": earliest["transactionHash"],
             "tokenId": int(earliest["topics"][3], 16),
             "to": "0x" + earliest["topics"][2][-40:],
             "timestamp": int(blk["timestamp"], 16) if blk else None}
    print("FIRST MINT:", first, flush=True)
else:
    print("NO MINTS FOUND in scanned window", flush=True)

out = {"head_block": head, "registry_in_bytecode": has_reg,
       "registry_balanceOf_user": int(bal, 16) if bal and bal != "0x" else None,
       "first_mint": first, "mints_in_scanned_window": mints_total,
       "scanned_back_blocks": 20000}
json.dump(out, open(BASE + "run-2026-11-13-2031-c43f-firstmint.json", "w"), indent=1)
print("written", BASE + "run-2026-11-13-2031-c43f-firstmint.json")
