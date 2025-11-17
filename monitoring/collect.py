import paramiko
import time
import json

VMS = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]

def collect_metrics(ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username="ankith", key_filename="/root/.ssh/id_rsa")

    commands = {
        "cpu": "top -bn1 | grep Cpu",
        "mem": "free -m",
        "disk": "df -h /",
        "net": "ifconfig"
    }

    result = {}
    for key, cmd in commands.items():
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result[key] = stdout.read().decode()

    ssh.close()
    return result
