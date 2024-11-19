import queue
import threading

class MessageQueue:
    def __init__(self, max_size=100):
        """
        メッセージキュー
        :param max_size: キューの最大サイズ（デフォルト: 100）
        """
        self.queue = queue.Queue(maxsize=max_size)
        self.lock = threading.Lock()
        self.listened_types = set()  # リッスンするメッセージタイプを保持するセット

    def set_listened_types(self, types):
        """
        リッスンするメッセージタイプを設定
        :param types: リッスンするメッセージタイプのリストまたはセット
        """
        with self.lock:
            self.listened_types = set(types)

    def enqueue(self, message):
        """
        メッセージをキューに追加（リッスン型に基づくフィルタリング）
        :param message: MavlinkMessageオブジェクト
        """
        with self.lock:
            if message.msg_type not in self.listened_types:
                return  # リッスン対象でないメッセージは無視

            try:
                self.queue.put(message, block=False)
            except queue.Full:
                print("Queue is full! Oldest message will be discarded.")
                self.queue.get()  # 古いメッセージを削除
                self.queue.put(message, block=False)

    def dequeue(self):
        """
        キューからメッセージを取得
        :return: MavlinkMessageオブジェクト
        """
        with self.lock:
            try:
                return self.queue.get(block=False)
            except queue.Empty:
                print("Queue is empty!")
                return None

    def size(self):
        """
        現在のキューサイズを返す
        """
        with self.lock:
            return self.queue.qsize()

    def is_empty(self):
        """
        キューが空かどうかを返す
        """
        with self.lock:
            return self.queue.empty()
