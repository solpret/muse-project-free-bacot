#!/usr/bin/env python3
"""Triage 3 scan first-seen contracts, run 2026-11-08 19:31 WIB. Read-only.
Agent-shape: Sourcify ABI / registry ref / AgentGate / free-mint fn / free-supply const.
First-mint block time via dataseed eth_getBlockByNumber (Ankr returns fake timestamps)."""
import sys, json, urllib.request, subprocess, datetime
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from fast_rpc import _post as _fr_post
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
ADDRS = {
    "0x5e0Ca9E1eCB5A6205E0B0d7a1FbE16983d2E8665": {"scan_mints": 20, "scan_minters": 20, "first_block": 132394604},
    "0x4EF929aF00cB93993c3D01834C4DA79200d31e32": {"scan_mints": 12, "scan_minters": 12, "first_block": 132395479},
    "0xe4f59512edE0e773E6905bbcb04BEDa09947354a": {"scan_mints": 6, "scan_minters": 1, "first_block": 132394781},
}
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
            if isinstance(out, dict) and "result" in out:
                return out["result"]
            if isinstance(out, dict) and "error" in out:
                return None
        except Exception:
            continue
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
        except Exception:
            continue
    return None

discards = json.load(open(BASE + "/same-owner-discards.json"))
disc_owners = {str(d.get("owner", "")).lower() for d in discards if isinstance(d, dict)}

out = {}
for A, meta in ADDRS.items():
    r = dict(meta)
    r["name"] = dec_str(call(A, sel("name()")))
    r["symbol"] = dec_str(call(A, sel("symbol()")))
    r["totalSupply"] = dec(call(A, sel("totalSupply()")))
    r["totalMinted"] = dec(call(A, sel("totalMinted()")))
    r["MAX_SUPPLY"] = dec(call(A, sel("MAX_SUPPLY()")))
    r["FREE_SUPPLY"] = dec(call(A, sel("FREE_SUPPLY()")))
    r["freeClaimed"] = dec(call(A, sel("freeClaimed()")))
    r["freeMinted"] = dec(call(A, sel("freeMinted()")))
    r["freeLeft"] = dec(call(A, sel("freeLeft()")))
    r["mintOpen"] = dec(call(A, sel("mintOpen()")))
    r["PRICE"] = dec(call(A, sel("PRICE()")))
    r["owner"] = dec_addr(call(A, sel("owner()")))
    r["owner_in_discards"] = (r["owner"] or "").lower() in disc_owners if r["owner"] else None
    r["agentRegistry"] = dec_addr(call(A, sel("agentRegistry()")))
    r["AGENT_ID"] = dec_addr(call(A, sel("AGENT_ID()")))
    r["registry"] = dec_addr(call(A, sel("registry()")))
    r["balanceOf_user"] = dec(call(A, sel("balanceOf(address)") + enc_addr(USER)))
    r["freeClaimed_user"] = dec(call(A, sel("freeClaimed(address)") + enc_addr(USER)))
    r["freeLeft_user"] = dec(call(A, sel("freeLeft(address)") + enc_addr(USER)))
    r["freeUsed_user"] = dec(call(A, sel("freeUsed(address)") + enc_addr(USER)))
    r["mintedBy_user"] = dec(call(A, sel("mintedBy(address)") + enc_addr(USER)))
    r["first_mint_wib"] = block_time_wib(meta["first_block"])
    url = f"https://sourcify.dev/server/v2/contract/56/{A}?fields=abi"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            j = json.load(resp)
        abi = j.get("abi") or []
        fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
        r["sourcify"] = j.get("match") or "verified"
        r["fns"] = fns
        r["mint_fns"] = [f for f in fns if "mint" in f.lower() or f in ("freeMint", "claimFree")]
        r["free_views"] = [f for f in fns if f.lower().startswith("free")]
        r["registry_in_abi_json"] = REG_BYTES in json.dumps(j).lower()
    except Exception as e:
        try:
            p = subprocess.run(["curl", "-sS", "-m", "20", "-A", "Mozilla/5.0", url],
                               capture_output=True, text=True, timeout=30)
            j = json.loads(p.stdout)
            abi = j.get("abi") or []
            fns = [f.get("name", "") for f in abi if f.get("type") == "function"]
            r["sourcify"] = (j.get("match") or "verified") + "(curl)"
            r["fns"] = fns
            r["mint_fns"] = [f for f in fns if "mint" in f.lower() or f in ("freeMint", "claimFree")]
            r["free_views"] = [f for f in fns if f.lower().startswith("free")]
            r["registry_in_abi_json"] = REG_BYTES in json.dumps(j).lower()
        except Exception as e2:
            r["sourcify"] = f"error:{str(e2)[:80]}"
    out[A] = r
    print(A, json.dumps(r), flush=True)

json.dump(out, open(BASE + "/run-2026-11-08-1931-scan-triage.json", "w"), indent=1)
print("DONE")
