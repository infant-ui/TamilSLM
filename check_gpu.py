import paramiko
import sys

def check_gpu():
    host = '10.11.152.55'
    user = 'pa'
    password = 'Project1'

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=host, username=user, password=password, timeout=10)
        print("Successfully connected to 10.11.152.55 via SSH.")
        
        commands = [
            'nvidia-smi',
            'docker ps',
            'systemctl status ollama'
        ]
        
        for cmd in commands:
            print(f"\n--- Running: {cmd} ---")
            stdin, stdout, stderr = client.exec_command(cmd)
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            if out:
                print(out)
            if err:
                print("Error Output:")
                print(err)
                
    except Exception as e:
        print(f"Failed to connect or execute commands: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    check_gpu()
