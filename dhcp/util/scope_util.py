import ipaddress
from modules.dhcp import dhcp_pwsh

_cached_scopes = None
_cached_limited_scopes = None

def get_dhcp_scopes():
    global _cached_scopes
    if _cached_scopes is not None:
        return _cached_scopes

    raw_scopes = dhcp_pwsh.get_all_scopes_with_domain()
    scopes = normalize_all_dhcp_scopes(raw_scopes)

    _cached_scopes = scopes
    return scopes

def find_scope_for_ip(ip_str):
    ip = ipaddress.IPv4Address(ip_str)
    scopes = get_dhcp_scopes()

    for scope in scopes:
        if ip in scope["network"]:
            return scope["scope_id"]

    return None

def get_scopes():
    global _cached_limited_scopes
    if _cached_limited_scopes is not None:
        return _cached_limited_scopes
    
    scopes = []

    scopes = get_dhcp_scopes()
    for scope in scopes:
        scope_domain = scope["domain_name"]
        if scope_domain.lower() == "limited.domain.com":
            scopes.append(scope)

    _cached_limited_scopes = scopes
    return scopes

def is_ip_in_scopes(ip):
    ip_address = ipaddress.ip_address(ip)
    scopes = get_scopes()
    return any(ip_address in s["network"] for s in scopes)

def normalize_all_dhcp_scopes(scopes):
    if isinstance(scopes, dict):
        scopes = [scopes]

    parsed = []
    for scope in scopes:
        net = scope["ScopeId"]
        mask = scope["SubnetMask"]
        domain = scope["DomainName"]

        if not net or not mask:
            continue

        if isinstance(net, dict):
            net = net["IPAddressToString"]
        if isinstance(mask, dict):
            mask = mask["IPAddressToString"]

        try:
            network = ipaddress.IPv4Network((net, mask), strict=False)
        except Exception:
            continue

        parsed.append({
            "scope_id": net,
            "subnet_mask": mask,
            "network": network,
            "domain_name": domain or "",
        })
    return parsed
