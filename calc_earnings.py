import json
from datetime import datetime
from datetime import timedelta

import mcl_conn


BeginHeigth = int(input('Enter Begin Heigth as integer : '))
EndHeigth = int(input('Enter End Heigth as integer : '))
latestblock = mcl_conn.curl_response('getblockcount', [])[0]

if BeginHeigth < EndHeigth < int(latestblock):
    days = []
    begin_date = json.loads(mcl_conn.curl_response('getblock', [str(BeginHeigth)])[0]).get('time')
    end_date = json.loads(mcl_conn.curl_response('getblock', [str(EndHeigth)])[0]).get('time')
    # print(datetime.fromtimestamp(begin_date).date())
    # print(datetime.fromtimestamp(end_date).date())
    begin_day = datetime.fromtimestamp(begin_date).date()
    end_day = datetime.fromtimestamp(end_date).date()
    days.append(begin_day)
    # print(days)
    day_delta = (end_day - begin_day).days
    # print(day_delta)
    count = 0
    while day_delta != count:
        days.append(days[count] + timedelta(days=1))
        count = count + 1

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
    #
    for item in json.loads(activatedaddresses).get("WalletActivatedAddresses"):
        activatedaddresslist.append(item.get('activatedaddress'))
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
    print('Total normal addresses txids ' + str(len(normaladdresstxidslist)))
    print('getting activated addresses txids between ' + str(BeginHeigth) + ' and ' + str(EndHeigth))
    for activatedaddress in activatedaddresslist:
        activatedaddresstxids = mcl_conn.curl_response('getaddresstxids', [{'addresses': [activatedaddress], 'start': BeginHeigth, 'end': EndHeigth}, 0])[0]
        if activatedaddresstxids:
            for txid in json.loads(activatedaddresstxids):
                activatedaddresstxidslist.append(txid)
    print('Total activated addresses txids ' + str(len(activatedaddresstxidslist)))

    na_earninglist = {}
    aa_earninglist = {}
    for daytime in days:
        na_earninglist.__setitem__(daytime, 0)
        aa_earninglist.__setitem__(daytime, 0)

    print('Calculating earnings within the txids')

    if normaladdresstxidslist:
        for txid in normaladdresstxidslist:
            # print(txid)
            rawtx = mcl_conn.curl_response('getrawtransaction', [txid])[0]
            if rawtx:
                rawtx = json.loads(rawtx)
                txdetail = mcl_conn.curl_response('decoderawtransaction', [str(rawtx)])[0]
                txdetail = json.loads(txdetail)
                txvins = txdetail.get('vin')
                for vin in txvins:
                    if vin.get('coinbase'):
                        timestmp = datetime.fromtimestamp(txdetail.get('locktime')).date()
                        amount = txdetail.get('vout')[0].get('value')
                        prv_value = na_earninglist.__getitem__(timestmp)
                        na_earninglist.__setitem__(timestmp, (prv_value + amount))
    if activatedaddresstxidslist:
        for txid in activatedaddresstxidslist:
            rawtx = mcl_conn.curl_response('getrawtransaction', [txid])[0]
            if rawtx:
                rawtx = json.loads(rawtx)
                txdetail = mcl_conn.curl_response('decoderawtransaction', [str(rawtx)])[0]
                txdetail = json.loads(txdetail)
                txvins = txdetail.get('vin')
                for vin in txvins:
                    if vin.get('coinbase'):
                        timestmp = datetime.fromtimestamp(txdetail.get('locktime')).date()
                        amount = txdetail.get('vout')[0].get('value')
                        prv_value = aa_earninglist.__getitem__(timestmp)
                        aa_earninglist.__setitem__(timestmp, (prv_value + amount))

    # print(na_earninglist)
    # print(aa_earninglist)

    na_amount_sum = 0
    for item in na_earninglist:
        na_amount_sum = na_earninglist.get(item) + na_amount_sum
    print("earnings in normal " + str(na_amount_sum) + " between " + str(begin_day) + " and " + str(end_day))

    aa_amount_sum = 0
    for item in aa_earninglist:
        aa_amount_sum = aa_earninglist.get(item) + aa_amount_sum

    print("earnings in activated " + str(aa_amount_sum) + " between " + str(begin_day) + " and " + str(end_day))
    print("earnings total  " + str(aa_amount_sum + na_amount_sum) + " between " + str(begin_day) + " and " + str(end_day))

else:
    if EndHeigth > int(latestblock):
        print('EndHeigth cant be bigger than ' + str(latestblock))
    if BeginHeigth > EndHeigth:
        print("BeginHeigth must be smaller then EndHeigth")
