#dhcp lease util

def cleanLeaseDict(data):
    #Clean data from DHCP info.
    if isinstance(data, dict):
        return [processLease(data)]
    else:
        return [processLease(lease) for lease in data]

def processLease(lease):
    #Process individual JSON lease.
    lease["IP"] = lease["IPAddress"]["IPAddressToString"]
    del lease["IPAddress"]
    lease["LeaseExpiryTime"] = extractTime(lease["LeaseExpiryTime"])
    return lease

def extractTime(rawTime):
    #Extract and format time from raw string.
    if rawTime:
        start = rawTime.find('/Date(') + 6
        end = rawTime.find(')/', start)
        return rawTime[start:end]
    return ""