# Hakoniwa Drone Simulator v3.3.0 → v3.4.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v3.4.0 では、以下のリポジトリおよびライブラリがアップデートが必要です。

本ドキュメントでは、各リポジトリおよびライブラリのアップデート手順について説明します。


## v3.4.0 の新機能・変更点

- MuJoCo 連携機能の追加
  - 箱庭ドローンの物理モデルを MuJoCo でシミュレーション可能に
- Gemini 連携機能の追加
  - 箱庭RPCサーバーを通じて Gemini と連携可能に
- Scratch 連携機能の追加
  - 箱庭RPCサーバーを通じて Scratch と連携可能に
- 箱庭環境シミュレーション用リポジトリの新設
  - hakoniwa-envsim リポジトリを新設し、環境シミュレーション機能を提供
- 箱庭ドローンPROユーザ向けの機能アップデート
  - ビルドした箱庭ドローンPROバイナリをdockerコンテナ内で利用可能に
  - 箱庭環境シミュレーションデータをセンサ/アクチュエータデータとして利用可能に

## 前提とする環境

- OS: Windows 11 / WSL2 Ubuntu 24.04 LTS
- 箱庭ドローンシミュレータのアーキテクチャパターン： [コンテナパターン](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/getting_started/container.md)


WSL2/Ubuntu 環境で、`${HOME}/hakoniwa` 直下にアップデート対象リポジトリ(後述)がクローンされていることを前提とします。

## アップデート手順
### アップデート対象リポジトリ

- hakoniwa-drone-core
  - target version: v3.4.0
- hakoniwa-unreal-drone
  - target version: v1.1.0
- hakoniwa-unity-drone
  - target version: v3.3.0
- hakoniwa-webserver
  - target version: v1.0.1

もしすでに編集中のファイルがある場合は、バックアップ退避してください。

その後、各リポジトリ配下で以下のコマンドを実行し、対象バージョンにチェックアウトしてください。

```bash
git pull origin main
git submodule update --init --recursive
```

## 新規追加リポジトリ

- hakoniwa-envsim
  - GitHub URL: https://github.com/hakoniwalab/hakoniwa-envsim.git
  - target version: v1.0.0
  - 箱庭環境シミュレーション用の専用リポジトリを新設しました。
  - 今後のアップデートはこちらで行いますので、必要に応じてクローンしてください。
- hakoniwa-scratch
  - GitHub URL: https://github.com/hakoniwalab/hakoniwa-scratch.git
  - target version: v1.0.0
  - Scratch 連携機能を提供するリポジトリを新設しました。

`${HOME}/hakoniwa` 配下で以下のコマンドを実行し、リポジトリをクローンしてください。
    
```bash
git clone --recursive https://github.com/hakoniwalab/hakoniwa-envsim.git
```

Scratch 連携機能を利用する場合は、以下のコマンドを実行し、リポジトリをクローンしてください。

```bash
git clone --recursive https://github.com/hakoniwalab/hakoniwa-scratch.git
```


## アップデート対象ライブラリ等

- hakoniwa-pdu Python ライブラリ
  - target version: 1.3.1
- hakoniwa-core-full debian パッケージ
  - target version: 1.1.1-2
- hakoniwa-drone-core docker イメージ
  - target version: v2.4.4

今回のアップデートに伴い、上記ライブラリ等のアップデートが必要です。
ただ、今回説明するアップデート手順は、コンテナパターンを前提としていますので、docker イメージのアップデートのみで完了します。

`hakoniwa-drone-core` 直下で、以下のコマンドを実行し、docker イメージをアップデートしてください。

```bash
bash docker/pull-image.bash
```

アップデートが完了したら、以下のコマンドを実行し、`hakoniwa-drone-core` の docker イメージが `v2.4.4` に更新されていることを確認してください。


```bash
docker images
```
```
REPOSITORY                            TAG            IMAGE ID       CREATED         SIZE
toppersjp/hakoniwa-drone-core         v2.4.4         5dcd7b5b71e6   20 hours ago    1.41GB
```

以下、ホスト環境での `hakoniwa-pdu` および `hakoniwa-core-full` のアップデート手順を示します。

### hakoniwa-pdu Python ライブラリのアップデート手順

```bash
pip install --upgrade hakoniwa-pdu
```

```bash
pip show hakoniwa-pdu
```

```bash
Name: hakoniwa-pdu
Version: 1.3.1
Summary: Hakoniwa PDU communication library for Python
Home-page: https://github.com/hakoniwalab
Author: 
Author-email: Takashi Mori <tmori@hakoniwa-lab.net>
License: 
Location: /Users/tmori/.local/lib/python3.10/site-packages
Requires: jsonsc
```

### hakoniwa-core-full debian パッケージのアップデート手順

```bash
sudo apt-get update
sudo apt-get install --only-upgrade hakoniwa-core-full
```

```bash
dpkg -s hakoniwa-core-full | grep Version
```

```
Package: hakoniwa-core-full
Status: install ok installed
Priority: optional
Section: utils
Installed-Size: 153
Maintainer: Takashi Mori <tmori@hakoniwa-lab.net>
Architecture: all
Source: hakoniwa-core
Version: 1.1.1-2
Depends: hakoniwa-core (= 1.1.1-2), libhakoniwa-conductor1 (= 1.1.1-2), libhakoniwa-assets1 (= 1.1.1-2), libhakoniwa-shakoc1 (= 1.1.1-2), python3-hakopy (= 1.1.1-2), hakoniwa-core-dev (= 1.1.1-2)
Description: Meta package: full Hakoniwa core (tools, libs, python, headers)
 Installs the full Hakoniwa toolchain: CLI tools, runtime libs, Python bindings,
 and development headers.
Homepage: https://github.com/hakoniwalab/hakoniwa-core-pro
```

## アップデート動作確認

各リポジトリおよびライブラリのアップデートが完了したら、箱庭ドローンシミュレータが正常に動作することを確認してください。


- 箱庭ドローンシミュレータの動作確認
  - [Getting Started: コンテナパターン（箱庭あり）](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/getting_started/container.md)
- MuJoCo 連携機能の動作確認
  - [MuJoCo 連携機能の使い方](https://qiita.com/kanetugu2018/items/4ef4668adbe3ee77e6c0)
- Gemini 連携機能の動作確認
  - [Gemini 連携機能の使い方](https://qiita.com/kanetugu2018/items/60c6fb3b906a430097fc)
- Scratch 連携機能の動作確認
  - [Scratch 連携機能の使い方](https://github.com/hakoniwalab/hakoniwa-scratch/blob/main/README.md)
- 箱庭環境シミュレーション機能の動作確認
  - [概要説明およびシミュレーション実行手順](https://www.docswell.com/s/kanetugu2015/537NE2-hakoniwa-drone-environment)
  - [その他の利用方法](https://github.com/hakoniwalab/hakoniwa-envsim/blob/main/README.md)

  