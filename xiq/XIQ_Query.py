from modules.xiq import XIQ_API
import re

def getXIQInfo(ip_or_mac):
    """
    Fetch XIQ info for a given MAC or IP address.
    """
    try:
        if not (isValidMAC(ip_or_mac) or isValidIP(ip_or_mac)):
            raise Exception(f"Not a valid IP or MAC: {ip_or_mac}")
        
        if (isValidMAC(ip_or_mac)):
            results = get_switch_info_by_mac(ip_or_mac)
        else:
            results = get_switch_info_by_ip(ip_or_mac)
                
        return results
    except:
        results = [{
            "switchIP": "",
            "switchPortId": "",
            "sysName": "",
            "sysLocation": ""     
        }]
        return results
    

    
def get_switch_info_by_mac(mac):
    # Correct the MAC address formatting
    mac = mac.replace("-", ":").upper()

    # Get switch info
    switchInfo = XIQ_API.get_xiq_switch_info_by_endpoint_mac(mac)

    #List format required so put as list
    return [switchInfo]



def get_switch_info_by_ip(ip):
    # Get switch info
    switchInfo = XIQ_API.get_xiq_switch_info_by_endpoint_ip(ip)

    #List format required so put as list
    return [switchInfo]


def isValidMAC(value):
    """
    Check if the value is a valid MAC address.
    """
    return bool(re.search(r"^([a-zA-Z0-9]{2}-){5}[a-zA-Z0-9]{2}$", value))

def isValidIP(value):
    """
    Check if the value is a valid IP address.
    """
    return bool(re.search(r"^(\d{1,3}\.){3}\d{1,3}$", value))