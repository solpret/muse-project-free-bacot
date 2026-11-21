#!/usr/bin/env python3
"""Merge run free-mint-search 2026-11-20 09:31 WIB into onchain-snapshot.json.
Main re-read ~09:35 WIB (blok 134616099, 49 kontrak, 304 eth_call, 155 errors).
Aturan merge: nilai baru None / dict-error TIDAK menimpa nilai lama.
Plus: GETAGENT track_c watchlist-only (shape+age unverified); seen-file update.
Read-only kecuali snapshot + hot-leg-seen.json."""
import json, shutil
BASE = "/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/"
NOW_WIB = "2026-11-20 ~09:45 WIB"
BLOCK = 134616099
MINUTES = 30.0
shutil.copy(BASE + "onchain-snapshot.json", BASE + "onchain-snapshot.json.bak-0931")
snap = json.load(open(BASE + "onchain-snapshot.json"))
reread = json.load(open(BASE + "run-2026-11-20-0931-reread.json"))
interim = json.load(open(BASE + "run-2026-11-20-0931-interim.json"))
vel = interim["velocity"]
def num(d,k):
    x=d.get(k); return x if isinstance(x,int) else None
def is_err(v): return isinstance(v,dict)
by_addr={}
for k,v in snap.get("contracts",{}).items():
    if isinstance(v,dict) and isinstance(v.get("address"),str): by_addr[v["address"].lower()]=(k,v)
n_upd=0
for name,v in vel.items():
    addr=v["address"].lower()
    if addr not in by_addr: continue
    sk,sv=by_addr[addr]
    old_sup=v["old_supply"]; new_sup=v["new_supply"]
    if new_sup is not None:
        sv["previousTotalSupply"]=old_sup; sv["totalSupply"]=new_sup
    if v["delta"] is not None:
        sv["mintedInInterval"]=v["delta"]; sv["intervalMinutes"]=v["minutes"]
        sv["currentRatePerMin"]=v["rate_per_min"]
    sv["velocityLegPasses"]=bool(v["velocity_pass"])
    if v["free_pct"] is not None: sv["freePctInference"]=v["free_pct"]
    sv["lastReadBlock"]=BLOCK; sv["lastReadWib"]=NOW_WIB
    sv["runNote0931_1120"]=(f"Run 0931 (blok {BLOCK}, interval ~{v['minutes']} mnt): "
        f"totalSupply {old_sup}->{new_sup} (+{v['delta']}, {v['rate_per_min']}/mnt vs prev {v['prev_rate_per_min']} = {v['ratio']}x) -> velocity "
        f"{'LOLOS' if v['velocity_pass'] else 'GAGAL'}; free% {v['free_pct']}; bal_user {v['balanceOf_user']}; "
        f"status {sv.get('status')}. DIAM.")
    n_upd+=1
# binanceai pending claim
pc=snap.get("pending_claims",{}).get("binanceai.fun",{})
bv=reread["reads"]["binanceai-mint"]["views"]
pc["launched"]=bv.get("launched"); pc["failed"]=bv.get("failed")
pc["isRefundPhase"]=bv.get("isRefundPhase"); pc["totalShares"]=bv.get("totalShares")
pc["tokenClaimed_user"]=bv.get("tokenClaimed_user"); pc["lastReadWib"]=NOW_WIB
pc["runNote0931"]=(f"Run 0931 (blok {BLOCK}): launched={bv.get('launched')}, failed={bv.get('failed')}, "
    f"isRefundPhase={bv.get('isRefundPhase')}, totalShares {bv.get('totalShares')}, tokenClaimed(user)={bv.get('tokenClaimed_user')}, "
    f"refundClaimed(user)={bv.get('refundClaimed_user')} - tetap pending/refund, sudah dilaporkan sekali (2026-11-02). DIAM.")
# track_c sales re-reads
tc=snap.get("track_c",{})
for key,rkey in (("bsccat","bsccat-sale"),("AONE","AONE-sale")):
    if key in tc and rkey in reread["reads"]:
        fm=num(reread["reads"][rkey]["views"],"freeMinted")
        if fm is not None: tc[key]["freeMinted"]=fm
        tc[key]["runNote0931_1120"]=(f"Run 0931 (blok {BLOCK}): freeMinted {fm} (tidak berubah). DIAM.")
# GETAGENT watchlist-only (baru dari sapuan rute 3 run ini)
tc["GETAGENT"]={
 "sale":"0x233188403A5301220cc40f47446628d722e00F6c",
 "token":"0xc83B8b406F43BB89aDd0941bAA3Cba153B5221E1",
 "vault":"0x9CD646AB1d6a48c2dcf18f7FF53fFA74098Db6E2",
 "website":"https://getagent-bnb.web.app/",
 "status":"watchlist-only-age-unverified-shape-unverified-2026-11-20",
 "saleShape":"FAIL: Sourcify NOT verified (n_fns 0, match None); S1=False S2=False; selector tebakan (freeQuotaNow/totalMints/price/agentRegistry/dll) revert - tanpa bukti registry/AgentGate/free-mint konkret dari bytecode saja",
 "freePool":"UNVERIFIED: freeQuotaNow() mengembalikan data tak-terurai (selector mungkin berargumen/fallback); situs menampilkan kuota jendela 5/100 terpakai saat crawl 02:16 UTC + total mints 54/5555; token totalSupply 8.711.111 (baca 02:40 UTC) vs situs 5.511.111 (crawl 02:16 UTC)",
 "userSlot":"UNVERIFIED: questListed(user)=0; slot gratis belum terbukti terbuka",
 "ageNote":"UNVERIFIED: situs tidak menyatakan waktu launch; tidak ada timestamp pengumuman ditemukan (search 09:40 WIB); koroborasi first-mint terhalang (Ankr 401; BscScan V2 free tier tidak mencakup BSC chainid 56)",
 "xNote":"X @GetAgentBNB disebut di situs (follow + share caption syarat free mint) - handle belum diverifikasi independen",
 "websiteNote":"Situs getagent-bnb.web.app mencetak kontrak exact mint/token/vault (dibaca langsung 09:40 WIB) - bukti website ADA bila nanti lolos shape+umur; BUKAN lead hari ini",
 "boundary":"WATCHLIST-ONLY. BUKAN lead/kandidat: shape unverified + umur unverified. TIDAK PERNAH di-preview/di-mint. Dilaporkan HANYA bila re-read rutin menunjukkan promosi (shape lolos + umur terverifikasi <24 jam + slot terbuka).",
 "firstSeenWib":"2026-11-20 ~09:36 WIB","source":"route-3 web sweep (typefully search hit) run 0931",
 "lastReadBlock":134616211,"lastReadWib":NOW_WIB}
json.dump(snap, open(BASE+"onchain-snapshot.json","w"), indent=1)
# seen-file: Sourcify baru + GETAGENT mint agar hot-leg tidak lapor ulang
seen=json.load(open(BASE+"hot-leg-seen.json"))
for a,note in (("0x4E417894fF073881B8e18A39d1D5B190d61f0880","Sourcify feed baru run 0931: S1=False S2=False, n_fns 0 (unverified/no ABI) - checked-not-sale-shape"),
               ("0x233188403A5301220cc40f47446628d722e00F6c","GETAGENT mint, track_c watchlist-only run 0931 (shape+age unverified)")):
    if a not in seen:
        seen[a]={"first_seen_wib":"2026-11-20T09:40:00+07:00","note":note,"source":"free-mint-search-0931","status":"checked-not-sale-shape"}
json.dump(seen, open(BASE+"hot-leg-seen.json","w"), indent=1)
print("merged contracts:",n_upd,"| track_c GETAGENT added | seen n:",len(seen))
