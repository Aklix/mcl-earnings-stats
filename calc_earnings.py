import json

import mcl_conn

#  getaddresstxids  '{"addresses": ["address"], "start": number,  "end": number}' 1
#  gettxout "txid" 1
#  marmaraposstat beginheight endheight

BeginHeigth = int(input('Enter Begin Heigth as integer : '))
# BeginHeigth = 0
# EndHeigth = 0
EndHeigth = int(input('Enter End Heigth as integer : '))
#

address = mcl_conn.curl_response('listaddressgroupings', [])
print('Getting addresses')
getaddress = json.loads(str(address[0]))
# print(len(getaddress))
if len(getaddress) > 0:
    getaddress = getaddress[0]
else:
    getaddress = getaddress
normaladdresseslist = []
for item in getaddress:
    # print(item[0])
    normaladdresseslist.append(item[0])
if len(normaladdresseslist) == 0:
    for item in json.loads(mcl_conn.curl_response('getaddressesbyaccount', [""])[0]):
        normaladdresseslist.append(item)
activatedaddresses = mcl_conn.curl_response("marmaralistactivatedaddresses", [])[0]
activatedaddresslist = []

for item in json.loads(activatedaddresses).get("WalletActivatedAddresses"):
    activatedaddresslist.append(item)

print('normal addressses :' + str(normaladdresseslist))
print('activated addressses :' + str(activatedaddresslist))
normaladdresstxidslist = []
activatedaddresstxidslist = []
print('getting normal addresses txids between ' + str(BeginHeigth) + ' and ' + str(EndHeigth))
for naddress in normaladdresseslist:
    normaladdresstxids = mcl_conn.curl_response('getaddresstxids', [{'addresses': [naddress], 'start': BeginHeigth, 'end': EndHeigth}])[0]
    if normaladdresstxids:
        for txid in json.loads(normaladdresstxids):
            normaladdresstxidslist.append(txid)
print('Total normal addresses txids ' + str(len(normaladdresstxids)))
print('getting activated addresses txids between ' + str(BeginHeigth) + ' and ' + str(EndHeigth))
for activatedaddress in json.loads(activatedaddresses).get("WalletActivatedAddresses"):
    activatedaddresstxids = mcl_conn.curl_response('getaddresstxids', [{'addresses': [activatedaddress.get('activatedaddress')], 'start': BeginHeigth, 'end': EndHeigth}, 1])[0]
    if activatedaddresstxids:
        for txid in json.loads(activatedaddresstxids):
            activatedaddresstxidslist.append(txid)
print('Total activated addresses txids ' + str(len(activatedaddresstxidslist)))
na_earninglist = {'no': 0, 'amount': 0}
aa_earninglist = {'no': 0, 'amount': 0}

print('Calculating earnings within the txids')
if normaladdresstxidslist:
    for txid in normaladdresstxidslist:
        # print(txid)
        txout = mcl_conn.curl_response('gettxout', [txid, 0])[0]
        if txout:
            txout = json.loads(txout)
            if txout.get('coinbase') == True:
                # print(txout)
                na_earninglist.__setitem__('no', na_earninglist.get('no') + 1)
                na_earninglist.__setitem__('amount', na_earninglist.get('amount') + txout.get('value'))

if activatedaddresstxidslist:
    for txid in activatedaddresstxidslist:
        txout = mcl_conn.curl_response('gettxout', [txid, 0])[0]
        if txout:
            if json.loads(txout).get('coinbase') == True:
                aa_earninglist.__setitem__('no', aa_earninglist.get('no') + 1)
                aa_earninglist.__setitem__('amount', aa_earninglist.get('amount') + txout.get('value'))

print("earnings in normal " + str(na_earninglist))
print("earnings in activated " + str(aa_earninglist))

# posstat = mcl_conn.curl_response('marmaraposstat',[str(BeginHeigth), str(EndHeigth)])[0]
#
# # print(lcladdresslist)
# for item in json.loads(posstat).get('StakingStat'):
#     if item.get('CoinbaseAddress') == activatedaddress:
#         print(item)
