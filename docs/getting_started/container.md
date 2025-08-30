[English](container.en.md) | 日本語

# Getting Started: コンテナパターン（箱庭あり）

箱庭ドローンシミュレータを **コンテナパターン（箱庭あり）** で利用する場合、Dockerコンテナを使用して、物理モデルや制御モデルを**分離実行**できます。
この構成では、UnityやUnreal Engine、ROS2、Webなどと**Bridgeを介して連携**することが可能です。


📘 [コンテナパターン全体の概要と構成イメージを見る](/docs/architecture/overview.md) 

---

## ✅ 特徴

* 各構成要素（PX4/Ardupilot, hakoniwa-drone-core, hakoniwa-coreなど）を独立コンテナ化
* dockerによるインストールの簡素化
* Bridge経由でROS2やWeb、Pythonスクリプトなどと接続
* WSL2やクラウドでも動作可能
* ゲームパッドやXRとの統合も可能

---

## 🧰 チュートリアルと実例（Qiita）

> コンテナパターンでの実行は、目的やOS構成によりセットアップが多岐にわたるため、以下のQiita記事で詳細な手順を解説しています。

| タイトル                          | 内容                        | リンク                                                                   |
| ----------------------------- | ------------------------- | --------------------------------------------------------------------- |
| PX4 + Unity + Docker構成        | PX4とUnityをDockerで分離実行する構成 | [📘 記事を読む](https://qiita.com/kanetugu2018/items/d4a21b590950774c6cf8) |
| ArduPilotをWSL+Dockerで高速セットアップ | ArduPilotと連携して飛行制御を行う構成   | [📘 記事を読む](https://qiita.com/kanetugu2018/items/59e3b657c402691bff54) |
| Python + Unity + GamePad構成    | Python制御とゲームパッドを組み合わせた事例  | [📘 記事を読む](https://qiita.com/kanetugu2018/items/24d66fc9ac189feca952) |
| Python API + Unity 構成       | Python APIを使ったUnity連携の事例        | [📘 記事を読む](https://qiita.com/kanetugu2018/items/d9763ceb4e527b50c7e2) |
---

## TIPS

- [Windows で 箱庭あり版PX4/Ardupilot連携する場合について](/docs/tips/wsl/hakoniwa-wsl.md)
- [WSL で、Ardupilot を起動すると Warning, time moved backwards. Restarting timer.が出た時の対処方法](/docs/tips/wsl/warning-timer.md)
- [Ardupilot SITL のセットアップ方法](/docs/tips/wsl/ardupilot-setup.md)
- [WSL/docker 環境のセットアップ方法](/docs/tips/wsl/docker-setup.md)
- [WSL/docker 環境で箱庭&PX4連携方法](/docs/tips/wsl/docker-px4.md)
- [WSL/docker 環境で箱庭&Ardupilot連携方法](/docs/tips/wsl/docker-ardupilot.md)
- [WSL/docker 環境で箱庭&Python API連携方法](/docs/tips/wsl/docker-python-api.md)
- [WSL/docker 環境で箱庭&ゲームパッド操作方法](/docs/tips/wsl/docker-gamepad.md)
- [WSL2でのポート転送設定方法](/docs/tips/wsl/wsl-portforward.md)

