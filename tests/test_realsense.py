def main() -> None:
    try:
        from src.camera.realsense import RealSenseCamera
    except Exception as e:
        print("ข้ามการทดสอบ RealSense:", e)
        return

    cam = RealSenseCamera()
    cam.open()
    ok, frame = cam.read()
    assert ok and frame is not None, "ไม่สามารถอ่านภาพจาก RealSense"
    cam.release()
    print("realsense ok")


if __name__ == "__main__":
    main()

