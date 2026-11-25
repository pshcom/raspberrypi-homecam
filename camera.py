import cv2
from picamera2 import Picamera2
import numpy as np
from datetime import datetime  # [추가] 파일명에 시간을 넣기 위함
import os

class VideoCamera(object):
    def __init__(self):
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(
            main={'format': 'XRGB8888', 'size': (640, 360)}
        ))
        self.camera.start()
        self.prev_frame = None
        self.current_bgr_frame = None  # [추가] 캡처를 위해 현재 프레임을 보관할 변수

    def __del__(self):
        try:
            self.camera.stop()
        except:
            pass

    def get_frame(self):
        image = self.camera.capture_array()
        if image is None:
            return None
        
        frame = image[:, :, 0:3]
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.prev_frame is None:
            self.prev_frame = gray
            self.current_bgr_frame = frame_bgr.copy()  # 현재 프레임 복사 저장
            ret, buffer = cv2.imencode('.jpg', frame_bgr)
            return buffer.tobytes()
        
        frame_delta = cv2.absdiff(self.prev_frame, gray)
        ret, thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
            motion_detected = True
            
        if motion_detected:
            cv2.putText(frame_bgr, "MOTION DETECTED", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            
        self.prev_frame = gray
        self.current_bgr_frame = frame_bgr.copy()  # [추가] 가공(사각형/글씨)이 완료된 현재 프레임을 복사해서 보관
        
        ret, buffer = cv2.imencode('.jpg', frame_bgr)
        return buffer.tobytes()

    # 💾 [마지막 4단계 핵심 함수 추가]
    def capture_image(self):
        if self.current_bgr_frame is not None:
            # 대략 '20260613_153022.jpg' 형태로 중복 없는 파일명 생성
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{now}.jpg"
            
            # cv2.imwrite를 사용하여 라즈베리파이 현재 디렉토리에 사진 저장
            cv2.imwrite(filename, self.current_bgr_frame)
            print(f"[알림] 사진이 성공적으로 저장되었습니다: {filename}")
            return filename
        return None