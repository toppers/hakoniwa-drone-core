import os

class BinaryLogger:
    def __init__(self, log_filename):
        """
        バイナリデータ保存用のロガー
        :param log_filename: 保存するファイルのパス
        """
        self.log_filename = log_filename

        # 初期化時にログファイルを空にする（既存データをクリア）
        with open(self.log_filename, "wb") as log_file:
            pass

    def save_binary_data(self, data):
        """
        バイナリデータをファイルに保存
        :param data: 保存するバイナリデータ
        """
        try:
            with open(self.log_filename, "ab") as log_file:
                log_file.write(data)
        except Exception as e:
            print(f"Failed to save binary data: {e}")

    def clear_log(self):
        """
        ログファイルを初期化（既存の内容を削除）
        """
        with open(self.log_filename, "wb") as log_file:
            pass
