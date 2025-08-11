## Win10 YOLOv8 + RealSense + KUKA (GPU/CPU switch) – พร้อมใช้งานและทดสอบแยกส่วน

โปรเจกต์นี้ช่วยให้คุณทำ Object Detection ด้วย YOLOv8 บน Windows 10 ได้อย่างรวดเร็ว โดยเลือกกล้องได้ทั้ง `webcam` หรือ `Intel RealSense` พร้อมตัวเลือกการรันแบบ `GPU` หรือ `CPU` โดยสลับได้ง่ายผ่านพารามิเตอร์ นอกจากนี้ยังเตรียมสคริปต์สำหรับการติดตั้งสภาพแวดล้อม, รันทดสอบแยกส่วน, และอัปโหลดขึ้น GitHub ได้สะดวก

### คุณสมบัติหลัก
- รองรับ YOLOv8 พร้อมเลือกโมเดล เช่น `yolov8n.pt`
- เลือกแหล่งภาพ: `webcam` หรือ `realsense` (สี)
- สลับโหมดประมวลผล: `GPU` หรือ `CPU`
- ทดสอบแยกส่วน (camera, detector, robot client)
- สคริปต์ตั้งค่าสภาพแวดล้อมและการรันแบบง่ายใน Windows PowerShell
- สคริปต์อัปโหลดขึ้น GitHub เมื่อมีการเปลี่ยนแปลง

---

### โครงสร้างโปรเจกต์โดยสรุป

```
.
├─ config/
│  └─ config.yaml
├─ scripts/
│  ├─ setup_env.ps1               # ติดตั้ง venv + ไลบรารี (เลือก GPU/CPU, ติดตั้ง RealSense ได้)
│  ├─ run.ps1                     # ตัวอย่างคำสั่งรันแบบปรับแต่งได้
│  ├─ run_webcam.ps1              # รัน YOLO ด้วย Webcam
│  ├─ run_realsense.ps1           # รัน YOLO ด้วย RealSense
│  └─ git_init_and_push.ps1       # สคริปต์ช่วย init + push ขึ้น GitHub
├─ src/
│  ├─ app.py                      # Entry point หลัก (CLI)
│  ├─ camera/
│  │  ├─ webcam.py
│  │  └─ realsense.py
│  ├─ detector/
│  │  └─ yolo_detector.py
│  ├─ robot/
│  │  └─ kuka_client.py
│  └─ utils/
│     └─ draw.py
├─ tests/
│  ├─ test_webcam.py
│  ├─ test_realsense.py
│  ├─ test_detector.py
│  └─ test_robot_client.py
├─ .gitignore
├─ requirements.txt
└─ README.md
```

---

### ข้อกำหนดเบื้องต้น
- Windows 10 (PowerShell)
- Python 3.10 หรือ 3.11 (แนะนำ 3.10)
- (ทางเลือก) NVIDIA GPU + ติดตั้งไดรเวอร์/CUDA ให้ตรงกับเวอร์ชัน PyTorch ที่จะใช้
- (ทางเลือก) Intel RealSense SDK/ไดรเวอร์ หากต้องการใช้กล้อง RealSense

---

### ขั้นตอนติดตั้งแบบรวดเร็ว (ครั้งแรก)
1) เปิด PowerShell ในโฟลเดอร์โปรเจกต์นี้
2) ติดตั้งสภาพแวดล้อมและไลบรารี

รันแบบ GPU พร้อมติดตั้งไลบรารี RealSense:

```
scripts\setup_env.ps1 -Device GPU -WithRealSense
```

หรือรันแบบ CPU โดยไม่ใช้ RealSense:

```
scripts\setup_env.ps1 -Device CPU
```

สคริปต์จะสร้าง virtual environment ที่ `.venv` และติดตั้ง PyTorch + ไลบรารีจำเป็น

---

### วิธีใช้งาน (ตัวอย่างรวดเร็ว)
- Webcam + GPU (ค่าเริ่มต้น: แสดงผลบนหน้าจอ):
```
scripts\run_webcam.ps1
```

- RealSense + CPU:
```
scripts\run_realsense.ps1 -Device CPU
```

- ปรับแต่งเองผ่านสคริปต์รวม:
```
scripts\run.ps1 -Source webcam -Device GPU -Model yolov8n.pt -Conf 0.5 -Show
```

พารามิเตอร์ที่ใช้บ่อย:
- `-Source`: `webcam` | `realsense` | path วิดีโอ/รูป
- `-Device`: `GPU` หรือ `CPU` (ในตัวโปรแกรมจะ map เป็น `cuda` หรือ `cpu`)
- `-Model`: ชื่อโมเดลเช่น `yolov8n.pt` หรือ path โมเดลของคุณเอง
- `-Conf`: ค่า confidence threshold (เช่น 0.5)
- `-Show`: ให้เปิดหน้าต่างแสดงผล
- `-Save`: บันทึกวิดีโอ Annotated ลงโฟลเดอร์ `runs/`

หากพบปัญหา cuDNN บนบางเครื่อง (เช่นข้อความเตือน Conv_v8): เพิ่มตัวเลือก `-DisableCudnn` ได้ เช่น
```
scripts\run_webcam.ps1 -Device GPU -DisableCudnn
```

---

### การทดสอบแยกส่วน
เปิดสภาพแวดล้อมก่อน:
```
.\.venv\Scripts\Activate.ps1
```

- ทดสอบ Webcam:
```
python -m tests.test_webcam
```

- ทดสอบ RealSense (ต้องติดตั้ง `pyrealsense2` และต่อกล้อง):
```
python -m tests.test_realsense
```

- ทดสอบ Detector:
```
python -m tests.test_detector
```

- ทดสอบ KUKA Client (ส่ง UDP loopback):
```
python -m tests.test_robot_client
```

---

### อัปโหลดขึ้น GitHub อย่างง่าย
ครั้งแรก (init repo + ตั้ง origin + push):
```
scripts\git_init_and_push.ps1 -RepoUrl "https://github.com/<USER>/<REPO>.git" -Branch "main" -Message "init" 
```

ครั้งถัดไป (commit + push):
```
scripts\git_init_and_push.ps1 -Message "update: ..."
```

หมายเหตุ: หากใช้ Token ให้กำหนดใน Credential ของเครื่องหรือใส่ใน URL รูปแบบ `https://<TOKEN>@github.com/<USER>/<REPO>.git` (พิจารณาความปลอดภัยของ Token)

---

### Troubleshooting (GPU/cuDNN)
- หากขึ้นคำเตือน/ข้อผิดพลาดเกี่ยวกับ cuDNN Conv_v8 ให้ลอง:
  - เพิ่มพารามิเตอร์ `-DisableCudnn` (หรือ `--disable-cudnn` ใน CLI)
  - ลดขนาดภาพ `--imgsz 640` หรือใช้รุ่นโมเดลเล็กลง (`yolov8n.pt`)
  - อัปเดต NVIDIA Driver/CUDA ให้ตรงกับเวอร์ชันที่ติดตั้ง PyTorch
  - ทดลองโหมด CPU ชั่วคราว: `scripts\run_webcam.ps1 -Device CPU`

---

### คำแนะนำเกี่ยวกับ RealSense
- ติดตั้ง `Intel RealSense SDK` และไดรเวอร์ให้พร้อมก่อนใช้งาน
- หากติดตั้ง `pyrealsense2` ไม่สำเร็จผ่าน `pip` อาจต้องตรงกับเวอร์ชัน Python/SDK ของเครื่อง หรือใช้ wheel ที่สอดคล้องตามรุ่น

---

### การเชื่อมต่อกับ KUKA
โมดูล `src/robot/kuka_client.py` เตรียมโครง TCP/UDP Client ไว้ส่งผลการตรวจจับในรูป JSON ไปยังคอนโทรลเลอร์/PC ปลายทาง คุณสามารถปรับโปรโตคอล/ฟอร์แมตให้ตรงกับ KUKA RSI/Sunrise/แอปพลิเคชันของคุณได้

---

### ปรับแต่งค่าเริ่มต้น
ตั้งค่าจากไฟล์ `config/config.yaml` หรือส่งค่าผ่าน CLI (CLI จะมีสิทธิ์ทับค่าจาก config)

---

### ใบอนุญาต
โค้ดในโปรเจกต์นี้อยู่ภายใต้ MIT License (ปรับใช้ได้อิสระ โปรดตรวจสอบไลเซนส์ของโมเดล/ไลบรารีที่ใช้งานร่วมด้วย)

