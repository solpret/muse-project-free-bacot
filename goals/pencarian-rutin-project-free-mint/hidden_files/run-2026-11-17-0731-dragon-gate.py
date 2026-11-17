#!/usr/bin/env python3
"""DRAGON 0xfc191b76041498b14dcae3c802af3389c74263e6 gate probe run 0731.
Methods (H) contractURI, (I) tokenURI, (J) ABI site-fn grep, (C) Sourcify metadata/URL grep.
Read-only. Writes run-2026-11-17-0731-dragon-gate.json."""
import json, re, subprocess, sys, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
from eth_hash.auto import keccak
import fast_rpc
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
ADDR = "0xfc191b76041498b14dcae3c802af3389c74263e6"
def sel(sig): return keccak(sig.encode())[:4].hex()
def call(to, data): return (to, "0x" + data)
calls = [
    call(ADDR, sel("contractURI()")),
    call(ADDR, sel("tokenURI(uint256)") + "%064x" % 1),
    call(ADDR, sel("tokenURI(uint256)") + "%064x" % 0),
    call(ADDR, sel("owner()")),
    call(ADDR, sel("name()")),
    call(ADDR, sel("symbol()")),
]
def batch(calls, timeout=15):
    payload = [{"jsonrpc":"2.0","id":i+1,"method":"eth_call","params":[{"to":t,"data":d},"latest"]} for i,(t,d) in enumerate(calls)]
    body = json.dumps(payload).encode()
    for ep in fast_rpc.healthy_endpoints() or fast_rpc.ENDPOINTS:
        try:
            req = urllib.request.Request(ep, data=body, headers={"Content-Type":"application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                outp = json.loads(r.read().decode())
            res=[]
            by={it["id"]:it for it in outp if isinstance(it,dict)}
            for i in range(len(calls)):
                it=by.get(i+1,{})
                res.append(it.get("result"))
            return res, ep
        except Exception:
            continue
    raise IOError("all endpoints failed")
out = {"contract": ADDR}
try:
    res, ep = batch(calls)
    out["endpoint"] = ep
    labels = ["contractURI","tokenURI(1)","tokenURI(0)","owner","name","symbol"]
    for lab, v in zip(labels, res):
        out[lab] = v
    def dec_str(hexv):
        if not hexv or hexv=="0x": return None
        try:
            b = bytes.fromhex(hexv[2:])
            # ABI string: offset(32)+len(32)+data
            if len(b) >= 64:
                ln = int.from_bytes(b[32:64], "big")
                s = b[64:64+ln].decode("utf-8", errors="replace")
                return s
            return b.decode("utf-8", errors="replace")
        except Exception as e:
            return f"<decode-error {e}>"
    out["contractURI_decoded"] = dec_str(res[0])
    out["tokenURI1_decoded"] = dec_str(res[1])
    out["tokenURI0_decoded"] = dec_str(res[2])
except Exception as e:
    out["rpc_error"] = f"{type(e).__name__}: {e}"
# (C)+(J) Sourcify metadata + ABI
try:
    req = urllib.request.Request(f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi,stdJson,metadata",
                                 headers={"User-Agent":"free-mint-search/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        meta = json.loads(r.read().decode())
    abi = meta.get("abi", [])
    fns = [e.get("name") for e in abi if e.get("type")=="function"]
    site_fns = [n for n in fns if any(k in n.lower() for k in ("website","siteurl","domain","external","url","link"))]
    out["sourcify"] = {"verified": True, "n_fns": len(fns), "site_fns": site_fns,
                       "fn_names": sorted(set(fns))}
    blob = json.dumps(meta)
    urls = sorted(set(re.findall(r"https?://[A-Za-z0-9._\-/:?#=&%+]+", blob)))
    out["sourcify_urls"] = urls
except Exception as e:
    try:
        r = subprocess.run(["curl","-s","-L","--max-time","25", f"https://sourcify.dev/server/v2/contract/56/{ADDR}?fields=abi,stdJson,metadata"],
                           capture_output=True, timeout=30)
        meta = json.loads(r.stdout.decode())
        abi = meta.get("abi", [])
        fns = [e.get("name") for e in abi if e.get("type")=="function"]
        site_fns = [n for n in fns if any(k in n.lower() for k in ("website","siteurl","domain","external","url","link"))]
        out["sourcify"] = {"verified": True, "n_fns": len(fns), "site_fns": site_fns,
                           "fn_names": sorted(set(fns)), "fetch": "curl-fallback"}
        blob = json.dumps(meta)
        out["sourcify_urls"] = sorted(set(re.findall(r"https?://[A-Za-z0-9._\-/:?#=&%+]+", blob)))
    except Exception as e2:
        out["sourcify"] = {"error": f"{type(e2).__name__}: {str(e2)[:200]}"}
json.dump(out, open(f"{HF}/run-2026-11-17-0731-dragon-gate.json","w"), indent=1)
print(json.dumps(out, indent=1)[:6000])
