import paramiko
import base64

def run_command_over_ssh_with_connection(connection, command, timeout=30):
    #Runs with connection passed
    stdin, stdout, stderr = connection.exec_command(command, timeout=timeout)
    out = stdout.read().decode("utf-8", errors="replace").strip()
    err = stderr.read().decode("utf-8", errors="replace").strip()
    code = stdout.channel.recv_exit_status()

    if code != 0:
        raise RuntimeError(f"SSH command failed ({code}): {err or out}. Command: {command}")
    return out

def run_command_over_ssh(command, host, port, username, keypath, timeout=30):
    #Open, run once, close
    with SSHClientManager(host, port, username, keypath, timeout) as connection:
        return run_command_over_ssh_with_connection(connection, command, timeout)

def run_powershell_over_ssh(ps_command, host, port, username, keypath, timeout=30):
    full_ps_command = _build_ps(ps_command)
    encoded = _encode_ps(full_ps_command)
    command = f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded}"
    return run_command_over_ssh(command, host, port, username, keypath, timeout)
    
def run_powershell_over_ssh_with_connection(connection, ps_command, timeout=30):
    full_ps_command = _build_ps(ps_command)
    encoded = _encode_ps(full_ps_command)
    command = f"powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand {encoded}"
    return run_command_over_ssh_with_connection(connection, command, timeout)

def _encode_ps(script):
    return base64.b64encode(script.encode('utf-16le')).decode('ascii')

def _build_ps(command):
    return f"""
        $ErrorActionPreference = 'Stop'
        $ProgressPreference = 'SilentlyContinue'
        $InformationPreference = 'SilentlyContinue'
        $WarningPreference = 'SilentlyContinue'
        $VerbosePreference = 'SilentlyContinue'

        try {{
            & {{ {command} }}
            exit 0
        }}
        catch {{
            $_ | Out-String | Write-Error
            exit 1
        }}
        """



class SSHClientManager:
    #Reuse an SSH connection

    def __init__(self, host, port, username, keypath, timeout=30):
        self.host = host
        self.port = port
        self.username = username
        self.keypath = keypath
        self.timeout = timeout
        self.client = None

    def __enter__(self):
        key = paramiko.RSAKey.from_private_key_file(self.keypath)
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(
            self.host,
            port=self.port,
            username=self.username,
            pkey=key,
            look_for_keys=False,
            allow_agent=False,
            timeout=self.timeout,
        )
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()