#!/usr/bin/env python3
"""Hot-leg run 2026-11-11 12:14 WIB. Legs: feed shape-check (done partly inline),
Boltbook, leg4 prio re-read via fast_rpc.batch eth_call. Read-only; no preview/mint."""
import json, sys, time, urllib.request
sys.path.insert(0, "/home/hatch/workspace/fast_exec")
sys.path.insert(0, "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files")
from fast_rpc import _single
from Crypto.Hash import keccak

USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = "0" * 24 + USER[2:].lower()
HF = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"

def sel(sig):
    k = keccak.new(digest_bits=256); k.update(sig.encode()); return "0x" + k.hexdigest()[:8]

def call_spec(to, sig, args_hex=""):
    return {"to": to, "data": sel(sig) + args_hex}

def decode_uint(h):
    if not h or h == "0x" or len(h) < 66: return None
    try: return int(h[2:66], 16)
    except Exception: return None

def decode_str(h):
    if not h or len(h) < 130: return None
    try:
        ln = int(h[66:130], 16)
        return bytes.fromhex(h[130:130 + 2 * ln]).decode("utf-8", "replace")
    except Exception: return None

# curated no-arg + user-arg reads per contract: (label, sig, argkind)
# argkind: None | 'user' | 'agentid'
PRIO = {
 "NIGHTFORGE": ("0x22f43ba09fd4beb9417d4484c60370354b220186", [
    ("totalSupply","totalSupply()","uint"),("mintOpen","mintOpen()","uint"),
    ("agentFreeUsed","agentFreeUsed()","uint"),("freeLeft","freeLeft()","uint"),
    ("balanceOf_user","balanceOf(address)","user"),("agentFreeByWallet_user","agentFreeByWallet(address)","user")]),
 "AgentPals": ("0xD265a929D0E50bD5ee4675e4E97F38D8380802E2", [
    ("totalMinted","totalMinted()","uint"),("freeMinted","freeMinted()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "ABYSSCABLE": ("0xd2e9242b0d7c0186cc181a5fc8534541dad278a2", [
    ("totalSupply","totalSupply()","uint"),("agentFreeUsed","agentFreeUsed()","uint"),
    ("mintOpen","mintOpen()","uint"),("balanceOf_user","balanceOf(address)","user")]),
 "Stampooor": ("0x467696af8c2206B977B24081445104632dc1D459", [
    ("totalMinted","totalMinted()","uint"),("freeMinted","freeMinted()","uint"),
    ("FREE_SUPPLY","FREE_SUPPLY()","uint"),("mintOpen","mintOpen()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "LOWB": ("0x00487ED061C77A1dd5085ef3a2D593366f9C6B35", [
    ("opened","opened()","uint"),("totalFreeMinted","totalFreeMinted()","uint"),
    ("totalMinted","totalMinted()","uint")]),
 "SHINE": ("0xDDc2352d1ceC10b42e05A297232f5328902C6c2C", [
    ("launched","launched()","uint"),("startTime","startTime()","uint"),
    ("freeClaimed_user","freeClaimed(address)","user")]),
 "UFO": ("0xE4059eA596392AcA14100af6CDC9481c330E2728", [
    ("FREE_SHARES","FREE_SHARES()","uint"),("freeClaimed_user","freeClaimed(address)","user")]),
 "CAP7": ("0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd", [
    ("freeMinted","freeMinted()","uint"),("sharesMinted","sharesMinted()","uint"),
    ("soldOut","soldOut()","uint"),("phase","phase()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "RigForge": ("0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
    ("SALE_START","SALE_START()","uint"),("FREE_SHARES","FREE_SHARES()","uint"),
    ("freeSharesLeft","freeSharesLeft()","uint"),("openedAt","openedAt()","uint")]),
 "BotFighters": ("0x58a704d9e02FE11c0A61683AE7F606E4366F13eb", [
    ("FREE_CAP","FREE_CAP()","uint"),("freeMinted","freeMinted()","uint"),
    ("balanceOf_user","balanceOf(address)","user")]),
 "CopperNook": ("0xb5b121e1CEC5aDD53708DB93D8997a837918f89e", [
    ("name","name()","str"),("symbol","symbol()","str"),("PRICE","PRICE()","uint"),
    ("spotsLeft","spotsLeft()","uint"),("totalSpotsMinted","totalSpotsMinted()","uint"),
    ("MAX_SPOTS","MAX_SPOTS()","uint"),("AGENT_REGISTRY","AGENT_REGISTRY()","addr"),
    ("isAgent_user","isAgent(address)","user"),("quote1","quote(uint256)","uint1")]),
 "EmberFord": ("0x6d02F55f4d21220d3F60498C963A4e882a564A7f", [
    ("name","name()","str"),("symbol","symbol()","str"),("PRICE","PRICE()","uint"),
    ("spotsLeft","spotsLeft()","uint"),("totalSpotsMinted","totalSpotsMinted()","uint"),
    ("MAX_SPOTS","MAX_SPOTS()","uint"),("AGENT_REGISTRY","AGENT_REGISTRY()","addr"),
    ("isAgent_user","isAgent(address)","user"),("quote1","quote(uint256)","uint1")]),
}
# CAP7 freeClaimed(agentId) needs agentId; get agentIdOf(user) first via separate call
AGENTID = "12411464190637771618140538948436718430879438309640658942350393382867700450815750101755948145101197728078227495339265465644916641821446368465628375122182145"

t0 = time.time()
calls, meta = [], []
for name, (addr, specs) in PRIO.items():
    for label, sig, kind in specs:
        arg = ""
        if kind == "user": arg = USER_PAD
        elif kind == "uint1": arg = "0" * 63 + "1"
        calls.append(("eth_call", [{"to": addr, "data": sel(sig) + arg}, "latest"]))
        meta.append((name, label, kind))
# agentIdOf(user) for CAP7 + freeClaimed(agentId)
calls.append(("eth_call", [{"to": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd", "data": sel("agentIdOf(address)") + USER_PAD}, "latest"]))
meta.append(("CAP7", "agentIdOf_user", "uint"))
calls.append(("eth_call", [{"to": "0x748F6a0613D55cEc01fcF59B8Cb09f381b10B7Fd", "data": sel("freeClaimed(uint256)") + format(int(AGENTID), "064x")}, "latest"]))
meta.append(("CAP7", "freeClaimed_agentId", "uint"))
# head block
calls.append(("eth_blockNumber", [])); meta.append(("HEAD", "block", "uint"))

results = {}
EPS = ["https://bsc-dataseed.binance.org/", "https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/", "https://bsc-dataseed3.bnbchain.org/"]
for (name, label, kind), (method, params) in zip(meta, calls):
    val = None; err = None
    for ep in EPS:
        try:
            val = _single(ep, method, params, 12, retries=0)
            break
        except Exception as e:
            err = str(e)[:120]
    if val is None:
        results.setdefault(name, {})[label] = {"error": err}
    elif kind == "str":
        results.setdefault(name, {})[label] = decode_str(val)
    elif kind == "addr":
        results.setdefault(name, {})[label] = "0x" + val[-40:] if isinstance(val, str) and len(val) >= 42 else val
    else:
        results.setdefault(name, {})[label] = decode_uint(val)
head = results.get("HEAD", {}).get("block")
print(json.dumps({"block": head, "values": {k: v for k, v in results.items() if k != "HEAD"}, "elapsed": round(time.time() - t0, 1)}, indent=1))
with open(HF + "hot-leg-2026-11-11-1214-prio.json", "w") as f:
    json.dump({"block": head, "values": {k: v for k, v in results.items() if k != "HEAD"}}, f, indent=1)
