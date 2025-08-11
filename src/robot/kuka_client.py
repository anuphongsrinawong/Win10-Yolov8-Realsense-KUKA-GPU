import json
import socket
from typing import Any, Dict, Optional


class KukaClient:
    def __init__(self, host: str, port: int, protocol: str = "udp") -> None:
        self.host = host
        self.port = port
        self.protocol = protocol.lower()
        self.sock: Optional[socket.socket] = None

    def connect(self) -> None:
        if self.protocol == "udp":
            # UDP ไม่ต้อง connect จริงจัง แต่เตรียม socket ไว้
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        elif self.protocol == "tcp":
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        else:
            raise ValueError("protocol ต้องเป็น 'udp' หรือ 'tcp'")

    def send_json(self, payload: Dict[str, Any]) -> None:
        if self.sock is None:
            self.connect()
        data = json.dumps(payload).encode("utf-8")
        if self.protocol == "udp":
            assert self.sock is not None
            self.sock.sendto(data, (self.host, self.port))
        else:
            assert self.sock is not None
            self.sock.sendall(data + b"\n")

    def close(self) -> None:
        if self.sock is not None:
            try:
                if self.protocol == "tcp":
                    self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            self.sock.close()
            self.sock = None

