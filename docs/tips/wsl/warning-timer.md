[English](warning-timer.en.md) | 日本語

# TIPS
## WSL で、Ardupilot を起動すると Warning, time moved backwards. Restarting timer.が出た時の対処方法

この警告は、Ardupilot SITL がシステム時刻の逆行を検出した際に表示されるメッセージです。

### 対処方法

WSL2の時刻同期を手動で実行

```bash
sudo hwclock -s
```

chrony による時刻同期

```bash
sudo apt update
sudo apt install chrony
sudo systemctl start chronyd
sudo systemctl enable chronyd
```

WSL2を再起動する