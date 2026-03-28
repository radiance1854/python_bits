from modules.dhcp.util import scope_util
adminGroupId = 'XXXXXXXXXX'
limitedscopeGroupId = 'XXXXXXXXXX'

#dhcp reservation util

def cleanReservationDict(data):
    #Clean data from DHCP info.
    if isinstance(data, dict):
        return [processReservation(data)]
    else:
        return [processReservation(reservation) for reservation in data]

def processReservation(reservation):
    #Process individual JSON reservation.

    reservation["IP"] = reservation["IPAddress"]["IPAddressToString"]
    del reservation["IPAddress"]
    reservation["Scope"] = reservation["ScopeId"]["IPAddressToString"]
    del reservation["ScopeId"]
    reservation["Hostname"] = reservation["Name"]
    del reservation["Name"]
    return reservation

def confirm_ip_permission(ip, user_groups):
    isAdmin = adminGroupId in user_groups
    isLimited = limitedscopeGroupId in user_groups
    if not ((scope_util.is_ip_in_scopes(ip) and isLimited) or isAdmin):
        raise Exception(f"Permission denied to Scope")
