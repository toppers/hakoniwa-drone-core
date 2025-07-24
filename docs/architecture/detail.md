# アーキテクチャ

![image](https://github.com/user-attachments/assets/e36e559e-a424-4a4d-a66a-a498378c375e)

- [comm (通信モジュール)](/docs/architecture/comm/README.md) : TCP/UDP の通信インタフェース
- [mavlink (MAVLINK通信)](/docs/architecture/mavlink/README.md) : MAVLINK通信のインタフェース
- [physics (物理モデル)](/docs/architecture/physics/README-ja.md) : 機体の物理モデル
- [controller (制御モデル)](/docs/architecture/controller/README.md) : 機体の制御モデル
- [aircraft (機体モデル)](/docs/architecture/aircraft/README.md) : 物理モデルおよびセンサ/アクチュエータを統合した機体モデル
- [service (サービス)](/docs/architecture/service/README.md) : ドローンサービスと機体サービスを提供
- [hakoniwa (箱庭)](/docs/architecture/hakoniwa/README.md) : serviceを箱庭に統合したサービス
- [logger (ログ)](/docs/architecture/logger/README.md) : 機体のログ
- [config (コンフィグ)](/docs/architecture/config/README.md) : ドローンのコンフィグ

# パラメータ説明

- [機体パラメータ](/docs/architecture/config/aircraft-param.md)
- [制御パラメータ](/docs/architecture/config/controller-param.md)