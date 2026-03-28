import json
from modules.tools import ssh_util

DHCP_SERVER_IP = "XX.XX.XX.XX"
DHCP_SERVER_SSH_PORT = 22
DHCP_SSH_USERNAME = "testuser"
DHCP_SSH_USER_KEY_FILE_LOCATION = "/path/to/ssh/key"

# Run powershell over SSH function

def _run(ps_command):
    results = ssh_util.run_powershell_over_ssh(ps_command, DHCP_SERVER_IP, DHCP_SERVER_SSH_PORT, DHCP_SSH_USERNAME, DHCP_SSH_USER_KEY_FILE_LOCATION)
    if not results:
        return None
    else:
        return json.loads(results)

# Get Leases

def get_lease_for_mac(mac):
    ps_command = rf"""
        Get-DhcpServerv4Scope | 
        Get-DhcpServerv4Lease |
        Where-Object {{ $_.ClientId -like "{mac}" }} |
        Select-Object IPAddress, ClientId, HostName, LeaseExpiryTime, AddressState |
        ConvertTo-Json -Compress
    """
    return _run(ps_command)

def get_lease_for_ip(ip):
    ps_command = rf"""
        Get-DHCPServerv4Lease -IPAddress "{ip}" |
        Select-Object IPAddress, ClientId, HostName, LeaseExpiryTime, AddressState |
        ConvertTo-Json -Compress
    """
    return _run(ps_command)

# Get Reservations

def get_reservation_for_mac(mac):
    ps_command = rf"""
        Get-DhcpServerv4Scope |
        Get-DhcpServerv4Reservation |
        Where-Object {{ $_.ClientId -like "{mac}" }} | 
        Select-Object IPAddress, ScopeId, ClientId, Name, Description |
        ConvertTo-Json -Compress
    """
    return _run(ps_command)

def get_reservation_for_ip(scopeId, ip):
    ps_command = rf"""
        Get-DhcpServerv4Reservation -ScopeId "{scopeId}" | 
        Where-Object {{ $_.IPAddress -like "{ip}" }} | 
        Select-Object IPAddress, ScopeId, ClientId, Name, Description |
        ConvertTo-Json -Compress
    """
    return _run(ps_command)

# Changes

def modify_reservation_by_ip(ip, mac, description, name):
    ps_command = rf"""
        Set-DhcpServerv4Reservation -IPAddress "{ip}" -ClientID "{mac}" -Description "{description}" -Name "{name}"
    """
    return _run(ps_command)

def delete_reservation_by_ip(ip):
    ps_command = rf"""
        Remove-DhcpServerv4Reservation -IPAddress "{ip}"
    """
    return _run(ps_command)

def add_reservation_by_ip(scopeId, ip, mac, description, name):
    ps_command = rf"""
        Add-DhcpServerv4Reservation -ScopeId "{scopeId}" -IPAddress "{ip}" -ClientId "{mac}" -Description "{description}" -Name "{name}"
    """
    return _run(ps_command)

# Helpers

def update_replication_for_scope(scope_id):
    ps_command = rf"""
        $ScopeId = '{scope_id}'
        
        $domainUsername = "AD\testuser"
        $domainPassword = "XXXXXXXX"

        $taskName = "replicate_" + ($ScopeId -replace '\.', '_')

        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"Invoke-DhcpServerv4FailoverReplication -ScopeId '$ScopeId' -Force`""

        $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddSeconds(1.5)

        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
            -User $domainUsername -Password $domainPassword | Out-Null

        Start-ScheduledTask -TaskName $taskName

        Start-Sleep -Seconds 5
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    """
    return _run(ps_command)

def get_all_scopes_with_domain():
    ps_command = r"""
        $scopes = Get-DhcpServerv4Scope -ErrorAction SilentlyContinue

        $results = foreach ($s in $scopes) {
            try {
                $opt = Get-DhcpServerv4OptionValue -ScopeId $s.ScopeId -OptionId 15 -ErrorAction Stop
                $domain = if ($opt) { $opt.Value -join '' } else { $null }
            } catch {
                $domain = $null
            }

            [PSCustomObject]@{
                ScopeId    = $s.ScopeId
                SubnetMask = $s.SubnetMask
                DomainName = $domain
            }
        }

        $results | ConvertTo-Json -Compress
    """
    return _run(ps_command)
