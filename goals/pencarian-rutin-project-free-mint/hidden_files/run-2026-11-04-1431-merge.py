#!/usr/bin/env python3
"""Merge run 1431 reread into snapshot (nulls retained, never overwrite with null).
Run AFTER scan triage; scan first-seen additions are applied separately by hand
following the 1401 pattern (watchlist-only unless agent-shaped+first-mint)."""
import json
snap = json.load(open('onchain-snapshot.json'))
rr = json.load(open('run-2026-11-04-1431-reread.json'))['reread']
# name -> snapshot key mapping for reread items (keys in reread file match snapshot keys
# for most items; Jolly/PixelTrump/WDNFT/LunaBirds keys are the snapshot keys too)
for name, vals in rr.items():
    if name in ('block', 'TrackB_MINT', 'DROID', 'OSK', 'IMARS', 'NIULAI', 'KillZero', 'FABE', 'E6BA', 'E246'):
        continue
    ent = snap['contracts'].get(name)
    if ent is None:
        continue
    ts = vals.get('totalSupply()')
    fc = vals.get('freeClaimed()')
    if ts is not None:
        ent['previousTotalSupply'] = ent.get('totalSupply')
        ent['totalSupply'] = ts
    if fc is not None:
        ent['freeClaimed'] = fc
    # user slot: only record a loss if a read positively shows used; all reads here are 0/None
    ent['lastReadWib'] = '2026-11-04T14:31:00+07:00'
    if vals.get('totalSupply()') is not None or vals.get('freeClaimed()') is not None:
        ent['run1431Note'] = f"Run 1431 re-read: totalSupply {vals.get('totalSupply()')}, freeClaimed {vals.get('freeClaimed()')}, FREE_SUPPLY {vals.get('FREE_SUPPLY()')}, freeMinted {vals.get('freeMinted()')}, slot user mintedBy {vals.get('mintedBy(address)')}/freeUsed {vals.get('freeUsed(address)')}/balance {vals.get('balanceOf(address)')}; null = gagal baca sesaat, nilai lama dipertahankan."
# E6BA / E246 follow-up notes (already-flagged items, not new reports)
for key, note in [
    ('Unnamed-E6BA-1401', 'Run 1431 follow-up: totalSupply 1 (1401) -> 24 (reread 1431) -> 26 (konfirmasi ulang), freeClaimed(user)=0 (slot gratis user masih terbuka); 26/5000 = 0,52%, jauh di bawah 25% strong lead; website tetap UNVERIFIED (gate run 1401); tetap EARLY, TIDAK di-preview/di-mint, TIDAK dilaporkan ulang sebagai baru.'),
    ('Unnamed-miner-E246-1401', 'Run 1431 follow-up: nextId 7 (1401) -> 45 (konfirmasi ulang 1431), klaim berjalan cepat; freeMinedCount/totalSupply null (gagal baca/nama view); tier tetap TIDAK ditetapkan, TIDAK di-preview/di-klaim, TIDAK dilaporkan ulang sebagai baru.'),
]:
    if key in snap['contracts']:
        snap['contracts'][key]['run1431Note'] = note
json.dump(snap, open('onchain-snapshot.json', 'w'), indent=1)
print('merged reread; contracts:', len(snap['contracts']))
