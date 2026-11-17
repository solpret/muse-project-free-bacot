#!/usr/bin/env python3
"""Triage backfill chunk 131903549-131905548 first-seen (read-only)."""
import json, sys, time, urllib.request, urllib.error
from eth_hash.auto import keccak

EPS = ["https://bsc-dataseed.binance.org/",
       "https://bsc-dataseed1.bnbchain.org/",
       "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed3.bnbchain.org/"]
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
REGISTRY_EXPECTED = "0x60B9262456dE011F7d15a54CdD8c48bAaa8B022F"

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def single(ep, method, params, timeout=10):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read().decode())
    if "error" in d:
        raise RuntimeError(str(d["error"]))
    return d["result"]

def rpc(method, params, timeout=10):
    last = None
    for ep in EPS:
        try:
            return single(ep, method, params, timeout)
        except Exception as e:
            last = e
    raise last

def call(addr, data, timeout=10):
    return rpc("eth_call", [{"to": addr, "data": data}, "latest"], timeout)

def u256(hexdata):
    if not isinstance(hexdata, str) or not hexdata.startswith("0x") or len(hexdata) < 66:
        return None
    return int(hexdata[-64:], 16)

def addr_of(hexdata):
    if not isinstance(hexdata, str) or not hexdata.startswith("0x") or len(hexdata) < 66:
        return None
    return "0x" + hexdata[-40:]

def dec_str(hexdata):
    if not isinstance(hexdata, str) or not hexdata.startswith("0x"):
        return None
    raw = bytes.fromhex(hexdata[2:])
    if len(raw) >= 64:
        try:
            ln = int.from_bytes(raw[32:64], "big")
            if 0 < ln <= len(raw) - 64:
                return raw[64:64+ln].decode("utf-8", "replace")
        except Exception:
            pass
    if len(raw) == 32:
        return raw.rstrip(b"\x00").decode("utf-8", "replace") or None
    return None

def enc_addr(a):
    return "0x" + "0"*24 + a[2:].lower()

def enc_u256(n):
    return "0x" + format(n, "064x")

def block_ts(blk):
    b = rpc("eth_getBlockByNumber", [hex(blk), False], timeout=10)
    return int(b["timestamp"], 16) if b else None

def main():
    targets = [
        ("0x3102812c656128ECAbAAfc0C9b1a18d6675a30f9", 131903757, "Pulse Viper Agent/PULV"),
        ("0x2FD93F9EbA69Ee7C46a18c469F816B0E4c22e12c", 131904459, "?"),
        ("0xE8Ec42bDce6898c962A60971F428029265335aa4", 131905162, "?"),
    ]
    discards = json.load(open("same-owner-discards.json"))
    discard_owners = set()
    if isinstance(discards, list):
        for r in discards:
            o = r.get("owner") or r.get("owner_address") or r.get("address")
            if o: discard_owners.add(o.lower())
    elif isinstance(discards, dict):
        for v in discards.values():
            if isinstance(v, dict):
                o = v.get("owner") or v.get("owner_address")
                if o: discard_owners.add(o.lower())
    print("discard owners loaded:", len(discard_owners))
    out = {}
    for addr, fblk, label in targets:
        print(f"\n== {addr} ({label}) first_block={fblk}")
        r = {}
        try:
            r["first_block_ts"] = block_ts(fblk)
            import datetime
            r["first_block_wib"] = datetime.datetime.fromtimestamp(
                r["first_block_ts"], datetime.timezone(datetime.timedelta(hours=7))
            ).strftime("%Y-%m-%d %H:%M:%S WIB") if r["first_block_ts"] else None
        except Exception as e:
            r["first_block_ts_error"] = str(e)
        print("  first mint:", r.get("first_block_wib"), r.get("first_block_ts"))
        for name, sig, dec in [
            ("AGENT_REGISTRY", "AGENT_REGISTRY()", addr_of),
            ("PRICE", "PRICE()", u256),
            ("MAX_SUPPLY", "MAX_SUPPLY()", u256),
            ("MAX_PER_WALLET", "MAX_PER_WALLET()", u256),
            ("minted", "minted()", u256),
            ("spotsLeft", "spotsLeft()", u256),
            ("OWNER", "OWNER()", addr_of),
            ("TREASURY", "TREASURY()", addr_of),
            ("name", "name()", dec_str),
            ("symbol", "symbol()", dec_str),
            ("BASE_URI", "BASE_URI()", dec_str),
        ]:
            try:
                v = dec(call(addr, sel(sig)))
                r[name] = v
                print(f"  {name}: {v}")
            except Exception as e:
                r[name + "_error"] = str(e)
                print(f"  {name}: ERROR {e}")
        # quote(user,1)
        try:
            q = u256(call(addr, sel("quote(uint256)") + enc_u256(1)[2:]))
            r["quote_user_1"] = q
            print(f"  quote(user,1) [quote(1) pure]: {q} wei = {q/1e18 if q is not None else None} BNB")
        except Exception as e:
            r["quote_error"] = str(e)
            print(f"  quote: ERROR {e}")
        # mintedBy(user)
        try:
            mb = u256(call(addr, sel("mintedBy(address)") + enc_addr(USER)[2:]))
            r["mintedBy_user"] = mb
            print(f"  mintedBy(user): {mb}")
        except Exception as e:
            r["mintedBy_error"] = str(e)
            print(f"  mintedBy: ERROR {e}")
        # agentRegistry() lowercase variant (body requirement) — try, expect revert if absent
        try:
            v = addr_of(call(addr, sel("agentRegistry()")))
            r["agentRegistry_fn"] = v
            print(f"  agentRegistry(): {v}")
        except Exception as e:
            r["agentRegistry_fn_error"] = str(e)
            print(f"  agentRegistry(): ERROR/revert {e}")
        owner = (r.get("OWNER") or "").lower()
        # owner() lowercase variant
        try:
            v = addr_of(call(addr, sel("owner()")))
            r["owner_fn"] = v
            print(f"  owner(): {v}")
            if not owner:
                owner = (v or "").lower()
        except Exception as e:
            r["owner_fn_error"] = str(e)
            print(f"  owner(): ERROR/revert {e}")
        # quote(address,uint256) variant for user wallet
        try:
            q2 = u256(call(addr, sel("quote(address,uint256)") + enc_addr(USER)[2:] + enc_u256(1)[2:]))
            r["quote_addr_user_1"] = q2
            print(f"  quote(user,1) [quote(address,uint256)]: {q2} wei = {q2/1e18 if q2 is not None else None} BNB")
        except Exception as e:
            r["quote_addr_error"] = str(e)
            print(f"  quote(address,uint256): ERROR/revert {e}")
        # free quota views
        for name, sig, dec in [
            ("freeClaimed_user", "freeClaimed(address)", None),
            ("freeMinted", "freeMinted()", u256),
            ("FREE_SUPPLY", "FREE_SUPPLY()", u256),
            ("FREE_SLOTS", "FREE_SLOTS()", u256),
            ("freeSupply", "freeSupply()", u256),
            ("totalFreeMinted", "totalFreeMinted()", u256),
            ("freeAllocation", "freeAllocation()", u256),
            ("totalSupply", "totalSupply()", u256),
            ("totalMinted", "totalMinted()", u256),
            ("maxSupply", "maxSupply()", u256),
            ("mintPrice", "mintPrice()", u256),
        ]:
            try:
                data = sel(sig)
                if "(address)" in sig:
                    data = data + enc_addr(USER)[2:]
                v = call(addr, data)
                r[name] = (u256(v) if dec is u256 else (dec(v) if dec else v))
                print(f"  {name}: {r[name]}")
            except Exception as e:
                r[name + "_error"] = str(e)
                print(f"  {name}: ERROR {e}")
        # Sourcify ABI via curl fallback (urllib often IncompleteRead)
        try:
            import subprocess
            url = f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=abi"
            p = subprocess.run(["curl", "-s", "-m", "20", "-A", "Mozilla/5.0", url],
                               capture_output=True, text=True, timeout=30)
            d = json.loads(p.stdout)
            abi = d.get("abi")
            if isinstance(abi, list):
                fns = sorted({it.get("name", "") for it in abi if it.get("type") == "function"})
                r["sourcify"] = "verified"
                r["abi_functions"] = fns
                print(f"  sourcify: verified, {len(fns)} fns: {fns}")
            else:
                r["sourcify"] = "no-abi"
                print(f"  sourcify: no-abi in response")
        except Exception as e:
            r["sourcify"] = f"error:{type(e).__name__}"
            print(f"  sourcify: ERROR {e}")
        r["owner_in_discards"] = owner in discard_owners if owner else None
        print(f"  owner in same-owner-discards: {r['owner_in_discards']}")
        r["registry_match_expected"] = (
            (r.get("AGENT_REGISTRY") or "").lower() == REGISTRY_EXPECTED.lower())
        print(f"  AGENT_REGISTRY == expected 0x60B9...22F: {r['registry_match_expected']}")
        out[addr] = r
    json.dump(out, open("/tmp/triage-131903549-131905548.json", "w"), indent=1)
    print("\nsaved /tmp/triage-131903549-131905548.json")

if __name__ == "__main__":
    main()
