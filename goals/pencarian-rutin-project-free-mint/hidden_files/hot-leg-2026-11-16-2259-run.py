#!/usr/bin/env python3
"""Hot-leg 2026-11-16 22:59 WIB — legs 1+2+bridge+leg4, curl-based, read-only.
Reuses the 22:54 pattern (shape_check with ?fields=metadata,abi; registry
check also via bytecode; bridge via bridge['contracts'] vs snapshot addrs)
with the 22:54 15-item re-read plan PLUS ORBIT/RigForge/CosmicSentinel/BUBB
from the 22:54 plan; diff baseline = hot-leg-2026-11-16-2254-reread.json.
Poffzi NOT re-read (dedicated fcfs_fast loop owns it); loop liveness noted
via pgrep only.
Writes: hot-leg-2026-11-16-2259-sourcify.json, -feedshape.json,
 hot-leg-2026-11-16-2259-boltbook-en.html/.json, -boltbook-zh.html/.json,
 hot-leg-2026-11-16-2259-reread.json, hot-leg-2026-11-16-2259-runlog.md
Never writes the main snapshot / main seen files / bridge."""
import json, os, re, subprocess, time
from eth_hash.auto import keccak

BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files"
STAMP = "2026-11-16-2259"
USER = "0xeb237F6f9FB4e826739F0954e9768914F28b2c2E"
USER_PAD = USER[2:].lower().rjust(64, "0")
REGISTRY = "0x60b9262456de011f7d15a54cdd8c48baa8b022f"
REG_HEX = REGISTRY[2:].lower()
ENDPOINTS = ["https://bsc-dataseed1.bnbchain.org/", "https://bsc-dataseed.binance.org/",
             "https://bsc-dataseed2.bnbchain.org/", "https://bsc-rpc.publicnode.com/"]
FREE_VIEWS = ["freeSharesRemaining", "freeClaimed", "freeFor", "freeLeft",
              "freeUsed", "freeAvailable", "freeSharePoolExhausted", "freeSharesClaimed",
              "freeMinted", "freeMintedBy"]
ADDR_RE = re.compile(r"0x[a-fA-F0-9]{40}")

def curl(url, timeout=25, extra=None):
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-L"] + (extra or []) + [url]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
    return p.returncode, p.stdout, p.stderr

def load_json(path):
    with open(path) as f:
        return json.load(f)

def sel(sig):
    return "0x" + keccak(sig.encode()).hex()[:8]

def rpc_batch(calls, endpoint, timeout=25):
    payload = json.dumps([{"jsonrpc": "2.0", "id": i, "method": "eth_call",
                           "params": [{"to": to, "data": data}, "latest"]}
                          for i, (to, data) in enumerate(calls)])
    p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-X", "POST",
                        "-H", "Content-Type: application/json", "-d", payload,
                        endpoint], capture_output=True, text=True, timeout=timeout + 5)
    if p.returncode != 0:
        raise RuntimeError(f"curl rc={p.returncode} {p.stderr[:100]}")
    d = json.loads(p.stdout)
    if isinstance(d, dict) and "error" in d:
        raise RuntimeError(f"rpc error: {d['error']}")
    return [r.get("result") if isinstance(r, dict) else None for r in d]

def rpc_single(method, endpoint, timeout=20):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []})
    p = subprocess.run(["curl", "-sS", "--max-time", str(timeout), "-X", "POST",
                        "-H", "Content-Type: application/json", "-d", payload,
                        endpoint], capture_output=True, text=True, timeout=timeout + 5)
    return json.loads(p.stdout).get("result")

def decode(h):
    if h is None:
        return None
    h = h[2:] if h.startswith("0x") else h
    if not h:
        return None
    try:
        return int(h, 16)
    except ValueError:
        return f"RAW:{h[:40]}"

def get_code(addr):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_getCode",
                          "params": [addr, "latest"]})
    for ep in ENDPOINTS:
        try:
            p = subprocess.run(["curl", "-sS", "--max-time", "20", "-X", "POST",
                                "-H", "Content-Type: application/json", "-d", payload,
                                ep], capture_output=True, text=True, timeout=25)
            return json.loads(p.stdout).get("result", "") or ""
        except Exception:
            continue
    return ""

def shape_check(addr):
    rc, out, err = curl(f"https://sourcify.dev/server/v2/contract/56/{addr}?fields=metadata,abi", timeout=20)
    fns = []
    if rc == 0 and out:
        try:
            d = json.loads(out)
            abi = d.get("abi") or (d.get("metadata") or {}).get("output", {}).get("abi") or []
            for e in abi:
                if isinstance(e, dict) and e.get("type") == "function":
                    fns.append(e.get("name", ""))
        except Exception:
            pass
    names = set(fns)
    mint = any(n.startswith("mint") or n in ("claimFree", "claim") for n in names)
    quote = any("quote" in n.lower() or "cost" in n.lower() for n in names)
    free_views = [v for v in FREE_VIEWS if v in names]
    code = get_code(addr)
    agent = ("AGENT_ID_REGISTRY" in names or "agentRegistry" in names or
             "agentGate" in names or "AgentGate" in names or
             "AGENT_ID" in names or REG_HEX in code.lower())
    token = bool({"name", "symbol", "decimals", "totalSupply"} & names)
    mint_free = "mintFree" in names
    free_slots = bool({"FREE_SLOTS", "FREE_SUPPLY"} & names)
    s1 = mint and quote and bool(free_views) and agent
    s2 = token and mint_free and bool({"freeClaimed", "freeMinted"} & names) and \
        free_slots and agent
    return {"shape": ("S1" if s1 else "S2" if s2 else "checked-not-sale-shape"),
            "fns": len(fns), "mint": mint, "quote": quote,
            "free_views": free_views, "registry": agent, "token": token,
            "mintFree": mint_free, "free_slots_const": free_slots}

def main():
    t0 = time.time()
    log = []
    seen = load_json(os.path.join(BASE, "hot-leg-seen.json"))
    seen_lower = {k.lower(): k for k in seen}
    new_seen = {}
    feedshape = {}
    # ---- Leg 1: Sourcify feed ----
    rc, out, err = curl("https://sourcify.dev/server/v2/contracts/56?limit=20&sort=desc", timeout=25)
    feed_addrs, feed_new = [], []
    if rc == 0 and out:
        with open(os.path.join(BASE, f"hot-leg-{STAMP}-sourcify.json"), "w") as f:
            f.write(out)
        try:
            d = json.loads(out)
            items = d.get("results") or d.get("contracts") or []
            for it in items:
                a = it.get("address") or it.get("contractAddress")
                if a:
                    feed_addrs.append(a)
        except Exception as e:
            log.append(f"Leg1 feed JSON parse failed: {e}")
    else:
        log.append(f"Leg1 Sourcify feed fetch FAILED rc={rc} err={err[:120]}")
    for a in feed_addrs:
        if a.lower() not in seen_lower and a.lower() not in {k.lower() for k in new_seen}:
            feed_new.append(a)
    log.append(f"Leg1 feed: {len(feed_addrs)} contracts, {len(feed_new)} new vs seen")
    for a in feed_new:
        if a.lower() in ("0x827e83e49bd7e15b67efa0e90fc25f17b8d96124",
                         "0x8b47354e7b76b1970a0d06365c8244a810d37493"):
            new_seen[a] = {"first_seen_wib": "2026-11-16T22:59:00+07:00",
                           "note": "excluded example rediscovered", "source": "sourcify-feed",
                           "status": "excluded"}
            log.append(f"Leg1 EXCLUDED rediscovery: {a}")
            continue
        try:
            sc = shape_check(a)
        except Exception as e:
            sc = {"shape": "shape-check-failed", "error": str(e)[:120]}
        feedshape[a] = sc
        new_seen[a] = {"first_seen_wib": "2026-11-16T22:59:00+07:00",
                       "note": json.dumps(sc)[:600], "source": "sourcify-feed",
                       "status": sc["shape"]}
        log.append(f"Leg1 new {a}: {sc}")

    # ---- Leg 2: Boltbook EN + ZH ----
    bolt_new = []
    for lang, suffix in (("en", ""), ("zh", "?lang=zh")):
        url = f"https://boltbook.fun/{suffix}"
        rc, out, err = curl(url, timeout=25)
        tag = f"boltbook-{lang}"
        if rc != 0 or not out:
            log.append(f"Leg2 {tag} fetch FAILED rc={rc} err={err[:120]} — leg skipped")
            continue
        with open(os.path.join(BASE, f"hot-leg-{STAMP}-{tag}.html"), "w") as f:
            f.write(out)
        addrs = sorted(set(ADDR_RE.findall(out)), key=str.lower)
        log.append(f"Leg2 {tag}: {len(out)} bytes, {len(addrs)} addrs")
        for a in addrs:
            if a.lower() not in seen_lower and a.lower() not in {k.lower() for k in new_seen}:
                bolt_new.append((a, tag))
    for a, tag in bolt_new:
        code = get_code(a)
        if code in (None, "0x", "0x0", ""):
            note = "eth_getCode empty, not a contract"
            status = "checked-not-contract"
        else:
            try:
                sc = shape_check(a)
                note = json.dumps(sc)[:600]
                status = sc["shape"]
                feedshape[a] = sc
            except Exception as e:
                note = f"shape-check failed: {e}"
                status = "shape-check-failed"
        new_seen[a] = {"first_seen_wib": "2026-11-16T22:59:00+07:00",
                       "note": note, "source": tag, "status": status}
        log.append(f"Leg2 new {a} ({tag}): {status} — {note[:200]}")
    with open(os.path.join(BASE, f"hot-leg-{STAMP}-feedshape.json"), "w") as f:
        json.dump(feedshape, f, indent=1)

    # ---- Bridge (read-only) ----
    try:
        bridge = load_json(os.path.join(BASE, "scan-bridge.json"))
        snap = load_json(os.path.join(BASE, "onchain-snapshot.json"))
        snap_addrs = set()
        for sec in ("contracts", "track_c", "pending_claims"):
            v = snap.get(sec)
            if isinstance(v, dict):
                for k, it in v.items():
                    if isinstance(k, str) and k.startswith("0x"):
                        snap_addrs.add(k.lower())
                    if isinstance(it, dict):
                        for kk in ("address", "sale", "contract", "token", "sale_contract"):
                            if it.get(kk):
                                snap_addrs.add(str(it[kk]).lower())
            elif isinstance(v, list):
                for it in v:
                    if isinstance(it, dict):
                        for k in ("address", "sale", "contract"):
                            if it.get(k):
                                snap_addrs.add(str(it[k]).lower())
        bridge_contracts = bridge.get("contracts", {}) if isinstance(bridge, dict) else {}
        bridge_addrs = {k.lower() for k in bridge_contracts}
        outside = sorted(bridge_addrs - snap_addrs)
        same_owner = [k for k, v in bridge_contracts.items()
                      if isinstance(v, dict) and v.get("same_owner_discarded")]
        mtime = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(os.path.getmtime(os.path.join(BASE, "scan-bridge.json"))))
        log.append(f"Bridge: mtime {mtime}, {len(bridge_addrs)} contracts, {len(outside)} outside snapshot (first 10): {outside[:10]}; same_owner_discarded: {len(same_owner)}")
    except Exception as e:
        log.append(f"Bridge read FAILED (skip, not fatal): {e}")

    # ---- Leg 4: reread snapshot items (22:39 plan + 22:24 extras) ----
    PLAN = [
        ("AGCLUB", "0x67270bb351515abf3089ca5420456897363f5e75", [
            ("totalMinted", sel("totalMinted()")), ("freeMinted", sel("freeMinted()")),
            ("FREE_CAP", sel("FREE_CAP()")), ("mintOpen", sel("mintOpen()")),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("RaceAgents", "0x4BB9Cf796048b3dC5Ea9A32434982b9d52Efa63f", [
            ("totalSupply", sel("totalSupply()")), ("freeMinted", sel("freeMinted()")),
            ("FREE_MAX", sel("FREE_MAX()")), ("mintOpen", sel("mintOpen()"))]),
        ("Matrix Agents", "0x1F669b714337F3C2585072c53fdDD89581F928fF", [
            ("totalSupply", sel("totalSupply()")), ("freeMinted", sel("freeMinted()")),
            ("freeRemaining", sel("freeRemaining()")), ("mintOpen", sel("mintOpen()")),
            ("FREE_MAX", sel("FREE_MAX()"))]),
        ("Ledgera", "0x8d292d7d423bc48b5f1954f2c0440cfbe9dabd7d", [
            ("totalSupply", sel("totalSupply()")), ("freeClaimed", sel("freeClaimed()")),
            ("FREE_SUPPLY", sel("FREE_SUPPLY()")), ("mintOpen", sel("mintOpen()")),
            ("mintedBy_user", sel("mintedBy(address)") + USER_PAD),
            ("freeUsed_user", sel("freeUsed(address)") + USER_PAD),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("WANGCAI", "0x61A2ff9Be3db25e23886bC59D92d44fAa05959Cd", [
            ("totalSupply", sel("totalSupply()")), ("freeClaimed", sel("freeClaimed()")),
            ("FREE_SUPPLY", sel("FREE_SUPPLY()")), ("mintOpen", sel("mintOpen()")),
            ("mintedBy_user", sel("mintedBy(address)") + USER_PAD),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("YUANBAO", "0xE8cF9969f8E8601a5Fed1DD39dE0E6c7959E7f9E", [
            ("totalSupply", sel("totalSupply()")), ("freeClaimed", sel("freeClaimed()")),
            ("FREE_SUPPLY", sel("FREE_SUPPLY()")), ("mintOpen", sel("mintOpen()")),
            ("mintedBy_user", sel("mintedBy(address)") + USER_PAD),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("Bold Leonidas", "0x84bcb8c16566e81ce902530c9da1e3de291f9941", [
            ("totalSupply", sel("totalSupply()")), ("totalMinted", sel("totalMinted()")),
            ("mintOpen", sel("mintOpen()")),
            ("mintPriceFor_user_1", sel("mintPriceFor(address,uint256)") + USER_PAD + format(1, "064x")),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("Punch Card", "0x1d4ef0587dd3ff3875a141d4711c60bca40587c4", [
            ("totalSupply", sel("totalSupply()")), ("totalMinted", sel("totalMinted()")),
            ("freeMinted", sel("freeMinted()")), ("mintOpen", sel("mintOpen()")),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("PXIO", "0x58e8f1b34B60687B36BCdc78e02a2fd443De71Ab", [
            ("totalSupply", sel("totalSupply()")), ("mintOpen", sel("mintOpen()")),
            ("mintedBy_user", sel("mintedBy(address)") + USER_PAD),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("ALIEN", "0xf5767ac3beb8bbfaf4596dfc1925fc5aca779dcb", [
            ("totalSupply", sel("totalSupply()")), ("mintOpen", sel("mintOpen()")),
            ("isFreePhase", sel("isFreePhase()")),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("BinanceAI-mint", "0x46cb1D3efd4307506Cda7EbBa5a51be64746739E", [
            ("launched", sel("launched()")), ("failed", sel("failed()")),
            ("isRefundPhase", sel("isRefundPhase()")), ("totalShares", sel("totalShares()")),
            ("tokenClaimed_user", sel("tokenClaimed(address)") + USER_PAD)]),
        ("ORBIT", "0x7d5F7f323db3050AF92E9aa1584E883B3b24d680", [
            ("freeClaimed", sel("freeClaimed()")), ("FREE_MAX", sel("FREE_MAX()")),
            ("claimOpen", sel("claimOpen()")),
            ("hasFreeClaimed_user", sel("hasFreeClaimed(address)") + USER_PAD),
            ("totalSupply", sel("totalSupply()"))]),
        ("RigForge", "0xa1cc0d7c0534f824f2cf6eeb865a8fede96c8f7d", [
            ("freeSharesLeft", sel("freeSharesLeft()")), ("openedAt", sel("openedAt()")),
            ("freeClaimed", sel("freeClaimed()")),
            ("freeBooked_user", sel("freeBooked(address)") + USER_PAD)]),
        ("CosmicSentinel", "0x88731d1eb41c36f3d705fdb58b658244c06afc36", [
            ("totalSupply", sel("totalSupply()")), ("totalMinted", sel("totalMinted()")),
            ("freeMinted", sel("freeMinted()")), ("mintOpen", sel("mintOpen()")),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
        ("BUBB", "0x0d72970046c056db90888351b739246f468bff0b", [
            ("totalSupply", sel("totalSupply()")), ("freeMinted", sel("freeMinted()")),
            ("mintOpen", sel("mintOpen()")),
            ("balanceOf_user", sel("balanceOf(address)") + USER_PAD)]),
    ]
    reads = {}
    for name, addr, views in PLAN:
        calls = [(addr, data) for _, data in views]
        got, err = None, None
        for ep in ENDPOINTS:
            try:
                got = rpc_batch(calls, ep)
                break
            except Exception as e:
                err = f"{ep}: {type(e).__name__}: {str(e)[:100]}"
        if got is None:
            reads[name] = {"address": addr, "error": err,
                           "views": {v: "ERROR" for v, _ in views}}
            log.append(f"Leg4 {name} FAILED: {err}")
            continue
        vals = {v: decode(r) for (v, _), r in zip(views, got)}
        reads[name] = {"address": addr, "views": vals}
        log.append(f"Leg4 {name}: {vals}")
    block = None
    for ep in ENDPOINTS:
        try:
            block = int(rpc_single("eth_blockNumber", ep), 16)
            break
        except Exception:
            continue
    log.append(f"Leg4 block: {block}")
    try:
        prev = load_json(os.path.join(BASE, "hot-leg-2026-11-16-2254-reread.json"))
        prev_reads = prev.get("reads", {})
        for name in reads:
            pv = prev_reads.get(name, {}).get("views", {})
            cv = reads[name].get("views", {})
            diffs = {k: (pv.get(k), cv.get(k)) for k in cv if pv.get(k) != cv.get(k)}
            if diffs:
                log.append(f"Leg4 CHANGE {name}: {diffs}")
            else:
                log.append(f"Leg4 {name}: no change vs 22:54")
    except Exception as e:
        log.append(f"Leg4 diff vs 22:54 unavailable: {e}")
    out = {"mode": "curl-per-contract-batch", "block": block,
           "elapsed_s": round(time.time() - t0, 1), "reads": reads}
    with open(os.path.join(BASE, f"hot-leg-{STAMP}-reread.json"), "w") as f:
        json.dump(out, f, indent=1)

    # ---- Poffzi fcfs loop liveness (info only, no re-read) ----
    try:
        p = subprocess.run(["pgrep", "-af", "fcfs_fast"], capture_output=True, text=True, timeout=10)
        log.append(f"Poffzi fcfs_fast: {p.stdout.strip()[:300] or 'NO PROCESS FOUND'}")
    except Exception as e:
        log.append(f"Poffzi fcfs_fast check failed: {e}")

    # ---- update hot-leg-seen.json (only state file this job writes) ----
    if new_seen:
        seen.update(new_seen)
        with open(os.path.join(BASE, "hot-leg-seen.json"), "w") as f:
            json.dump(seen, f, indent=1, sort_keys=True)
        log.append(f"hot-leg-seen.json updated: +{len(new_seen)} entries (was {len(seen)-len(new_seen)})")
    else:
        log.append("hot-leg-seen.json unchanged (0 new)")
    log.append(f"TOTAL elapsed {round(time.time()-t0,1)}s")
    with open(os.path.join(BASE, f"hot-leg-{STAMP}-runlog.md"), "w") as f:
        f.write(f"# Hot-leg run 2026-11-16 22:59 WIB\n\n" + "\n".join(f"- {l}" for l in log) + "\n")
    print("\n".join(log))

if __name__ == "__main__":
    main()
