from liquid_rpc_class import RPCHost
import time

network = 'regtest'

def connect():
    if network == 'regtest':
        serverURL_1 = 'http://username:password@127.0.0.1:18888/wallet/wallet_1.dat'
        serverURL_2 = 'http://username:password@127.0.0.1:18888/wallet/wallet_2.dat'
        serverURL_3 = 'http://username:password@127.0.0.1:18888/wallet/wallet_3.dat'
        serverURL_4 = 'http://username:password@127.0.0.1:18888/wallet/wallet_4.dat'
        serverURL_5 = 'http://username:password@127.0.0.1:18888/wallet/wallet_5.dat'
        serverURL_6 = 'http://username:password@127.0.0.1:18888/wallet/wallet_6.dat'
        serverURL_7 = 'http://username:password@127.0.0.1:18888/wallet/wallet_7.dat'
        serverURL_8 = 'http://username:password@127.0.0.1:18888/wallet/wallet_8.dat'
        serverURL_9 = 'http://username:password@127.0.0.1:18888/wallet/wallet_9.dat'
    else:
        serverURL_1 = 'http://username:password@127.0.0.1:7041/wallet/wallet_1.dat'
        serverURL_2 = 'http://username:password@127.0.0.1:7041/wallet/wallet_2.dat'
        serverURL_3 = 'http://username:password@127.0.0.1:7041/wallet/wallet_3.dat'
        serverURL_4 = 'http://username:password@127.0.0.1:7041/wallet/wallet_4.dat'
        serverURL_5 = 'http://username:password@127.0.0.1:7041/wallet/wallet_5.dat'
        serverURL_6 = 'http://username:password@127.0.0.1:7041/wallet/wallet_6.dat'
        serverURL_7 = 'http://username:password@127.0.0.1:7041/wallet/wallet_7.dat'
        serverURL_8 = 'http://username:password@127.0.0.1:7041/wallet/wallet_8.dat'
        serverURL_9 = 'http://username:password@127.0.0.1:7041/wallet/wallet_9.dat'

    host_1 = RPCHost(serverURL_1)
    host_2 = RPCHost(serverURL_2)
    host_3 = RPCHost(serverURL_3)
    host_4 = RPCHost(serverURL_4)
    host_5 = RPCHost(serverURL_5)
    host_6 = RPCHost(serverURL_6)
    host_7 = RPCHost(serverURL_7)
    host_8 = RPCHost(serverURL_8)
    host_9 = RPCHost(serverURL_9)


    return(host_1, host_2, host_3, host_4, host_5, host_6, host_7, host_8, host_9)

def generate():
    time.sleep(5)
    if network == 'regtest':
        serverURL = 'http://username:password@127.0.0.1:18888/wallet/wallet.dat'
        host = RPCHost(serverURL)
        address = host.call('getnewaddress')
        return(host.call('generatetoaddress', 1, address))
    else:
        return(0)
