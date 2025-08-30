[English](wsl-portfoward.en.md) | 日本語

# 🌐 外部PCからWSL2のシミュレータに接続する方法

Hakoniwa Drone Simulator を **WSL2 上で実行**し、外部PC（同一ネットワーク内）から接続したい場合は、以下の手順を参考にしてください。

## ✅ 前提条件

* **WSL2 を使用していること**
* **サーバーが `0.0.0.0:<port>` または `:::<port>` で待ち受けていること**

---

## ① WSL2内のIPアドレスを確認

WSL2は独立した仮想ネットワーク内で動作するため、**Windowsホストとは別のIPアドレス**を持ちます。

WSL2内で以下を実行してIPを確認します：

```bash
ip addr show eth0
# または
hostname -I
```

出力されるIP（例：`172.26.125.1`）がWSL2の内部IPです。

---

## ② Windowsにポートフォワード設定を追加

WindowsのPowerShell（管理者権限）で以下を実行します。
これは **Windowsのポート8080をWSL2内のポート8080に転送**する例です：

```powershell
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=172.26.125.1
```

確認するには：

```powershell
netsh interface portproxy show all
```

削除するには：

```powershell
netsh interface portproxy delete v4tov4 listenport=8080 listenaddress=0.0.0.0
```

---

## ③ Windowsのファイアウォールを許可

該当ポート（例：8080）が**Windows Defender ファイアウォールにブロックされていないこと**を確認します。

### GUIで設定する場合：

1. コントロールパネル → システムとセキュリティ → Windows Defender ファイアウォール
2. 左メニューから「受信の規則」を選択
3. 「新しい規則の作成」から「ポート」を選び、該当ポートを開放

### PowerShellで設定する場合：

```powershell
New-NetFirewallRule -DisplayName "Allow Port 8080" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

---

## ④ 外部PCからの接続

外部PCでは、**WindowsホストのローカルIPアドレス**を使用して接続します：

例：

```text
http://192.168.1.100:8080
```

WindowsのIP確認方法：

```powershell
ipconfig
```

> 💡 `IPv4 アドレス` を確認してください。

---

## 🔁 補足：ポート転送を自動化するには

WSL2のIPは再起動ごとに変わることがあるため、**PowerShellスクリプトで動的に設定する**ことが可能です：

```powershell
$wsl_ip = wsl hostname -I
netsh interface portproxy set v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=8080 connectaddress=$wsl_ip
```

> スクリプトをスタートアップ登録すれば、自動化も可能です。


---