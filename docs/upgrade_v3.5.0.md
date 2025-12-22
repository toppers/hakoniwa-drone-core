# Hakoniwa Drone Simulator v3.4.0 → v3.5.0 アップデート手順

## はじめに

Hakoniwa Drone Simulator v3.5.0 では、以下のリポジトリおよびライブラリがアップデートが必要です。

本ドキュメントでは、各リポジトリおよびライブラリのアップデート手順について説明します。


## v3.5.0 の新機能・変更点

今回のバージョンアップのメインは、MuJoCo 連携機能の強化です。

- Mujoco 連携機能の強化
  - MuJoCoのバージョンアップ（v3.3.7 → v3.4.0）
  - MuJoCoの風影響機能追加
  - MuJoCoの衝突判定機能追加
  - MuJoCoの都市データ対応
  - MuJoCoの複数機体対応
    - １個のMJCFファイルで複数機体を定義する方針に変更
- 箱庭環境シミュレーションとの連携強化
  - 環境シミュレーションと連携可能なドローン飛行Pythonサンプルスクリプトを追加(drone_api/pymavlink/env_api_test.py)
  - [hakoniwa-map-viewer](https://github.com/hakoniwalab/hakoniwa-map-viewer)
    - 箱庭ドローンシミュレータと連携し、PLATEAU都市データ上でのドローン飛行を、地図および3Dビューでリアルタイムに可視化する ブラウザビューアと連携可能に
  - [hakoniwa-envsim](https://github.com/hakoniwalab/hakoniwa-envsim)
    - ブラウザ上で、オープンストリートマップ地図を参照しながら、環境データやドローン移動ルートを作成可能に

## 前提とする環境

- OS: Windows 11 / WSL2 Ubuntu 24.04 LTS
- 箱庭ドローンシミュレータのアーキテクチャパターン： [コンテナパターン](https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/getting_started/container.md)


WSL2/Ubuntu 環境で、`${HOME}/hakoniwa` 直下にアップデート対象リポジトリ(後述)がクローンされていることを前提とします。

## アップデート手順
### アップデート対象リポジトリ

- hakoniwa-drone-core
  - target version: v3.5.0
- hakoniwa-unreal-drone
  - target version: v1.1.2
- hakoniwa-unity-drone
  - target version: v3.3.1
- hakoniwa-envsim
  - target version: v2.0.0
- hakoniwa-map-viewer
  - target version: v1.0.0

もしすでに編集中のファイルがある場合は、バックアップ退避してください。

その後、各リポジトリ配下で以下のコマンドを実行し、対象バージョンにチェックアウトしてください。

```bash
git pull origin main
git submodule update --init --recursive
```

## 新規追加リポジトリ

- hakoniwa-mav-viewer
  - GitHub URL: https://github.com/hakoniwalab/hakoniwa-mav-viewer.git
  - target version: v1.0.0
  - 箱庭ドローンシミュレータと連携し、PLATEAU都市データ上でのドローン飛行を、地図および3Dビューでリアルタイムに可視化する ブラウザビューアと連携可能に


`${HOME}/hakoniwa` 配下で以下のコマンドを実行し、リポジトリをクローンしてください。
    
```bash
git clone --recursive https://github.com/hakoniwalab/hakoniwa-mav-viewer.git
```


## アップデート対象ライブラリ等

- hakoniwa-pdu Python ライブラリ
  - target version: 1.3.5
- hakoniwa-core-full debian パッケージ
  - target version: 1.1.1-3
- hakoniwa-drone-core docker イメージ
  - target version: v2.4.8

今回のアップデートに伴い、上記ライブラリ等のアップデートが必要です。
ただ、今回説明するアップデート手順は、コンテナパターンを前提としていますので、docker イメージのアップデートのみで完了します。

`hakoniwa-drone-core` 直下で、以下のコマンドを実行し、docker イメージをアップデートしてください。

```bash
bash docker/pull-image.bash
```

アップデートが完了したら、以下のコマンドを実行し、`hakoniwa-drone-core` の docker イメージが `v2.4.8` に更新されていることを確認してください。


```bash
docker images
```
```
REPOSITORY                                                                 TAG       IMAGE ID       CREATED         SIZE
toppersjp/hakoniwa-drone-core                                              v2.4.8    48141885726d   2 minutes ago   1.6GB
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
Version: 1.3.5
Summary: Hakoniwa PDU communication library for Python
Home-page: https://github.com/hakoniwalab
Author: 
Author-email: Takashi Mori <tmori@hakoniwa-lab.net>
License: 
Location: /Users/tmori/.local/lib/python3.10/site-packages
Requires: jsonschema, mcp, pydantic, websockets
Required-by: 
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
Version: 1.1.1-3
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

  