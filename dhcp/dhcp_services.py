from modules.dhcp import dhcp_pwsh
from modules.dhcp import dhcp_validation
from modules.dhcp.util import lease_util
from modules.dhcp.util import reservation_util
from modules.dhcp.util import scope_util
from modules.dhcp.util import bulk_util

# Bulk reservations

def bulkReservations(csv_data, user_groups=None, user_email=None):
    #Use csv to perform bulk dhcp reservation work

    # Converts csv string to dict list
    reservations = bulk_util.read_bulk_csv_data(csv_data)

    # Validation
    dhcp_validation.validate_bulk_data(reservations, user_groups)

    # Process Results
    results = bulk_util.bulk_reservation_update(reservations)

    # Convert to csv string and send email
    results_csv_string = bulk_util.results_to_csv(results)
    bulk_util.send_bulk_reservation_email(user_email, results_csv_string, csv_data)

    return results

# Single Reservations

def searchReservations(ip_or_mac):
    #Fetch DHCP Reservation information for a given IP or MAC address

    try:
        if not (dhcp_validation.isValidMAC(ip_or_mac) or dhcp_validation.isValidIP(ip_or_mac)):
            raise Exception(f"Not a valid IP or MAC: {ip_or_mac}")
        elif (dhcp_validation.isValidMAC(ip_or_mac)):
            deviceJSON = dhcp_pwsh.get_reservation_for_mac(ip_or_mac)
        else:
            scopeId = scope_util.find_scope_for_ip(ip_or_mac)
            deviceJSON = dhcp_pwsh.get_reservation_for_ip(scopeId, ip_or_mac)

        deviceJSONout = reservation_util.cleanReservationDict(deviceJSON)
        return deviceJSONout
    except Exception as e:
        returnJSON = [{
            "ClientId": "",
            "Hostname": "",
            "IP": "",
            "Scope": "",
            "Description": ""
        }]
        return returnJSON

def modifyReservation(IP, MAC, Description, dhcpName, user_groups=None):
    # Modify a DHCP Reservation

    try:
        if not (dhcp_validation.isValidIP(IP) and dhcp_validation.isValidDescription(Description) and dhcp_validation.isValidName(dhcpName) and dhcp_validation.isValidMAC(MAC)):
            raise Exception(f"Not a valid IP, MAC, Name, or Description")
        
        reservation_util.confirm_ip_permission(IP, user_groups)
        scopeId = scope_util.find_scope_for_ip(IP)
        dhcp_pwsh.modify_reservation_by_ip(IP, MAC, Description, dhcpName)
        dhcp_pwsh.update_replication_for_scope(scopeId)

        return [{"Results": "OK"}]
    except Exception as e:
        return [{"Results": "Error"}]

def deleteReservation(IP, user_groups=None):
    # Delete a DHCP Reservation

    try:
        if not (dhcp_validation.isValidIP(IP)):
            raise Exception(f"Not a valid IP")
        
        reservation_util.confirm_ip_permission(IP, user_groups)
        
        scopeId = scope_util.find_scope_for_ip(IP)
        dhcp_pwsh.delete_reservation_by_ip(IP)
        dhcp_pwsh.update_replication_for_scope(scopeId)

        return [{"Results": "OK"}]
    except:
        return [{"Results": "Error"}]

def addReservation(IP, MAC, Description, dhcpName, user_groups=None):
    # Add a DHCP Reservation

    try:
        if not (dhcp_validation.isValidMAC(MAC) and dhcp_validation.isValidIP(IP) and dhcp_validation.isValidName(dhcpName) and dhcp_validation.isValidDescription(Description)):
            raise Exception(f"Not a valid IP or MAC or Name or Description")
        
        reservation_util.confirm_ip_permission(IP, user_groups)
        
        scopeId = scope_util.find_scope_for_ip(IP)
        dhcp_pwsh.add_reservation_by_ip(scopeId, IP, MAC, Description, dhcpName)
        dhcp_pwsh.update_replication_for_scope(scopeId)

        return [{"Results": "OK"}]
    except:
        return [{"Results": "Error"}]


######

def searchLeases(ip_or_mac):
    # Fetch DHCP information for a given IP or MAC address

    #try:
    if not (dhcp_validation.isValidMAC(ip_or_mac) or dhcp_validation.isValidIP(ip_or_mac)):
        raise Exception(f"Not a valid IP or MAC: {ip_or_mac}")
    elif (dhcp_validation.isValidMAC(ip_or_mac)):
        deviceDict = dhcp_pwsh.get_lease_for_mac(ip_or_mac)
    else:
        deviceDict = dhcp_pwsh.get_lease_for_ip(ip_or_mac)
    
    deviceDictout = lease_util.cleanLeaseDict(deviceDict)
    return deviceDictout


##### SCOPES

def get_scopes_cidrs():
    scopes = scope_util.get_scopes()
    cidrs = [str(scope["network"]) for scope in scopes]
    return cidrs