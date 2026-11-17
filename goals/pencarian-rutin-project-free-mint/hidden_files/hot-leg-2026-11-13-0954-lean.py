#!/usr/bin/env python3
"""Hot-leg 0954 LEAN salvage v2: ONE direct JSON-RPC batch via curl to a
single BSC dataseed (bypasses fast_rpc race/batch which stalled twice),
plus curl retries for Sourcify shape-check (3 feed-new) and Boltbook.
Strict timeouts. Read-only. Writes hot-leg-run-2026-11-13-0954-lean.json."""
import json, re, subprocess, sys, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=25):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

# minimal views: (name, addr, [(fn, userarg?)])
PLAN = [
 ("OBFG", "0x5314071bba19943f58347ba5dec423e5032a6818",
  [("freeMinted", False), ("FREE_SUPPLY", False), ("saleOpen", False), ("freeAvailable", True)]),
 ("JNTM", "0x13204B86c56e709a7E2D1e95ABBA3638a93FB84b",
  [("freeClaimed", False), ("FREE_LOTS_CAP", False), ("opened", False), ("mintStart", False)]),
 ("Agentx", "0x64a5e5f475defdf9b7302cc40641a1cbcb94e492",
  [("freeMinted", False), ("FREE_CAP", False), ("freeClaimed", True)]),
 ("BC1B", "0xBC1B62550D69Fc02683CD4836f24CBf5D90BE053",
  [("freeCount", False), ("FREE_CAP", False)]),
 ("Pickgrid", "0x7f541bcc33abed0e64455565da723e949c6f76f0",
  [("freeMinted", False)]),
 ("MECHA", "0xEEe31D337866a57cD59fdECc8B6e6548e182Ea78",
  [("freeClaimed", False)]),
 ("NOTV", "0x0415d265FdaE1CE6D0E778f78Daf6D0722f6Ab01",
  [("totalMinted", False)]),
]

def main():
    t0 = time.time()
    out = {"run": "hot-leg 0954 lean salvage v2 (single direct batch)",
           "started_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600))}
    # Sourcify shape-check retry + Boltbook retry via curl
    sc = {}
    for a in ("0x7535181f3b2208a560F90B6A1F6c473D0fDafefa",
              "0xf96c66a8730df490037B7cd1cc2Ca1a17a544444",
              "0xb31De539a79A5B5d9Bf6A6071f38240E19Fc2D7b"):
        body = curl(f"https://sourcify.dev/server/v2/contracts/56/{a}", timeout=20)
        if not body:
            sc[a] = {"status": "shape-check-failed", "reason": "sourcify-fetch-failed"}
            continue
        try:
            meta = json.loads(body)
            abi = meta["stdJson"]["output"]["abi"]
        except Exception:
            sc[a] = {"status": "shape-check-failed", "reason": "no-abi-in-sourcify"}
            continue
        fns = {e.get("name") for e in abi if e.get("type") == "function"}
        mint = any(n in fns for n in ("mint", "mintFree", "claimFree", "mintWithAgentId"))
        quote = any(n in fns for n in ("quote", "cost", "getQuote", "price"))
        free = [n for n in fns if n.startswith("free")]
        agent = any(n in fns for n in ("agentId", "registry", "AGENT_ID_REGISTRY", "agentRegistry", "agentGate")) or "0x60b9262456de011f7d15a54cdd8c48baa8b022f" in json.dumps(abi).lower()
        s1 = bool(mint and quote and free and agent)
        s2 = bool(("name" in fns or "symbol" in fns) and ("mintFree" in fns or "claimFree" in fns) and free and agent)
        sc[a] = {"S1": s1, "S2": s2, "mint": mint, "quote": quote, "free": free,
                 "agent": agent, "status": "ok" if (s1 or s2) else "not-sale-shape"}
    out["shapecheck_retry"] = sc
    bb = {}
    for lang, url in (("en", "https://boltbook.fun/"), ("zh", "https://boltbook.fun/?lang=zh")):
        body = curl(url, timeout=20)
        if body:
            bb[lang] = {"bytes": len(body), "addrs": sorted(set(re.findall(r"0x[0-9a-fA-F]{40}", body)))}
        else:
            bb[lang] = {"error": "fetch-failed"}
    out["boltbook_retry"] = bb

    # single direct batch
    reqs, keys = [], []
    for name, addr, views in PLAN:
        for fn, uarg in views:
            data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
            reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                         "params": [{"to": addr, "data": data}, "latest"]})
            keys.append((name, fn + ("_user" if uarg else "")))
    reads = {}
    body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(reqs), timeout=30)
    if body:
        try:
            resp = json.loads(body)
            for item in resp if isinstance(resp, list) else [resp]:
                i = item.get("id")
                if i is None:
                    continue
                name, fn = keys[i]
                r = item.get("result")
                v = None
                if r and r != "0x" and len(r) >= 66:
                    try:
                        v = int(r[-64:], 16)
                    except Exception:
                        v = None
                reads.setdefault(name, {})[fn] = v
        except Exception as e:
            out["batch_error"] = f"parse-failed: {e}"
    else:
        out["batch_error"] = "dataseed-batch-fetch-failed"
    out["reads"] = reads
    out["reads_ok"] = sum(1 for n in reads if any(v is not None for v in reads[n].values()))
    out["elapsed_s"] = round(time.time() - t0, 1)
    json.dump(out, open(f"{HF}/hot-leg-run-2026-11-13-0954-lean.json", "w"), indent=1)
    print(json.dumps(out, indent=1))

if __name__ == "__main__":
    main()
