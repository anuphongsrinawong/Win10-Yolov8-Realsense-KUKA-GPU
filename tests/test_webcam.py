from src.camera.webcam import WebcamCamera


def main() -> None:
    cam = WebcamCamera(index=0)
    cam.open()
    ok, frame = cam.read()
    assert ok and frame is not None, "ไม่สามารถอ่านภาพจาก webcam"
    cam.release()
    print("webcam ok")


if __name__ == "__main__":
    main()

