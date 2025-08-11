import socket
import threading
from src.robot.kuka_client import KukaClient


def udp_echo_server(host: str, port: int, ready_evt: threading.Event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    ready_evt.set()
    try:
        data, addr = sock.recvfrom(65535)
        # พิมพ์แค่ยืนยัน
        print("received:", data.decode("utf-8")[:80])
    finally:
        sock.close()


def main() -> None:
    host, port = "127.0.0.1", 30010
    ready = threading.Event()
    t = threading.Thread(target=udp_echo_server, args=(host, port, ready), daemon=True)
    t.start()
    ready.wait(3)

    client = KukaClient(host, port, protocol="udp")
    client.send_json({"hello": "kuka"})
    client.close()
    print("kuka client ok")


if __name__ == "__main__":
    main()

