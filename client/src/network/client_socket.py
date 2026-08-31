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
    """
    _closed = False
    running = False
    listener_thread: threading.Thread | None = None


    def __init__(self, timeout: float = 30.0):
        self.sock: socket.socket | None = None
        self.timeout = timeout
        self.send_lock = threading.Lock()
        self.pending: dict[str, queue.Queue] = {}
        self.pending_lock = threading.Lock()
        self.push_callbacks: list[callable] = []

        self._closed = False
        self.running = False
        self.listener_thread: threading.Thread | None = None

    def connect(self, host: str, port: int) -> bool:
        """Установить TCP-соединение. Возвращает True при успехе."""
        if self._closed:
            raise ConnectionError("Socket already closed, create new ClientSocket")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((host, port))
            self.sock.settimeout(None)
            # TCP keepalive lets the OS detect a genuinely dead peer (cable
            # pulled, box crashed, NAT dropped the mapping) without us having
            # to guess at an idle timeout for the app-level protocol, which
            # is naturally silent for long stretches (no push, no requests).
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listener_thread.start()
            return True
        except Exception as e:
            print(f"[ClientSocket] Connection failed: {e}")
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
            return False

    def send_request(self, action: str, **kwargs) -> dict:
        """Отправить запрос и дождаться ответа."""
        if self._closed or self.sock is None:
            raise ConnectionError("Socket is not connected")

        req_id = uuid.uuid4().hex
        payload = {"action": action, "req_id": req_id, **kwargs}
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        msg = struct.pack(">I", len(data)) + data

        response_queue: queue.Queue = queue.Queue()
        with self.pending_lock:
            if self._closed:
                raise ConnectionError("Socket is closed")
            self.pending[req_id] = response_queue

        try:
            with self.send_lock:
                if self.sock is None:
                    raise ConnectionError("Socket is not connected")
                self.sock.sendall(msg)
        except Exception as e:
            with self.pending_lock:
                self.pending.pop(req_id, None)
            raise ConnectionError(f"Send failed: {e}")

        try:
            return response_queue.get(timeout=self.timeout)
        except queue.Empty:
            with self.pending_lock:
                self.pending.pop(req_id, None)
            raise ConnectionError("Request timeout")
        finally:
            with self.pending_lock:
                self.pending.pop(req_id, None)

    def on_push(self, callback: callable) -> None:
        """Подписать функцию на входящие push-уведомления."""
        self.push_callbacks.append(callback)

    def close(self) -> None:
        """Корректно закрыть соединение, очистить pending."""
        if self._closed:
            return
        self._closed = True
        self.running = False

        with self.pending_lock:
            for q in list(self.pending.values()):
                q.put({"status": "error", "message": "Connection closed"})
            self.pending.clear()

        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            try:
                self.sock.close()
            except OSError:
                pass
            self.sock = None

        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=5)

    # --------------------------------------------------------------------- #
    # Internal
    # --------------------------------------------------------------------- #

    def _listen_loop(self) -> None:
        while self.running and not self._closed:
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

                for cb in self.push_callbacks:
                    try:
                        cb(msg)
                    except Exception as e:
                        print(f"[Push callback error] {e}")

            except Exception as e:
                if self.running and not self._closed:
                    print(f"[ClientSocket] Listen error: {e}")
                break

        with self.pending_lock:
            for q in list(self.pending.values()):
                q.put({"status": "error", "message": "Connection lost"})
            self.pending.clear()

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
        """
        Читать ровно n байт. Блокируется, пока не придут данные, пир не
        закроет соединение или сокет не будет закрыт из другого потока
        (через close()) — без искусственного тайм-аута.

        ВАЖНО: этот метод вызывается из фонового потока-слушателя
        (_listen_loop), который простаивает бОльшую часть времени —
        сообщения (в т.ч. push) приходят нерегулярно, иногда с паузами
        в минуты. Раньше здесь стоял self.sock.settimeout(10.0): если за
        10 секунд ничего не приходило, recv() поднимал socket.timeout,
        _recv_all тихо возвращал None, и _listen_loop интерпретировал это
        как обрыв соединения и завершал поток — при этом сам TCP-сокет
        оставался открытым. Следующий send_request() успешно отправлял
        запрос (сокет ведь жив), но ответ было уже некому забрать: поток,
        читавший входящие сообщения, уже умер. Через self.timeout секунд
        response_queue.get() поднимал queue.Empty -> "Request timeout".
        Именно это и проявлялось как "иногда работает, иногда нет" —
        зависело от того, был ли перерыв между запросами больше 10 секунд.

        Реальный обрыв соединения по-прежнему обнаруживается штатно:
        recv() возвращает b"" при закрытии пиром, либо поднимает OSError,
        если сокет закрыли локально (close()) или порвался TCP. TCP
        keepalive (включён в connect()) обнаруживает "тихо умерших" пиров
        без явного закрытия соединения.
        """
        if self.sock is None:
            return None
        try:
            buf = b""
            while len(buf) < n:
                chunk = self.sock.recv(n - len(buf))
                if not chunk:
                    return None
                buf += chunk
            return buf
        except OSError:
            return None
