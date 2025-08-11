from typing import Any, Dict, List, Optional, Tuple

import numpy as np


class YOLODetector:
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        device: str = "auto",
        conf: float = 0.5,
        imgsz: int = 640,
        classes: Optional[List[int]] = None,
    ) -> None:
        from ultralytics import YOLO  # import เมื่อใช้งานจริง เพื่อลดเวลานำเข้า

        self.model = YOLO(model_path)
        self.device = device
        self.conf = conf
        self.imgsz = imgsz
        self.classes = classes

    def predict(self, frame: np.ndarray):
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            imgsz=self.imgsz,
            device=self.device,
            classes=self.classes,
            verbose=False,
        )
        return results

    @staticmethod
    def to_dicts(result) -> List[Dict[str, Any]]:
        # แปลงผลลัพธ์ตัวแรกเป็น list ของ dict เพื่อส่งออก/serialize
        dets: List[Dict[str, Any]] = []
        if result is None or result.boxes is None:
            return dets
        boxes = result.boxes
        xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, "cpu") else boxes.xyxy
        confs = boxes.conf.cpu().numpy() if hasattr(boxes.conf, "cpu") else boxes.conf
        clss = boxes.cls.cpu().numpy() if hasattr(boxes.cls, "cpu") else boxes.cls
        for i in range(len(xyxy)):
            x1, y1, x2, y2 = [float(v) for v in xyxy[i]]
            dets.append(
                {
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(confs[i]),
                    "class_id": int(clss[i]),
                }
            )
        return dets

    @staticmethod
    def draw(result, frame: np.ndarray) -> np.ndarray:
        # ใช้ plot() จาก ultralytics เพื่อวาดกล่อง
        return result.plot() if result is not None else frame

