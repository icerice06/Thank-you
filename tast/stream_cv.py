# https://elomaot.blogspot.com/2021/08/fastapi-opencv.html
# https://access-violation.tistory.com/17
# uvicorn main:app --reload
# http://127.0.0.1:8000/video
# http://172.28.33.137:8000/video
# uvicorn main:app --reload --host=0.0.0.0 --port=8000
import cv2

def get_stream_video():
    # camera 정의
    cam = cv2.VideoCapture(0)

    while True:
        # 카메라 값 불러오기
        success, frame = cam.read()

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            # frame을 byte로 변경 후 특정 식??으로 변환 후에
            # yield로 하나씩 넘겨준다.
            frame = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(frame) + b'\r\n')