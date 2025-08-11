import numpy as np

from src.detector.yolo_detector import YOLODetector


def main() -> None:
    # สร้างภาพ dummy ทดสอบ forward (จะไม่ตรวจเจออะไรซึ่งปกติ)
    dummy = np.zeros((480, 640, 3), dtype=np.uint8)
    det = YOLODetector(model_path="yolov8n.pt", device="cpu", conf=0.25)
    _ = det.predict(dummy)
    print("detector ok")


if __name__ == "__main__":
    main()

