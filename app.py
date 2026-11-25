from flask import Flask, render_template, Response, jsonify  # jsonify 추가
from camera import VideoCamera

app = Flask(__name__)
video_camera = VideoCamera()

def generate_frames(camera):
    while True:
        frame_bytes = camera.get_frame()
        if frame_bytes is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(video_camera), mimetype='multipart/x-mixed-replace; boundary=frame')

# 📸 [마지막 4단계 웹 요청 라우터 추가]
@app.route('/capture')
def capture():
    # camera.py에 만든 저장 함수 실행
    filename = video_camera.capture_image()
    if filename:
        return jsonify({"status": "success", "filename": filename})
    else:
        return jsonify({"status": "fail", "message": "카메라 프레임 확보 실패"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True, use_reloader=False)