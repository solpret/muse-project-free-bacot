#!/usr/bin/env python3
"""Run 0531 THYRK re-read (read-only, follow-up task).
THYRK 0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e — early lead reported by hot-leg
0524, NOT yet in onchain-snapshot.json. Reads fresh on-chain state so the entry
can be added to the snapshot at finalize. Curl transport via dataseed (25s).
Writes run-2026-11-10-0531-thyrk.json (never touches snapshot/state)."""
import json, subprocess, time
from Crypto.Hash import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
THY = "0x4D90fFC3075FB8897EDFf6d7c6269c906664a20e"
EPS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed2.bnbchain.org/",
       "https://bsc-dataseed.binance.org/"]
OUT = f"{BASE}/run-2026-11-10-0531-thyrk.json"
T0 = time.time()

def sel(s):
    k = keccak.new(digest_bits=256); k.update(s.encode()); return "0x" + k.hexdigest()[:8]
def enc_addr(a): return a[2:].lower().rjust(64, "0")
def enc_uint(n): return format(n, "064x")
def to_int(v):
    try:
        if v is None or v == "0x": return None
        return int(v, 16)
    except Exception: return None

def post_rpc(ep, payload, timeout=25):
    out = subprocess.run(["curl", "-sL", "--max-time", str(timeout), "-X", "POST", ep,
                          "-H", "Content-Type: application/json", "-d", json.dumps(payload)],
                         capture_output=True, text=True, timeout=timeout + 5).stdout
    return json.loads(out)

def raw_hex(addr, data):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                              "params": [{"to": addr, "data": data}, "latest"]}, timeout=25)
            if isinstance(r, dict) and "result" in r and r["result"] not in (None, "0x"):
                return r["result"]
        except Exception:
            continue
    return None

def raw_int(addr, sig, arg=None, argtype=None):
    data = sel(sig)
    if arg is not None:
        data += enc_addr(arg) if argtype == "address" else enc_uint(arg)
    return to_int(raw_hex(addr, data))

def decode_string(hexv):
    try:
        b = bytes.fromhex(hexv[2:])
        if len(b) < 96: return None
        ln = int.from_bytes(b[64:96], "big")
        return b[96:96+ln].decode("utf-8", "replace")
    except Exception:
        return None

def get_block():
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []}, timeout=25)
            return int(r["result"], 16)
        except Exception:
            continue
    return None

def block_ts(n):
    for ep in EPS:
        try:
            r = post_rpc(ep, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber",
                              "params": [hex(n), False]}, timeout=25)
            return int(r["result"]["timestamp"], 16)
        except Exception:
            continue
    return None

out = {"contract": THY, "name": "THYRK", "tag": "2026-11-10-0531",
       "hot_leg_baseline": {"block": 132665025, "totalSupply": 747, "freeMinted": 742,
                            "mintActive": 1, "first_seen_wib": "2026-11-10 05:19:52 WIB",
                            "slot_user": "terbuka (priceFor=0, quote=0)",
                            "website": "https://thyrk.fun (TERVERIFIKASI hot-leg)"},
       "special_read_0531": {"block": 132667374, "totalSupply": 1005, "freeMinted": 1000,
                             "mintActive": 1}}
out["head_block"] = get_block()
print("HEAD BLOCK", out["head_block"], flush=True)

reads = {}
reads["totalSupply"] = raw_int(THY, "totalSupply()")
reads["freeMinted"] = raw_int(THY, "freeMinted()")
reads["mintActive"] = raw_int(THY, "mintActive()")
reads["MAX_SUPPLY"] = raw_int(THY, "MAX_SUPPLY()")
reads["MAX_PER_WALLET"] = raw_int(THY, "MAX_PER_WALLET()")
reads["currentPrice"] = raw_int(THY, "currentPrice()")
reads["balanceOf_user"] = raw_int(THY, "balanceOf(address)", USER, "address")
reads["freeUsed_user"] = raw_int(THY, "freeUsed(address)", USER, "address")
reads["mintCount_user"] = raw_int(THY, "mintCount(address)", USER, "address")
reads["priceFor_user"] = raw_int(THY, "priceFor(address)", USER, "address")
reads["holdsAgentId_user"] = raw_int(THY, "holdsAgentId(address)", USER, "address")
reads["agentIdRegistry"] = raw_hex(THY, sel("agentIdRegistry()"))
reads["thyrkToken"] = raw_hex(THY, sel("thyrkToken()"))
hx = raw_hex(THY, sel("name()")); reads["name"] = decode_string(hx) if hx else None
hx = raw_hex(THY, sel("symbol()")); reads["symbol"] = decode_string(hx) if hx else None
hx = raw_hex(THY, sel("baseURI()")); reads["baseURI"] = decode_string(hx) if hx else None
out["reads"] = reads
for k, v in reads.items():
    print(f"  {k} = {v}", flush=True)

# --- velocity vs baselines (block timestamps) ---
out["head_ts"] = block_ts(out["head_block"]) if out["head_block"] else None
base_ts = block_ts(132665025)
spec_ts = block_ts(132667374)
out["baseline_ts"] = {"hot_leg_block_132665025": base_ts, "special_block_132667374": spec_ts}
vel = {}
fm_now = reads.get("freeMinted"); ts_now = reads.get("totalSupply")
if fm_now is not None and base_ts and out["head_ts"]:
    mins = (out["head_ts"] - base_ts) / 60.0
    vel["vs_hot_leg"] = {"freeMinted_delta": fm_now - 742, "totalSupply_delta": (ts_now - 747) if ts_now is not None else None,
                         "interval_min": round(mins, 2), "free_rate_per_min": round((fm_now - 742) / mins, 4) if mins > 0 else None,
                         "delta_ge_20": (fm_now - 742) >= 20,
                         "prev_rate": None, "ratio": None,
                         "note": "Tidak ada prev rate (interval pertama yang dilacak) — rasio velocity TIDAK terhitung; rate interval ini menjadi baseline."}
if fm_now is not None and spec_ts and out["head_ts"]:
    mins2 = (out["head_ts"] - spec_ts) / 60.0
    vel["vs_special_0531"] = {"freeMinted_delta": fm_now - 1000, "totalSupply_delta": (ts_now - 1005) if ts_now is not None else None,
                              "interval_min": round(mins2, 2), "free_rate_per_min": round((fm_now - 1000) / mins2, 4) if mins2 > 0 else None,
                              "delta_ge_20": (fm_now - 1000) >= 20}
out["velocity"] = vel
print("VELOCITY", json.dumps(vel), flush=True)

# --- legs / snapshot-ready entry ---
slot_open = (reads.get("freeUsed_user") == 0 and reads.get("priceFor_user") == 0
             and reads.get("mintActive") == 1)
out["legs"] = {
    "free_pct": "N/A (tanpa free cap — 1 free/wallet; MAX_SUPPLY=%s, freeMinted=%s)" % (reads.get("MAX_SUPPLY"), fm_now),
    "slot_user_open": slot_open,
    "slot_evidence": {"freeUsed_user (false=belum pakai)": reads.get("freeUsed_user"),
                      "priceFor_user": reads.get("priceFor_user"),
                      "balanceOf_user": reads.get("balanceOf_user"),
                      "mintCount_user": reads.get("mintCount_user"),
                      "holdsAgentId_user": reads.get("holdsAgentId_user"),
                      "mintActive": reads.get("mintActive")},
    "age": "UNVERIFIED presisi (pertama terlihat 2026-11-10 05:19:52 WIB; first-mint block persis tak terbaca — getLogs mati). Umur ≤48 jam belum terverifikasi presisi.",
    "website": "TERVERIFIKASI — https://thyrk.fun mencetak kontrak NFT+token persis (hot-leg; dicek ulang run 0531 via curl, 2 kemunculan alamat kontrak).",
    "promotion_to_strong_lead": "BELUM — butuh umur terverifikasi ≤48 jam + slot terbuka + website (website sudah ada). Slot saat ini: %s." % ("TERBUKA" if slot_open else "BELUM TERVERIFIKASI TERBUKA"),
}
out["snapshot_entry"] = {
    "address": THY, "name": "THYRK", "symbol": reads.get("symbol"),
    "status": "early-lead-reported-hot-leg-2026-11-10-0524",
    "totalSupply": ts_now, "freeMinted": fm_now,
    "mintActive": reads.get("mintActive"),
    "MAX_SUPPLY": reads.get("MAX_SUPPLY"), "MAX_PER_WALLET": reads.get("MAX_PER_WALLET"),
    "currentPrice": reads.get("currentPrice"),
    "priceFor_user": reads.get("priceFor_user"), "freeUsed_user": reads.get("freeUsed_user"),
    "balanceOf_user": reads.get("balanceOf_user"),
    "agentIdRegistry": reads.get("agentIdRegistry"), "thyrkToken": reads.get("thyrkToken"),
    "website": "https://thyrk.fun",
    "firstSeenWib": "2026-11-10 05:19:52 WIB", "firstSeenBlock": 132665025,
    "lastReadBlock": out["head_block"], "lastReadWib": "2026-11-10 06:14 WIB",
    "note": "Early lead dilaporkan hot-leg 0524 — JANGAN laporkan ulang sebagai baru. Bukan kandidat (umur presisi + % leg belum terverifikasi).",
}
out["elapsed_s"] = round(time.time() - T0, 1)
with open(OUT, "w") as f: json.dump(out, f, indent=1)
print("THYRK DONE in", out["elapsed_s"], "s ->", OUT, flush=True)
