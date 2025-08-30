English | [日本語](wsl-portfoward.md)

# 🌐 How to connect to a simulator on WSL2 from an external PC

If you want to run the Hakoniwa Drone Simulator on **WSL2** and connect to it from an external PC (on the same network), please refer to the following procedure.

## ✅ Prerequisites

*   **You are using WSL2**
*   **The server is listening on `0.0.0.0:<port>` or `:::<port>`**

---

## ① Check the IP address in WSL2

Since WSL2 operates in an independent virtual network, it has a **different IP address from the Windows host**.

Execute the following in WSL2 to check the IP:

```bash
ip addr show eth0
# or
hostname -I
```

The output IP (e.g., `172.26.125.1`) is the internal IP of WSL2.

---

## ② Add port forwarding settings to Windows

Execute the following in Windows PowerShell (with administrator privileges).
This is an example of **forwarding Windows port 8080 to port 8080 in WSL2**:

```powershell
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.26.125.1
```

To check:

```powershell
netsh interface portproxy show all
```

To delete:

```powershell
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
```

---

## ③ Allow through Windows Firewall

Make sure that the corresponding port (e.g., 8080) is **not blocked by the Windows Defender Firewall**.

### To configure with GUI:

1.  Control Panel → System and Security → Windows Defender Firewall
2.  Select "Inbound Rules" from the left menu
3.  Select "New Rule..." and choose "Port" to open the corresponding port

### To configure with PowerShell:

```powershell
New-NetFirewallRule -DisplayName "Allow Port 8080" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

---

## ④ Connection from an external PC

On the external PC, connect using the **local IP address of the Windows host**:

Example:

```text
http://192.168.1.100:8080
```

How to check the IP of Windows:

```powershell
ipconfig
```

> 💡 Please check the `IPv4 Address`.

---

## 🔁 Supplement: To automate port forwarding

Since the IP of WSL2 may change with each restart, it is possible to **set it dynamically with a PowerShell script**:

```powershell
$wsl_ip = wsl hostname -I
netsh interface portproxy set v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$wsl_ip
```

> It is also possible to automate by registering the script at startup.


---