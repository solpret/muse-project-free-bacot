#!/usr/bin/env python3
"""Gate check (A-N) for Ochre Medallion 0xF3A8A59F... run 2026-11-13 15:01.
On-chain: contractURI(), tokenURI(0), tokenURI(1); Sourcify metadata + ABI
grep for site/URL functions; decode base64 JSON where present.
Read-only; writes run-2026-11-13-1501-gate.json."""
import json, re, subprocess, base64
from Crypto.Hash import keccak
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
ADDR = "0xF3A8A59Fc607D0930E17335937E8Fb3Dce80038D"
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/"]
def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_u(n): return hex(n)[2:].rjust(64, "0")
def curl(url, timeout=25):
    try:
        return subprocess.run(["curl","-sL","--max-time",str(timeout),url],
            capture_output=True, text=True, timeout=timeout+5).stdout
    except Exception:
        return ""
def rpc(ep, payload, timeout=20):
    out = subprocess.run(["curl","-sL","--max-time",str(timeout),"-X","POST",ep,
        "-H","Content-Type: application/json","-d",json.dumps(payload)],
        capture_output=True, text=True, timeout=timeout+5).stdout
    return json.loads(out)
def call(sig, arg=""):
    data = sel(sig) + arg
    for ep in EPS:
        try:
            r = rpc(ep, {"jsonrpc":"2.0","id":1,"method":"eth_call",
                         "params":[{"to":ADDR,"data":data},"latest"]})
            res = r.get("result")
            if res and res != "0x":
                return res
        except Exception:
            continue
    return None
def decode_str(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 64: return None
        off = int.from_bytes(b[:32], "big"); ln = int.from_bytes(b[32:64], "big")
        return b[64:64+ln].decode("utf-8", "replace")
    except Exception as e:
        return f"decode-error: {e}"
out = {"address": ADDR}
out["contractURI_raw"] = call("contractURI()")
out["contractURI"] = decode_str(out["contractURI_raw"]) if out["contractURI_raw"] else None
for tid in (0, 1):
    raw = call("tokenURI(uint256)", enc_u(tid))
    out[f"tokenURI_{tid}_raw"] = (raw or "")[:400]
    out[f"tokenURI_{tid}"] = decode_str(raw) if raw else None
# (C/J) Sourcify metadata + ABI
meta = curl(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi", 25)
out["sourcify_bytes"] = len(meta)
try:
    mj = json.loads(meta)
    abi = mj.get("abi") or []
    fns = [f.get("name") for f in abi if f.get("type") == "function"]
    out["sourcify_abi_fns"] = fns
    out["site_fns"] = [n for n in fns if any(w in n.lower() for w in ("site","url","domain","external","website"))]
    src = json.dumps(mj).lower()
    out["sourcify_urls"] = sorted(set(re.findall(r"https?://[^\s\"'<>]+", src)))[:20]
    out["sourcify_registry_ref"] = "0x60b9262456de011f7d15a54cdd8c48baaa8b022f" in src
except Exception as e:
    out["sourcify_error"] = str(e)[:200]
# decode contractURI/tokenURI payloads if base64 JSON
for k in ("contractURI", "tokenURI_0", "tokenURI_1"):
    v = out.get(k)
    if v and v.startswith("data:application/json;base64,"):
        try:
            out[k + "_decoded"] = json.loads(base64.b64decode(v.split(",", 1)[1]).decode())
        except Exception as e:
            out[k + "_decode_error"] = str(e)[:150]
print(json.dumps(out, indent=1))
json.dump(out, open(BASE + "run-2026-11-13-1501-gate.json", "w"), indent=1)
