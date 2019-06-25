#!/usr/bin/env python3
from liquid_rpc_class import RPCHost
import json
import sys
from liquid_utils import connect

if len (sys.argv) != 2 :
    print('Usage: python '+sys.argv[0]+' LABEL' )
    sys.exit (1)

label = sys.argv[1]
res = {}
host_1, host_2, host_3 = connect()

res['participants'] = []

# Get unblinded addresses, private and public from each participant, in M>2 add lines from other wallets
address_1 = host_1.call('getnewaddress', label)
address_1_info = host_1.call('getaddressinfo', address_1)
res['participants'].append({'name':'first', 'address':address_1, 'pubkey':address_1_info['pubkey']})

address_2 = host_2.call('getnewaddress', label)
address_2_info= host_2.call('getaddressinfo', address_2)
res['participants'].append({'name':'second', 'address':address_2, 'pubkey':address_2_info['pubkey']})

# Get blinding key from 1st address (this is an arbitrary choice)
blindingkey = host_1.call('dumpblindingkey', address_1)
res['blindingkey'] = blindingkey

# Make multisig 2of2 address like usual
N = 2
M = len(res['participants'])
multisig = host_1.call('createmultisig', N, [address_1_info['pubkey'], address_2_info['pubkey']])
# if  M>2 add other pubkeys
res['kind'] = 'multisig {} of {}'.format(N, M)

# Blind the address using the blinding pubkey from address 1
blinded_addr = host_1.call('createblindedaddress', multisig["address"], address_1_info["confidential_key"])
res['multisig'] = blinded_addr
host_1.call('importaddress', multisig['redeemScript'], '', False, True)
host_1.call('importaddress', blinded_addr, label+' multisig', False)
host_1.call('importblindingkey', blinded_addr, blindingkey)

host_2.call('importaddress', multisig['redeemScript'], '', False, True)
host_2.call('importaddress', blinded_addr, label+' multisig', False)
host_2.call('importblindingkey', blinded_addr, blindingkey)

# if M>2 add other lines in order to import addresses and blinding key in the other wallets

print(json.dumps(res, indent=4, sort_keys=True))
