#!/usr/bin/env python3
"""Follow-up probe backfill 132480915-132486914 (read-only).
Sakura Ronin 0xE56f...: remainingFree/currentPhase/mintOpen/agentGateOn/maxSupply/
costOf(user,1)/mintedBy(user)/allowanceOf(user)/phasePrices/phaseQuotas.
0xe4c7... (Sourcify unverified, registry-bytes hit): direct agentRegistry()/owner()/
name()/symbol()/totalSupply() calls.
Writes backfill-triage-132480915-132486914-followup.json. No preview/mint/sign.
"""
import json, subprocess
from eth_hash.auto import keccak

RPC_EPS = ["https://bsc-dataseed2.bnbchain.org/",
           "https://bsc-dataseed3.bnbchain.org/",
           "https://bsc-dataseed.binance.org/",
           "https://bsc-dataseed1.bnbchain.org/"]

def rpc(method, params, timeout=30):
    payload = json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1})
    last = None
    for ep in RPC_EPS:
        try:
            r = subprocess.run(["curl", "-s", "-m", str(timeout), "-X", "POST", ep,
                                "-H", "Content-Type: application/json", "-d", payload],
                               capture_output=True, text=True, timeout=timeout + 10)
            d = json.loads(r.stdout)
            if "error" in d:
                return {"error": str(d["error"])[:150]}
            return d.get("result")
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
    raise OSError(f"all curl-RPC endpoints failed: {last}")

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
SR = "0xE56fD19a19E684b94db1Dd3c81896736E3631D47"
UNK = "0xe4c7e94Bdb109e2B37e45dB46B4f6944e8F5358f"

def sel(sig):
    return keccak(sig.encode())[:4].hex()

def enc_addr(a):
    return "0" * 24 + a.lower()[2:]

def enc_uint(n):
    return format(int(n), "064x")

def eth_call(to, data):
    try:
        r = rpc("eth_call", [{"to": to, "data": data}, "latest"])
        if isinstance(r, dict) and "error" in r:
            return {"error": str(r["error"])[:150]}
        return {"result": r}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {str(e)[:150]}"}

def dec_addr(h):
    if not h or h == "0x" or len(h) < 66:
        return None
    return "0x" + h[-40:]

def dec_uint(h):
    if not h or h == "0x":
        return None
    try:
        return int(h, 16)
    except Exception:
        return None

def dec_bool(h):
    v = dec_uint(h)
    return bool(v) if v is not None else None

def dec_str(h):
    if not h or h == "0x" or len(h) < 130:
        return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + ln * 2]).decode("utf-8", "replace")
    except Exception:
        return None

def vcall(addr, sig, args=None, decode="uint"):
    data = "0x" + sel(sig)
    for a in (args or []):
        if isinstance(a, str) and a.startswith("0x") and len(a) == 42:
            data += enc_addr(a)
        else:
            data += enc_uint(a)
    r = eth_call(addr, data)
    if "error" in r:
        return {"fn": sig, "error": r["error"]}
    h = r["result"]
    if decode == "uint":
        v = dec_uint(h)
    elif decode == "addr":
        v = dec_addr(h)
    elif decode == "bool":
        v = dec_bool(h)
    elif decode == "str":
        v = dec_str(h)
    elif decode == "raw":
        v = h
    else:
        v = h
    return {"fn": sig, "value": v}

out = {"sakura_ronin": {"contract": SR}}
sr = out["sakura_ronin"]
for sig, dec in [("remainingFree()", "uint"), ("currentPhase()", "uint"),
                 ("mintOpen()", "bool"), ("agentGateOn()", "bool"),
                 ("maxSupply()", "uint"), ("baseMaxPerWallet()", "uint"),
                 ("referralCap()", "uint"), ("totalMinted()", "uint")]:
    sr[sig] = vcall(SR, sig, decode=dec)
sr["costOf(user,1)"] = vcall(SR, "costOf(address,uint256)", [USER, 1])
sr["mintedBy(user)"] = vcall(SR, "mintedBy(address)", [USER])
sr["allowanceOf(user)"] = vcall(SR, "allowanceOf(address)", [USER])
sr["bonusEarned(user)"] = vcall(SR, "bonusEarned(address)", [USER])
sr["balanceOf(user)"] = vcall(SR, "balanceOf(address)", [USER])
ph = sr["currentPhase()"].get("value")
if isinstance(ph, int):
    for p in range(0, ph + 1):
        sr[f"phasePrices({p})"] = vcall(SR, "phasePrices(uint256)", [p])
        sr[f"phaseQuotas({p})"] = vcall(SR, "phaseQuotas(uint256)", [p])
        sr[f"phaseAt({p})"] = vcall(SR, "phaseAt(uint256)", [p])

out["unknown_0xe4c7"] = {"contract": UNK}
uk = out["unknown_0xe4c7"]
for sig, dec in [("agentRegistry()", "addr"), ("owner()", "addr"),
                 ("name()", "str"), ("symbol()", "str"),
                 ("totalSupply()", "uint"), ("totalMinted()", "uint"),
                 ("freeMinted()", "uint")]:
    uk[sig] = vcall(UNK, sig, decode=dec)
uk["freeClaimed(user)"] = vcall(UNK, "freeClaimed(address)", [USER])
try:
    code = rpc("eth_getCode", [UNK, "latest"])
    uk["code_len_bytes"] = (len(code) - 2) // 2 if code else 0
    uk["registry_bytes_in_code"] = "60b9262456de011f7d15a54cdd8c48baaa8b022f" in (code or "").lower()
except Exception as e:
    uk["code_error"] = f"{type(e).__name__}: {e}"
# owner vs discards
try:
    disc = json.load(open(f"{BASE}/same-owner-discards.json"))
    owners = set()
    if isinstance(disc, dict):
        for v in disc.values():
            if isinstance(v, dict):
                o = v.get("owner") or v.get("owner_address")
                if o: owners.add(o.lower())
            elif isinstance(v, str):
                owners.add(v.lower())
    elif isinstance(disc, list):
        for v in disc:
            if isinstance(v, dict):
                o = v.get("owner") or v.get("owner_address")
                if o: owners.add(o.lower())
            elif isinstance(v, str):
                owners.add(v.lower())
    oc = uk.get("owner()")
    ov = oc.get("value") if isinstance(oc, dict) else None
    uk["owner_in_discards"] = (ov.lower() in owners) if ov else None
    uk["discards_owner_count"] = len(owners)
except Exception as e:
    uk["discards_error"] = f"{type(e).__name__}: {e}"

json.dump(out, open(f"{BASE}/backfill-triage-132480915-132486914-followup.json", "w"), indent=1)
print(json.dumps(out, indent=1))
