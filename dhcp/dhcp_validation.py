import re
import ipaddress
from modules.dhcp.util import reservation_util

# individual

def isValidMAC(value):
    #Check if the value is a valid MAC address

    value = value.replace(":", "-").upper()
    return bool(re.search(r"^([a-zA-Z0-9]{2}-){5}[a-zA-Z0-9]{2}$", value))

def isValidIP(value):
    #Check if the value is a valid IP address.

    try:
        ipaddress.IPv4Address(value)
        return True
    except Exception:
        return False

def isValidDescription(value):
    #Check if the value is not too long

    return bool(len(value) <= 255)

def isValidName(value):
    # Check if the value is alphanumeric, hyphens, and underscores only.

    return bool(re.match(r"^[a-zA-Z0-9_.\s-]+$", value)) and len(value) <= 255

def isValidDelete(value):
    #Check if the value is either 'yes' or blank
    
    return bool(value == '' or value.lower() == 'yes' or value.lower() == 'no')

# bulk

def validate_bulk_data(reservations, user_groups):
    _validate_columns(reservations)
    _validate_formats(reservations)
    _validate_row_count(reservations)
    _validate_permissions(reservations, user_groups)
    
def _validate_columns(reservations):
    REQUIRED = {"ip", "mac", "description", "name", "delete"}
    for r in reservations:
        if set(r.keys()) != REQUIRED:
            raise Exception("Incorrect or missing columns. Required: IPAddress, MACAddress, Description, Name, Delete")

def _validate_formats(reservations):
    for r in reservations:
        if not isValidIP(r["ip"]):
            raise Exception("Invalid IPAddress in row: " + r["ip"])
        if not isValidMAC(r["mac"]):
            raise Exception("Invalid MACAddress in row: " + r["ip"])
        if not isValidDescription(r["description"]):
            raise Exception("Invalid Description in row: " + r["ip"])
        if not isValidName(r["name"]):
            raise Exception("Invalid Name in row: " + r["ip"])
        if not isValidDelete(r["delete"]):
            raise Exception("Invalid Delete flag in row: " + r["ip"])
    
def _validate_row_count(reservations):
    if len(reservations) >= 1000:
        raise Exception("Too many items (<1000 required)")
    
def _validate_permissions(reservations, user_groups):
    for r in reservations:
        reservation_util.confirm_ip_permission(r["ip"], user_groups)