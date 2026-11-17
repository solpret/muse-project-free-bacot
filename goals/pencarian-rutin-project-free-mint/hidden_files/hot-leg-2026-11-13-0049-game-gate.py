#!/usr/bin/env python3
"""Gate discovery for Game-9c20 (0x9c204b333538F853cD5FD8306277130514B86F04) + fd55 sellout re-verify.
Run 2026-11-13 00:49 hot-leg follow-up. Read-only. Methods (A)-(N) per body; (F) is browser-only
(X optional, never gates) - not attempted here; (L) browser-only - noted as limitation if needed."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
GAME = "0x9c204b333538F853cD5FD8306277130514B86F04"
FD55 = "0xfd55F5b70F6eb6E59CEb6FF5c449f0cd1A3a5C0F"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
T0 = time.time()
out = {"started_wib": "2026-11-13T00:49-followup", "game": GAME}

def curl(url, timeout=10, data=None):
    cmd = ["curl", "-sL", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=timeout + 5)
        return r.stdout
    except Exception:
        return b""

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc(a): return a[2:].lower().rjust(64, "0")
def to_int(v):
    try: return int(v, 16) if v and v != "0x" else None
    except Exception: return None

EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/"]
def _post_one(ep, payload, timeout=12):
    r = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                        "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                       capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(r.stdout)
def post_rpc_race(payload, timeout=12):
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(_post_one, ep, payload, timeout): ep for ep in EPS}
        for fut in as_completed(futs):
            try:
                res = fut.result()
                if isinstance(res, list) and len(res) == len(payload):
                    return res
            except Exception:
                continue
    return None
def eth_call(addr, data):
    res = post_rpc_race([{"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                          "params": [{"to": addr, "data": data}, "latest"]}], timeout=12)
    if isinstance(res, list) and res and isinstance(res[0], dict):
        return res[0].get("result")
    return None
def decode_str(hexdata):
    if not hexdata or hexdata == "0x":
        return None
    try:
        b = bytes.fromhex(hexdata[2:])
        if len(b) < 64:
            return None
        off = int.from_bytes(b[:32], "big")
        ln = int.from_bytes(b[off:off + 32], "big")
        return b[off + 32:off + 32 + ln].decode(errors="replace")
    except Exception as e:
        return f"decode-error {e}"

# (H) contractURI + (I) tokenURI(0/1) + (E) owner + name/symbol + quote + re-verify pool
out["contractURI_raw"] = eth_call(GAME, sel("contractURI()"))
out["contractURI"] = decode_str(out["contractURI_raw"])
out["tokenURI_0_raw"] = eth_call(GAME, sel("tokenURI(uint256)") + format(0, "064x"))
out["tokenURI_0"] = decode_str(out["tokenURI_0_raw"])
out["tokenURI_1_raw"] = eth_call(GAME, sel("tokenURI(uint256)") + format(1, "064x"))
out["tokenURI_1"] = decode_str(out["tokenURI_1_raw"])
out["owner_raw"] = eth_call(GAME, sel("owner()"))
out["name"] = decode_str(eth_call(GAME, sel("name()")))
out["symbol"] = decode_str(eth_call(GAME, sel("symbol()")))
# quote(user,1)
q = eth_call(GAME, sel("quote(address,uint256)") + enc(USER) + format(1, "064x"))
out["quote_user_1_raw"] = q
if q and q != "0x":
    try:
        b = bytes.fromhex(q[2:])
        words = [int.from_bytes(b[i:i + 32], "big") for i in range(0, min(len(b), 160), 32)]
        tail = None
        if len(words) >= 5 and words[4] < len(b):
            off = words[4]
            ln = int.from_bytes(b[off:off + 32], "big")
            tail = b[off + 32:off + 32 + ln].decode(errors="replace")
        out["quote_user_1"] = {"words": words, "tail_string": tail}
    except Exception as e:
        out["quote_user_1"] = {"decode_error": str(e)[:100]}
# fresh pool re-verify for GAME + fd55
def batch(addr, views):
    calls, keys = [], []
    for i, sig in enumerate(views):
        if "(address)" in sig:
            data = sel(sig) + enc(USER); key = sig.split("(")[0] + "_user"
        else:
            data = sel(sig); key = sig.split("(")[0]
        calls.append({"jsonrpc": "2.0", "id": i + 1, "method": "eth_call",
                      "params": [{"to": addr, "data": data}, "latest"]})
        keys.append(key)
    res = post_rpc_race(calls, timeout=12)
    if res is None:
        return None
    return {key: (None if (isinstance(it, dict) and "error" in it)
                  else (to_int(it.get("result")) if isinstance(it, dict) else None))
            for it, key in zip(res, keys)}
VIEWS = ["freeMinted()", "FREE_CAP()", "mintOpen()", "freeClaimed(address)",
         "balanceOf(address)", "totalMinted()", "mintOpensAt()"]
out["game_reverify"] = batch(GAME, VIEWS)
out["fd55_reverify"] = batch(FD55, VIEWS)

# (C) Sourcify metadata + source (URLs?) ; (J) ABI grep for site functions
meta = curl(f"https://sourcify.dev/server/v2/contract/56/{GAME}?fields=metadata,abi", 10)
try:
    meta_j = json.loads(meta.decode(errors="replace"))
except Exception:
    meta_j = None
out["sourcify_meta_ok"] = isinstance(meta_j, dict)
if isinstance(meta_j, dict):
    m = meta_j.get("metadata") or {}
    out["sourcify_metadata_keys"] = list(m.keys()) if isinstance(m, dict) else str(type(m))
    out["sourcify_metadata_str"] = json.dumps(m)[:2000]
    abi = meta_j.get("abi") or (meta_j.get("stdJson") or {}).get("abi") or []
    names = [ (fn.get("name") or "") for fn in abi if isinstance(fn, dict)]
    out["abi_site_fns"] = [n for n in names if any(w in n.lower() for w in
                           ("site", "website", "url", "domain", "external", "link", "uri"))]
    out["abi_n_fns"] = len(names)
    src_txt = json.dumps(meta_j).lower()
    import re as _re
    out["sourcify_urls_in_meta"] = sorted(set(_re.findall(r"https?://[a-z0-9./_-]+", src_txt)))[:20]
    out["sourcify_has_registry"] = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in src_txt
    # full source files for URLs (metadata sources)
    try:
        files = curl(f"https://sourcify.dev/server/v2/contract/56/{GAME}?fields=stdJson", 10)
        fj = json.loads(files.decode(errors="replace"))
        sj = json.dumps(fj).lower()
        out["stdjson_urls"] = sorted(set(_re.findall(r"https?://[a-z0-9./_-]+", sj)))[:20]
    except Exception as e:
        out["stdjson_urls"] = [f"error {e}"]

# tokenURI decode follow-through: if data:application/json;base64, decode
import base64
for key in ("tokenURI_0", "tokenURI_1", "contractURI"):
    v = out.get(key)
    if v and v.startswith("data:application/json;base64,"):
        try:
            out[key + "_decoded"] = base64.b64decode(v.split(",", 1)[1]).decode(errors="replace")[:1500]
        except Exception as e:
            out[key + "_decoded"] = f"b64-error {e}"
    elif v and v.startswith("ipfs://"):
        out[key + "_ipfs"] = v

out["elapsed_s"] = round(time.time() - T0, 1)
json.dump(out, open(BASE + "hot-leg-2026-11-13-0049-game-gate.json", "w"), indent=1)
print(json.dumps(out, indent=1))
print("ELAPSED", out["elapsed_s"])
