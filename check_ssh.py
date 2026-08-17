import paramiko
import sys

def try_ssh(password):
    host = '10.11.152.55'
    user = 'pa'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=host, username=user, password=password, timeout=5)
        print(f"Success with password: {password}")
        stdin, stdout, stderr = client.exec_command('nvidia-smi')
        print(stdout.read().decode())
    except Exception as e:
        print(f"Failed with password {password}: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    try_ssh('Project')
