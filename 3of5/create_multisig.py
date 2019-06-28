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
host_1, host_2, host_3, host_4, host_5, host_6, host_7, host_8, host_9 = connect()

res['participants'] = []

# Get unblinded addresses, private and public from each participant, in M>2 add lines from other wallets
address_1 = host_1.call('getnewaddress', label)
address_1_info = host_1.call('getaddressinfo', address_1)
res['participants'].append({'name':'first', 'address':address_1, 'pubkey':address_1_info['pubkey']})

address_2 = host_2.call('getnewaddress', label)
address_2_info= host_2.call('getaddressinfo', address_2)
res['participants'].append({'name':'second', 'address':address_2, 'pubkey':address_2_info['pubkey']})

address_3 = host_3.call('getnewaddress', label)
address_3_info= host_3.call('getaddressinfo', address_3)
res['participants'].append({'name':'third', 'address':address_3, 'pubkey':address_3_info['pubkey']})

address_4 = host_4.call('getnewaddress', label)
address_4_info= host_4.call('getaddressinfo', address_4)
res['participants'].append({'name':'fourth', 'address':address_4, 'pubkey':address_4_info['pubkey']})

address_5 = host_5.call('getnewaddress', label)
address_5_info= host_5.call('getaddressinfo', address_5)
res['participants'].append({'name':'fifth', 'address':address_5, 'pubkey':address_5_info['pubkey']})

# Get blinding key from 1st address (this is an arbitrary choice)
blindingkey = host_1.call('dumpblindingkey', address_1)
res['blindingkey'] = blindingkey

# Make multisig 3of5 address like usual
N = 3
M = len(res['participants'])
multisig = host_1.call('createmultisig', N, [address_1_info['pubkey'], address_2_info['pubkey'], address_3_info['pubkey'], address_4_info['pubkey'], address_5_info['pubkey']])
# if  M>5 add other pubkeys
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

host_3.call('importaddress', multisig['redeemScript'], '', False, True)
host_3.call('importaddress', blinded_addr, label+' multisig', False)
host_3.call('importblindingkey', blinded_addr, blindingkey)

host_4.call('importaddress', multisig['redeemScript'], '', False, True)
host_4.call('importaddress', blinded_addr, label+' multisig', False)
host_4.call('importblindingkey', blinded_addr, blindingkey)

host_5.call('importaddress', multisig['redeemScript'], '', False, True)
host_5.call('importaddress', blinded_addr, label+' multisig', False)
host_5.call('importblindingkey', blinded_addr, blindingkey)

# if M>5 add other lines in order to import addresses and blinding key in the other wallets

print(json.dumps(res, indent=4, sort_keys=True))
