#!/usr/bin/env python3
"""Run 1931 triage deepening: HELIX (agent-shaped, owner EXCEPTION not discarded)
+ Pokechain (Sourcify 404, registry-bytes only). Read-only."""
import sys, json, base64
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post, batch as _batch
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
REG_BYTES = "60b9262456de011f7d15a54cdd8c48baaa8b022f"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
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
def dec(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try: return int(h, 16)
    except Exception: return None
def dec_str(h):
    if not isinstance(h, str) or not h or h == "0x": return None
    try:
        b = bytes.fromhex(h[2:])
        if len(b) < 64: return b.decode(errors="replace")
        ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode(errors="replace")
    except Exception: return None
def get_code(addr):
    for ep in EPS:
        try:
            out = _batch([("eth_getCode", [addr, "latest"])], endpoint=ep, timeout=15)
            if out and isinstance(out[0], str): return out[0]
        except Exception: continue
    return None

out = {}
# --- HELIX ---
H = "0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665"
h = {"address": H}
h["mintActive"] = dec(call(H, sel("mintActive()")))
h["mintCost"] = dec(call(H, sel("mintCost()")))
h["price"] = dec(call(H, sel("price()")))
h["totalPaidMinted"] = dec(call(H, sel("totalPaidMinted()")))
h["publicRemaining"] = dec(call(H, sel("publicRemaining()")))
h["reserveMinted"] = dec(call(H, sel("reserveMinted()")))
h["requireAgentId"] = dec(call(H, sel("requireAgentId()")))
h["hasAgentId_user"] = dec(call(H, sel("hasAgentId(address)") + enc_addr(USER)))
h["freeUsed_user"] = dec(call(H, sel("freeUsed(address)") + enc_addr(USER)))
h["walletInfo_user_raw"] = call(H, sel("walletInfo(address)") + enc_addr(USER))
uri = dec_str(call(H, sel("contractURI()")))
h["contractURI"] = uri
if uri and uri.startswith("data:application/json;base64,"):
    try: h["contractURI_json"] = json.loads(base64.b64decode(uri.split(",", 1)[1]).decode())
    except Exception as e: h["contractURI_json"] = {"decode_error": str(e)[:100]}
# freeMint signature from ABI file (exact_match saved? re-fetch quickly via triage json fns)
triage = json.load(open(BASE + "/run-2026-11-08-1931-scan-triage.json"))
h["abi_freeMint_inputs"] = "see triage fns (freeMint present)"
h["code_registry_bytes"] = None
code = get_code(H)
h["code_registry_bytes"] = (REG_BYTES in code[2:].lower()) if isinstance(code, str) else None
h["code_len"] = len(code) if isinstance(code, str) else None
out["HELIX"] = h
print("HELIX", json.dumps(h), flush=True)

# --- Pokechain ---
P = "0x4EF929aF00cB93993c3D01834C4DA79200d31e32"
p = {"address": P}
code = get_code(P)
p["code_len"] = len(code) if isinstance(code, str) else None
p["code_registry_bytes"] = (REG_BYTES in code[2:].lower()) if isinstance(code, str) else None
# free-mint selector presence in bytecode: freeMint() = keccak('freeMint()')[:4], mintFree() etc.
for sig in ["freeMint()", "mintFree()", "claimFree()", "freeMint(uint256)", "mint(uint256)"]:
    s = sel(sig)[2:]
    p[f"selector_{sig}"] = (s in code[2:].lower()) if isinstance(code, str) else None
p["contractURI"] = dec_str(call(P, sel("contractURI()")))
p["tokenURI_1"] = dec_str(call(P, sel("tokenURI(uint256)") + "%064x" % 1))
p["totalSupply"] = dec(call(P, sel("totalSupply()")))
p["totalMinted"] = dec(call(P, sel("totalMinted()")))
p["mintOpen"] = dec(call(P, sel("mintOpen()")))
p["mintActive"] = dec(call(P, sel("mintActive()")))
p["FREE_SUPPLY"] = dec(call(P, sel("FREE_SUPPLY()")))
p["freeMinted"] = dec(call(P, sel("freeMinted()")))
p["freeClaimed"] = dec(call(P, sel("freeClaimed()")))
p["MAX_SUPPLY"] = dec(call(P, sel("MAX_SUPPLY()")))
p["name"] = dec_str(call(P, sel("name()")))
p["symbol"] = dec_str(call(P, sel("symbol()")))
out["Pokechain"] = p
print("Pokechain", json.dumps(p), flush=True)

json.dump(out, open(BASE + "/run-2026-11-08-1931-scan-triage2.json", "w"), indent=1)
print("DONE")
