import cv2
from typing import Optional, Tuple


class WebcamCamera:
    def __init__(
        self,
        index: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[int] = None,
    ) -> None:
        self.index = index
        self.width = width
        self.height = height
        self.fps = fps
        self.cap: Optional[cv2.VideoCapture] = None

    def open(self) -> None:
        # สำหรับ Windows แนะนำใช้ CAP_DSHOW เพื่อลดดีเลย์เปิดกล้อง
        self.cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW)
        if self.width:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height:
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        if self.fps:
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
        if not self.cap.isOpened():
            raise RuntimeError(f"ไม่สามารถเปิด webcam ที่ index {self.index}")

    def read(self) -> Tuple[bool, Optional[any]]:
        if self.cap is None:
            raise RuntimeError("กล้องยังไม่ถูกเปิด เรียกใช้ open() ก่อน")
        return self.cap.read()

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None

