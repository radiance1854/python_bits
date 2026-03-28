# Run XIQ API Query:
from modules.xiq import XMC_NBI

# XIQ Connection Info
XIQ_SERVER_IP = 'XX.XX.XX.XX'
XIQ_CLIENT_ID = 'XXXXXXXXXX'
XIQ_SECRET    = 'XXXXXXXXXX'


def xiq_api_get_query(query):

    try:
        # Establish the API XIQ Connection
        session = XMC_NBI.XMC_NBI(XIQ_SERVER_IP, XIQ_CLIENT_ID, XIQ_SECRET)
        if session.error:
            raise Exception(f"Error connecting to XIQ API: {session.error}")

        # Run query
        data = session.query(query)

    except Exception as e:
        raise Exception(f"Error connecting to XIQ API: {e}") from e
    
    return data


def get_xiq_switch_info_by_endpoint_ip(ip):

    # XIQ API query to retrieve switch information about the target IP
    query = f"""
        query {{
            accessControl {{
                endSystemByIp(ipAddress: "{ip}") {{
                    endSystem {{
                        switchIP
                        switchPortId
                    }}
                }}
            }}
        }}
        """

    # Run query and remove unneeded data layers
    results = xiq_api_get_query(query)
    switchInfo = results["accessControl"]["endSystemByIp"]["endSystem"]

    if switchInfo is None:
        raise Exception(f"Target IP could not be found in the XIQ database")

    # Get Switch Name and Location
    switchInfo["sysName"], switchInfo["sysLocation"] = get_xiq_switch_name_and_location_by_switch_ip(switchInfo["switchIP"])

    return switchInfo


def get_xiq_switch_info_by_endpoint_mac(mac):

    # XIQ API query to retrieve switch information about the target MAC
    query = f"""
        query {{
            accessControl {{
                endSystemByMac(macAddress: "{mac}") {{
                    endSystem {{
                        switchIP
                        switchPortId
                    }}
                }}
            }}
        }}
        """

    # Run query and remove unneeded data layers
    results = xiq_api_get_query(query)
    switchInfo = results["accessControl"]["endSystemByMac"]["endSystem"]

    # Get Switch Name and Location
    switchInfo["sysName"], switchInfo["sysLocation"] = get_xiq_switch_name_and_location_by_switch_ip(switchInfo["switchIP"])

    return switchInfo


def get_xiq_switch_name_and_location_by_switch_ip(ip):

    query = f"""
        query {{
            network {{
                device(ip: "{ip}") {{
                    sysName
                    sysLocation
                }}
            }}
        }}
        """
    
    # Run query and remove unneeded data layers
    results = xiq_api_get_query(query)
    switchResults = results["network"]["device"]

    return switchResults["sysName"], switchResults["sysLocation"]