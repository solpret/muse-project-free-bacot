#!/usr/bin/env python3
"""Hot-leg 0749 targeted re-read (ONE pass, <=24 calls, 1 chunk).
Follows 0734 precedent: all-None items in main pass are re-read once to
distinguish RPC read failure from a real state change."""
import json, subprocess, time
from eth_hash.auto import keccak

HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def curl(url, data=None, timeout=60):
    cmd = ["curl", "-sS", "-m", str(timeout), "-A", "Mozilla/5.0"]
    if data is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", data]
    cmd.append(url)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
        return p.stdout if p.returncode == 0 and p.stdout else None
    except Exception:
        return None

PLAN = [
 ("OLIVER", "0xad86e4d52e55709d1bda08f922853d4b109e0810",
  [("freeMinted", False), ("FREE_MAX", False), ("freeRemaining", False), ("mintOpen", False)]),
 ("binanceai-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E",
  [("launched", False), ("failed", False), ("isRefundPhase", False), ("tokenClaimed", True)]),
 ("AngelEye-77D9", "0x77D98247BA3dDAfa9ffBceA1F13d3e4cFe3f2d4C",
  [("freeMinted", False), ("freeRemaining", False), ("FREE_POOL", False),
   ("saleActive", False), ("mintStart", False)]),
 ("AbsurdAgentNFT", "0x72c14121681F1133545947B0735563835CC07B67",
  [("totalMinted", False), ("mintOpen", False), ("mintStartTime", False)]),
 ("AZEN", "0x699b6397986cc6c444069efe692023b1253dc26d",
  [("totalSupply", False), ("MAX_SUPPLY", False), ("freeMintedPerWallet", True)]),
 ("CRACE", "0x7B1ca439312368dE8652b9B5d7A54cA74A884680",
  [("FREE_QUOTA", False), ("mintOpen", False), ("totalSupply", False), ("freeClaimed", True)]),
]
reqs, keys = [], []
for name, addr, views in PLAN:
    for fn, uarg in views:
        data = sel(fn + ("(address)" if uarg else "()")) + (USER_PAD if uarg else "")
        reqs.append({"jsonrpc": "2.0", "id": len(reqs), "method": "eth_call",
                     "params": [{"to": addr, "data": data}, "latest"]})
        keys.append((name, fn + ("_user" if uarg else "")))
print("calls:", len(reqs))
body = curl("https://bsc-dataseed.binance.org/", data=json.dumps(reqs), timeout=60)
if not body:
    body = curl("https://bsc-dataseed1.bnbchain.org/", data=json.dumps(reqs), timeout=60)
reads = {}
if body:
    try:
        resp = json.loads(body)
        items = resp if isinstance(resp, list) else [resp]
        by_id = {it.get("id"): it for it in items if isinstance(it, dict)}
        for cid, r, err in [(c["id"], by_id.get(c["id"], {}).get("result"), by_id.get(c["id"], {}).get("error")) for c in reqs]:
            name, fn = keys[cid]
            v = None
            if r and r != "0x" and len(r) >= 66:
                try:
                    v = int(r[-64:], 16)
                except Exception:
                    v = None
            reads.setdefault(name, {})[fn] = v
    except Exception as e:
        reads = {"parse_error": str(e)}
else:
    reads = {"fetch_error": "both endpoints empty"}
out = {"run": "free-mint-hot-leg 2026-11-14 07:49 WIB targeted re-read",
       "crawl_wib": time.strftime("%Y-%m-%dT%H:%M:%S+07:00", time.gmtime(time.time() + 7 * 3600)),
       "reads": reads}
json.dump(out, open(f"{HF}/hot-leg-run-2026-11-14-0749-reread.json", "w"), indent=1)
print(json.dumps(out, indent=1))
