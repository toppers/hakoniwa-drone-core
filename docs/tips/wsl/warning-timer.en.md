English | [日本語](warning-timer.md)

# TIPS
## How to deal with "Warning, time moved backwards. Restarting timer." when starting Ardupilot on WSL

This warning is a message displayed when Ardupilot SITL detects that the system time has moved backwards.

### Solution

Manually perform time synchronization for WSL2.

```bash
sudo hwclock -s
```

Time synchronization by chrony.

```bash
sudo apt update
sudo apt install chrony
sudo systemctl start chronyd
sudo systemctl enable chronyd
```

Restart WSL2.