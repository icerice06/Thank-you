import time
import cv2
import imutils
import platform
import numpy as np
from threading import Thread
from queue import Queue

class Streamer:
    
    def __init__(self):
        # OpenCL 사용 가능 여부 확인 및 설정
        if cv2.ocl.haveOpenCL():
            cv2.ocl.setUseOpenCL(True)
        print('[wandlab] ', 'OpenCL : ', cv2.ocl.haveOpenCL())
        
        self.capture = None
        self.thread = None
        self.width = 640
        self.height = 360
        self.stat = False
        self.current_time = time.time()
        self.preview_time = time.time()
        self.sec = 0
        self.Q = Queue(maxsize=128)
        self.started = False
        
    def run(self, src=0):
        # 스트리밍 시작
        self.stop()
    
        if platform.system() == 'Windows':        
            self.capture = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        else:
            self.capture = cv2.VideoCapture(src)
            
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        if self.thread is None:
            self.thread = Thread(target=self.update, args=())
            self.thread.daemon = False
            self.thread.start()
        
        self.started = True
    
    def stop(self):
        # 스트리밍 중지
        self.started = False
        
        if self.capture is not None:
            self.capture.release()
            self.clear()
            
    def update(self):
        # 프레임 업데이트 스레드
        while True:
            if self.started:
                grabbed, frame = self.capture.read()
                
                if grabbed:
                    self.Q.put(frame)
                          
    def clear(self):
        # 큐 비우기
        with self.Q.mutex:
            self.Q.queue.clear()
            
    def read(self):
        # 프레임 읽기
        return self.Q.get()

    def blank(self):
        # 빈 화면 생성
        return np.ones(shape=[self.height, self.width, 3], dtype=np.uint8)
    
    def bytescode(self):
        # 프레임을 JPEG 바이트 코드로 변환
        if not self.capture.isOpened():
            frame = self.blank()
        else:
            frame = imutils.resize(self.read(), width=int(self.width))
        
            if self.stat:
                cv2.rectangle(frame, (0,0), (120,30), (0,0,0), -1)
                fps = 'FPS : ' + str(self.fps())
                cv2.putText(frame, fps, (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv2.LINE_AA)
            
        return cv2.imencode('.jpg', frame)[1].tobytes()
    
    def fps(self):
        # 프레임 속도 계산
        self.current_time = time.time()
        self.sec = self.current_time - self.preview_time
        self.preview_time = self.current_time
        
        if self.sec > 0:
            fps = round(1 / self.sec, 1)
        else:
            fps = 1
            
        return fps
                   
    def __exit__(self):
        # 클래스 종료 시 호출되는 메서드
        print('* streamer class exit')
        self.capture.release()
