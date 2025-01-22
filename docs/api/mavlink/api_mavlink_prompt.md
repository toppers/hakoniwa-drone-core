# タスクの説明
## タスクの概要

本タスクでは、[mavlink.hpp](https://github.com/toppers/hakoniwa-drone-core/blob/main/include/mavlink.hpp) のクラス設計情報を作成します。

クラス設計情報としては、以下の情報を整理します。

- クラス概要
- クラス図
- シーケンス図
- API リファレンスへの参照（リンクは不要です）

ドキュメントとしては、以下を参考にしてください。

https://github.com/toppers/hakoniwa-drone-core/blob/main/docs/api/comm/api_comm.md


## 対象

- MavlinkServiceIoType
- MavlinkMsgType
- MavlinkHakoMessage
- IMavlinkCommEndpointType
- IMavLinkService
- MavLinkServiceContainer

## 前提情報

- ユーザは、最初にMavLinkServiceContainerをインスタンス化します。
- 次に、IMavLinkServiceを create() で生成します。
- この際に、インスタンスのインデックス番号(0からの連番)とserver_endpointとclient_endpointを指定します。
- server_endpointは、自分がTCP \UDPのサーバーとしてのIPアドレスとポート番号を指定します。
- client_endpointは、自分がTCP \UDPのクライアントとしてのIPアドレスとポート番号を指定します。nullptrを指定すると、自動採番されます。
- 生成したIMavLinkServiceを、MavLinkServiceContainerに登録します。
