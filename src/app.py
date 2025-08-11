import argparse
import os
import sys
import time
from typing import Optional

import cv2
import yaml

from .camera.webcam import WebcamCamera
from .detector.yolo_detector import YOLODetector
from .robot.kuka_client import KukaClient

try:
    from .camera.realsense import RealSenseCamera
    HAS_RS = True
except Exception:
    HAS_RS = False


def load_config(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def parse_args(defaults: dict) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 – Webcam/RealSense – GPU/CPU switch")
    parser.add_argument("--source", type=str, default=defaults.get("source", "webcam"), help="webcam | realsense | path ไฟล์")
    parser.add_argument("--webcam-index", type=int, default=defaults.get("webcam_index", 0))
    parser.add_argument("--device", type=str, default=defaults.get("device", "auto"), help="auto | cpu | cuda:0")
    parser.add_argument("--model", type=str, default=defaults.get("model", "yolov8n.pt"))
    parser.add_argument("--conf", type=float, default=defaults.get("conf", 0.5))
    parser.add_argument("--imgsz", type=int, default=defaults.get("imgsz", 640))
    parser.add_argument("--disable-cudnn", dest="disable_cudnn", action="store_true", help="ปิดใช้ cuDNN (ช่วยเลี่ยงบาง error ของ Conv_v8)")
    # show
    parser.add_argument("--show", dest="show", action="store_true")
    parser.add_argument("--no-show", dest="show", action="store_false")
    parser.set_defaults(show=defaults.get("show", True))
    # save
    parser.add_argument("--save", dest="save", action="store_true")
    parser.add_argument("--no-save", dest="save", action="store_false")
    parser.set_defaults(save=defaults.get("save", False))

    # KUKA
    parser.add_argument("--send-to-kuka", dest="send_to_kuka", action="store_true")
    parser.add_argument("--no-send-to-kuka", dest="send_to_kuka", action="store_false")
    parser.set_defaults(send_to_kuka=defaults.get("send_to_kuka", False))
    parser.add_argument("--kuka-host", type=str, default=defaults.get("kuka", {}).get("host", "127.0.0.1"))
    parser.add_argument("--kuka-port", type=int, default=defaults.get("kuka", {}).get("port", 30010))
    parser.add_argument("--kuka-protocol", type=str, default=defaults.get("kuka", {}).get("protocol", "udp"))

    return parser.parse_args()


def open_source(args: argparse.Namespace):
    source = args.source
    if source == "webcam":
        cam = WebcamCamera(index=args.webcam_index)
        cam.open()
        return cam, "webcam"
    elif source == "realsense":
        if not HAS_RS:
            raise RuntimeError("ต้องติดตั้ง pyrealsense2 ก่อน หรือใช้ scripts/setup_env.ps1 -WithRealSense")
        cam = RealSenseCamera()
        cam.open()
        return cam, "realsense"
    else:
        # path ไฟล์ภาพ/วิดีโอ
        if not os.path.exists(source):
            raise FileNotFoundError(f"ไม่พบไฟล์/โฟลเดอร์: {source}")
        return source, "file"


def run() -> None:
    defaults = load_config(os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "config.yaml"))
    args = parse_args(defaults)

    device = args.device
    if device.lower() == "gpu":
        device = "cuda:0"
    elif device.lower() == "cpu":
        device = "cpu"

    if args.disable_cudnn and device.startswith("cuda"):
        try:
            import torch
            torch.backends.cudnn.enabled = False
            torch.backends.cudnn.benchmark = False
        except Exception:
            pass

    detector = YOLODetector(model_path=args.model, device=device, conf=args.conf, imgsz=args.imgsz)

    src, kind = open_source(args)

    writer: Optional[cv2.VideoWriter] = None
    if args.save:
        os.makedirs("runs", exist_ok=True)
        ts = time.strftime("%Y%m%d-%H%M%S")
        out_path = os.path.join("runs", f"output-{ts}.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        fps = 30.0
        width, height = 640, 480
        if kind == "webcam":
            width = int(src.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(src.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = float(src.cap.get(cv2.CAP_PROP_FPS) or 30.0)
        writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    kuka: Optional[KukaClient] = None
    if args.send_to_kuka:
        kuka = KukaClient(args.kuka_host, args.kuka_port, args.kuka_protocol)
        kuka.connect()

    try:
        if kind in ("webcam", "realsense"):
            while True:
                ok, frame = src.read()
                if not ok or frame is None:
                    break
                results = detector.predict(frame)
                res0 = results[0] if results else None
                annotated = detector.draw(res0, frame)

                if kuka is not None and res0 is not None:
                    dets = YOLODetector.to_dicts(res0)
                    payload = {"timestamp": time.time(), "detections": dets}
                    try:
                        kuka.send_json(payload)
                    except Exception:
                        pass

                if writer is not None:
                    writer.write(annotated)
                if args.show:
                    cv2.imshow("YOLOv8", annotated)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break
        else:
            # ใช้ API ของ ultralytics สำหรับไฟล์/โฟลเดอร์
            from ultralytics import YOLO

            model = detector.model  # reuse model
            results_gen = model.predict(
                source=src,
                conf=detector.conf,
                imgsz=detector.imgsz,
                device=detector.device,
                stream=True,
                verbose=False,
            )
            for res in results_gen:
                frame = res.orig_img
                annotated = res.plot()
                if kuka is not None:
                    dets = YOLODetector.to_dicts(res)
                    payload = {"timestamp": time.time(), "detections": dets}
                    try:
                        kuka.send_json(payload)
                    except Exception:
                        pass
                if writer is not None and frame is not None:
                    writer.write(annotated)
                if args.show and frame is not None:
                    cv2.imshow("YOLOv8", annotated)
                    if cv2.waitKey(1) & 0xFF == 27:
                        break
    finally:
        if isinstance(src, (WebcamCamera,)):
            src.release()
        if HAS_RS and isinstance(src, (RealSenseCamera,)):
            src.release()
        if writer is not None:
            writer.release()
        if args.show:
            cv2.destroyAllWindows()
        if kuka is not None:
            kuka.close()


if __name__ == "__main__":
    run()

