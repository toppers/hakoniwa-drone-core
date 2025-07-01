@echo off
REM WindowsでPS4コントローラによるPDU送信を実行するバッチファイル

REM 仮想環境を有効化（必要に応じて）
REM call ..\venv\Scripts\activate.bat

REM 相対パスでHAKO_BINARY_PATHを設定（バッチファイルから見た位置）
set HAKO_BINARY_PATH=..\..\thirdparty\hakoniwa-ros2pdu\pdu\offset
echo HAKO_BINARY_PATH=%HAKO_BINARY_PATH%

REM スクリプトの実行
python rc-custom-pdu.py ^
  --config ..\..\config\pdudef\webavatar.json ^
  --rc_config .\rc_config\ps4-control.json ^
  --uri ws://172.31.9.252:8765

pause
