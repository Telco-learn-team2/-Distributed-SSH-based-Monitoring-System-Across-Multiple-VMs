# Team 2

# Distributed SSH-based Monitoring System — README

> *Project 2* — Centralized monitoring of multiple Ubuntu VMs via SSH. Dockerized monitoring container hosts a Flask dashboard, collects metrics via SSH, logs anomalies, and stores metrics. This README documents setup, usage, troubleshooting (including detailed problems faced with SSH ports and dashboard access), security considerations, and individual contributions for the GitHub repository.

---

## Table of Contents

1. Project overview
2. Architecture
3. Prerequisites
4. VM configuration (example netplan / static IPs)
5. SSH key-based authentication (generation, distribution, automation)
6. Monitoring application (design, components, key files)
7. Docker & Docker Compose (how to build/run)
8. Running the system (checklist + commands)
9. PCAP capture and Wireshark verification
10. Logs, data formats and anomaly detection
11. Troubleshooting (detailed problems faced & root cause analysis)
12. Security & key management
13. Git branching strategy, PR examples and VSCode settings
14. Individual contributions
15. Appendix (useful commands, sample configs, troubleshooting snippets)

---

## 1. Project overview

This project runs a centralized monitoring application (containerized with Docker) on a host machine that connects to a set of minimum *3 Ubuntu VMs* using *SSH key-based* connections. For each VM the monitor collects system metrics (CPU, memory, disk I/O, network interface stats) at an interval that does *not exceed 5 seconds per VM*. The monitor aggregates metrics, detects anomalies (e.g., CPU spikes, low disk space), logs them in human-readable and machine-parseable formats (CSV/JSON), and triggers alerts.

The monitor includes a lightweight Flask dashboard (served from the monitoring container) to display near real-time metrics. Wireshark PCAP files are used to verify SSH handshakes and metric transmissions.

Performance & constraints emphasized in this project:

* SSH connection retries are graceful with exponential backoff.
* Metric collection > 5s per VM is avoided.
* Dashboard must load under 2s in normal conditions.
* Monitoring must detect anomalies within 1 minute of occurrence.

## 2. Architecture


Monitoring container -> SSH -> VMs (collect metrics via remote commands / small agent)


Notes: VMs should be reachable from the host container IP. Use separate subnets if possible (virtual network adapters) to match project constraint.

## 3. Prerequisites

* Host: Linux (Ubuntu recommended) with Docker & Docker Compose installed.
* At least 3 Ubuntu VM images configured as guests on the host (VirtualBox, KVM, or libvirt). Each VM should have a static IP or predictable DHCP mapping.
* ssh, scp, tcpdump, wireshark (on host for PCAP capture).
* git and VSCode for development.
* Python 3.10+ (monitoring app uses Python + Flask + paramiko/asyncssh/psutil)

## 4. VM configuration — sample netplan files (static IPs)

Below are *example* netplan files for three VMs. Adjust gateways/subnets for your environment.

*/etc/netplan/01-netcfg.yaml (VM1)*

yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    ens33:
      dhcp4: no
      addresses: [10.0.1.11/24]
      gateway4: 10.0.1.1
      nameservers:
        addresses: [8.8.8.8,8.8.4.4]


*VM2* — 10.0.2.12/24 (gateway 10.0.2.1)

*VM3* — 10.0.3.13/24 (gateway 10.0.3.1)

Apply with:

bash
sudo netplan apply
ip a    # verify


## 5. SSH key-based authentication (generation, distribution, automation)

### Generate a key pair (on host / monitoring container)

bash
ssh-keygen -t ed25519 -C "monitor@host" -f ~/.ssh/monitor_key -N ""  # use passphrase for production


### Copy public key to VM (manual)

bash
ssh-copy-id -i ~/.ssh/monitor_key.pub ubuntu@10.0.1.11
ssh-copy-id -i ~/.ssh/monitor_key.pub ubuntu@10.0.2.12
ssh-copy-id -i ~/.ssh/monitor_key.pub ubuntu@10.0.3.13


### Automated key deployment script (scripts/deploy_keys.sh)

bash
#!/bin/bash
KEY=~/.ssh/monitor_key.pub
for host in 10.0.1.11 10.0.2.12 10.0.3.13; do
  echo "Deploying key to $host"
  sshpass -p "$VM_PASSWORD" ssh-copy-id -i "$KEY" "ubuntu@$host"
done


## 6. Monitoring application — design & components

*Language / libs:* Python 3 + Flask + paramiko or asyncssh

*Key files (in repo)*


monitor/
  app.py
  collector.py
  docker/
  requirements.txt
  docker-compose.yml
  config.yaml
  templates/
  static/


## 7. Docker & Docker Compose

*docker-compose.yml*

yaml
version: '3.8'
services:
  monitor:
    build: ./monitor
    container_name: monitor_app
    volumes:
      - ./monitor/data:/app/data
      - ./monitor/logs:/app/logs
      - ~/.ssh:/root/.ssh:ro
    ports:
      - "5000:5000"
    restart: unless-stopped


## 8. Running the system (checklist + commands)

bash
docker compose up --build -d
docker logs -f monitor_app


Dashboard URL: http://<host-ip>:5000/

## 9. PCAP capture & Wireshark verification

bash
sudo tcpdump -i any port 22 -w ssh_traffic.pcap


## 10. Logs, data formats and anomaly detection

Metrics stored in CSV/JSON under monitor/data. Anomalies logged in monitor/logs.

## 11. Troubleshooting — Detailed Problems Faced

### Problem A — SSH "Connection refused"

* Cause: UFW blocked port 22 / sshd listening on 127.0.0.1 only.
* Fix: sudo ufw allow 22/tcp, update sshd_config.

### Problem B — Public key authentication failure

* Cause: Wrong permissions on ~/.ssh and authorized_keys.
* Fix: chmod 700 ~/.ssh, chmod 600 ~/.ssh/authorized_keys.

### Problem C — Dashboard not accessible

* Cause: Flask bound to 127.0.0.1, blocking external access.
* Fix: Bind to 0.0.0.0, use gunicorn workers.

### Problem D — Unable to access SSH from host

* Cause: VM network mode set to NAT, no route from host.
* Fix: Switch to Bridged/Host-only.

## 12. Security & Key Management

* Avoid storing private keys in container.
* Use key rotation.
* Use restricted SSH options where possible.

## 13. Git branching strategy

* main — stable branch
* develop — integration
* feature/* — new features

## 14. Individual contributions

*Ankitha H R, Pragati*

* VM setup, netplan config
* Implementation of SSH monitoring logic
* Documentation & troubleshooting

*Ankith M , Jeevan Shetty*

* Dockerization, Compose config
* Flask UI

*Kiran D H*

* Key deployment automation
* Wireshark analysis

## 15. Appendix

Useful commands, ssh tests, tcpdump filters, snippets, etc.
