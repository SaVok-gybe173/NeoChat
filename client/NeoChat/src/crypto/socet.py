import socket
import json
import struct
import threading
import queue
import uuid


class ClientSocket:
    """
    TCP-клиент для мессенджера.
    Протокол: 4 байта big-endian (длина) + JSON payload.
    Поддерживает синхронные request/response (с req_id) и асинхронные push-уведомления.
    """

    def __init__(self):
        self.sock: socket.socket | None = None
        self.send_lock = threading.Lock()
        self.pending: dict[str, queue.Queue] = {}
        self.pending_lock = threading.Lock()
        self.push_callbacks: list[callable] = []
        self.listener_thread: threading.Thread | None = None
        self.running = False

    def connect(self, host: str, port: int) -> None:
        """Установить TCP-соединение и запустить фоновый слушатель."""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True, name="listen loop")
        self.listener_thread.start()

    def send_request(self, action: str, **kwargs) -> dict:
        """
        Отправить запрос и дождаться ответа.
        Автоматически добавляет req_id для сопоставления ответа.
        Поддерживает параллельные вызовы из разных потоков.
        """
        req_id = uuid.uuid4().hex
        payload = {"action": action, "req_id": req_id, **kwargs}
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        msg = struct.pack(">I", len(data)) + data

        response_queue: queue.Queue = queue.Queue()
        with self.pending_lock:
            self.pending[req_id] = response_queue

        with self.send_lock:
            self.sock.sendall(msg)

        try:
            return response_queue.get(timeout=30)
        finally:
            with self.pending_lock:
                self.pending.pop(req_id, None)

    def on_push(self, callback: callable) -> None:
        """Подписать функцию на входящие push-уведомления (new_message и др.)."""
        self.push_callbacks.append(callback)

    def close(self) -> None:
        """Корректно закрыть соединение и остановить слушатель."""
        self.running = False
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=5)

    # Internal
    
    def _listen_loop(self) -> None:
        while self.running:
            try:
                msg = self._read_message()
                if msg is None:
                    break
                
                req_id = msg.get("req_id")
                if req_id:
                    with self.pending_lock:
                        q = self.pending.get(req_id)
                    if q is not None:
                        q.put(msg)
                        continue
                
                # Push сообщение
                for cb in self.push_callbacks:
                    try:
                        cb(msg)
                    except Exception as e:
                        print(f"[Push callback error] {e}")
                        
            except Exception as e:
                if self.running:
                    print(f"[ClientSocket] Listen error: {e}")
                break

    def _read_message(self) -> dict | None:
        raw_len = self._recv_all(4)
        if not raw_len:
            return None
        length = struct.unpack(">I", raw_len)[0]
        data = self._recv_all(length)
        if not data:
            return None
        return json.loads(data.decode("utf-8"))

    def _recv_all(self, n: int) -> bytes | None:
        buf = b""
        while len(buf) < n:
            chunk = self.sock.recv(n - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf