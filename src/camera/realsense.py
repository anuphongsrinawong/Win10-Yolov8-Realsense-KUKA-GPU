from typing import Optional, Tuple

try:
    import pyrealsense2 as rs
    _HAS_RS = True
except Exception:
    _HAS_RS = False

import numpy as np


class RealSenseCamera:
    def __init__(
        self,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        enable_depth: bool = False,
    ) -> None:
        if not _HAS_RS:
            raise ImportError(
                "ไม่พบ pyrealsense2 โปรดติดตั้งด้วย scripts/setup_env.ps1 -WithRealSense หรือ pip install pyrealsense2"
            )
        self.width = width
        self.height = height
        self.fps = fps
        self.enable_depth = enable_depth
        self.pipeline: Optional[rs.pipeline] = None
        self.align: Optional[rs.align] = None

    def open(self) -> None:
        self.pipeline = rs.pipeline()
        config = rs.config()
        config.enable_stream(rs.stream.color, self.width, self.height, rs.format.bgr8, self.fps)
        if self.enable_depth:
            config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.fps)
            self.align = rs.align(rs.stream.color)
        self.pipeline.start(config)

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        if self.pipeline is None:
            raise RuntimeError("กล้องยังไม่ถูกเปิด เรียกใช้ open() ก่อน")
        frames = self.pipeline.wait_for_frames()
        if self.enable_depth and self.align is not None:
            frames = self.align.process(frames)
        color_frame = frames.get_color_frame()
        if not color_frame:
            return False, None
        color_image = np.asanyarray(color_frame.get_data())
        return True, color_image

    def release(self) -> None:
        if self.pipeline is not None:
            self.pipeline.stop()
            self.pipeline = None

