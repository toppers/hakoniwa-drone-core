# 箱庭ドローン・コントロールLink

箱庭ドローン・コントロールLinkは、PX4や自社の制御プログラムなどを箱庭ドローンPROの仮想環境と接続し、軽量で高速な閉ループ検証を可能にするためのオプションです。

具体的には、
- 箱庭ドローンPROのコンポーネントである、`controller` のコード（制御コア）を、
- [箱庭ドローン・コントロールアダプター](https://github.com/hakoniwalab/hakoniwa-drone-control-adapter)インタフェース（Adapter Interface）を通して、
- PX4や自社の制御プログラムなどの外部制御に接続する
ためのオプションです。

お使いの制御ソフトを箱庭ドローンPROに直接接続することで、フルスタックのSITL環境に入る前の段階で、制御挙動の確認や大量・反復テストを軽量に実施できます。

SITLで最終確認する前に、本オプションで検証条件を絞り込むことで、実機試験全体の効率化と安全性向上を支援します。

外部制御の標準実装として、[箱庭ドローン・コントロールアダプターPX4](https://github.com/hakoniwalab/hakoniwa-drone-control-adapter-px4) があります。これを利用することで、PX4を箱庭ドローンPROの外部制御として利用できます。

Adapter Interface の内訳は以下の通りです。

- 高度/水平制御
- 姿勢角度制御
- 姿勢角速度制御
- ミキサー
- EKF

制御コアは、上記インタフェースを呼び出す責務を持ち、箱庭ドローンのAPIおよびRC操作APIに関する機能を実装します。

箱庭標準アダプターは、Adapter Interface の標準実装の一つです。PX4アダプターと同じ Adapter Interface に接続されますが、外部制御ではなく、従来の箱庭制御実装をアダプター化したものです。

## 補足

本ライセンスは、制御コアそのものを制限するものではありません。箱庭ドローンPROライセンス契約者は、契約範囲内で制御コアを改変できます。

箱庭ドローン無償版では、標準制御機能を利用できます。ただし、箱庭標準アダプター以外の外部制御システムとの接続機能は無効です。

## コード上の境界

箱庭ドローン・コントロールLinkのビルド境界は、CMake のビルドオプション `HAKO_ENABLE_CONTROL_LINK` で表現します。

箱庭ドローン・コントロールLinkを含まない利用形態では、以下の設定で機能提供されます。

```sh
-DHAKO_ENABLE_CONTROL_LINK=OFF
```

この設定では、箱庭標準アダプター以外の外部制御システムとの接続機能は無効になります。

箱庭ドローン・コントロールLinkのライセンス契約者は、以下の設定を利用できます。

```sh
-DHAKO_ENABLE_CONTROL_LINK=ON
```

この設定では、Adapter Interface を通した外部制御アダプター接続を有効にできます。

PX4アダプターは、コントロールLinkで利用できる標準外部アダプターとして提供します。PX4アダプターのインストール先を指定することで、PX4制御との接続が可能になります。

オリジナル制御との接続は、契約者が Adapter Interface およびPX4アダプターの実装例を参考に、契約範囲内で実装・改変することを想定します。

```sh
-DHAKO_ENABLE_CONTROL_LINK=ON \
-DHAKO_PX4_CONTROL_ADAPTER_ROOT=/path/to/hakoniwa-drone-control-adapter-px4/install
```

## ビルド方法

通常のビルドでは、箱庭ドローン・コントロールLinkは無効です。

```sh
tools/build-mac.bash build
tools/build-ubuntu.bash build
```

```powershell
.\tools\build-win.ps1
```

箱庭ドローン・コントロールLinkを有効にしてビルドする場合は、PX4アダプターを事前にインストールしたうえで、以下を実行します。

```sh
tools/build-adapter.bash build
```

この場合、PX4アダプターのインストール先は、デフォルトで以下を参照します。

```text
work/hakoniwa-drone-control-adapter-px4/install
```

インストール先を変更する場合は、引数または環境変数で指定できます。

```sh
tools/build-adapter.bash build /path/to/hakoniwa-drone-control-adapter-px4/install

HAKO_PX4_CONTROL_ADAPTER_ROOT=/path/to/hakoniwa-drone-control-adapter-px4/install \
tools/build-adapter.bash build
```

Windowsでは、以下のように `HAKO_ENABLE_CONTROL_LINK` と `HAKO_PX4_CONTROL_ADAPTER_ROOT` を指定してビルドします。

```powershell
$env:HAKO_ENABLE_CONTROL_LINK="ON"
$env:HAKO_PX4_CONTROL_ADAPTER_ROOT="C:\path\to\hakoniwa-drone-control-adapter-px4\install"
.\tools\build-win.ps1

.\tools\build-win.ps1 -Px4AdapterRoot "C:\path\to\hakoniwa-drone-control-adapter-px4\install"
```

主なコード上の対象は以下です。

| 対象                                                                | 内容                                 |
| ----------------------------------------------------------------- | ---------------------------------- |
| `src/controller/impl/orchestrator/controller_backend_factory.cpp` | PX4 control backend の生成            |
| `src/controller/impl/mixer/aircraft_mixer_factory.cpp`            | PX4 control allocation backend の生成 |
| `src/controller/impl/aircraft_controller_factory.cpp`             | PX4 config sync の実行                |
| `src/controller/impl/ekf/ekf_factory.hpp`                         | PX4 EKF adapter の生成                |
