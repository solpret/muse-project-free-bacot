#!/usr/bin/env python3
"""Run 1401 stage-2 bookkeeping: add 7 confirmed EARLY leads to the snapshot.
Neurolucha is NOT added here - it awaits the (L) BscScan browser result.
Sources: run-2026-11-05-1401-verify-new.json (on-chain verification),
onchain-scan-2026-11-05-1401.json (window counts), Goats/Owls freeClaimed()
no-arg probe (proc_89ab934005f3)."""
import json, shutil, urllib.request

D = '/home/hatch/workspace/goals/pencarian-rutin-project-free-mint/hidden_files/'
RPCS = ['https://bsc-dataseed1.bnbchain.org', 'https://bsc-dataseed2.bnbchain.org', 'https://bsc.publicnode.com']

def head_block():
    for rpc in RPCS:
        try:
            body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_blockNumber', 'params': []}).encode()
            req = urllib.request.Request(rpc, data=body, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=15) as r:
                return int(json.load(r)['result'], 16)
        except Exception:
            continue
    return None

def hexaddr(n):
    return '0x' + format(n, '040x') if isinstance(n, int) else n

shutil.copy(D + 'onchain-snapshot.json', D + 'onchain-snapshot-1401-stage2.bak.json')
snap = json.load(open(D + 'onchain-snapshot.json'))
verify = json.load(open(D + 'run-2026-11-05-1401-verify-new.json'))
scan = json.load(open(D + 'onchain-scan-2026-11-05-1401.json'))
scan_by_addr = {e['address'].lower(): e for e in scan['contracts']}
head = head_block()

# (key in snapshot, verify key, address, free counter kind, free value, cap field, cap value)
SPECS = [
    ('Roguefall', 'Roguefall', '0x5fe03829a2f94a8bA3906459258b1305F0e68934', 'freeMinted', None, 'FREE_CAP', 2000),
    ('Agent Goats', 'Agent Goats', '0x0E9E0a3B46dC0d36A1Ab64f553Dd8A0693E6aAa6', 'freeClaimed', 108, 'FREE_SUPPLY', 1111),
    ('Agent Owls', 'Agent Owls', '0x50B4bD215c409C975c940d5CF23B56D8F3ecfd3b', 'freeClaimed', 104, 'FREE_SUPPLY', 1111),
    ('Hirelings-A', 'Hirelings-A', '0xff61A6e13776B0823E18d960b3f9ee2C78685601', 'freeMinted', None, 'FREE_CAP', 2000),
    ('Hirelings-B', 'Hirelings-B', '0xcbE18caA6d2A8BEaC563972d7457E8Afbb0E7C4a', 'freeMinted', None, 'FREE_CAP', 2000),
    ('Forklings', 'Forklings', '0xD7B3FD33e0b465B0e374906F60567D317b758FD8', 'freeMinted', None, 'FREE_CAP', 2000),
    ('Auspibots', 'Auspibots', '0x3E56Ace6760ba03F3Ff669C51bcCa662bB96f955', 'freeMinted', None, 'FREE_CAP', 2000),
]

for name, vkey, addr, free_kind, free_override, cap_field, cap_val in SPECS:
    v = verify[vkey]
    sc = scan_by_addr.get(addr.lower(), {})
    free_val = free_override if free_override is not None else v.get('freeMinted()')
    ts = v.get('totalSupply()')
    pct = round(100.0 * free_val / cap_val, 2)
    owner = v.get('owner()')
    owner_hex = hexaddr(owner) if isinstance(owner, int) else ('revert-on-read' if isinstance(owner, dict) else owner)
    can_free = v.get('canFreeMint(address)')
    claimed = v.get('claimedFree(address)')
    entry = {
        'address': addr,
        'name': v.get('name()'),
        'symbol': v.get('symbol()'),
        'kind': 'ERC721',
        'totalSupply': ts,
        'freeMinted': v.get('freeMinted()') if not isinstance(v.get('freeMinted()'), dict) else 'revert-on-read',
        'freeClaimed': free_val if free_kind == 'freeClaimed' else (claimed if not isinstance(claimed, dict) else 'revert-on-read'),
        cap_field: cap_val,
        'MAX_SUPPLY': v.get('MAX_SUPPLY()'),
        'freePctVerified': pct,
        'balanceOf(user)': v.get('balanceOf(address)'),
        'claimedFree(user)': claimed if not isinstance(claimed, dict) else 'revert-on-read',
        'canFreeMint(user)': can_free if not isinstance(can_free, dict) else 'revert-on-read',
        'mintedBy(user)': 0,
        'mintOpen': v.get('mintOpen()') if not isinstance(v.get('mintOpen()'), dict) else 'revert-on-read',
        'paidMinted': v.get('paidMinted()') if not isinstance(v.get('paidMinted()'), dict) else 'revert-on-read',
        'firstMintBlock': v.get('first_mint_block'),
        'firstMintTx': v.get('first_mint_tx'),
        'firstMintWib': v.get('first_mint_wib'),
        'firstSeenBlock': 131771337,
        'scanMints': sc.get('mint_count'),
        'scanMinters': sc.get('distinct_minters'),
        'scanWindow': '131771337-131773336',
        'status': 'early-lead-reported-2026-11-05',
        'launchNote': 'First mint terverifikasi on-chain via Ankr getLogs (Transfer-from-zero): blok %s = %s WIB; umur TERVERIFIKASI <=48 jam.' % (v.get('first_mint_block'), v.get('first_mint_wib')),
        'baselineNote': ('EARLY lead dilaporkan run 1401. Agent-shaped: Sourcify verified, registry_bytes_hit + free views (%s). '
                         'BUKAN strong lead (%.2f%% <25%%), BUKAN kandidat, TIDAK di-preview/di-mint (website/X unverified).' % (', '.join(sc.get('free_shaped', [])), pct)),
        'gateNote': ('Website UNVERIFIED run 1401: (H) contractURI %s; (I) tokenURI(1) base64 JSON tanpa external_url/http; '
                     '(G) pencarian nama proyek nihil. X UNVERIFIED. Gate penuh (A)-(N) belum didalami (hanya untuk strong lead/kandidat).'
                     % ('revert' if isinstance(v.get('contractURI()'), dict) else 'base64 tanpa external_link')),
        'lastReadBlock': head,
        'lastReadWib': '2026-11-05 run 1401',
        'velocityVerified': False,
        'xVerified': False,
    }
    if name == 'Agent Goats':
        entry['owner'] = owner_hex
        entry['AGENT_ID()'] = hexaddr(v.get('AGENT_ID()'))
        entry['note'] = 'freeClaimed() no-arg = 108 (probe pasca-verify); freeClaimed(user)/quote(user,1) revert (bukan overload template ini); slot user terbuka via mintedBy(user)=0.'
    if name == 'Agent Owls':
        entry['owner'] = owner_hex
        entry['AGENT_ID()'] = hexaddr(v.get('AGENT_ID()'))
        entry['note'] = 'freeClaimed() no-arg = 104 (probe pasca-verify, supply bergerak 100->104 antara verify dan probe); freeClaimed(user)/quote(user,1) revert; slot user terbuka via mintedBy(user)=0.'
    if name == 'Roguefall':
        entry['owner'] = owner_hex
    if name in ('Hirelings-A', 'Hirelings-B'):
        entry['note'] = 'Dua kontrak Hirelings (HIRE) berbagi nama/simbol/template; owner() revert pada keduanya.'
    snap['contracts'][name] = entry
    print('ADDED', name, '| free', free_val, '/', cap_val, '=', pct, '% | owner', owner_hex, '| scanMints', sc.get('mint_count'), '| scanMinters', sc.get('distinct_minters'))

snap['runNote1401_stage2'] = ('Stage-2 run 1401: 7 EARLY lead ditambahkan (Roguefall, Agent Goats, Agent Owls, Hirelings-A, Hirelings-B, Forklings, Auspibots). '
    'Neurolucha BELUM ditambahkan - menunggu hasil metode (L) BscScan via browser.')
snap['last_run'] = '2026-11-05 run 1401'
json.dump(snap, open(D + 'onchain-snapshot.json', 'w'), indent=1)
print('contracts now:', len(snap['contracts']), '| head block:', head)
print('OK stage-2 done')
