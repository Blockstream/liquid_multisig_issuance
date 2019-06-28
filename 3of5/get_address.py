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

res['address'] = host_9.call('getnewaddress', label)

print(json.dumps(res, indent=4, sort_keys=True))
