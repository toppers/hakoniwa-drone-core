# アーキテクチャ

![image](https://github.com/user-attachments/assets/e36e559e-a424-4a4d-a66a-a498378c375e)

- comm (通信モジュール) : TCP/UDP の通信インタフェース
  - ICommServer API: サーバーサイドの通信機能を提供
    - TCP/UDPプロトコルに対応した通信サーバーの生成
    - エンドポイントでの接続待ち受けと通信管理
    - 使用前には必ずcomm_init()の呼び出しが必要
  - ICommClient API: クライアントサイドの通信機能を提供
    - TCP/UDPプロトコルに対応した通信クライアントの生成
    - 送信元・送信先エンドポイントの指定による通信確立
    - 使用前には必ずcomm_init()の呼び出しが必要
  - ICommIO API: 通信データの送受信機能を提供
    - データの送信・受信操作の抽象化インターフェース
    - TCPでは到達保証とリトライ機能を提供
    - UDPでは高速な通信を実現（到達保証なし）
  - 詳細な API 仕様は[サーバー](/docs/architecture/comm/server/api_comm_server.md)、[クライアント](/docs/architecture/comm/client/api_comm_client.md)、[IO](/docs/architecture/comm/io/api_comm_io.md)を参照
- mavlink (MAVLINK通信) : MAVLINK通信のインタフェース
- physics (物理モデル) :  [機体の物理モデル](/docs/architecture/physics/README-ja.md)
- controller (制御モデル) : 機体の制御モデル
- aircraft (機体モデル) : 物理モデルおよびセンサ/アクチュエータを統合した機体モデル
- service (サービス)
  - aircaft_service (機体サービス) : 箱庭なしで、PX4と連携するためのサービス
  - drone_service (ドローンサービス) : 箱庭なしで、制御/物理モデルを実行するためのサービス
- hakoniwa (箱庭) :  serviceを箱庭に統合したサービス
- logger (ログ) :  機体のログ
- config (コンフィグ) :  ドローンのコンフィグ

# パラメータ説明

- [機体パラメータ](/docs/architecture/config/aircraft-param.md)
- [制御パラメータ](/docs/architecture/config/controller-param.md)