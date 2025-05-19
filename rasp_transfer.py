import paramiko

hostname = "raspberrypi"  # Using the VNC hostname instead of IP
username = "ciara"
password = "ciara@1234"  # Update if you changed the default password
local_path = "D:/CIARA/1csv_transfer/CSV/matlab/sqfr_angles.csv"
remote_path = "/home/ciara/New/sq_frc.csv"

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("Connecting to Raspberry Pi...")
    ssh.connect(hostname, username=username, password=password)
    print("Connected!")

    sftp = ssh.open_sftp()
    print("Transferring file...")
    sftp.put(local_path, remote_path)
    sftp.close()
    print("File successfully transferred to Raspberry Pi!")
except paramiko.AuthenticationException:
    print("Authentication failed. Please check your username and password.")
except FileNotFoundError as e:
    print(f"Local file not found: {e}")
except paramiko.ssh_exception.NoValidConnectionsError as e:
    print(f"Cannot connect to {hostname}. Check the IP address or SSH service: {e}")
except Exception as e:
    print(f"File transfer failed: {e}")
finally:
    ssh.close()
